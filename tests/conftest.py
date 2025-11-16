"""
Shared pytest fixtures for DVOACAP tests.

This module provides common fixtures used across multiple test files,
including sample data, common objects, and test utilities.
"""

import pytest
import numpy as np
from pathlib import Path
from datetime import datetime

from dvoacap.path_geometry import GeoPoint
from dvoacap.voacap_parser import VoacapParser
from dvoacap.fourier_maps import FourierMaps
from dvoacap.antenna_gain import AntennaModel, IsotropicAntenna, HalfWaveDipole
from dvoacap.noise_model import NoiseModel, TripleValue, Distribution


# ============================================================================
# Directory and File Fixtures
# ============================================================================

@pytest.fixture
def repo_root():
    """Get the repository root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def data_dir(repo_root):
    """Get the DVoaData directory path."""
    return repo_root / "DVoaData"


@pytest.fixture
def sample_coeff_file(data_dir):
    """Get a sample coefficient file (January)."""
    return data_dir / "Coeff01.dat"


@pytest.fixture
def sample_f2_file(data_dir):
    """Get a sample F2 file (January)."""
    return data_dir / "FOF2CCIR01.dat"


# ============================================================================
# Geographic Point Fixtures
# ============================================================================

@pytest.fixture
def new_york():
    """Geographic point for New York City (40.7128° N, 74.0060° W)."""
    return GeoPoint(
        lat=np.radians(40.7128),
        lon=np.radians(-74.0060)
    )


@pytest.fixture
def london():
    """Geographic point for London (51.5074° N, 0.1278° W)."""
    return GeoPoint(
        lat=np.radians(51.5074),
        lon=np.radians(-0.1278)
    )


@pytest.fixture
def tokyo():
    """Geographic point for Tokyo (35.6762° N, 139.6503° E)."""
    return GeoPoint(
        lat=np.radians(35.6762),
        lon=np.radians(139.6503)
    )


@pytest.fixture
def sydney():
    """Geographic point for Sydney (33.8688° S, 151.2093° E)."""
    return GeoPoint(
        lat=np.radians(-33.8688),
        lon=np.radians(151.2093)
    )


@pytest.fixture
def north_pole():
    """Geographic point near the North Pole."""
    return GeoPoint(
        lat=np.radians(89.5),
        lon=np.radians(0.0)
    )


@pytest.fixture
def south_pole():
    """Geographic point near the South Pole."""
    return GeoPoint(
        lat=np.radians(-89.5),
        lon=np.radians(0.0)
    )


@pytest.fixture
def equator_point():
    """Geographic point on the equator."""
    return GeoPoint(
        lat=0.0,
        lon=0.0
    )


# ============================================================================
# VOACAP Parser and Data Fixtures
# ============================================================================

@pytest.fixture
def voacap_parser(data_dir):
    """Create a VoacapParser instance with the data directory."""
    parser = VoacapParser()
    parser.data_dir = data_dir
    return parser


@pytest.fixture
def fourier_maps(data_dir):
    """Create a FourierMaps instance loaded with January data."""
    fourier_maps = FourierMaps(data_dir=str(data_dir))
    # Initialize with January, SSN=100, noon UTC
    fourier_maps.set_conditions(month=1, ssn=100.0, utc_fraction=0.5)
    return fourier_maps


# ============================================================================
# Antenna Fixtures
# ============================================================================

@pytest.fixture
def isotropic_antenna():
    """Create a basic isotropic antenna."""
    return IsotropicAntenna()


@pytest.fixture
def half_wave_dipole():
    """Create a half-wave dipole antenna."""
    return HalfWaveDipole()


@pytest.fixture
def antenna_with_gain():
    """Create an isotropic antenna with 10 dB extra gain."""
    return IsotropicAntenna(extra_gain_db=10.0)


@pytest.fixture
def tx_antenna():
    """Create a transmit antenna with realistic power (100W = 20 dBW)."""
    return IsotropicAntenna(tx_power_dbw=20.0)


# ============================================================================
# Noise Model Fixtures
# ============================================================================

@pytest.fixture
def noise_model(fourier_maps):
    """Create a NoiseModel instance."""
    return NoiseModel(fourier_maps)


@pytest.fixture
def sample_triple_value():
    """Create a sample TripleValue for testing."""
    return TripleValue(median=50.0, lower=45.0, upper=55.0)


@pytest.fixture
def sample_distribution():
    """Create a sample Distribution for testing."""
    dist = Distribution()
    dist.value = TripleValue(median=50.0, lower=45.0, upper=55.0)
    dist.error = TripleValue(median=5.0, lower=3.0, upper=7.0)
    return dist


# ============================================================================
# Frequency and Time Fixtures
# ============================================================================

@pytest.fixture
def hf_frequencies():
    """Common HF band frequencies in MHz."""
    return [3.5, 7.0, 10.1, 14.0, 18.1, 21.0, 24.9, 28.0]


@pytest.fixture
def test_frequencies():
    """Test frequencies covering the HF spectrum (MHz)."""
    return np.array([2.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0])


@pytest.fixture
def single_frequency():
    """Single test frequency (14 MHz - 20m band)."""
    return 14.0


@pytest.fixture
def sample_datetime():
    """Sample datetime for testing (noon UTC on Jan 1, 2024)."""
    return datetime(2024, 1, 1, 12, 0, 0)


@pytest.fixture
def sample_month():
    """Sample month number for testing (January)."""
    return 1


@pytest.fixture
def sample_ssn():
    """Sample sunspot number (moderate solar activity)."""
    return 100.0


# ============================================================================
# Propagation Mode Fixtures
# ============================================================================

@pytest.fixture
def propagation_modes():
    """List of propagation modes to test."""
    return ['E', 'F1', 'F2', 'Es']


@pytest.fixture
def hop_counts():
    """Common hop counts for testing."""
    return [1, 2, 3, 4]


# ============================================================================
# Test Utilities
# ============================================================================

@pytest.fixture
def assert_close():
    """Helper function for asserting floating point values are close."""
    def _assert_close(actual, expected, rel_tol=1e-5, abs_tol=1e-8, msg=""):
        """
        Assert that two values are close within tolerances.

        Args:
            actual: The actual value
            expected: The expected value
            rel_tol: Relative tolerance (default 1e-5)
            abs_tol: Absolute tolerance (default 1e-8)
            msg: Optional message to display on failure
        """
        if not np.isclose(actual, expected, rtol=rel_tol, atol=abs_tol):
            diff = abs(actual - expected)
            raise AssertionError(
                f"{msg}\nExpected: {expected}\nActual: {actual}\n"
                f"Difference: {diff} (rel_tol={rel_tol}, abs_tol={abs_tol})"
            )
    return _assert_close


@pytest.fixture
def assert_array_close():
    """Helper function for asserting arrays are close."""
    def _assert_array_close(actual, expected, rel_tol=1e-5, abs_tol=1e-8, msg=""):
        """
        Assert that two arrays are close within tolerances.

        Args:
            actual: The actual array
            expected: The expected array
            rel_tol: Relative tolerance (default 1e-5)
            abs_tol: Absolute tolerance (default 1e-8)
            msg: Optional message to display on failure
        """
        actual_arr = np.asarray(actual)
        expected_arr = np.asarray(expected)

        if not np.allclose(actual_arr, expected_arr, rtol=rel_tol, atol=abs_tol):
            diff = np.abs(actual_arr - expected_arr)
            max_diff = np.max(diff)
            raise AssertionError(
                f"{msg}\nMax difference: {max_diff} (rel_tol={rel_tol}, abs_tol={abs_tol})\n"
                f"Expected:\n{expected_arr}\nActual:\n{actual_arr}\n"
                f"Differences:\n{diff}"
            )
    return _assert_array_close


@pytest.fixture
def sample_array():
    """Create a sample numpy array for testing."""
    return np.array([1.0, 2.0, 3.0, 4.0, 5.0])


@pytest.fixture
def sample_2d_array():
    """Create a sample 2D numpy array for testing."""
    return np.array([
        [1.0, 2.0, 3.0],
        [4.0, 5.0, 6.0],
        [7.0, 8.0, 9.0]
    ])
