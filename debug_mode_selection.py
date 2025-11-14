#!/usr/bin/env python3
"""Debug mode selection to understand why 2F2 is chosen instead of 1F2"""

import sys
sys.path.insert(0, 'src')

import numpy as np
from dvoacap.prediction_engine import PredictionEngine
from dvoacap.path_geometry import GeoPoint

# Monkey-patch to add debug logging
original_find_best_mode = PredictionEngine._find_best_mode

def debug_find_best_mode(self):
    """Debug version of _find_best_mode"""
    print("\n" + "=" * 80)
    print("MODE SELECTION DEBUG")
    print("=" * 80)
    print(f"Total modes found: {len(self._modes)}")
    print()

    for i, mode in enumerate(self._modes):
        layer_name = mode.layer.name if hasattr(mode.layer, 'name') else str(mode.layer)
        print(f"Mode {i+1}:")
        print(f"  Hops:        {mode.hop_cnt}")
        print(f"  Layer:       {layer_name}")
        print(f"  Hop dist:    {mode.hop_dist:.4f} rad ({mode.hop_dist * 6370:.1f} km)")
        print(f"  Elevation:   {np.rad2deg(mode.ref.elevation):.2f}°")
        print(f"  Virt height: {mode.ref.virt_height:.1f} km")
        print(f"  Total loss:  {mode.signal.total_loss_db:.1f} dB")
        print(f"  Signal pwr:  {mode.signal.power_dbw:.1f} dBW")
        print(f"  SNR:         {mode.signal.snr_db:.1f} dB")
        print(f"  Reliability: {mode.signal.reliability*100:.1f}%")
        print(f"  MUF day:     {mode.signal.muf_day:.3f}")
        print()

    result = original_find_best_mode(self)

    print("SELECTED MODE:")
    layer_name = result.layer.name if hasattr(result.layer, 'name') else str(result.layer)
    print(f"  {result.hop_cnt}{layer_name}")
    print(f"  Hops: {result.hop_cnt}, Loss: {result.signal.total_loss_db:.1f} dB")
    print(f"  Reliability: {result.signal.reliability*100:.1f}%")
    print("=" * 80)
    print()

    return result

PredictionEngine._find_best_mode = debug_find_best_mode

# Run test
engine = PredictionEngine()
engine.params.ssn = 100.0
engine.params.month = 6
engine.params.tx_power = 500000.0
engine.params.tx_location = GeoPoint.from_degrees(35.80, -5.90)
engine.params.min_angle = np.deg2rad(0.1)

rx_location = GeoPoint.from_degrees(44.90, 20.50)
utc_fraction = 1.0 / 24.0

print("Testing 6.07 MHz at UTC hour 1")

engine.predict(rx_location=rx_location, utc_time=utc_fraction, frequencies=[6.07])

print(f"Calculated distance: {engine.path.dist * 6370:.1f} km")
print(f"Expected: 1F2 mode with ~7.8° elevation, 295 km virtual height")
print()

if len(engine.predictions) > 0:
    pred = engine.predictions[0]
    print("\nFINAL PREDICTION:")
    print(f"  Mode:    {pred.get_mode_name(engine.path.dist)}")
    print(f"  SNR:     {pred.signal.snr_db:.1f} dB (reference: 76 dB)")
    print(f"  Loss:    {pred.signal.total_loss_db:.1f} dB (reference: 131 dB)")
