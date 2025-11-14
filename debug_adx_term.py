#!/usr/bin/env python3
"""Debug ADX term calculation"""
import sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.dvoacap.path_geometry import GeoPoint
from src.dvoacap.prediction_engine import PredictionEngine

# Test case: 9.70 MHz @ 11 UTC
TX_LAT, TX_LON = 35.80, -5.90
RX_LAT, RX_LON = 44.90, 20.50
SSN = 100.0
MONTH = 6
TX_POWER = 500000
FREQ = 9.70
UTC = 11.0

engine = PredictionEngine()
engine.params.ssn = SSN
engine.params.month = MONTH
engine.params.tx_power = TX_POWER
engine.params.tx_location = GeoPoint.from_degrees(TX_LAT, TX_LON)
engine.params.min_angle = np.deg2rad(0.1)

rx_location = GeoPoint.from_degrees(RX_LAT, RX_LON)
utc_fraction = UTC / 24.0

engine.predict(rx_location=rx_location, utc_time=utc_fraction, frequencies=[FREQ])

print("=" * 80)
print("ADX TERM ANALYSIS")
print("=" * 80)

print(f"\nGlobal Adjustments:")
print(f"  _adj_de_loss: {engine._adj_de_loss:.6f}")
print(f"  _adj_ccir252_a: {engine._adj_ccir252_a:.3f}")
print(f"  _adj_ccir252_b: {engine._adj_ccir252_b:.3f}")

prof = engine._current_profile
print(f"\nIonospheric Profile:")
print(f"  foE: {prof.e.fo:.2f} MHz")
print(f"  foF2: {prof.f2.fo:.2f} MHz")

# Find E-layer mode
e_mode = None
for mode in engine._modes:
    if mode.layer == 'E' and mode.hop_cnt == 2:
        e_mode = mode
        break

if e_mode:
    print(f"\n2E Mode Parameters:")
    print(f"  vert_freq: {e_mode.ref.vert_freq:.2f} MHz")
    print(f"  Ratio (vert_freq / foE): {e_mode.ref.vert_freq / prof.e.fo:.4f}")
    print(f"  _adj_de_loss: {engine._adj_de_loss:.4f}")

    # Calculate ADX step by step
    ratio = e_mode.ref.vert_freq / prof.e.fo
    max_val = max(ratio, engine._adj_de_loss)
    log_val = np.log(max_val)
    adx = engine._adj_ccir252_a + engine._adj_ccir252_b * log_val

    print(f"\n  ADX Calculation:")
    print(f"    max(ratio, _adj_de_loss) = max({ratio:.4f}, {engine._adj_de_loss:.4f}) = {max_val:.4f}")
    print(f"    ln({max_val:.4f}) = {log_val:.4f}")
    print(f"    ADX = {engine._adj_ccir252_a:.3f} + {engine._adj_ccir252_b:.3f} × {log_val:.4f}")
    print(f"    ADX = {adx:.2f} dB")

    print(f"\n  Actual deviation_term: {e_mode.deviation_term:.2f} dB")

    print(f"\n  PROBLEM: ADX is negative!")
    print(f"  This REDUCES total loss instead of increasing it.")
    print(f"\n  SOLUTION: Need to ensure the argument to ln() is >= 1.0")
    print(f"  The _adj_de_loss value should be >= 1.0, but it's {engine._adj_de_loss:.4f}")
