#!/usr/bin/env python3
"""Debug why no modes are found for high frequencies"""

import sys
sys.path.insert(0, 'src')

import numpy as np
from dvoacap.prediction_engine import PredictionEngine
from dvoacap.path_geometry import GeoPoint

# Monkey-patch to see what's happening
original_evaluate_short = PredictionEngine._evaluate_short_model

def debug_evaluate_short(self, reflectrix, freq):
    """Debug version of _evaluate_short_model"""
    freq_val = self.frequencies[freq]

    print(f"\n{'='*80}")
    print(f"EVALUATING FREQUENCY: {freq_val:.2f} MHz")
    print(f"{'='*80}")
    print(f"Circuit MUF:     {self.circuit_muf.muf:.2f} MHz")
    print(f"Freq/MUF ratio:  {freq_val/self.circuit_muf.muf:.3f}")

    result = original_evaluate_short(self, reflectrix, freq)

    print(f"\nModes found: {len(self._modes)}")
    if self._modes:
        for i, mode in enumerate(self._modes):
            layer_name = mode.layer.name if hasattr(mode.layer, 'name') else str(mode.layer)
            print(f"  Mode {i+1}: {mode.hop_cnt}{layer_name}, "
                  f"MUF day={mode.signal.muf_day:.4f}, "
                  f"SNR={mode.signal.snr_db:.1f} dB")
    else:
        print(f"  NO MODES FOUND!")

    print(f"\nFinal prediction:")
    print(f"  SNR:    {result.signal.snr_db:.1f} dB")
    print(f"  Signal: {result.signal.power_dbw:.1f} dBW")
    print(f"  Noise:  {result.noise_dbw:.1f} dBW")

    return result

PredictionEngine._evaluate_short_model = debug_evaluate_short

# Run test
engine = PredictionEngine()
engine.params.ssn = 100.0
engine.params.month = 6
engine.params.tx_power = 500000.0
engine.params.tx_location = GeoPoint.from_degrees(35.80, -5.90)
engine.params.min_angle = np.deg2rad(0.1)

rx_location = GeoPoint.from_degrees(44.90, 20.50)
utc_fraction = 1.0 / 24.0

print("Testing high frequencies above MUF")
engine.predict(rx_location=rx_location, utc_time=utc_fraction, frequencies=[17.73, 21.65])
