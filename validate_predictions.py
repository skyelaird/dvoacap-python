#!/usr/bin/env python3
"""
Validation Script - Compare DVOACAP-Python vs VOACAP Online
Compares local predictions against proppy.net (VOACAP reference) to identify discrepancies
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
from Dashboard.proppy_net_api import ProppyNetAPI


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
# Comparison Functions
# =============================================================================

def compare_predictions(local_pred: Dict, voacap_pred: Dict, tolerance: Dict) -> Dict:
    """
    Compare local prediction against VOACAP online

    Returns dict with comparison results and flags for significant differences
    """
    comparison = {
        'match': True,
        'differences': [],
        'metrics': {}
    }

    # Compare reliability
    local_rel = local_pred.get('reliability', 0)
    voacap_rel = voacap_pred.get('reliability', 0)
    rel_diff = abs(local_rel - voacap_rel)

    comparison['metrics']['reliability'] = {
        'local': local_rel,
        'voacap': voacap_rel,
        'diff': rel_diff,
        'match': rel_diff <= tolerance['reliability']
    }

    if rel_diff > tolerance['reliability']:
        comparison['match'] = False
        comparison['differences'].append(
            f"Reliability: local={local_rel:.1f}% vs VOACAP={voacap_rel:.1f}% (diff={rel_diff:.1f}%)"
        )

    # Compare SNR
    local_snr = local_pred.get('snr', -999)
    voacap_snr = voacap_pred.get('snr_db', -999)

    # Only compare if both are valid
    if local_snr > -900 and voacap_snr > -900:
        snr_diff = abs(local_snr - voacap_snr)

        comparison['metrics']['snr'] = {
            'local': local_snr,
            'voacap': voacap_snr,
            'diff': snr_diff,
            'match': snr_diff <= tolerance['snr']
        }

        if snr_diff > tolerance['snr']:
            comparison['match'] = False
            comparison['differences'].append(
                f"SNR: local={local_snr:.1f}dB vs VOACAP={voacap_snr:.1f}dB (diff={snr_diff:.1f}dB)"
            )

    # Compare MUF (if available)
    local_muf = local_pred.get('muf', 0)
    voacap_muf = voacap_pred.get('muf', 0)

    if local_muf > 0 and voacap_muf > 0:
        muf_diff = abs(local_muf - voacap_muf)

        comparison['metrics']['muf'] = {
            'local': local_muf,
            'voacap': voacap_muf,
            'diff': muf_diff,
            'match': muf_diff <= tolerance['muf']
        }

        if muf_diff > tolerance['muf']:
            comparison['match'] = False
            comparison['differences'].append(
                f"MUF: local={local_muf:.1f}MHz vs VOACAP={voacap_muf:.1f}MHz (diff={muf_diff:.1f}MHz)"
            )

    return comparison


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


def run_voacap_online(api: ProppyNetAPI, rx_lat: float, rx_lon: float,
                     freq_mhz: float, utc_hour: int, month: int, ssn: int) -> Dict:
    """Run VOACAP online prediction via proppy.net"""

    try:
        result = api.get_prediction(
            rx_lat=rx_lat,
            rx_lon=rx_lon,
            freq_mhz=freq_mhz,
            hour_utc=utc_hour,
            month=month,
            ssn=ssn
        )

        if result:
            return result
        else:
            return {'reliability': 0, 'snr_db': -999, 'muf': 0, 'quality': 'ERROR'}

    except Exception as e:
        print(f"    [ERROR] VOACAP online failed: {e}")
        return {'reliability': 0, 'snr_db': -999, 'muf': 0, 'quality': 'ERROR'}


# =============================================================================
# Main Validation
# =============================================================================

def validate_predictions(test_regions: List[str] = None,
                        test_bands_list: List[str] = None,
                        utc_hours: List[int] = None,
                        verbose: bool = True):
    """
    Run comprehensive validation comparing local vs VOACAP online

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

    # Tolerance thresholds
    tolerance = {
        'reliability': 15.0,  # ±15% for reliability
        'snr': 5.0,           # ±5 dB for SNR
        'muf': 2.0            # ±2 MHz for MUF
    }

    print("=" * 80)
    print("DVOACAP VALIDATION - Compare Local vs VOACAP Online")
    print("=" * 80)
    print()
    print(f"Station: {MY_QTH['call']} @ {MY_QTH['lat']:.3f}°N, {MY_QTH['lon']:.3f}°W")
    print(f"Power: {MY_QTH['power']}W")
    print(f"Tolerance: ±{tolerance['reliability']:.0f}% reliability, ±{tolerance['snr']:.0f}dB SNR, ±{tolerance['muf']:.0f}MHz MUF")
    print()
    print(f"Testing: {len(test_regions)} regions × {len(test_bands_list)} bands × {len(utc_hours)} hours = {len(test_regions) * len(test_bands_list) * len(utc_hours)} comparisons")
    print()

    # Initialize engines
    print("[1/3] Initializing local DVOACAP engine...")
    engine = PredictionEngine()
    now = datetime.now(timezone.utc)
    engine.params.ssn = 100.0  # Use fixed SSN for comparison
    engine.params.month = now.month
    engine.params.tx_power = MY_QTH['power']
    engine.params.tx_location = GeoPoint.from_degrees(MY_QTH['lat'], MY_QTH['lon'])
    engine.params.min_angle = np.deg2rad(3.0)
    print(f"      Configuration: Month={now.month}, SSN=100, Power={MY_QTH['power']}W")

    print("[2/3] Initializing VOACAP online API (proppy.net)...")
    api = ProppyNetAPI(tx_lat=MY_QTH['lat'], tx_lon=MY_QTH['lon'], tx_power=MY_QTH['power'])
    print("      Ready")

    print("[3/3] Running comparisons...")
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

                # Wait to be nice to proppy.net
                time.sleep(2)

                # Run VOACAP online
                voacap_result = run_voacap_online(
                    api, region['rx_lat'], region['rx_lon'], freq_mhz, utc_hour, now.month, 100
                )

                # Compare
                comparison = compare_predictions(local_result, voacap_result, tolerance)

                total_tests += 1

                if comparison['match']:
                    passed_tests += 1
                    print("✓ MATCH")
                    if verbose:
                        print(f"        Local:  Rel={local_result['reliability']:5.1f}% SNR={local_result['snr']:6.1f}dB Mode={local_result['mode']}")
                        print(f"        VOACAP: Rel={voacap_result['reliability']:5.1f}% SNR={voacap_result.get('snr_db', -999):6.1f}dB")
                else:
                    failed_tests += 1
                    print("✗ MISMATCH")
                    print(f"        Local:  Rel={local_result['reliability']:5.1f}% SNR={local_result['snr']:6.1f}dB MUF={local_result['muf']:5.1f}MHz Mode={local_result['mode']}")
                    print(f"        VOACAP: Rel={voacap_result['reliability']:5.1f}% SNR={voacap_result.get('snr_db', -999):6.1f}dB MUF={voacap_result.get('muf', 0):5.1f}MHz")
                    for diff in comparison['differences']:
                        print(f"        → {diff}")

                # Store result
                all_results.append({
                    'region': region_code,
                    'band': band_name,
                    'freq_mhz': freq_mhz,
                    'utc_hour': utc_hour,
                    'local': local_result,
                    'voacap': voacap_result,
                    'comparison': comparison,
                    'match': comparison['match']
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

        # By metric
        rel_failures = sum(1 for r in all_results if not r['comparison']['metrics'].get('reliability', {}).get('match', True))
        snr_failures = sum(1 for r in all_results if not r['comparison']['metrics'].get('snr', {}).get('match', True))
        muf_failures = sum(1 for r in all_results if not r['comparison']['metrics'].get('muf', {}).get('match', True))

        print(f"  Reliability mismatches: {rel_failures}")
        print(f"  SNR mismatches:         {snr_failures}")
        print(f"  MUF mismatches:         {muf_failures}")
        print()

        # By band
        print("  By band:")
        for band in test_bands_list:
            band_failures = sum(1 for r in all_results if r['band'] == band and not r['match'])
            band_total = sum(1 for r in all_results if r['band'] == band)
            if band_total > 0:
                print(f"    {band}: {band_failures}/{band_total} failures ({100*band_failures/band_total:.0f}%)")
        print()

        # By region
        print("  By region:")
        for region_code in test_regions:
            region_failures = sum(1 for r in all_results if r['region'] == region_code and not r['match'])
            region_total = sum(1 for r in all_results if r['region'] == region_code)
            if region_total > 0:
                print(f"    {region_code}: {region_failures}/{region_total} failures ({100*region_failures/region_total:.0f}%)")

    # Save detailed results
    output_file = Path(__file__).parent / 'validation_results.json'
    with open(output_file, 'w') as f:
        # Remove raw prediction objects for JSON serialization
        results_for_json = []
        for r in all_results:
            r_copy = r.copy()
            if 'raw' in r_copy['local']:
                del r_copy['local']['raw']
            results_for_json.append(r_copy)

        json.dump({
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'summary': {
                'total': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'pass_rate': 100 * passed_tests / total_tests if total_tests > 0 else 0
            },
            'tolerance': tolerance,
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

    # Now get VOACAP online
    print()
    print("[VOACAP ONLINE (proppy.net)]")
    print()

    api = ProppyNetAPI(tx_lat=MY_QTH['lat'], tx_lon=MY_QTH['lon'], tx_power=MY_QTH['power'])

    result = api.get_prediction(
        rx_lat=region['rx_lat'],
        rx_lon=region['rx_lon'],
        freq_mhz=freq_mhz,
        hour_utc=utc_hour,
        month=now.month,
        ssn=100
    )

    if result:
        print(f"  Reliability:   {result['reliability']}%")
        print(f"  SNR:           {result.get('snr_db', 'N/A')} dB")
        print(f"  MUF:           {result.get('muf', 'N/A')} MHz")
        print(f"  Quality:       {result.get('quality', 'N/A')}")
        print()
        print("  Raw response (first 500 chars):")
        print("  " + "-" * 76)
        raw = result.get('raw_response', '')
        for line in raw[:500].split('\n'):
            print(f"  {line}")
        print()
    else:
        print("  FAILED - Could not get VOACAP online prediction")
        print()

    print("=" * 80)


# =============================================================================
# CLI
# =============================================================================

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Validate DVOACAP predictions against VOACAP online')
    parser.add_argument('--regions', nargs='+', choices=list(TEST_CASES.keys()),
                       help='Regions to test (default: all)')
    parser.add_argument('--bands', nargs='+', choices=list(TEST_BANDS.keys()),
                       help='Bands to test (default: all)')
    parser.add_argument('--hours', nargs='+', type=int,
                       help='UTC hours to test (default: current hour)')
    parser.add_argument('--debug', nargs=2, metavar=('REGION', 'BAND'),
                       help='Debug single prediction in detail')
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
