#!/usr/bin/env python3
"""
Reference VOACAP Validation Test

This script validates DVOACAP-Python accuracy against reference output from
the original VOACAP engine. It uses the sample data in SampleIO/ directory:

- voacapx.out: Reference output from original VOACAP (Voacapwin.exe)
- input.json: Input parameters for the test case
- output.txt: Output from DVOACAP DLL wrapper

Test Case:
- Path: Tangier, Morocco (35.80°N, 5.90°W) → Belgrade (44.90°N, 20.50°E)
- Distance: ~2440 km
- Month: June 1994
- SSN: 100
- Frequencies: 6.07, 7.20, 9.70, 11.85, 13.70, 15.35, 17.73, 21.65, 25.89 MHz
- UTC Hours: 1-24

This is TRUE VALIDATION - comparing against a known-good reference implementation
rather than just checking if values are in reasonable ranges.
"""

import json
import sys
import re
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.dvoacap.path_geometry import GeoPoint
from src.dvoacap.prediction_engine import PredictionEngine


# =============================================================================
# Reference Data Parser
# =============================================================================

class VoacapReferenceParser:
    """Parse reference VOACAP output files"""

    @staticmethod
    def parse_voacapx_out(filepath: Path) -> Dict:
        """
        Parse voacapx.out reference file

        Returns dict with structure:
        {
            'metadata': {...},
            'predictions': [
                {
                    'utc_hour': 1,
                    'frequencies': [6.07, 7.20, ...],
                    'metrics': {
                        'MODE': [...],
                        'SNR': [...],
                        'REL': [...],
                        ...
                    }
                },
                ...
            ]
        }
        """
        with open(filepath, 'r') as f:
            content = f.read()

        results = {
            'metadata': {},
            'predictions': []
        }

        # Extract metadata
        circuit_match = re.search(r'(\d+\.\d+)\s+([NS])\s+(\d+\.\d+)\s+([EW])\s+-\s+(\d+\.\d+)\s+([NS])\s+(\d+\.\d+)\s+([EW])', content)
        if circuit_match:
            results['metadata']['tx_lat'] = float(circuit_match.group(1)) * (1 if circuit_match.group(2) == 'N' else -1)
            results['metadata']['tx_lon'] = float(circuit_match.group(3)) * (-1 if circuit_match.group(4) == 'W' else 1)
            results['metadata']['rx_lat'] = float(circuit_match.group(5)) * (1 if circuit_match.group(6) == 'N' else -1)
            results['metadata']['rx_lon'] = float(circuit_match.group(7)) * (-1 if circuit_match.group(8) == 'W' else 1)

        ssn_match = re.search(r'SSN\s*=\s*(\d+)', content)
        if ssn_match:
            results['metadata']['ssn'] = int(ssn_match.group(1))

        # Parse prediction blocks (each UTC hour)
        # Format: "   1.0 16.2  6.1  7.2  9.7 ... FREQ"
        hour_blocks = re.findall(
            r'^\s+(\d+\.\d+)\s+(\d+\.\d+)\s+([\d.\s]+)\s+FREQ\n(.*?)(?=^\s+\d+\.\d+\s+\d+\.\d+\s+[\d.\s]+\s+FREQ|CCIR Coefficients|\Z)',
            content,
            re.MULTILINE | re.DOTALL
        )

        for utc_hour_str, muf_str, freq_str, block in hour_blocks:
            utc_hour = float(utc_hour_str)

            prediction = {
                'utc_hour': utc_hour,
                'muf': float(muf_str),
                'frequencies': [],
                'metrics': {}
            }

            # Extract frequencies from the FREQ line
            freq_values = freq_str.split()
            prediction['frequencies'] = [float(f) for f in freq_values if f not in ['-', '0.0', '0.00'] and float(f) > 0.1]
            num_freqs = len(prediction['frequencies'])

            # Extract metric lines
            metric_names = ['MODE', 'TANGLE', 'DELAY', 'V HITE', 'MUFday', 'LOSS',
                           'DBU', 'S DBW', 'N DBW', 'SNR', 'RPWRG', 'REL', 'MPROB',
                           'S PRB', 'SIG LW', 'SIG UP', 'SNR LW', 'SNR UP',
                           'TGAIN', 'RGAIN', 'SNRxx']

            for metric in metric_names:
                # Pattern should match values BEFORE the metric name on same line
                # Format: "  value1  value2  value3  -  - METRIC_NAME"
                # Note: The first value corresponds to the MUF column, not the first frequency!
                pattern = r'^\s*([\d.\sEFef-]+?)\s+' + re.escape(metric) + r'\s*$'
                match = re.search(pattern, block, re.MULTILINE)
                if match:
                    values_str = match.group(1).split()
                    if metric == 'MODE':
                        # MODE is text like '1F2', '2 E' (can contain spaces!)
                        # Values are separated by 2+ spaces, but MODE like "2 E" has only 1 space
                        # So we split on 2 or more spaces to preserve "2 E" as a single value
                        mode_pattern = r'^\s*([\dEFef\s-]+?)\s+MODE\s*$'
                        mode_match = re.search(mode_pattern, block, re.MULTILINE)
                        if mode_match:
                            # Split on 2+ spaces instead of any whitespace to preserve values like "2 E"
                            mode_values = re.split(r'\s{2,}', mode_match.group(1).strip())
                            # Convert dashes to None
                            mode_values = [v if v != '-' else None for v in mode_values]
                            # Skip first value (MUF column) and take only num_freqs values
                            prediction['metrics'][metric] = mode_values[1:1+num_freqs] if len(mode_values) > 1 else mode_values[:num_freqs]
                    else:
                        # Numeric values - convert and align with frequencies
                        numeric_values = [
                            float(v) if v not in ['-', ''] else None
                            for v in values_str
                        ]
                        # Skip first value (MUF column) and take only num_freqs values
                        prediction['metrics'][metric] = numeric_values[1:1+num_freqs] if len(numeric_values) > 1 else numeric_values[:num_freqs]

            results['predictions'].append(prediction)

        return results


