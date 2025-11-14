#!/usr/bin/env python3
"""Debug E-layer mode selection and absorption"""
import sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.dvoacap.path_geometry import GeoPoint
from src.dvoacap.prediction_engine import PredictionEngine

# Test case: 9.70 MHz @ 11 UTC (midday)
# This should select 2E mode but is selecting 2F2
TX_LAT, TX_LON = 35.80, -5.90
RX_LAT, RX_LON = 44.90, 20.50
SSN = 100.0
MONTH = 6
TX_POWER = 500000  # 500 kW
FREQ = 9.70
UTC = 11.0

print("=" * 80)
print(f"DEBUGGING E-LAYER MODE SELECTION: {FREQ} MHz @ {UTC} UTC")
print("=" * 80)

# Setup engine
engine = PredictionEngine()
engine.params.ssn = SSN
engine.params.month = MONTH
engine.params.tx_power = TX_POWER
engine.params.tx_location = GeoPoint.from_degrees(TX_LAT, TX_LON)
engine.params.min_angle = np.deg2rad(0.1)

rx_location = GeoPoint.from_degrees(RX_LAT, RX_LON)
utc_fraction = UTC / 24.0

# Run prediction
engine.predict(rx_location=rx_location, utc_time=utc_fraction, frequencies=[FREQ])

pred = engine.predictions[0]

print(f"\nIonospheric Parameters:")
print(f"  foE: {engine._current_profile.e.fo:.2f} MHz")
print(f"  foF1: {engine._current_profile.f1.fo:.2f} MHz")
print(f"  foF2: {engine._current_profile.f2.fo:.2f} MHz")
print(f"  Absorption Index: {engine._absorption_index:.4f}")
print(f"  CCIR252 adj_a: {engine._adj_ccir252_a:.3f}")
print(f"  CCIR252 adj_b: {engine._adj_ccir252_b:.3f}")
print(f"  Auroral adj: {engine._adj_auroral:.2f} dB")

print(f"\n{'=' * 80}")
print(f"ALL MODES FOUND (Total: {len(engine._modes)})")
print(f"{'=' * 80}")

for i, mode in enumerate(engine._modes):
    mode_name = f"{mode.hop_cnt}{mode.layer}"
    print(f"\nMode {i+1}: {mode_name}")
    print(f"  Layer: {mode.layer}")
    print(f"  Hops: {mode.hop_cnt}")
    print(f"  Elevation: {np.rad2deg(mode.ref.elevation):.2f}°")
    print(f"  Virtual Height: {mode.ref.virt_height:.1f} km")
    print(f"  True Height: {mode.ref.true_height:.1f} km")
    print(f"  Vert Freq: {mode.ref.vert_freq:.2f} MHz")
    print(f"  ---")
    print(f"  Free Space Loss: {mode.free_space_loss:.1f} dB")
    print(f"  Absorption Loss: {mode.absorption_loss:.1f} dB/hop")
    print(f"  Deviation Term: {mode.deviation_term:.1f} dB/hop")
    print(f"  Ground Loss: {mode.ground_loss:.1f} dB/hop")
    print(f"  Total Loss: {mode.signal.total_loss_db:.1f} dB")
    print(f"  ---")
    print(f"  SNR: {mode.signal.snr_db:.1f} dB")
    print(f"  Reliability: {mode.signal.reliability*100:.1f}%")
    print(f"  MUF Prob: {mode.signal.muf_day:.4f}")

print(f"\n{'=' * 80}")
print(f"BEST MODE SELECTED")
print(f"{'=' * 80}")
mode_name = pred.get_mode_name(engine.path.dist)
print(f"  Mode: {mode_name}")
print(f"  SNR: {pred.signal.snr_db:.1f} dB")
print(f"  Reliability: {pred.signal.reliability*100:.1f}%")
print(f"\n  Expected (VOACAP): 2E mode, SNR = -15 dB")
print(f"  Error: SNR is {pred.signal.snr_db - (-15):.1f} dB too high")
