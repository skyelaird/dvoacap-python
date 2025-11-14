#!/usr/bin/env python3
"""
Validation Script - DVOACAP-Python Functionality Test
Tests that the local DVOACAP engine produces valid predictions across representative paths

Note: Online VOACAP API comparison removed as proppy.net is no longer operational.
For comparison against reference VOACAP data, see test_voacap_reference.py
"""

import json
import sys
import numpy as np
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple
import time

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.dvoacap.path_geometry import GeoPoint
from src.dvoacap.prediction_engine import PredictionEngine


# =============================================================================
# Configuration
# =============================================================================

# Test cases - representative paths
TEST_CASES = {
    'UK': {
        'name': 'United Kingdom (London)',
        'rx_lat': 51.5,
        'rx_lon': -0.1,
        'distance_km': 4500,
        'comment': 'Trans-Atlantic, typical EU path'
    },
    'JA': {
        'name': 'Japan (Tokyo)',
        'rx_lat': 35.7,
        'rx_lon': 139.7,
        'distance_km': 10500,
        'comment': 'Long path over Pacific'
    },
    'VK': {
        'name': 'Australia (Sydney)',
        'rx_lat': -33.9,
        'rx_lon': 151.2,
        'distance_km': 16500,
        'comment': 'Very long path, antipodal'
    },
    'SA': {
        'name': 'South America (Brazil)',
        'rx_lat': -15.8,
        'rx_lon': -47.9,
        'distance_km': 6500,
        'comment': 'South, different hemisphere'
    }
}

# Test bands
TEST_BANDS = {
    '40m': 7.150,
    '20m': 14.150,
    '15m': 21.200,
    '10m': 28.500
}

# VE1ATM station
MY_QTH = {
    'call': 'VE1ATM',
    'lat': 44.374,
    'lon': -64.300,
    'power': 100,  # Watts
}


# =============================================================================
# Validation Functions
# =============================================================================

def validate_prediction(pred: Dict) -> Dict:
    """
    Validate that a local prediction produced reasonable results

    Returns dict with validation results
    """
    validation = {
        'valid': True,
        'issues': [],
        'metrics': {}
    }

    # Check for error conditions
    snr = pred.get('snr', -999)
    mode = pred.get('mode', '')
    reliability = pred.get('reliability', 0)
    muf = pred.get('muf', 0)

    # Detect if prediction failed
    if snr <= -900 or mode in ['ERROR', 'N/A']:
        validation['valid'] = False
        validation['issues'].append("Prediction failed or returned error")
        return validation

    # Sanity check values
    if not (0 <= reliability <= 100):
        validation['valid'] = False
        validation['issues'].append(f"Reliability out of range: {reliability}%")

    if not (-50 <= snr <= 100):
        validation['valid'] = False
        validation['issues'].append(f"SNR out of reasonable range: {snr:.1f}dB")

    if muf < 0 or muf > 100:
        validation['valid'] = False
        validation['issues'].append(f"MUF out of reasonable range: {muf:.1f}MHz")

    validation['metrics'] = {
        'reliability': reliability,
        'snr': snr,
        'muf': muf,
        'mode': mode,
        'hops': pred.get('hops', 0)
    }

    return validation


def run_local_prediction(engine: PredictionEngine, rx_lat: float, rx_lon: float,
                        freq_mhz: float, utc_hour: int) -> Dict:
    """Run local DVOACAP prediction"""

    rx_location = GeoPoint.from_degrees(rx_lat, rx_lon)
    utc_fraction = utc_hour / 24.0

    try:
        engine.predict(
            rx_location=rx_location,
            utc_time=utc_fraction,
            frequencies=[freq_mhz]
        )

        if len(engine.predictions) > 0:
            pred = engine.predictions[0]

            return {
                'reliability': pred.signal.reliability * 100,
                'snr': pred.signal.snr_db,
                'muf': engine.circuit_muf.muf if engine.circuit_muf else 0,
                'mode': pred.get_mode_name(engine.path.dist),
                'hops': pred.hop_count,
                'elevation': np.rad2deg(pred.tx_elevation),
                'method': pred.method.value,
                'raw': pred  # Keep full prediction for debugging
            }
        else:
            return {'reliability': 0, 'snr': -999, 'muf': 0, 'mode': 'N/A', 'hops': 0, 'elevation': 0}

    except Exception as e:
        print(f"    [ERROR] Local prediction failed: {e}")
        return {'reliability': 0, 'snr': -999, 'muf': 0, 'mode': 'ERROR', 'hops': 0, 'elevation': 0}




# =============================================================================
# Main Validation
# =============================================================================