# =============================================================================
# Validation Functions
# =============================================================================

def run_dvoacap_prediction(tx_lat: float, tx_lon: float, rx_lat: float, rx_lon: float,
                          freq_mhz: float, utc_hour: int, month: int, ssn: int,
                          tx_power_w: int = 500000) -> Optional[Dict]:
    """
    Run DVOACAP-Python prediction for comparison

    Returns dict with prediction results or None on error
    """
    engine = PredictionEngine()
    engine.params.ssn = float(ssn)
    engine.params.month = month
    engine.params.tx_power = tx_power_w
    engine.params.tx_location = GeoPoint.from_degrees(tx_lat, tx_lon)
    engine.params.min_angle = np.deg2rad(0.1)  # Match VOACAP default

    rx_location = GeoPoint.from_degrees(rx_lat, rx_lon)
    utc_fraction = utc_hour / 24.0

    try:
        engine.predict(rx_location=rx_location, utc_time=utc_fraction, frequencies=[freq_mhz])

        if len(engine.predictions) > 0:
            pred = engine.predictions[0]

            return {
                'mode': pred.get_mode_name(engine.path.dist),
                'snr': pred.signal.snr_db,
                'reliability': pred.signal.reliability * 100,  # Convert to percent
                'loss': pred.signal.total_loss_db,
                'muf_day': pred.signal.muf_day,
                'signal_dbw': pred.signal.power_dbw,
                'virt_height': pred.virt_height,
                'tx_angle': np.rad2deg(pred.tx_elevation),
            }
        else:
            return None

    except Exception as e:
        print(f"Error running prediction: {e}")
        return None


