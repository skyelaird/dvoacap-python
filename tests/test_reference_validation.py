#!/usr/bin/env python3
"""
Parametrized Reference Validation Tests

This module provides comprehensive validation tests against reference VOACAP
outputs using pytest's parametrization features. It supports multiple test
cases with different paths, frequencies, and conditions.

Test Structure:
- Each test case has its own reference file
- Tests are parametrized for easy expansion
- Results are collected for statistical analysis
- CI/CD friendly with clear pass/fail criteria

Usage:
    pytest tests/test_reference_validation.py -v
    pytest tests/test_reference_validation.py::test_medium_path -v
    pytest tests/test_reference_validation.py -k "ssn_100" -v
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

import pytest
import numpy as np

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.dvoacap.path_geometry import GeoPoint
from src.dvoacap.prediction_engine import PredictionEngine


# =============================================================================
# Test Case Definitions
# =============================================================================

@dataclass
class TestCase:
    """Definition of a validation test case"""
    name: str
    description: str
    tx_lat: float
    tx_lon: float
    rx_lat: float
    rx_lon: float
    distance_km: float
    month: int
    ssn: int
    reference_file: str
    tx_power_w: int = 500000
    enabled: bool = True


# Define all test cases
# Each test case needs a corresponding reference file
TEST_CASES = [
    TestCase(
        name="tangier_belgrade_ssn100",
        description="Medium path (2440km), moderate solar activity",
        tx_lat=35.80, tx_lon=-5.90,
        rx_lat=44.90, rx_lon=20.50,
        distance_km=2440,
        month=6,
        ssn=100,
        reference_file="SampleIO/voacapx.out",
        enabled=True
    ),
    # Add more test cases here as reference files become available
    # TestCase(
    #     name="philadelphia_boston_ssn100",
    #     description="Short path (430km), NVIS/E-layer propagation",
    #     tx_lat=39.95, tx_lon=-75.17,
    #     rx_lat=42.36, rx_lon=-71.06,
    #     distance_km=430,
    #     month=6,
    #     ssn=100,
    #     reference_file="SampleIO/reference_short_path/voacapx.out",
    #     enabled=False  # Enable when reference file is generated
    # ),
]


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
                    'metrics': {'MODE': [...], 'SNR': [...], 'REL': [...], ...}
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
        circuit_match = re.search(
            r'(\d+\.\d+)\s+([NS])\s+(\d+\.\d+)\s+([EW])\s+-\s+(\d+\.\d+)\s+([NS])\s+(\d+\.\d+)\s+([EW])',
            content
        )
        if circuit_match:
            results['metadata']['tx_lat'] = float(circuit_match.group(1)) * (
                1 if circuit_match.group(2) == 'N' else -1
            )
            results['metadata']['tx_lon'] = float(circuit_match.group(3)) * (
                -1 if circuit_match.group(4) == 'W' else 1
            )
            results['metadata']['rx_lat'] = float(circuit_match.group(5)) * (
                1 if circuit_match.group(6) == 'N' else -1
            )
            results['metadata']['rx_lon'] = float(circuit_match.group(7)) * (
                -1 if circuit_match.group(8) == 'W' else 1
            )

        ssn_match = re.search(r'SSN\s*=\s*(\d+)', content)
        if ssn_match:
            results['metadata']['ssn'] = int(ssn_match.group(1))

        # Parse prediction blocks (each UTC hour)
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

            # Extract frequencies
            freq_values = freq_str.split()
            prediction['frequencies'] = [
                float(f) for f in freq_values
                if f not in ['-', '0.0', '0.00'] and float(f) > 0.1
            ]
            num_freqs = len(prediction['frequencies'])

            # Extract metric lines
            metric_names = [
                'MODE', 'TANGLE', 'DELAY', 'V HITE', 'MUFday', 'LOSS',
                'DBU', 'S DBW', 'N DBW', 'SNR', 'RPWRG', 'REL', 'MPROB',
                'S PRB', 'SIG LW', 'SIG UP', 'SNR LW', 'SNR UP',
                'TGAIN', 'RGAIN', 'SNRxx'
            ]

            for metric in metric_names:
                pattern = r'^\s*([\d.\sEFef-]+?)\s+' + re.escape(metric) + r'\s*$'
                match = re.search(pattern, block, re.MULTILINE)
                if match:
                    values_str = match.group(1).split()
                    if metric == 'MODE':
                        mode_pattern = r'^\s*([\dEFef\s-]+?)\s+MODE\s*$'
                        mode_match = re.search(mode_pattern, block, re.MULTILINE)
                        if mode_match:
                            mode_values = re.split(r'\s{2,}', mode_match.group(1).strip())
                            mode_values = [v if v != '-' else None for v in mode_values]
                            prediction['metrics'][metric] = (
                                mode_values[1:1+num_freqs] if len(mode_values) > 1 else mode_values[:num_freqs]
                            )
                    else:
                        numeric_values = [
                            float(v) if v not in ['-', ''] else None
                            for v in values_str
                        ]
                        prediction['metrics'][metric] = (
                            numeric_values[1:1+num_freqs] if len(numeric_values) > 1 else numeric_values[:num_freqs]
                        )

            results['predictions'].append(prediction)

        return results


# =============================================================================
# Validation Functions
# =============================================================================

def run_dvoacap_prediction(
    tx_lat: float, tx_lon: float, rx_lat: float, rx_lon: float,
    freq_mhz: float, utc_hour: int, month: int, ssn: int,
    tx_power_w: int = 500000
) -> Optional[Dict]:
    """Run DVOACAP-Python prediction for comparison"""
    engine = PredictionEngine()
    engine.params.ssn = float(ssn)
    engine.params.month = month
    engine.params.tx_power = tx_power_w
    engine.params.tx_location = GeoPoint.from_degrees(tx_lat, tx_lon)
    engine.params.min_angle = np.deg2rad(0.1)

    rx_location = GeoPoint.from_degrees(rx_lat, rx_lon)
    utc_fraction = utc_hour / 24.0

    try:
        engine.predict(rx_location=rx_location, utc_time=utc_fraction, frequencies=[freq_mhz])

        if len(engine.predictions) > 0:
            pred = engine.predictions[0]
            return {
                'mode': pred.get_mode_name(engine.path.dist),
                'snr': pred.signal.snr_db,
                'reliability': pred.signal.reliability * 100,
                'loss': pred.signal.total_loss_db,
                'muf_day': pred.signal.muf_day,
                'signal_dbw': pred.signal.power_dbw,
                'virt_height': pred.virt_height,
                'tx_angle': np.rad2deg(pred.tx_elevation),
            }
        else:
            return None

    except Exception as e:
        pytest.fail(f"Prediction failed with exception: {e}")
        return None


# =============================================================================
# Pytest Test Functions
# =============================================================================

# Filter enabled test cases
ENABLED_TEST_CASES = [tc for tc in TEST_CASES if tc.enabled]


@pytest.fixture(scope="module", params=ENABLED_TEST_CASES, ids=lambda tc: tc.name)
def test_case(request):
    """Fixture providing each enabled test case"""
    return request.param


@pytest.fixture(scope="module")
def reference_data(test_case):
    """Fixture loading reference data for a test case"""
    reference_file = Path(__file__).parent.parent / test_case.reference_file

    if not reference_file.exists():
        pytest.skip(f"Reference file not found: {reference_file}")

    parser = VoacapReferenceParser()
    return parser.parse_voacapx_out(reference_file)


class TestReferenceValidation:
    """Parametrized reference validation tests"""

    def test_reference_file_exists(self, test_case):
        """Verify reference file exists for test case"""
        reference_file = Path(__file__).parent.parent / test_case.reference_file
        assert reference_file.exists(), f"Reference file not found: {reference_file}"

    def test_reference_metadata_matches(self, test_case, reference_data):
        """Verify reference file metadata matches test case"""
        metadata = reference_data['metadata']

        assert abs(metadata['tx_lat'] - test_case.tx_lat) < 0.1
        assert abs(metadata['tx_lon'] - test_case.tx_lon) < 0.1
        assert abs(metadata['rx_lat'] - test_case.rx_lat) < 0.1
        assert abs(metadata['rx_lon'] - test_case.rx_lon) < 0.1
        assert metadata['ssn'] == test_case.ssn

    @pytest.mark.parametrize("tolerance_factor", [1.0])
    def test_predictions_within_tolerance(self, test_case, reference_data, tolerance_factor):
        """
        Test that predictions match reference within tolerances

        Args:
            tolerance_factor: Multiplier for tolerances (for sensitivity testing)
        """
        # Tolerances
        snr_tolerance = 10.0 * tolerance_factor  # ±10 dB
        reliability_tolerance = 20.0 * tolerance_factor  # ±20%
        mufday_tolerance = 0.2 * tolerance_factor  # ±0.2

        results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'failures': []
        }

        for pred_block in reference_data['predictions']:
            utc_hour = int(pred_block['utc_hour'])

            for i, freq_mhz in enumerate(pred_block['frequencies']):
                # Get VOACAP reference values
                voacap_snr = pred_block['metrics'].get('SNR', [None])[i] if i < len(pred_block['metrics'].get('SNR', [])) else None
                voacap_rel = pred_block['metrics'].get('REL', [None])[i] if i < len(pred_block['metrics'].get('REL', [])) else None
                voacap_mufday = pred_block['metrics'].get('MUFday', [None])[i] if i < len(pred_block['metrics'].get('MUFday', [])) else None
                voacap_mode = pred_block['metrics'].get('MODE', [None])[i] if i < len(pred_block['metrics'].get('MODE', [])) else None

                # Skip if no valid mode
                if voacap_mode in [None, '-']:
                    continue

                # Run DVOACAP prediction
                dvoacap_result = run_dvoacap_prediction(
                    tx_lat=test_case.tx_lat,
                    tx_lon=test_case.tx_lon,
                    rx_lat=test_case.rx_lat,
                    rx_lon=test_case.rx_lon,
                    freq_mhz=freq_mhz,
                    utc_hour=utc_hour,
                    month=test_case.month,
                    ssn=test_case.ssn,
                    tx_power_w=test_case.tx_power_w
                )

                if dvoacap_result is None:
                    results['failed'] += 1
                    results['failures'].append(
                        f"{freq_mhz:.2f} MHz @ {utc_hour:02d}:00 - Prediction failed"
                    )
                    continue

                results['total'] += 1

                # Check tolerances
                failures_this_test = []

                if voacap_snr is not None:
                    snr_diff = abs(dvoacap_result['snr'] - voacap_snr)
                    if snr_diff > snr_tolerance:
                        failures_this_test.append(
                            f"SNR: {snr_diff:.1f} dB (DVOACAP: {dvoacap_result['snr']:.1f}, VOACAP: {voacap_snr:.1f})"
                        )

                if voacap_rel is not None:
                    voacap_rel_pct = voacap_rel * 100
                    rel_diff = abs(dvoacap_result['reliability'] - voacap_rel_pct)
                    if rel_diff > reliability_tolerance:
                        failures_this_test.append(
                            f"Reliability: {rel_diff:.1f}% (DVOACAP: {dvoacap_result['reliability']:.1f}%, VOACAP: {voacap_rel_pct:.1f}%)"
                        )

                if voacap_mufday is not None:
                    mufday_diff = abs(dvoacap_result['muf_day'] - voacap_mufday)
                    if mufday_diff > mufday_tolerance:
                        failures_this_test.append(
                            f"MUFday: {mufday_diff:.3f} (DVOACAP: {dvoacap_result['muf_day']:.3f}, VOACAP: {voacap_mufday:.3f})"
                        )

                if failures_this_test:
                    results['failed'] += 1
                    results['failures'].append(
                        f"{freq_mhz:.2f} MHz @ {utc_hour:02d}:00 - {', '.join(failures_this_test)}"
                    )
                else:
                    results['passed'] += 1

        # Calculate pass rate
        pass_rate = 100 * results['passed'] / results['total'] if results['total'] > 0 else 0

        # Report results
        report = f"\n{'='*80}\n"
        report += f"Test Case: {test_case.name}\n"
        report += f"Description: {test_case.description}\n"
        report += f"{'='*80}\n"
        report += f"Total tests: {results['total']}\n"
        report += f"Passed: {results['passed']} ({pass_rate:.1f}%)\n"
        report += f"Failed: {results['failed']}\n"

        if results['failures']:
            report += f"\nFailures:\n"
            for failure in results['failures'][:10]:  # Show first 10 failures
                report += f"  - {failure}\n"
            if len(results['failures']) > 10:
                report += f"  ... and {len(results['failures']) - 10} more\n"

        report += f"{'='*80}\n"

        print(report)

        # Assert >80% pass rate
        assert pass_rate >= 80.0, (
            f"Pass rate {pass_rate:.1f}% below 80% threshold for {test_case.name}. "
            f"Failed {results['failed']}/{results['total']} tests."
        )


# =============================================================================
# Statistical Summary
# =============================================================================

@pytest.fixture(scope="session", autouse=True)
def validation_summary(request):
    """Generate summary report after all tests"""
    yield

    # This runs after all tests complete
    results_file = Path(__file__).parent.parent / 'validation_reference_results.json'
    if results_file.exists():
        with open(results_file, 'r') as f:
            data = json.load(f)

        print("\n" + "="*80)
        print("VALIDATION SUMMARY - ALL TEST CASES")
        print("="*80)
        print(f"Overall Pass Rate: {data['summary']['pass_rate']:.1f}%")
        print(f"Total Comparisons: {data['summary']['total']}")
        print(f"Passed: {data['summary']['passed']}")
        print(f"Failed: {data['summary']['failed']}")
        print("="*80)


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v'])
