#!/usr/bin/env python3
"""
Test dashboard generation performance claims from wiki.

Wiki claims: "10 regions × 7 bands × 12 time points can take 60-90 seconds"
Let's verify this claim.
"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.dvoacap.path_geometry import GeoPoint
from src.dvoacap.prediction_engine import PredictionEngine


def test_dashboard_scenario():
    """Test the exact scenario from the wiki: 10 regions × 7 bands × 12 time points."""

    print("=" * 80)
    print("TESTING WIKI CLAIM: Dashboard Generation Performance")
    print("=" * 80)
    print("\nWiki states: '10 regions × 7 bands × 12 time points can take 60-90 seconds'")
    print("\nLet's test this claim...\n")

    # 10 regions (receivers) around the world
    regions = [
        ("New York", GeoPoint.from_degrees(40.7128, -74.0060)),
        ("London", GeoPoint.from_degrees(51.5074, -0.1278)),
        ("Tokyo", GeoPoint.from_degrees(35.6762, 139.6503)),
        ("Sydney", GeoPoint.from_degrees(-33.8688, 151.2093)),
        ("Moscow", GeoPoint.from_degrees(55.7558, 37.6173)),
        ("Beijing", GeoPoint.from_degrees(39.9042, 116.4074)),
        ("Rio", GeoPoint.from_degrees(-22.9068, -43.1729)),
        ("Cairo", GeoPoint.from_degrees(30.0444, 31.2357)),
        ("Mumbai", GeoPoint.from_degrees(19.0760, 72.8777)),
        ("Vancouver", GeoPoint.from_degrees(49.2827, -123.1207)),
    ]

    # 7 bands (common HF bands)
    bands = [3.5, 7.0, 10.1, 14.0, 18.1, 21.0, 28.0]  # MHz

    # 12 time points (every 2 hours)
    time_points = [i/24.0 for i in range(0, 24, 2)]  # 12 time points

    # Transmitter location (San Francisco)
    tx_location = GeoPoint.from_degrees(37.7749, -122.4194)

    # Initialize engine
    engine = PredictionEngine()
    engine.params.ssn = 100.0
    engine.params.month = 6
    engine.params.tx_power = 100
    engine.params.tx_location = tx_location

    total_predictions = len(regions) * len(bands) * len(time_points)
    print(f"Total predictions to run: {len(regions)} regions × {len(bands)} bands × {len(time_points)} time points = {total_predictions}")
    print()

    start_time = time.time()
    count = 0

    for region_name, rx_location in regions:
        for band in bands:
            for time_point in time_points:
                engine.predict(rx_location=rx_location, utc_time=time_point, frequencies=[band])
                count += 1

                if count % 100 == 0:
                    elapsed = time.time() - start_time
                    rate = count / elapsed
                    print(f"Progress: {count}/{total_predictions} predictions ({count*100/total_predictions:.1f}%) - {elapsed:.2f}s - {rate:.1f} pred/sec")

    elapsed = time.time() - start_time

    print("\n" + "=" * 80)
    print("RESULTS")
    print("=" * 80)
    print(f"Total predictions: {total_predictions}")
    print(f"Total time: {elapsed:.2f} seconds")
    print(f"Average per prediction: {elapsed/total_predictions*1000:.2f} ms")
    print(f"Predictions per second: {total_predictions/elapsed:.1f}")
    print()
    print(f"Wiki claim: 60-90 seconds")
    print(f"Actual time: {elapsed:.2f} seconds")
    print()

    if elapsed < 60:
        speedup = 60 / elapsed
        print(f"✓ MUCH FASTER than wiki claim!")
        print(f"  Performance is {speedup:.1f}x faster than minimum claimed time")
        print(f"  Performance is {90/elapsed:.1f}x faster than maximum claimed time")
        return False  # Wiki claim is wrong
    else:
        print(f"✓ Wiki claim appears accurate")
        return True  # Wiki claim is correct


if __name__ == '__main__':
    wiki_is_correct = test_dashboard_scenario()
    sys.exit(0 if wiki_is_correct else 1)
