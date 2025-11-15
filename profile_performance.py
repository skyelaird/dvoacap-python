#!/usr/bin/env python3
"""
Performance Profiling for DVOACAP Prediction Engine

Profiles the prediction engine to identify bottlenecks and optimization opportunities.
"""

import cProfile
import pstats
import io
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.dvoacap.path_geometry import GeoPoint
from src.dvoacap.prediction_engine import PredictionEngine


def profile_single_prediction():
    """Profile a single prediction run"""
    print("=" * 80)
    print("PROFILING: Single Prediction")
    print("=" * 80)

    engine = PredictionEngine()

    tx = GeoPoint.from_degrees(35.889167, -5.323333)  # Tangier
    rx = GeoPoint.from_degrees(44.816667, 20.466667)  # Belgrade

    # Set engine parameters
    engine.params.ssn = 100.0
    engine.params.month = 6
    engine.params.tx_power = 100
    engine.params.tx_location = tx

    profiler = cProfile.Profile()
    profiler.enable()

    # Run prediction
    engine.predict(rx_location=rx, utc_time=12.0/24.0, frequencies=[14.0])

    profiler.disable()

    # Print statistics
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s)
    ps.strip_dirs()
    ps.sort_stats('cumulative')
    ps.print_stats(30)  # Top 30 functions

    print(s.getvalue())
    return profiler


def profile_multi_frequency():
    """Profile multiple frequencies (typical use case)"""
    print("\n" + "=" * 80)
    print("PROFILING: Multi-Frequency Prediction (24 frequencies)")
    print("=" * 80)

    engine = PredictionEngine()

    tx = GeoPoint.from_degrees(35.889167, -5.323333)  # Tangier
    rx = GeoPoint.from_degrees(44.816667, 20.466667)  # Belgrade

    # Set engine parameters
    engine.params.ssn = 100.0
    engine.params.month = 6
    engine.params.tx_power = 100
    engine.params.tx_location = tx

    frequencies = [3.5, 5.0, 7.0, 10.1, 14.0, 18.1, 21.0, 24.9, 28.0]

    profiler = cProfile.Profile()
    profiler.enable()

    start = time.time()
    for freq in frequencies:
        engine.predict(rx_location=rx, utc_time=12.0/24.0, frequencies=[freq])
    elapsed = time.time() - start

    profiler.disable()

    print(f"\nTotal time for {len(frequencies)} frequencies: {elapsed:.2f} seconds")
    print(f"Average time per prediction: {elapsed/len(frequencies):.3f} seconds")

    # Print statistics
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s)
    ps.strip_dirs()
    ps.sort_stats('cumulative')
    ps.print_stats(30)

    print(s.getvalue())
    return profiler


def profile_24hour_scan():
    """Profile 24-hour time scan"""
    print("\n" + "=" * 80)
    print("PROFILING: 24-Hour Time Scan")
    print("=" * 80)

    engine = PredictionEngine()

    tx = GeoPoint.from_degrees(35.889167, -5.323333)  # Tangier
    rx = GeoPoint.from_degrees(44.816667, 20.466667)  # Belgrade

    # Set engine parameters
    engine.params.ssn = 100.0
    engine.params.month = 6
    engine.params.tx_power = 100
    engine.params.tx_location = tx

    profiler = cProfile.Profile()
    profiler.enable()

    start = time.time()
    for hour in range(24):
        engine.predict(rx_location=rx, utc_time=hour/24.0, frequencies=[14.0])
    elapsed = time.time() - start

    profiler.disable()

    print(f"\nTotal time for 24 hours: {elapsed:.2f} seconds")
    print(f"Average time per hour: {elapsed/24:.3f} seconds")

    # Print statistics
    s = io.StringIO()
    ps = pstats.Stats(profiler, stream=s)
    ps.strip_dirs()
    ps.sort_stats('cumulative')
    ps.print_stats(30)

    print(s.getvalue())
    return profiler


def benchmark_comparison():
    """Compare performance across different scenarios"""
    print("\n" + "=" * 80)
    print("PERFORMANCE BENCHMARKS")
    print("=" * 80)

    engine = PredictionEngine()

    tx = GeoPoint.from_degrees(35.889167, -5.323333)
    rx = GeoPoint.from_degrees(44.816667, 20.466667)

    # Set engine parameters
    engine.params.ssn = 100.0
    engine.params.month = 6
    engine.params.tx_power = 100
    engine.params.tx_location = tx

    # Single prediction
    start = time.time()
    for _ in range(10):
        engine.predict(rx_location=rx, utc_time=12.0/24.0, frequencies=[14.0])
    single_time = (time.time() - start) / 10

    print(f"Single prediction (avg of 10 runs): {single_time:.3f} seconds")

    # Area coverage simulation (10x10 grid = 100 points)
    print("\nSimulating area coverage (100 predictions)...")
    start = time.time()
    count = 0
    for lat_offset in range(-5, 5):
        for lon_offset in range(-5, 5):
            rx_test = GeoPoint.from_degrees(
                44.816667 + lat_offset,
                20.466667 + lon_offset
            )
            engine.predict(rx_location=rx_test, utc_time=12.0/24.0, frequencies=[14.0])
            count += 1
    area_time = time.time() - start

    print(f"Area coverage (100 predictions): {area_time:.2f} seconds")
    print(f"Average per prediction: {area_time/100:.3f} seconds")

    # Performance targets
    print("\n" + "=" * 80)
    print("PERFORMANCE TARGETS")
    print("=" * 80)
    print(f"Current single prediction: {single_time:.3f}s")
    print(f"Target: <1.000s ({'✓ PASS' if single_time < 1.0 else '✗ NEEDS WORK'})")
    print(f"\nCurrent area coverage (100 points): {area_time:.2f}s")
    print(f"Target: <30s ({'✓ PASS' if area_time < 30 else '✗ NEEDS WORK'})")


if __name__ == '__main__':
    print("DVOACAP Performance Profiling")
    print("=" * 80)

    # Run all profiling tests
    profile_single_prediction()
    profile_multi_frequency()
    profile_24hour_scan()
    benchmark_comparison()

    print("\n" + "=" * 80)
    print("PROFILING COMPLETE")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Identify hot spots in the profiling output above")
    print("2. Focus optimization on functions with highest cumulative time")
    print("3. Common targets:")
    print("   - Fourier map interpolation")
    print("   - Ionospheric profile computation")
    print("   - Ray path calculations")
    print("   - Coefficient file loading")