def validate_predictions(test_regions: List[str] = None,
                        test_bands_list: List[str] = None,
                        utc_hours: List[int] = None,
                        verbose: bool = True):
    """
    Run comprehensive validation of local DVOACAP engine

    Tests that predictions are generated successfully and produce
    reasonable values across representative propagation paths.

    Args:
        test_regions: List of region codes to test (default: all)
        test_bands_list: List of bands to test (default: all)
        utc_hours: UTC hours to test (default: current hour only)
        verbose: Print detailed output
    """

    # Defaults
    if test_regions is None:
        test_regions = list(TEST_CASES.keys())
    if test_bands_list is None:
        test_bands_list = list(TEST_BANDS.keys())
    if utc_hours is None:
        utc_hours = [datetime.now(timezone.utc).hour]

    print("=" * 80)
    print("DVOACAP VALIDATION - Local Engine Functionality Test")
    print("=" * 80)
    print()
    print(f"Station: {MY_QTH['call']} @ {MY_QTH['lat']:.3f}°N, {MY_QTH['lon']:.3f}°W")
    print(f"Power: {MY_QTH['power']}W")
    print()
    print(f"Testing: {len(test_regions)} regions × {len(test_bands_list)} bands × {len(utc_hours)} hours = {len(test_regions) * len(test_bands_list) * len(utc_hours)} predictions")
    print()

    # Initialize engine
    print("[1/2] Initializing local DVOACAP engine...")
    engine = PredictionEngine()
    now = datetime.now(timezone.utc)
    engine.params.ssn = 100.0
    engine.params.month = now.month
    engine.params.required_snr = 10.0  # 10 dB for operational predictions
    engine.params.tx_power = MY_QTH['power']
    engine.params.tx_location = GeoPoint.from_degrees(MY_QTH['lat'], MY_QTH['lon'])
    engine.params.min_angle = np.deg2rad(3.0)
    print(f"      Configuration: Month={now.month}, SSN=100, Power={MY_QTH['power']}W")
    print("      Ready")

    print("[2/2] Running predictions...")
    print()

    # Track results
    all_results = []
    total_tests = 0
    passed_tests = 0
    failed_tests = 0

    # Run tests
    for region_code in test_regions:
        region = TEST_CASES[region_code]

        print(f"\n{'─' * 80}")
        print(f"Region: {region['name']} ({region_code})")
        print(f"  Path: {region['distance_km']} km - {region['comment']}")
        print(f"  RX: {region['rx_lat']:.2f}°, {region['rx_lon']:.2f}°")
        print(f"{'─' * 80}")

        for utc_hour in utc_hours:
            print(f"\n  UTC Hour: {utc_hour:02d}00")

            for band_name in test_bands_list:
                freq_mhz = TEST_BANDS[band_name]

                print(f"    {band_name} ({freq_mhz:.3f} MHz):", end=' ', flush=True)

                # Run local prediction
                local_result = run_local_prediction(
                    engine, region['rx_lat'], region['rx_lon'], freq_mhz, utc_hour
                )

                # Validate result
                validation = validate_prediction(local_result)

                total_tests += 1

                if not validation['valid']:
                    failed_tests += 1
                    print("✗ FAILED")
                    for issue in validation['issues']:
                        print(f"        → {issue}")
                    if verbose:
                        print(f"        Rel={local_result.get('reliability', 0):5.1f}% SNR={local_result.get('snr', -999):6.1f}dB Mode={local_result.get('mode', 'N/A')}")
                else:
                    passed_tests += 1
                    print("✓ PASS")
                    if verbose:
                        print(f"        Rel={local_result['reliability']:5.1f}% SNR={local_result['snr']:6.1f}dB MUF={local_result['muf']:5.1f}MHz Mode={local_result['mode']} ({local_result['hops']} hop)")

                # Store result
                all_results.append({
                    'region': region_code,
                    'band': band_name,
                    'freq_mhz': freq_mhz,
                    'utc_hour': utc_hour,
                    'prediction': local_result,
                    'validation': validation,
                    'passed': validation['valid']
                })

    # Summary
    print()
    print("=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    print(f"Total tests:  {total_tests}")
    print(f"Passed:       {passed_tests} ({100*passed_tests/total_tests:.1f}%)")
    print(f"Failed:       {failed_tests} ({100*failed_tests/total_tests:.1f}%)")
    print()

    # Analyze failures
    if failed_tests > 0:
        print("FAILURE ANALYSIS:")
        print()

        # By band
        print("  By band:")
        for band in test_bands_list:
            band_failures = sum(1 for r in all_results if r['band'] == band and not r['passed'])
            band_total = sum(1 for r in all_results if r['band'] == band)
            if band_total > 0:
                print(f"    {band}: {band_failures}/{band_total} failures ({100*band_failures/band_total:.0f}%)")
        print()

        # By region
        print("  By region:")
        for region_code in test_regions:
            region_failures = sum(1 for r in all_results if r['region'] == region_code and not r['passed'])
            region_total = sum(1 for r in all_results if r['region'] == region_code)
            if region_total > 0:
                print(f"    {region_code}: {region_failures}/{region_total} failures ({100*region_failures/region_total:.0f}%)")

        # Common issues
        print()
        print("  Common issues:")
        all_issues = {}
        for r in all_results:
            if not r['passed']:
                for issue in r['validation']['issues']:
                    all_issues[issue] = all_issues.get(issue, 0) + 1
        for issue, count in sorted(all_issues.items(), key=lambda x: x[1], reverse=True):
            print(f"    {issue}: {count} occurrences")

    # Save detailed results
    output_file = Path(__file__).parent / 'validation_results.json'
    with open(output_file, 'w') as f:
        # Remove raw prediction objects for JSON serialization
        results_for_json = []
        for r in all_results:
            r_copy = r.copy()
            if 'raw' in r_copy.get('prediction', {}):
                del r_copy['prediction']['raw']
            results_for_json.append(r_copy)

        json.dump({
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'summary': {
                'total': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'pass_rate': 100 * passed_tests / total_tests if total_tests > 0 else 0
            },
            'results': results_for_json
        }, f, indent=2)

    print()
    print(f"Detailed results saved to: {output_file}")
    print()

    return all_results, passed_tests, failed_tests


# =============================================================================
# Debug Helpers
# =============================================================================

def debug_single_prediction(region_code: str, band: str, utc_hour: int = None):
    """
    Deep dive into a single prediction showing all intermediate values
    """
    if utc_hour is None:
        utc_hour = datetime.now(timezone.utc).hour

    region = TEST_CASES[region_code]
    freq_mhz = TEST_BANDS[band]

    print("=" * 80)
    print("DETAILED PREDICTION DEBUG")
    print("=" * 80)
    print(f"Path: {MY_QTH['call']} → {region['name']} ({region_code})")
    print(f"Band: {band} ({freq_mhz:.3f} MHz)")
    print(f"UTC Hour: {utc_hour:02d}00")
    print(f"Distance: ~{region['distance_km']} km")
    print()

    # Setup
    engine = PredictionEngine()
    now = datetime.now(timezone.utc)
    engine.params.ssn = 100.0
    engine.params.month = now.month
    engine.params.required_snr = 10.0  # 10 dB for operational predictions
    engine.params.tx_power = MY_QTH['power']
    engine.params.tx_location = GeoPoint.from_degrees(MY_QTH['lat'], MY_QTH['lon'])
    engine.params.min_angle = np.deg2rad(3.0)

    rx_location = GeoPoint.from_degrees(region['rx_lat'], region['rx_lon'])
    utc_fraction = utc_hour / 24.0

    # Run prediction with detailed output
    print("[LOCAL DVOACAP PREDICTION]")
    print()

    try:
        engine.predict(rx_location=rx_location, utc_time=utc_fraction, frequencies=[freq_mhz])

        print(f"  Path distance: {engine.path.dist * 6370:.1f} km")
        print(f"  Path azimuth:  {np.rad2deg(engine.path.azim_tr):.1f}°")
        print(f"  MUF:           {engine.circuit_muf.muf:.2f} MHz" if engine.circuit_muf else "  MUF:           N/A")
        print()

        if len(engine.predictions) > 0:
            pred = engine.predictions[0]

            print(f"  Method:        {pred.method.value}")
            print(f"  Mode:          {pred.get_mode_name(engine.path.dist)}")
            print(f"  Hops:          {pred.hop_count}")
            print(f"  TX elevation:  {np.rad2deg(pred.tx_elevation):.1f}°")
            print(f"  RX elevation:  {np.rad2deg(pred.rx_elevation):.1f}°")
            print(f"  Virt height:   {pred.virt_height:.1f} km")
            print()
            print(f"  Reliability:   {pred.signal.reliability * 100:.1f}%")
            print(f"  SNR:           {pred.signal.snr_db:.1f} dB")
            print(f"  Signal power:  {pred.signal.power_dbw:.1f} dBW")
            print(f"  Noise power:   {pred.noise_dbw:.1f} dBW")
            print(f"  Field strength:{pred.signal.field_dbuv:.1f} dBµV/m")
            print(f"  Total loss:    {pred.signal.total_loss_db:.1f} dB")
            print(f"  MUF day:       {pred.signal.muf_day:.3f}")
            print()
        else:
            print("  No valid modes found")
            print()

    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()

    print("=" * 80)
    print()
    print("Note: Online VOACAP API comparison removed as proppy.net is no longer operational.")


# =============================================================================
# CLI
# =============================================================================

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Validate DVOACAP local engine functionality')
    parser.add_argument('--regions', nargs='+', choices=list(TEST_CASES.keys()),
                       help='Regions to test (default: all)')
    parser.add_argument('--bands', nargs='+', choices=list(TEST_BANDS.keys()),
                       help='Bands to test (default: all)')
    parser.add_argument('--hours', nargs='+', type=int,
                       help='UTC hours to test (default: current hour)')
    parser.add_argument('--debug', nargs=2, metavar=('REGION', 'BAND'),
                       help='Debug single prediction in detail (local engine only)')
    parser.add_argument('--quiet', action='store_true',
                       help='Less verbose output')

    args = parser.parse_args()

    if args.debug:
        # Debug mode
        region_code, band = args.debug
        debug_single_prediction(region_code, band)
    else:
        # Validation mode
        results, passed, failed = validate_predictions(
            test_regions=args.regions,
            test_bands_list=args.bands,
            utc_hours=args.hours,
            verbose=not args.quiet
        )

        # Exit with error code if any tests failed
        sys.exit(0 if failed == 0 else 1)
