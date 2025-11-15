#!/usr/bin/env python3
"""
Comparative Analysis: Propagation North vs South of GN55-IN25 Line (45°N)

This script analyzes the differences in HF propagation characteristics between:
1. Areas NORTH of the 45°N latitude line (GN55-IN25)
2. Areas SOUTH of the 45°N latitude line

From the perspective of VE1ATM station (44.37°N, -64.30°W / FN74ui)
"""

import sys
import json
import numpy as np
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Tuple

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.dvoacap.path_geometry import GeoPoint
from src.dvoacap.prediction_engine import PredictionEngine

# Custom JSON encoder for numpy types
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)


# =============================================================================
# Configuration
# =============================================================================

# VE1ATM Station (just south of the 45°N line)
TX_LOCATION = GeoPoint.from_degrees(44.374, -64.300)
TX_GRID = 'FN74ui'

# Test frequencies (HF amateur bands)
TEST_FREQUENCIES = [
    7.150,   # 40m
    10.125,  # 30m
    14.150,  # 20m
    18.118,  # 17m
    21.200,  # 15m
    24.940,  # 12m
    28.500   # 10m
]

BAND_NAMES = {
    7.150: '40m',
    10.125: '30m',
    14.150: '20m',
    18.118: '17m',
    21.200: '15m',
    24.940: '12m',
    28.500: '10m'
}

# Sample target grids NORTH of 45°N (European sector)
NORTH_GRIDS = {
    'IO55': {'lat': 55.5, 'lon': -10.0, 'name': 'British Isles/North Sea'},
    'JP50': {'lat': 60.5, 'lon': 10.0, 'name': 'Southern Scandinavia'},
    'IO72': {'lat': 52.5, 'lon': -5.0, 'name': 'Ireland/UK'},
    'JN18': {'lat': 48.5, 'lon': 2.0, 'name': 'Northern France'},
    'JO20': {'lat': 50.5, 'lon': 4.0, 'name': 'Belgium/Netherlands'},
    'JO60': {'lat': 60.5, 'lon': 20.0, 'name': 'Southern Finland'},
}

# Sample target grids SOUTH of 45°N (European/Mediterranean sector)
SOUTH_GRIDS = {
    'IN62': {'lat': 42.5, 'lon': -8.0, 'name': 'Northern Spain/Portugal'},
    'JN70': {'lat': 40.5, 'lon': 14.0, 'name': 'Southern Italy'},
    'KM18': {'lat': 38.5, 'lon': 23.0, 'name': 'Greece'},
    'IM76': {'lat': 36.5, 'lon': -5.0, 'name': 'Southern Spain'},
    'IN80': {'lat': 40.5, 'lon': -4.0, 'name': 'Central Spain'},
    'KN23': {'lat': 43.5, 'lon': 7.0, 'name': 'Southern France/Riviera'},
}

# UTC times to test (sample 4 key times)
UTC_TIMES = [0.0, 0.25, 0.5, 0.75]  # 00:00, 06:00, 12:00, 18:00 UTC
UTC_LABELS = ['00:00', '06:00', '12:00', '18:00']


# =============================================================================
# Propagation Analysis Functions
# =============================================================================

def run_prediction(engine: PredictionEngine, target: GeoPoint, utc_fraction: float) -> Dict:
    """
    Run propagation prediction to a target location at a specific UTC time

    Returns dict with band-by-band predictions including:
    - reliability (%)
    - SNR (dB)
    - MUF (MHz)
    - mode/hops
    """
    try:
        engine.predict(
            rx_location=target,
            utc_time=utc_fraction,
            frequencies=TEST_FREQUENCIES
        )

        results = {}
        for i, freq in enumerate(TEST_FREQUENCIES):
            band = BAND_NAMES[freq]

            if i < len(engine.predictions):
                pred = engine.predictions[i]

                results[band] = {
                    'frequency_mhz': freq,
                    'reliability_pct': round(pred.signal.reliability * 100, 1),
                    'snr_db': round(pred.signal.snr_db, 1),
                    'signal_power_dbw': round(pred.signal.power_dbw, 1),
                    'mode': pred.get_mode_name(engine.path.dist),
                    'hops': int(pred.hop_count),
                    'elevation_deg': round(np.rad2deg(pred.tx_elevation), 1),
                }
            else:
                results[band] = {
                    'frequency_mhz': freq,
                    'reliability_pct': 0,
                    'snr_db': -999,
                    'signal_power_dbw': -999,
                    'mode': 'N/A',
                    'hops': 0,
                    'elevation_deg': 0,
                }

        # Calculate path info
        distance_km = engine.path.dist * 6370
        azimuth_deg = np.rad2deg(engine.path.azim_tr)

        # Overall circuit MUF
        circuit_muf = round(engine.circuit_muf.muf, 2) if engine.circuit_muf else 0

        return {
            'bands': results,
            'path': {
                'distance_km': round(distance_km, 0),
                'azimuth_deg': round(azimuth_deg, 1),
                'circuit_muf_mhz': circuit_muf
            }
        }

    except Exception as e:
        print(f"    ERROR: {e}")
        return None