def compare_predictions(dvoacap_result: Dict, voacap_result: Dict,
                       freq_mhz: float, utc_hour: int) -> Dict:
    """
    Compare DVOACAP-Python result against VOACAP reference

    Returns comparison metrics and pass/fail status
    """
    comparison = {
        'freq_mhz': freq_mhz,
        'utc_hour': utc_hour,
        'passed': True,
        'errors': [],
        'warnings': [],
        'metrics': {}
    }

    if dvoacap_result is None:
        comparison['passed'] = False
        comparison['errors'].append("DVOACAP prediction failed")
        return comparison

    # Compare SNR (most critical metric)
    if voacap_result['SNR'] is not None:
        dvoacap_snr = dvoacap_result['snr']
        voacap_snr = voacap_result['SNR']
        snr_diff = abs(dvoacap_snr - voacap_snr)

        comparison['metrics']['SNR'] = {
            'dvoacap': dvoacap_snr,
            'voacap': voacap_snr,
            'diff': snr_diff,
            'tolerance': 10.0  # ±10 dB tolerance
        }

        if snr_diff > 10.0:
            comparison['passed'] = False
            comparison['errors'].append(f"SNR deviation: {snr_diff:.1f} dB (DVOACAP: {dvoacap_snr:.1f}, VOACAP: {voacap_snr:.1f})")
        elif snr_diff > 5.0:
            comparison['warnings'].append(f"SNR deviation: {snr_diff:.1f} dB")

    # Compare Reliability
    if voacap_result['REL'] is not None:
        dvoacap_rel = dvoacap_result['reliability']
        voacap_rel = voacap_result['REL'] * 100  # Convert to percent
        rel_diff = abs(dvoacap_rel - voacap_rel)

        comparison['metrics']['REL'] = {
            'dvoacap': dvoacap_rel,
            'voacap': voacap_rel,
            'diff': rel_diff,
            'tolerance': 20.0  # ±20% tolerance
        }

        if rel_diff > 20.0:
            comparison['passed'] = False
            comparison['errors'].append(f"Reliability deviation: {rel_diff:.1f}% (DVOACAP: {dvoacap_rel:.1f}%, VOACAP: {voacap_rel:.1f}%)")
        elif rel_diff > 10.0:
            comparison['warnings'].append(f"Reliability deviation: {rel_diff:.1f}%")

    # Compare MUF day
    if voacap_result['MUFday'] is not None:
        dvoacap_mufday = dvoacap_result['muf_day']
        voacap_mufday = voacap_result['MUFday']
        mufday_diff = abs(dvoacap_mufday - voacap_mufday)

        comparison['metrics']['MUFday'] = {
            'dvoacap': dvoacap_mufday,
            'voacap': voacap_mufday,
            'diff': mufday_diff,
            'tolerance': 0.2
        }

        if mufday_diff > 0.2:
            comparison['warnings'].append(f"MUF day deviation: {mufday_diff:.3f}")

    return comparison


# =============================================================================
# Main Validation
# =============================================================================

