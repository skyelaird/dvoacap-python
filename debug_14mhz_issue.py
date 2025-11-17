#!/usr/bin/env python3
"""Debug why 14.1 MHz is showing no propagation"""

import sys
sys.path.insert(0, 'src')

import numpy as np
from dvoacap.prediction_engine import PredictionEngine
from dvoacap.path_geometry import GeoPoint

# VOACAP chart scenario
tx_location = GeoPoint.from_degrees(44.35, -64.29)  # FN74ui
rx_location = GeoPoint.from_degrees(49.0, -60.0)     # ~500 km away

engine = PredictionEngine()
engine.params.ssn = 81.0
engine.params.month = 11
engine.params.tx_power = 80.0
engine.params.tx_location = tx_location
engine.params.min_angle = np.deg2rad(3.0)

utc_time = 18.0 / 24.0  # 1800 UTC
freq = 14.10

print("=" * 80)
print("Debugging 14.1 MHz prediction")
print("=" * 80)
print(f"TX: FN74ui (44.35N, 64.29W)")
print(f"RX: (49.0N, 60.0W) - ~500 km away")
print(f"Frequency: {freq} MHz, Time: 1800 UTC, SSN: 81")
print("=" * 80)
print()

try:
    result = engine.predict(rx_location=rx_location, utc_time=utc_time, frequencies=[freq])

    print(f"Result type: {type(result)}")
    print(f"Result length: {len(result) if result else 0}")

    if result and len(result) > 0:
        pred = result[0]
        print(f"\nPrediction object: {pred}")
        print(f"Number of modes: {len(pred.modes) if hasattr(pred, 'modes') else 'N/A'}")

        if hasattr(pred, 'modes') and pred.modes:
            print("\nModes found:")
            for i, mode in enumerate(pred.modes):
                print(f"\n  Mode {i+1}:")
                if hasattr(mode, 'signal'):
                    print(f"    SNR: {mode.signal.snr_db:.2f} dB")
                    print(f"    Reliability: {mode.signal.reliability * 100:.1f}%")
                    print(f"    Total loss: {mode.signal.total_loss_db:.2f} dB")
                    print(f"    MUF day: {mode.signal.muf_day:.6f}")
                if hasattr(mode, 'layer'):
                    print(f"    Layer: {mode.layer}")
                if hasattr(mode, 'hop_cnt'):
                    print(f"    Hops: {mode.hop_cnt}")
        else:
            print("\nNo modes in prediction!")
    else:
        print("\nNo prediction result!")

except Exception as e:
    import traceback
    print(f"Error: {e}")
    traceback.print_exc()

print("\n" + "=" * 80)
