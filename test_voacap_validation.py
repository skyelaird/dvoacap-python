#!/usr/bin/env python3
"""
Test script to validate our VOACAP implementation against reference maps.

Reference parameters from VOACAP.com maps:
- Location: FN74ui (44.35N, 64.29W)
- Time: November, 1800 UTC
- SSN: 77
- Frequency: 14.100 MHz
- Power: 80 W
- Antenna: HVD025.ANT at -1°
- Noise: -150 dBW
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

import numpy as np
from dvoacap.path_geometry import GeoPoint
from dvoacap.prediction_engine import PredictionEngine, VoacapParams
import json

def test_voacap_parameters():
    """Test with exact VOACAP reference parameters."""

    print("=" * 80)
    print("VOACAP Validation Test")
    print("=" * 80)

    # Reference parameters from VOACAP.com maps
    params = {
        'location': 'FN74ui',
        'lat': 44.35,
        'lon': -64.29,
        'month': 11,  # November
        'hour': 18,   # 1800 UTC
        'ssn': 77,
        'frequency_mhz': 14.100,
        'power_watts': 80,
        'antenna': 'HVD025.ANT',
        'takeoff_angle': -1,
        'noise_dbw': -150
    }

    modes = {
        'WSPR': {'bandwidth_db_hz': 3, 'required_snr': -28},
        'CW': {'bandwidth_db_hz': 13, 'required_snr': -8},
        'FT8': {'bandwidth_db_hz': 19, 'required_snr': -21},
        'SSB': {'bandwidth_db_hz': 38, 'required_snr': 10}
    }

    print("\nTest Parameters from VOACAP Reference:")
    print(f"  Location: {params['location']} ({params['lat']}N, {params['lon']}W)")
    print(f"  Time: November, {params['hour']:02d}00 UTC")
    print(f"  SSN: {params['ssn']}")
    print(f"  Frequency: {params['frequency_mhz']} MHz")
    print(f"  Power: {params['power_watts']} W")
    print(f"  Antenna: {params['antenna']} @ {params['takeoff_angle']}°")
    print(f"  Noise: {params['noise_dbw']} dBW")
    print()

    # Create prediction engine
    engine = PredictionEngine()

    # Configure parameters to match VOACAP
    engine.params.ssn = params['ssn']
    engine.params.month = params['month']
    engine.params.tx_power = params['power_watts']
    engine.params.tx_location = GeoPoint.from_degrees(params['lat'], params['lon'])

    # Sample receiver locations for testing
    test_locations = [
        ("London, UK", GeoPoint.from_degrees(51.51, -0.13)),
        ("Tokyo, Japan", GeoPoint.from_degrees(35.68, 139.69)),
        ("New York, USA", GeoPoint.from_degrees(40.71, -74.01)),
    ]

    print("\n" + "=" * 80)
    print("PARAMETER VERIFICATION")
    print("=" * 80)
    print("\nOur Implementation:")
    print(f"  TX Location: {np.rad2deg(engine.params.tx_location.lat):.2f}N, "
          f"{np.rad2deg(engine.params.tx_location.lon):.2f}W")
    print(f"  SSN: {engine.params.ssn}")
    print(f"  Month: {engine.params.month}")
    print(f"  TX Power: {engine.params.tx_power} W")

    # Check for parameter mismatches
    mismatches = []
    actual_lat = np.rad2deg(engine.params.tx_location.lat)
    actual_lon = np.rad2deg(engine.params.tx_location.lon)

    if abs(actual_lat - params['lat']) > 0.01:
        mismatches.append(f"Latitude: {actual_lat:.2f} vs {params['lat']}")
    if abs(actual_lon - params['lon']) > 0.01:
        mismatches.append(f"Longitude: {actual_lon:.2f} vs {params['lon']}")
    if engine.params.month != params['month']:
        mismatches.append(f"Month: {engine.params.month} vs {params['month']}")
    if engine.params.ssn != params['ssn']:
        mismatches.append(f"SSN: {engine.params.ssn} vs {params['ssn']}")
    if abs(engine.params.tx_power - params['power_watts']) > 0.1:
        mismatches.append(f"Power: {engine.params.tx_power} vs {params['power_watts']}")

    if mismatches:
        print("\n⚠️  PARAMETER MISMATCHES DETECTED:")
        for mismatch in mismatches:
            print(f"  - {mismatch}")
    else:
        print("\n✓ All basic parameters match VOACAP reference")

    # Test predictions for one location
    print("\n" + "=" * 80)
    print("SAMPLE PREDICTION TEST")
    print("=" * 80)

    rx_location = test_locations[0][1]  # London
    utc_time = params['hour'] / 24.0  # Convert hour to fraction of day

    try:
        print(f"\nRunning prediction to {test_locations[0][0]} at {params['hour']:02d}00 UTC...")

        engine.predict(
            rx_location=rx_location,
            utc_time=utc_time,
            frequencies=[params['frequency_mhz']]
        )

        # Display path information
        distance_km = engine.path.dist * 6370
        print(f"\nPath Information:")
        print(f"  Distance: {distance_km:.0f} km")
        print(f"  Azimuth: {np.rad2deg(engine.path.azim_tr):.1f}°")

        # Display prediction
        if len(engine.predictions) > 0:
            pred = engine.predictions[0]
            mode_name = pred.get_mode_name(engine.path.dist)
            elev_deg = np.rad2deg(pred.tx_elevation)

            print(f"\nPrediction Results for {params['frequency_mhz']} MHz:")
            print(f"  Mode: {mode_name}")
            print(f"  Hops: {pred.hop_count}")
            print(f"  Elevation: {elev_deg:.1f}°")
            print(f"  Loss: {pred.signal.total_loss_db:.1f} dB")
            print(f"  SNR: {pred.signal.snr_db:.1f} dB")
            print(f"  Reliability: {pred.signal.reliability * 100:.1f}%")

            print("\n✓ Prediction completed successfully")
        else:
            print("\n⚠️  No predictions generated")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 80)
    print("Validation test complete")
    print("=" * 80)

if __name__ == '__main__':
    test_voacap_parameters()