def validate_against_reference(verbose: bool = True,
                               sample_hours: Optional[List[int]] = None,
                               sample_freqs: Optional[List[float]] = None):
    """
    Run comprehensive validation against VOACAP reference data

    Args:
        verbose: Print detailed comparison output
        sample_hours: Limit to specific UTC hours (default: all)
        sample_freqs: Limit to specific frequencies (default: all)
    """

    print("=" * 80)
    print("DVOACAP REFERENCE VALIDATION - Compare Against Original VOACAP")
    print("=" * 80)
    print()
    print("This test validates DVOACAP-Python accuracy by comparing predictions")
    print("against reference output from the original VOACAP engine.")
    print()

    # Load reference data
    sample_dir = Path(__file__).parent / 'SampleIO'
    voacapx_file = sample_dir / 'voacapx.out'

    if not voacapx_file.exists():
        print(f"ERROR: Reference file not found: {voacapx_file}")
        return None, 0, 0

    print(f"Loading reference data: {voacapx_file}")
    parser = VoacapReferenceParser()
    reference = parser.parse_voacapx_out(voacapx_file)

    print(f"Reference data loaded:")
    print(f"  Path: {reference['metadata']['tx_lat']:.2f}°N, {reference['metadata']['tx_lon']:.2f}°W")
    print(f"       → {reference['metadata']['rx_lat']:.2f}°N, {reference['metadata']['rx_lon']:.2f}°E")
    print(f"  SSN: {reference['metadata']['ssn']}")
    print(f"  UTC Hours: {len(reference['predictions'])}")
    print()

    # Run comparisons
    all_comparisons = []
    total_tests = 0
    passed_tests = 0
    failed_tests = 0

    for pred_block in reference['predictions']:
        utc_hour = int(pred_block['utc_hour'])

        # Skip if not in sample hours
        if sample_hours and utc_hour not in sample_hours:
            continue

        if verbose:
            print(f"\nUTC Hour {utc_hour:02d}00:")

        for i, freq_mhz in enumerate(pred_block['frequencies']):
            # Skip if not in sample freqs
            if sample_freqs and freq_mhz not in sample_freqs:
                continue

            # Get VOACAP reference values for this frequency
            voacap_result = {
                'SNR': pred_block['metrics'].get('SNR', [None])[i] if i < len(pred_block['metrics'].get('SNR', [])) else None,
                'REL': pred_block['metrics'].get('REL', [None])[i] if i < len(pred_block['metrics'].get('REL', [])) else None,
                'MUFday': pred_block['metrics'].get('MUFday', [None])[i] if i < len(pred_block['metrics'].get('MUFday', [])) else None,
                'MODE': pred_block['metrics'].get('MODE', [None])[i] if i < len(pred_block['metrics'].get('MODE', [])) else None,
            }

            # Skip if VOACAP shows no valid mode
            if voacap_result['MODE'] in [None, '-']:
                continue

            # Run DVOACAP prediction
            dvoacap_result = run_dvoacap_prediction(
                tx_lat=reference['metadata']['tx_lat'],
                tx_lon=reference['metadata']['tx_lon'],
                rx_lat=reference['metadata']['rx_lat'],
                rx_lon=reference['metadata']['rx_lon'],
                freq_mhz=freq_mhz,
                utc_hour=utc_hour,
                month=6,  # June
                ssn=reference['metadata']['ssn']
            )

            # Compare
            comparison = compare_predictions(dvoacap_result, voacap_result, freq_mhz, utc_hour)
            all_comparisons.append(comparison)

            total_tests += 1
            if comparison['passed']:
                passed_tests += 1
                if verbose:
                    print(f"  {freq_mhz:6.2f} MHz: ✓ PASS", end='')
                    if comparison['warnings']:
                        print(f" ({len(comparison['warnings'])} warnings)")
                    else:
                        print()
            else:
                failed_tests += 1
                if verbose:
                    print(f"  {freq_mhz:6.2f} MHz: ✗ FAIL")
                    for error in comparison['errors']:
                        print(f"      → {error}")

    # Summary
    print()
    print("=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)
    print(f"Total comparisons: {total_tests}")
    print(f"Passed:            {passed_tests} ({100*passed_tests/total_tests:.1f}%)" if total_tests > 0 else "Passed: N/A")
    print(f"Failed:            {failed_tests} ({100*failed_tests/total_tests:.1f}%)" if total_tests > 0 else "Failed: N/A")
    print()

    if failed_tests > 0:
        print("⚠️  ACCURACY ISSUES DETECTED")
        print("The DVOACAP-Python engine shows significant deviations from reference VOACAP.")
        print("This indicates potential bugs or incomplete implementation.")
    elif total_tests > 0:
        print("✓ VALIDATION PASSED")
        print("DVOACAP-Python predictions match reference VOACAP within tolerances.")

    print()

    # Save detailed results
    output_file = Path(__file__).parent / 'validation_reference_results.json'
    with open(output_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'pass_rate': 100 * passed_tests / total_tests if total_tests > 0 else 0
            },
            'reference_file': str(voacapx_file),
            'comparisons': all_comparisons
        }, f, indent=2)

    print(f"Detailed results saved to: {output_file}")
    print()

    return all_comparisons, passed_tests, failed_tests


# =============================================================================
# CLI
# =============================================================================

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Validate DVOACAP-Python against reference VOACAP output'
    )
    parser.add_argument('--hours', nargs='+', type=int,
                       help='UTC hours to test (default: all)')
    parser.add_argument('--freqs', nargs='+', type=float,
                       help='Frequencies to test in MHz (default: all)')
    parser.add_argument('--quiet', action='store_true',
                       help='Less verbose output')

    args = parser.parse_args()

    comparisons, passed, failed = validate_against_reference(
        verbose=not args.quiet,
        sample_hours=args.hours,
        sample_freqs=args.freqs
    )

    # Exit with error code if validation failed
    sys.exit(0 if failed == 0 else 1)
