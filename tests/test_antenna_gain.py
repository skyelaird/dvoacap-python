"""
Tests for DVOACAP antenna gain module.

This module tests antenna gain calculations, patterns, polarization,
and frequency effects for various antenna models.
"""

import pytest
import numpy as np

from dvoacap.antenna_gain import (
    AntennaModel,
    IsotropicAntenna,
    HalfWaveDipole,
    VerticalMonopole,
    AntennaFarm
)


class TestAntennaModel:
    """Tests for base AntennaModel class."""

    def test_initialization_defaults(self):
        """Test AntennaModel initialization with default parameters."""
        ant = AntennaModel()
        assert ant.low_frequency == 0.0
        assert ant.high_frequency == 1e9
        assert ant.extra_gain_db == 0.0
        assert ant.tx_power_dbw == 1.0
        assert ant.frequency == 0.0
        assert ant.azimuth == 0.0

    def test_initialization_custom(self):
        """Test AntennaModel initialization with custom parameters."""
        ant = AntennaModel(
            low_frequency=3.5,
            high_frequency=30.0,
            extra_gain_db=5.0,
            tx_power_dbw=20.0
        )
        assert ant.low_frequency == 3.5
        assert ant.high_frequency == 30.0
        assert ant.extra_gain_db == 5.0
        assert ant.tx_power_dbw == 20.0

    def test_frequency_property(self):
        """Test frequency property getter and setter."""
        ant = AntennaModel(low_frequency=3.5, high_frequency=30.0)
        ant.frequency = 14.0
        assert ant.frequency == 14.0

    def test_frequency_below_range(self):
        """Test that setting frequency below range raises ValueError."""
        ant = AntennaModel(low_frequency=3.5, high_frequency=30.0)
        with pytest.raises(ValueError, match="outside antenna range"):
            ant.frequency = 2.0

    def test_frequency_above_range(self):
        """Test that setting frequency above range raises ValueError."""
        ant = AntennaModel(low_frequency=3.5, high_frequency=30.0)
        with pytest.raises(ValueError, match="outside antenna range"):
            ant.frequency = 50.0

    def test_frequency_at_boundaries(self):
        """Test that frequency can be set at boundary values."""
        ant = AntennaModel(low_frequency=3.5, high_frequency=30.0)
        ant.frequency = 3.5  # Lower boundary
        assert ant.frequency == 3.5
        ant.frequency = 30.0  # Upper boundary
        assert ant.frequency == 30.0

    def test_azimuth_property(self):
        """Test azimuth property getter and setter."""
        ant = AntennaModel()
        ant.azimuth = np.pi / 4
        assert ant.azimuth == np.pi / 4

    def test_azimuth_full_range(self):
        """Test azimuth can be set to various angles."""
        ant = AntennaModel()
        for azimuth in [0.0, np.pi / 2, np.pi, 3 * np.pi / 2, 2 * np.pi]:
            ant.azimuth = azimuth
            assert ant.azimuth == azimuth

    def test_get_gain_db_base(self):
        """Test base class get_gain_db returns only extra_gain_db."""
        ant = AntennaModel(extra_gain_db=5.0)
        for elevation in [0.0, np.pi / 4, np.pi / 2]:
            assert ant.get_gain_db(elevation) == 5.0


class TestIsotropicAntenna:
    """Tests for IsotropicAntenna class."""

    def test_initialization_default(self):
        """Test IsotropicAntenna initialization with defaults."""
        ant = IsotropicAntenna()
        assert ant.low_frequency == 0.0
        assert ant.high_frequency == 1e9
        assert ant.extra_gain_db == 0.0
        assert ant.tx_power_dbw == 1.0

    def test_initialization_custom_power(self):
        """Test IsotropicAntenna with custom transmit power."""
        ant = IsotropicAntenna(tx_power_dbw=20.0)
        assert ant.tx_power_dbw == 20.0

    def test_gain_pattern_isotropic(self):
        """Test that isotropic antenna has 0 dBi gain at all elevations."""
        ant = IsotropicAntenna()
        elevations = np.linspace(0, np.pi / 2, 10)
        for elevation in elevations:
            assert ant.get_gain_db(elevation) == 0.0

    def test_gain_independent_of_elevation(self):
        """Test gain is independent of elevation angle."""
        ant = IsotropicAntenna()
        gain_horizon = ant.get_gain_db(0.0)
        gain_45deg = ant.get_gain_db(np.pi / 4)
        gain_zenith = ant.get_gain_db(np.pi / 2)
        assert gain_horizon == gain_45deg == gain_zenith == 0.0

    def test_frequency_range_unlimited(self):
        """Test that isotropic antenna works at any frequency."""
        ant = IsotropicAntenna()
        # Should not raise errors for any frequency
        ant.frequency = 0.1  # Very low frequency
        ant.frequency = 100.0  # Very high frequency
        ant.frequency = 14.0  # Normal HF frequency

    def test_extra_gain_not_applied(self):
        """Test that extra_gain_db is always 0 for isotropic antenna."""
        ant = IsotropicAntenna()
        ant.extra_gain_db = 10.0  # Try to set extra gain
        # Isotropic antenna always returns 0 dBi
        assert ant.get_gain_db(0.0) == 0.0


