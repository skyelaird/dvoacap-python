#!/usr/bin/env python3
"""Debug absorption calculation in detail"""

import sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.dvoacap.path_geometry import GeoPoint
from src.dvoacap.prediction_engine import PredictionEngine

# Test case: 6.10 MHz @ 1200 UTC
engine = PredictionEngine()
engine.params.ssn = 100.0
engine.params.month = 6
engine.params.tx_power = 500000
engine.params.tx_location = GeoPoint.from_degrees(35.80, -5.90)
engine.params.min_angle = np.deg2rad(0.1)

rx_location = GeoPoint.from_degrees(44.90, 20.50)
utc_fraction = 12 / 24.0
freq_mhz = 6.10

engine.predict(rx_location=rx_location, utc_time=utc_fraction, frequencies=[freq_mhz])

print("=" * 80)
print("ABSORPTION CALCULATION ANALYSIS - 6.10 MHz @ 1200 UTC")
print("=" * 80)
print()

# Profile information
prof = engine._current_profile
print("IONOSPHERIC PROFILE:")
print(f"  E-layer foE: {prof.e.fo:.2f} MHz")
print(f"  F1-layer foF1: {prof.f1.fo:.2f} MHz")
print(f"  F2-layer foF2: {prof.f2.fo:.2f} MHz")
print(f"  Absorption Index: {prof.absorption_index:.4f}")
print(f"  Avg Absorption Index: {engine._absorption_index:.4f}")
print(f"  Gyro Frequency: {prof.gyro_freq:.2f} MHz")
print()

# Absorption calculation parameters
ac = 677.2 * engine._absorption_index
bc = (freq_mhz + prof.gyro_freq) ** 1.98
print("ABSORPTION PARAMETERS:")
print(f"  ac = 677.2 × {engine._absorption_index:.4f} = {ac:.2f}")
print(f"  bc = ({freq_mhz:.2f} + {prof.gyro_freq:.2f})^1.98 = {bc:.2f}")
print()

# Mode details
if engine._modes:
    mode = engine._modes[0]  # Best mode (2-hop E)

    print("MODE DETAILS:")
    print(f"  Layer: E")
    print(f"  Hops: {mode.hop_cnt}")
    print(f"  Vertical Frequency: {mode.ref.vert_freq:.2f} MHz")
    print(f"  True Height: {mode.ref.true_height:.1f} km")
    print(f"  Elevation: {np.rad2deg(mode.ref.elevation):.2f}°")
    print()

    # Check which absorption path is taken
    is_de_mode = mode.ref.vert_freq <= prof.e.fo
    print(f"ABSORPTION PATH:")
    print(f"  vert_freq ({mode.ref.vert_freq:.2f}) <= foE ({prof.e.fo:.2f})? {is_de_mode}")
    print(f"  Using: {'D-E mode formula' if is_de_mode else 'F-layer formula'}")
    print()

    if is_de_mode:
        # D-E mode calculation (from prediction_engine.py lines 671-680)
        if mode.ref.true_height >= 88.0:  # HTLOSS = 88.0
            nsqr = 10.2
        else:
            XNUZ = 63.07
            HNU = 4.39
            nsqr = XNUZ * np.exp(
                -2 * (1 + 3 * (mode.ref.true_height - 70) / 18) / HNU
            )

        h_eff = min(100.0, mode.ref.true_height)

        adx = (engine._adj_ccir252_a + engine._adj_ccir252_b *
               np.log(max(mode.ref.vert_freq / prof.e.fo, engine._adj_de_loss)))

        print("D-E MODE CALCULATION:")
        print(f"  true_height ({mode.ref.true_height:.1f}) >= 88.0? {mode.ref.true_height >= 88.0}")
        print(f"  nsqr = {nsqr:.2f}")
        print(f"  h_eff = min(100.0, {mode.ref.true_height:.1f}) = {h_eff:.1f} km")
        print(f"  adj_ccir252_a = {engine._adj_ccir252_a:.4f}")
        print(f"  adj_ccir252_b = {engine._adj_ccir252_b:.4f}")
        print(f"  adj_de_loss = {engine._adj_de_loss:.4f}")
        print(f"  adx = {adx:.4f}")
        print()

        # Cosine of incidence
        cos_inc = engine._cos_of_incidence(mode.ref.elevation, h_eff)
        print(f"  cos(incidence) at h={h_eff:.1f} km: {cos_inc:.4f}")
        print(f"  sec(incidence) = 1/cos = {1/cos_inc:.2f}")
        print()

        # Final absorption
        absorption = ac / (bc + nsqr) / cos_inc
        print("ABSORPTION CALCULATION:")
        print(f"  absorption = ac / (bc + nsqr) / cos(inc)")
        print(f"  absorption = {ac:.2f} / ({bc:.2f} + {nsqr:.2f}) / {cos_inc:.4f}")
        print(f"  absorption = {ac:.2f} / {bc + nsqr:.2f} / {cos_inc:.4f}")
        print(f"  absorption = {ac / (bc + nsqr):.2f} / {cos_inc:.4f}")
        print(f"  absorption = {absorption:.2f} dB/hop")
        print()

        print("TOTAL ABSORPTION:")
        print(f"  {absorption:.2f} dB/hop × {mode.hop_cnt} hops = {absorption * mode.hop_cnt:.2f} dB")
        print()

        # What it should be (rough estimate)
        print("EXPECTED (rough estimate for daytime E-layer):")
        print("  Typical daytime absorption at 6 MHz: ~5-15 dB/hop")
        print("  For 2 hops: ~10-30 dB total")
        print(f"  Actual: {absorption * mode.hop_cnt:.1f} dB - **{(absorption * mode.hop_cnt) / 15:.1f}x too high!**")
        print()

print("=" * 80)
