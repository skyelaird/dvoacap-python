#!/usr/bin/env python3
"""Test mode selection for problematic frequencies"""
import sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.dvoacap.path_geometry import GeoPoint
from src.dvoacap.prediction_engine import PredictionEngine

# Test case from SampleIO/voacapx.out
# Tangier, Morocco -> Belgrade
TX_LAT, TX_LON = 35.80, -5.90
RX_LAT, RX_LON = 44.90, 20.50
SSN = 100.0
MONTH = 6
TX_POWER = 500000  # 500 kW

FREQUENCIES = [7.20, 9.70]  # Problematic frequencies
UTC_HOURS = [1.0, 11.0]  # Night (working) vs Midday (broken)

# Reference values from VOACAP
REFERENCE = {
    (7.20, 1.0): {'mode': '1F2', 'snr': 76, 'rel': 0.61},
    (9.70, 1.0): {'mode': '1F2', 'snr': 79, 'rel': 0.70},
    (7.20, 11.0): {'mode': '2E', 'snr': -64, 'rel': 0.00},
    (9.70, 11.0): {'mode': '2E', 'snr': -15, 'rel': 0.00},
}

print("=" * 80)
print("TESTING MODE SELECTION: 7.20 MHz and 9.70 MHz")
print("=" * 80)

for utc in UTC_HOURS:
    print(f"\n{'=' * 80}")
    print(f"UTC HOUR: {utc:.1f}")
    print(f"{'=' * 80}\n")

    # Setup engine
    engine = PredictionEngine()
    engine.params.ssn = SSN
    engine.params.month = MONTH
    engine.params.tx_power = TX_POWER
    engine.params.tx_location = GeoPoint.from_degrees(TX_LAT, TX_LON)
    engine.params.min_angle = np.deg2rad(0.1)

    rx_location = GeoPoint.from_degrees(RX_LAT, RX_LON)
    utc_fraction = utc / 24.0

    # Run predictions for both frequencies
    engine.predict(rx_location=rx_location, utc_time=utc_fraction, frequencies=FREQUENCIES)

    for freq, pred in zip(FREQUENCIES, engine.predictions):
        print(f"\n--- {freq:.2f} MHz @ {utc:.1f} UTC ---")

        if pred:
            mode_name = pred.get_mode_name(engine.path.dist)
            snr = pred.signal.snr_db
            rel = pred.signal.reliability

            print(f"  Mode: {mode_name}")
            print(f"  Hops: {pred.hop_count}")
            print(f"  SNR: {snr:.1f} dB")
            print(f"  Reliability: {rel*100:.1f}%")
            print(f"  TX Elevation: {np.rad2deg(pred.tx_elevation):.1f}°")
            print(f"  Virtual Height: {pred.virt_height:.1f} km")
            print(f"  Total Loss: {pred.signal.total_loss_db:.1f} dB")

            # Get reference
            ref = REFERENCE.get((freq, utc), {'mode': '?', 'snr': 0, 'rel': 0})

            print(f"\n  VOACAP Reference:")
            print(f"    Mode: {ref['mode']}")
            print(f"    SNR: {ref['snr']} dB")
            print(f"    Reliability: {ref['rel']*100:.0f}%")

            snr_error = snr - ref['snr']
            rel_error = (rel - ref['rel']) * 100

            print(f"\n  ERRORS:")
            print(f"    SNR Error: {snr_error:+.1f} dB")
            print(f"    Reliability Error: {rel_error:+.1f}%")

            if abs(snr_error) > 10:
                print(f"    ⚠️  SNR ERROR EXCEEDS ±10 dB THRESHOLD!")
            if abs(rel_error) > 20:
                print(f"    ⚠️  RELIABILITY ERROR EXCEEDS ±20% THRESHOLD!")
        else:
            print("  NO PREDICTION GENERATED")

print("\n" + "=" * 80)