class TestHalfWaveDipole:
    """Tests for HalfWaveDipole antenna class."""

    def test_initialization(self):
        """Test HalfWaveDipole initialization."""
        ant = HalfWaveDipole(low_frequency=14.0, high_frequency=14.5, tx_power_dbw=10.0)
        assert ant.low_frequency == 14.0
        assert ant.high_frequency == 14.5
        assert ant.tx_power_dbw == 10.0
        assert ant.extra_gain_db == 0.0

    def test_gain_at_horizon(self):
        """Test dipole gain at horizon (0 degrees elevation)."""
        ant = HalfWaveDipole(low_frequency=14.0, high_frequency=14.5)
        gain = ant.get_gain_db(0.0)
        # At horizon, cos(0) = 1, so gain should be 2.15 dBi
        assert np.isclose(gain, 2.15, atol=0.01)

    def test_gain_pattern_cosine(self):
        """Test dipole gain pattern follows cosine law."""
        ant = HalfWaveDipole(low_frequency=14.0, high_frequency=14.5)

        # Test at various elevations
        elevations = [0.0, np.pi / 6, np.pi / 4, np.pi / 3]
        for elev in elevations:
            gain = ant.get_gain_db(elev)
            expected = 2.15 + 10.0 * np.log10(max(0.001, np.cos(elev)))
            assert np.isclose(gain, expected, atol=0.01)

    def test_gain_below_horizon(self):
        """Test dipole gain below horizon is very low."""
        ant = HalfWaveDipole(low_frequency=14.0, high_frequency=14.5)
        gain = ant.get_gain_db(-np.pi / 4)  # 45 degrees below horizon
        assert gain == -40.0

    def test_gain_overhead(self):
        """Test dipole gain overhead is very low."""
        ant = HalfWaveDipole(low_frequency=14.0, high_frequency=14.5)
        gain = ant.get_gain_db(np.pi / 2 + 0.1)  # Slightly past vertical
        assert gain == -40.0

    def test_gain_decreases_with_elevation(self):
        """Test that gain decreases as elevation increases."""
        ant = HalfWaveDipole(low_frequency=14.0, high_frequency=14.5)

        gain_0deg = ant.get_gain_db(0.0)
        gain_30deg = ant.get_gain_db(np.pi / 6)
        gain_60deg = ant.get_gain_db(np.pi / 3)

        assert gain_0deg > gain_30deg > gain_60deg

    def test_extra_gain_applied(self):
        """Test that extra gain is properly applied."""
        ant = HalfWaveDipole(low_frequency=14.0, high_frequency=14.5)
        ant.extra_gain_db = 3.0

        gain_with_extra = ant.get_gain_db(0.0)
        ant.extra_gain_db = 0.0
        gain_without_extra = ant.get_gain_db(0.0)

        assert np.isclose(gain_with_extra, gain_without_extra + 3.0, atol=0.01)

    def test_frequency_range_enforcement(self):
        """Test that frequency range is enforced."""
        ant = HalfWaveDipole(low_frequency=14.0, high_frequency=14.5)

        # Should work within range
        ant.frequency = 14.2

        # Should fail outside range
        with pytest.raises(ValueError):
            ant.frequency = 10.0