def analyze_grid_set(engine: PredictionEngine, grids: Dict, label: str) -> List[Dict]:
    """
    Analyze propagation to a set of grids across all UTC times
    """
    print(f"\n{'='*80}")
    print(f"Analyzing {label}")
    print(f"{'='*80}")

    results = []

    for grid_code, grid_info in grids.items():
        print(f"\n  Grid {grid_code} - {grid_info['name']}")
        target = GeoPoint.from_degrees(grid_info['lat'], grid_info['lon'])

        grid_results = {
            'grid': grid_code,
            'name': grid_info['name'],
            'latitude': grid_info['lat'],
            'longitude': grid_info['lon'],
            'predictions': []
        }

        for utc_frac, utc_label in zip(UTC_TIMES, UTC_LABELS):
            print(f"    {utc_label} UTC...", end=' ')

            pred = run_prediction(engine, target, utc_frac)
            if pred:
                pred['utc_time'] = utc_label
                grid_results['predictions'].append(pred)

                # Show quick summary
                best_band = max(pred['bands'].items(),
                               key=lambda x: x[1]['reliability_pct'])
                print(f"Best: {best_band[0]} ({best_band[1]['reliability_pct']:.0f}%, "
                      f"{best_band[1]['snr_db']:.1f}dB SNR)")
            else:
                print("FAILED")

        results.append(grid_results)

    return results


def calculate_statistics(predictions: List[Dict]) -> Dict:
    """
    Calculate aggregate statistics for a set of predictions
    """
    all_reliabilities = []
    all_snrs = []
    band_stats = {band: {'reliabilities': [], 'snrs': []} for band in BAND_NAMES.values()}

    for grid_pred in predictions:
        for time_pred in grid_pred['predictions']:
            for band, data in time_pred['bands'].items():
                if data['reliability_pct'] > 0:
                    all_reliabilities.append(data['reliability_pct'])
                    band_stats[band]['reliabilities'].append(data['reliability_pct'])

                if data['snr_db'] > -100:
                    all_snrs.append(data['snr_db'])
                    band_stats[band]['snrs'].append(data['snr_db'])

    # Calculate overall stats
    stats = {
        'overall': {
            'mean_reliability_pct': round(np.mean(all_reliabilities), 1) if all_reliabilities else 0,
            'median_reliability_pct': round(np.median(all_reliabilities), 1) if all_reliabilities else 0,
            'mean_snr_db': round(np.mean(all_snrs), 1) if all_snrs else -999,
            'median_snr_db': round(np.median(all_snrs), 1) if all_snrs else -999,
        },
        'by_band': {}
    }

    # Calculate per-band stats
    for band in BAND_NAMES.values():
        band_rels = band_stats[band]['reliabilities']
        band_snrs = band_stats[band]['snrs']

        stats['by_band'][band] = {
            'mean_reliability_pct': round(np.mean(band_rels), 1) if band_rels else 0,
            'median_reliability_pct': round(np.median(band_rels), 1) if band_rels else 0,
            'mean_snr_db': round(np.mean(band_snrs), 1) if band_snrs else -999,
            'median_snr_db': round(np.median(band_snrs), 1) if band_snrs else -999,
            'samples': len(band_rels)
        }

    return stats


# =============================================================================
# Main Analysis
# =============================================================================

