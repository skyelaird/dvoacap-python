#!/usr/bin/env python3
"""Test high frequency predictions (17.7, 21.6, 25.9 MHz)"""

import sys
sys.path.insert(0, 'src')

import numpy as np
from dvoacap.prediction_engine import PredictionEngine
from dvoacap.path_geometry import GeoPoint

# Test configuration
engine = PredictionEngine()
engine.params.ssn = 100.0
engine.params.month = 6
engine.params.tx_power = 500000.0
engine.params.tx_location = GeoPoint.from_degrees(35.80, -5.90)
engine.params.min_angle = np.deg2rad(0.1)

rx_location = GeoPoint.from_degrees(44.90, 20.50)
utc_fraction = 1.0 / 24.0

# Test frequencies from reference
test_freqs = [17.73, 21.65, 25.89]

# Reference SNR values from voacapx.out (UTC hour 1)
reference_snr = {
    17.73: 72,   # From line 44
    21.65: 32,   # From line 44
    25.89: -33   # From line 44 (negative = very poor)
}

print("=" * 80)
print("HIGH FREQUENCY TESTING - UTC Hour 1")
print("=" * 80)
print(f"Circuit MUF at hour 1: 16.2 MHz (from reference)")
print()

engine.predict(rx_location=rx_location, utc_time=utc_fraction, frequencies=test_freqs)

print(f"DVOACAP Circuit MUF: {engine.circuit_muf.muf:.2f} MHz")
print()

for i, freq in enumerate(test_freqs):
    if i < len(engine.predictions):
        pred = engine.predictions[i]
        ref_snr = reference_snr.get(freq, None)

        print(f"{freq:.2f} MHz:")
        print(f"  Mode:        {pred.get_mode_name(engine.path.dist)}")
        print(f"  SNR:         {pred.signal.snr_db:.1f} dB (reference: {ref_snr} dB)")
        print(f"  Signal:      {pred.signal.power_dbw:.1f} dBW")
        print(f"  Noise:       {pred.noise_dbw:.1f} dBW")
        print(f"  Loss:        {pred.signal.total_loss_db:.1f} dB")
        print(f"  MUF day:     {pred.signal.muf_day:.3f}")
        print(f"  Reliability: {pred.signal.reliability*100:.1f}%")
        print()
    else:
        print(f"{freq:.2f} MHz: NO PREDICTION (no modes found)")
        print()

print("NOTES:")
print("  - 17.73 MHz is above MUF (~16.2 MHz) but should still have some propagation")
print("  - 21.65 MHz is well above MUF, should have poor SNR (~32 dB)")
print("  - 25.89 MHz is very far above MUF, should fail or have negative SNR (~-33 dB)")