class TestVerticalMonopole:
    """Tests for VerticalMonopole antenna class."""

    def test_initialization(self):
        """Test VerticalMonopole initialization."""
        ant = VerticalMonopole(low_frequency=7.0, high_frequency=7.3, tx_power_dbw=15.0)
        assert ant.low_frequency == 7.0
        assert ant.high_frequency == 7.3
        assert ant.tx_power_dbw == 15.0
        assert ant.extra_gain_db == 0.0

    def test_gain_at_horizon(self):
        """Test vertical monopole has maximum gain at horizon."""
        ant = VerticalMonopole(low_frequency=7.0, high_frequency=7.3)
        gain = ant.get_gain_db(0.0)
        assert np.isclose(gain, 5.0, atol=0.01)

    def test_gain_pattern(self):
        """Test vertical monopole gain pattern."""
        ant = VerticalMonopole(low_frequency=7.0, high_frequency=7.3)

        # Test at various elevations
        elevations = [0.0, np.pi / 6, np.pi / 4, np.pi / 3, np.pi / 2]
        for elev in elevations:
            if 0 <= elev <= np.pi / 2:
                gain = ant.get_gain_db(elev)
                expected = 5.0 - 10.0 * (elev / (np.pi / 2))
                assert np.isclose(gain, expected, atol=0.01)

    def test_gain_below_horizon(self):
        """Test vertical monopole has no radiation below horizon."""
        ant = VerticalMonopole(low_frequency=7.0, high_frequency=7.3)
        gain = ant.get_gain_db(-np.pi / 4)
        assert gain == -40.0

    def test_gain_overhead(self):
        """Test vertical monopole has no radiation overhead."""
        ant = VerticalMonopole(low_frequency=7.0, high_frequency=7.3)
        gain = ant.get_gain_db(np.pi / 2 + 0.1)
        assert gain == -40.0

    def test_gain_decreases_with_elevation(self):
        """Test that gain decreases linearly with elevation."""
        ant = VerticalMonopole(low_frequency=7.0, high_frequency=7.3)

        gain_0deg = ant.get_gain_db(0.0)
        gain_45deg = ant.get_gain_db(np.pi / 4)
        gain_90deg = ant.get_gain_db(np.pi / 2)

        assert gain_0deg > gain_45deg
        # At 90 degrees, gain should be 5.0 - 10.0 = -5.0
        assert np.isclose(gain_90deg, -5.0, atol=0.01)

    def test_low_angle_radiation(self):
        """Test vertical monopole has good low-angle radiation."""
        ant = VerticalMonopole(low_frequency=7.0, high_frequency=7.3)

        # Low angles (good for DX)
        gain_5deg = ant.get_gain_db(np.radians(5))
        gain_10deg = ant.get_gain_db(np.radians(10))

        # Should be close to maximum gain
        assert gain_5deg > 4.0
        assert gain_10deg > 3.5

    def test_extra_gain_applied(self):
        """Test that extra gain is properly applied."""
        ant = VerticalMonopole(low_frequency=7.0, high_frequency=7.3)
        ant.extra_gain_db = 2.0

        gain_with_extra = ant.get_gain_db(0.0)
        ant.extra_gain_db = 0.0
        gain_without_extra = ant.get_gain_db(0.0)

        assert np.isclose(gain_with_extra, gain_without_extra + 2.0, atol=0.01)


class TestAntennaFarm:
    """Tests for AntennaFarm class."""

    def test_initialization(self):
        """Test AntennaFarm initialization."""
        farm = AntennaFarm()
        assert isinstance(farm.current_antenna, IsotropicAntenna)
        assert len(farm.antennas) == 0

    def test_add_antenna(self):
        """Test adding antennas to the farm."""
        farm = AntennaFarm()
        ant1 = HalfWaveDipole(low_frequency=14.0, high_frequency=14.5)
        ant2 = VerticalMonopole(low_frequency=7.0, high_frequency=7.3)

        farm.add_antenna(ant1)
        assert len(farm.antennas) == 1

        farm.add_antenna(ant2)
        assert len(farm.antennas) == 2

    def test_select_antenna_in_range(self):
        """Test selecting antenna within its frequency range."""
        farm = AntennaFarm()
        dipole = HalfWaveDipole(low_frequency=14.0, high_frequency=14.5)
        farm.add_antenna(dipole)

        farm.select_antenna(14.2)
        assert farm.current_antenna is dipole
        assert farm.current_antenna.frequency == 14.2

    def test_select_antenna_out_of_range(self):
        """Test that isotropic is selected when no antenna covers frequency."""
        farm = AntennaFarm()
        dipole = HalfWaveDipole(low_frequency=14.0, high_frequency=14.5)
        farm.add_antenna(dipole)

        # Frequency outside dipole range
        farm.select_antenna(10.0)
        assert isinstance(farm.current_antenna, IsotropicAntenna)

    def test_select_antenna_multiple_options(self):
        """Test selecting first matching antenna when multiple are available."""
        farm = AntennaFarm()
        ant1 = HalfWaveDipole(low_frequency=14.0, high_frequency=14.5)
        ant2 = VerticalMonopole(low_frequency=7.0, high_frequency=7.3)

        farm.add_antenna(ant1)
        farm.add_antenna(ant2)

        # Select frequency that matches first antenna
        farm.select_antenna(14.2)
        assert farm.current_antenna is ant1

        # Select frequency that matches second antenna
        farm.select_antenna(7.1)
        assert farm.current_antenna is ant2

    def test_select_antenna_at_boundaries(self):
        """Test antenna selection at frequency boundaries."""
        farm = AntennaFarm()
        ant = HalfWaveDipole(low_frequency=14.0, high_frequency=14.5)
        farm.add_antenna(ant)

        # Lower boundary
        farm.select_antenna(14.0)
        assert farm.current_antenna is ant

        # Upper boundary
        farm.select_antenna(14.5)
        assert farm.current_antenna is ant

    def test_antenna_farm_frequency_sweep(self):
        """Test antenna farm with multiple antennas across HF spectrum."""
        farm = AntennaFarm()

        # Add antennas for different HF bands
        farm.add_antenna(VerticalMonopole(low_frequency=3.5, high_frequency=4.0))
        farm.add_antenna(HalfWaveDipole(low_frequency=7.0, high_frequency=7.3))
        farm.add_antenna(HalfWaveDipole(low_frequency=14.0, high_frequency=14.5))
        farm.add_antenna(VerticalMonopole(low_frequency=28.0, high_frequency=29.7))

        # Test frequency in each band
        farm.select_antenna(3.7)
        assert isinstance(farm.current_antenna, VerticalMonopole)

        farm.select_antenna(7.1)
        assert isinstance(farm.current_antenna, HalfWaveDipole)

        farm.select_antenna(14.2)
        assert isinstance(farm.current_antenna, HalfWaveDipole)

        farm.select_antenna(28.5)
        assert isinstance(farm.current_antenna, VerticalMonopole)

        # Frequency with no antenna
        farm.select_antenna(21.0)
        assert isinstance(farm.current_antenna, IsotropicAntenna)

    def test_default_isotropic_fallback(self):
        """Test that isotropic antenna is used when no antennas match."""
        farm = AntennaFarm()

        # No antennas added, should use isotropic
        farm.select_antenna(14.0)
        assert isinstance(farm.current_antenna, IsotropicAntenna)
        assert farm.current_antenna.frequency == 14.0


