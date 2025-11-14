#!/usr/bin/env python3
"""Debug high-frequency (25.90 MHz) loss calculations."""

import sys
sys.path.insert(0, 'src')

import numpy as np
from dvoacap.prediction_engine import PredictionEngine
from dvoacap.path_geometry import GeoPoint

# Setup engine
engine = PredictionEngine()
engine.params.ssn = 100
engine.params.month = 6
engine.params.tx_location = GeoPoint(
    lat=np.deg2rad(35.80),
    lon=np.deg2rad(-5.90)
)
rx_location = GeoPoint(
    lat=np.deg2rad(44.90),
    lon=np.deg2rad(20.50)
)

# Test problematic hours
test_hours = [1, 6, 7]  # Hours with large SNR deviations

print("="*70)
print("HIGH-FREQUENCY (25.90 MHz) LOSS INVESTIGATION")
print("="*70)

for hour in test_hours:
    utc_time = hour / 24.0

    # Run prediction
    engine.predict(rx_location, utc_time, [25.90])
    pred = engine.predictions[0]

    print(f"\nHour {hour:02d}:")
    print(f"  Mode: {pred.get_mode_name(engine.path.dist)}")
    print(f"  Hop count: {pred.hop_count}")
    print(f"  MUF day: {pred.signal.muf_day:.4f}")

    # Get the best mode to see loss components
    if engine._best_mode:
        mode = engine._best_mode
        print(f"\n  Loss components:")
        print(f"    Free space loss: {mode.free_space_loss:.2f} dB")
        print(f"    Absorption loss: {mode.absorption_loss:.2f} dB × {mode.hop_cnt} hops = {mode.hop_cnt * mode.absorption_loss:.2f} dB")
        print(f"    Deviation term: {mode.deviation_term:.2f} dB × {mode.hop_cnt} hops = {mode.hop_cnt * mode.deviation_term:.2f} dB")
        print(f"    Ground loss: {mode.ground_loss:.2f} dB × {mode.hop_cnt-1} = {mode.ground_loss * (mode.hop_cnt-1):.2f} dB")
        print(f"    Auroral adj: {engine._adj_auroral:.2f} dB")
        print(f"    Total loss: {mode.signal.total_loss_db:.2f} dB")

    print(f"\n  Signal:")
    print(f"    Power: {pred.signal.power_dbw:.2f} dBW")
    print(f"    Noise: {pred.noise_dbw:.2f} dBW")
    print(f"    SNR: {pred.signal.snr_db:.2f} dB")
    print(f"    Reliability: {pred.signal.reliability*100:.1f}%")

print("\n" + "="*70)
print("REFERENCE VALUES (from VOACAP):")
print("  Hour 01: SNR = -33.0 dB, MUFday = 0.00")
print("  Hour 06: SNR = +42.0 dB, MUFday = 0.02")
print("  Hour 07: SNR = +54.0 dB, MUFday = 0.08")
print("="*70)
