#!/usr/bin/env python3
"""
Test memory usage claims from wiki.

Wiki claims:
- "Each PredictionEngine instance loads CCIR/URSI coefficient maps (~50 MB) into memory"
- "Single prediction: ~60 MB"
- "Dashboard generation: ~100 MB peak"
"""

import sys
import gc
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("Warning: psutil not available, will use basic memory tracking")

from src.dvoacap.path_geometry import GeoPoint
from src.dvoacap.prediction_engine import PredictionEngine


def get_memory_mb():
    """Get current process memory in MB."""
    if HAS_PSUTIL:
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / (1024 * 1024)
    else:
        # Fallback: read /proc/self/status
        try:
            with open('/proc/self/status') as f:
                for line in f:
                    if line.startswith('VmRSS:'):
                        return int(line.split()[1]) / 1024
        except:
            return 0


def test_memory_usage():
    """Test memory usage for various scenarios."""

    print("=" * 80)
    print("TESTING WIKI CLAIM: Memory Usage")
    print("=" * 80)
    print()

    # Baseline memory
    gc.collect()
    baseline_mem = get_memory_mb()
    print(f"Baseline memory (before loading anything): {baseline_mem:.1f} MB")
    print()

    # Wiki claim: "Each PredictionEngine loads ~50 MB of CCIR/URSI maps"
    print("Creating PredictionEngine instance...")
    engine = PredictionEngine()
    gc.collect()
    after_engine_mem = get_memory_mb()
    engine_mem = after_engine_mem - baseline_mem
    print(f"Memory after creating engine: {after_engine_mem:.1f} MB")
    print(f"Engine memory usage: {engine_mem:.1f} MB")
    print(f"Wiki claim: ~50 MB for CCIR/URSI maps")
    print()

    # Wiki claim: "Single prediction: ~60 MB"
    print("Running single prediction...")
    tx = GeoPoint.from_degrees(37.7749, -122.4194)  # San Francisco
    rx = GeoPoint.from_degrees(40.7128, -74.0060)   # New York

    engine.params.ssn = 100.0
    engine.params.month = 6
    engine.params.tx_power = 100
    engine.params.tx_location = tx

    engine.predict(rx_location=rx, utc_time=12.0/24.0, frequencies=[14.0])
    gc.collect()
    after_single_mem = get_memory_mb()
    single_pred_mem = after_single_mem - baseline_mem
    print(f"Memory after single prediction: {after_single_mem:.1f} MB")
    print(f"Single prediction total memory: {single_pred_mem:.1f} MB")
    print(f"Wiki claim: ~60 MB")
    print()

    # Wiki claim: "Dashboard generation: ~100 MB peak"
    print("Simulating dashboard generation (100 predictions)...")
    regions = [
        GeoPoint.from_degrees(40.7128, -74.0060),
        GeoPoint.from_degrees(51.5074, -0.1278),
        GeoPoint.from_degrees(35.6762, 139.6503),
        GeoPoint.from_degrees(-33.8688, 151.2093),
        GeoPoint.from_degrees(55.7558, 37.6173),
    ]
    bands = [3.5, 7.0, 10.1, 14.0, 18.1, 21.0, 28.0]
    time_points = [i/24.0 for i in range(0, 24, 6)]  # 4 time points

    max_mem = after_single_mem
    count = 0
    for rx_location in regions:
        for band in bands:
            for time_point in time_points:
                engine.predict(rx_location=rx_location, utc_time=time_point, frequencies=[band])
                count += 1
                if count % 20 == 0:
                    current_mem = get_memory_mb()
                    max_mem = max(max_mem, current_mem)

    gc.collect()
    final_mem = get_memory_mb()
    max_mem = max(max_mem, final_mem)
    dashboard_mem = max_mem - baseline_mem

    print(f"Peak memory during dashboard generation: {max_mem:.1f} MB")
    print(f"Dashboard generation memory usage: {dashboard_mem:.1f} MB")
    print(f"Wiki claim: ~100 MB peak")
    print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"{'Scenario':<40} {'Actual':>12} {'Wiki Claim':>12} {'Accurate?':>12}")
    print("-" * 80)
    print(f"{'PredictionEngine + CCIR/URSI maps':<40} {engine_mem:>10.1f} MB {50:>10} MB {'❌ WRONG' if abs(engine_mem - 50) > 20 else '✓ OK':>12}")
    print(f"{'Single prediction':<40} {single_pred_mem:>10.1f} MB {60:>10} MB {'❌ WRONG' if abs(single_pred_mem - 60) > 20 else '✓ OK':>12}")
    print(f"{'Dashboard generation':<40} {dashboard_mem:>10.1f} MB {100:>10} MB {'❌ WRONG' if abs(dashboard_mem - 100) > 30 else '✓ OK':>12}")
    print()


if __name__ == '__main__':
    test_memory_usage()