def main():
    """Main analysis routine"""

    print("="*80)
    print("GN55-IN25 LINE COMPARISON ANALYSIS")
    print("="*80)
    print(f"TX Location: {TX_GRID} (44.374°N, 64.300°W)")
    print(f"Analysis Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"Comparing propagation to grids NORTH vs SOUTH of 45°N latitude")
    print("="*80)

    # Initialize prediction engine
    print("\nInitializing DVOACAP prediction engine...")
    engine = PredictionEngine()

    # Configure engine
    now = datetime.now(timezone.utc)
    engine.params.ssn = 100.0  # Mid-cycle conditions
    engine.params.month = now.month
    engine.params.tx_power = 100.0  # 100W
    engine.params.tx_location = TX_LOCATION
    engine.params.min_angle = np.deg2rad(3.0)  # 3° minimum takeoff angle
    engine.params.required_snr = 10.0
    engine.params.required_reliability = 0.9

    print(f"Configuration: SSN=100, Month={now.month}, TX Power=100W")

    # Analyze NORTH grids
    north_results = analyze_grid_set(engine, NORTH_GRIDS, "GRIDS NORTH OF 45°N")
    north_stats = calculate_statistics(north_results)

    # Analyze SOUTH grids
    south_results = analyze_grid_set(engine, SOUTH_GRIDS, "GRIDS SOUTH OF 45°N")
    south_stats = calculate_statistics(south_results)

    # Print comparison
    print("\n" + "="*80)
    print("STATISTICAL COMPARISON")
    print("="*80)

    print("\nNORTH of 45°N (Higher Latitudes):")
    print(f"  Overall Mean Reliability: {north_stats['overall']['mean_reliability_pct']:.1f}%")
    print(f"  Overall Mean SNR: {north_stats['overall']['mean_snr_db']:.1f} dB")
    print("\n  By Band:")
    for band in BAND_NAMES.values():
        bstat = north_stats['by_band'][band]
        print(f"    {band:4s}: {bstat['mean_reliability_pct']:5.1f}% reliability, "
              f"{bstat['mean_snr_db']:6.1f} dB SNR ({bstat['samples']} samples)")

    print("\nSOUTH of 45°N (Lower Latitudes):")
    print(f"  Overall Mean Reliability: {south_stats['overall']['mean_reliability_pct']:.1f}%")
    print(f"  Overall Mean SNR: {south_stats['overall']['mean_snr_db']:.1f} dB")
    print("\n  By Band:")
    for band in BAND_NAMES.values():
        bstat = south_stats['by_band'][band]
        print(f"    {band:4s}: {bstat['mean_reliability_pct']:5.1f}% reliability, "
              f"{bstat['mean_snr_db']:6.1f} dB SNR ({bstat['samples']} samples)")

    print("\nDIFFERENCE (South - North):")
    print(f"  Overall Reliability: {south_stats['overall']['mean_reliability_pct'] - north_stats['overall']['mean_reliability_pct']:+.1f}%")
    print(f"  Overall SNR: {south_stats['overall']['mean_snr_db'] - north_stats['overall']['mean_snr_db']:+.1f} dB")
    print("\n  By Band:")
    for band in BAND_NAMES.values():
        n_rel = north_stats['by_band'][band]['mean_reliability_pct']
        s_rel = south_stats['by_band'][band]['mean_reliability_pct']
        n_snr = north_stats['by_band'][band]['mean_snr_db']
        s_snr = south_stats['by_band'][band]['mean_snr_db']
        print(f"    {band:4s}: {s_rel - n_rel:+6.1f}% reliability, "
              f"{s_snr - n_snr:+6.1f} dB SNR")

    # Save detailed results
    output = {
        'generated': datetime.now(timezone.utc).isoformat(),
        'tx_location': {
            'grid': TX_GRID,
            'latitude': 44.374,
            'longitude': -64.300
        },
        'analysis': {
            'dividing_line': '45°N latitude (GN55-IN25)',
            'description': 'Comparison of propagation characteristics north vs south of 45°N'
        },
        'north_of_45n': {
            'grids': north_results,
            'statistics': north_stats
        },
        'south_of_45n': {
            'grids': south_results,
            'statistics': south_stats
        }
    }

    output_file = Path(__file__).parent / 'gn55_in25_comparison_results.json'
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2, cls=NumpyEncoder)

    print(f"\n{'='*80}")
    print(f"Analysis complete. Results saved to: {output_file}")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()