class TestAntennaGainPatterns:
    """Integration tests for antenna gain patterns."""

    @pytest.mark.parametrize("elevation_deg", [0, 5, 10, 15, 30, 45, 60, 75, 90])
    def test_isotropic_gain_all_elevations(self, elevation_deg):
        """Test isotropic antenna gain at all elevations."""
        ant = IsotropicAntenna()
        elevation = np.radians(elevation_deg)
        assert ant.get_gain_db(elevation) == 0.0

    @pytest.mark.parametrize("frequency", [3.5, 7.0, 14.0, 21.0, 28.0])
    def test_frequency_independence_isotropic(self, frequency):
        """Test isotropic antenna gain is independent of frequency."""
        ant = IsotropicAntenna()
        ant.frequency = frequency
        assert ant.get_gain_db(0.0) == 0.0

    def test_dipole_vs_vertical_pattern_comparison(self):
        """Compare gain patterns between dipole and vertical monopole."""
        dipole = HalfWaveDipole(low_frequency=14.0, high_frequency=14.5)
        vertical = VerticalMonopole(low_frequency=14.0, high_frequency=14.5)

        # Vertical should have higher gain at horizon
        assert vertical.get_gain_db(0.0) > dipole.get_gain_db(0.0)

        # Both should have reduced gain at high elevations
        assert dipole.get_gain_db(np.pi / 3) < dipole.get_gain_db(0.0)
        assert vertical.get_gain_db(np.pi / 3) < vertical.get_gain_db(0.0)

    def test_polarization_effect_simulation(self):
        """Simulate polarization effects through gain patterns."""
        # Horizontal polarization (dipole)
        horizontal = HalfWaveDipole(low_frequency=14.0, high_frequency=14.5)

        # Vertical polarization (monopole)
        vertical = VerticalMonopole(low_frequency=14.0, high_frequency=14.5)

        # Different antennas show different patterns
        # This simulates polarization effects
        low_angle = np.radians(5)

        # Vertical better at low angles
        assert vertical.get_gain_db(low_angle) > horizontal.get_gain_db(low_angle)


class TestAntennaErrorHandling:
    """Tests for error handling in antenna classes."""

    def test_frequency_validation_error_message(self):
        """Test that frequency validation provides clear error messages."""
        ant = AntennaModel(low_frequency=7.0, high_frequency=7.3)

        with pytest.raises(ValueError) as excinfo:
            ant.frequency = 10.0

        assert "10.0 MHz" in str(excinfo.value)
        assert "7.0" in str(excinfo.value)
        assert "7.3" in str(excinfo.value)

    def test_negative_frequency(self):
        """Test that negative frequency raises error."""
        ant = AntennaModel(low_frequency=3.5, high_frequency=30.0)

        with pytest.raises(ValueError):
            ant.frequency = -5.0

    def test_zero_frequency_range(self):
        """Test antenna with zero frequency range."""
        ant = AntennaModel(low_frequency=14.0, high_frequency=14.0)
        ant.frequency = 14.0  # Should work at exact frequency

        with pytest.raises(ValueError):
            ant.frequency = 14.1  # Just outside range
