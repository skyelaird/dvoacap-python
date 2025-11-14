#!/usr/bin/env python3
"""Quick test to check SNR calculation for 6.07 MHz"""

import sys
sys.path.insert(0, 'src')

import numpy as np
from dvoacap.prediction_engine import PredictionEngine
from dvoacap.path_geometry import GeoPoint

# Reference test case from voacapx.out
# Path: Tangier, Morocco (35.80°N, 5.90°W) → Belgrade (44.90°N, 20.50°E)
# Month: June 1994, SSN: 100
# UTC Hour: 1
# Frequency: 6.07 MHz
# Expected: SNR = 83 dB, N_DBW = -149 dBW, S_DBW = -73 dBW (wait, that's only 76 dB difference)

engine = PredictionEngine()
engine.params.ssn = 100.0
engine.params.month = 6
engine.params.tx_power = 500000.0  # 500 kW
engine.params.tx_location = GeoPoint.from_degrees(35.80, -5.90)
engine.params.min_angle = np.deg2rad(0.1)

rx_location = GeoPoint.from_degrees(44.90, 20.50)
utc_fraction = 1.0 / 24.0

print("=" * 80)
print("SNR Calculation Test - 6.07 MHz")
print("=" * 80)
print(f"TX: {35.80:.2f}°N, {5.90:.2f}°W (Tangier)")
print(f"RX: {44.90:.2f}°N, {20.50:.2f}°E (Belgrade)")
print(f"UTC Hour: 1, SSN: 100, Month: June")
print(f"TX Power: 500 kW")
print()

engine.predict(rx_location=rx_location, utc_time=utc_fraction, frequencies=[6.07])

if len(engine.predictions) > 0:
    pred = engine.predictions[0]
    print("DVOACAP-Python Results:")
    print(f"  Mode:             {pred.get_mode_name(engine.path.dist)}")
    print(f"  Signal Power:     {pred.signal.power_dbw:.1f} dBW")
    print(f"  Noise Power:      {pred.noise_dbw:.1f} dBW")
    print(f"  SNR:              {pred.signal.snr_db:.1f} dB")
    print(f"  Total Loss:       {pred.signal.total_loss_db:.1f} dB")
    print(f"  TX Gain:          {pred.signal.tx_gain_db:.1f} dB")
    print(f"  RX Gain:          {pred.signal.rx_gain_db:.1f} dB")
    print(f"  MUF day:          {pred.signal.muf_day:.3f}")
    print(f"  Reliability:      {pred.signal.reliability*100:.1f}%")
    print()

    # Show noise components
    print("Noise Components:")
    print(f"  Atmospheric:      {engine.noise_model.atmospheric_noise.value.median:.1f} dBW")
    print(f"  Galactic:         {engine.noise_model.galactic_noise.value.median:.1f} dBW")
    print(f"  Man-made:         {engine.noise_model.man_made_noise.value.median:.1f} dBW")
    print(f"  Combined:         {engine.noise_model.combined:.1f} dBW")
    print()

    print("VOACAP Reference (from voacapx.out, line 42-44):")
    print(f"  Signal Power:     -73.0 dBW")
    print(f"  Noise Power:      -149.0 dBW")
    print(f"  SNR:              76.0 dB")  # Let me verify this calculation
    print()

    print("Discrepancy:")
    signal_diff = pred.signal.power_dbw - (-73.0)
    noise_diff = pred.noise_dbw - (-149.0)
    snr_diff = pred.signal.snr_db - 76.0
    print(f"  Signal Power:     {signal_diff:+.1f} dB")
    print(f"  Noise Power:      {noise_diff:+.1f} dB")
    print(f"  SNR:              {snr_diff:+.1f} dB")
else:
    print("ERROR: No prediction generated!")
