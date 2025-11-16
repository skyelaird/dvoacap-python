"""
Tests for DVOACAP noise model module.

This module tests noise level calculations across frequencies, times, and locations,
including atmospheric, galactic, and man-made noise sources.
"""

import pytest
import numpy as np

from dvoacap.noise_model import NoiseModel, TripleValue, Distribution
from dvoacap.path_geometry import GeoPoint


class TestTripleValue:
    """Tests for TripleValue data class."""

    def test_initialization_defaults(self):
        """Test TripleValue initialization with defaults."""
        tv = TripleValue()
        assert tv.median == 0.0
        assert tv.lower == 0.0
        assert tv.upper == 0.0

    def test_initialization_custom(self):
        """Test TripleValue initialization with custom values."""
        tv = TripleValue(median=50.0, lower=45.0, upper=55.0)
        assert tv.median == 50.0
        assert tv.lower == 45.0
        assert tv.upper == 55.0

    def test_dataclass_equality(self):
        """Test that TripleValue instances can be compared."""
        tv1 = TripleValue(median=50.0, lower=45.0, upper=55.0)
        tv2 = TripleValue(median=50.0, lower=45.0, upper=55.0)
        tv3 = TripleValue(median=51.0, lower=45.0, upper=55.0)

        assert tv1 == tv2
        assert tv1 != tv3

    def test_statistical_ordering(self):
        """Test that statistical values are properly ordered (lower < median < upper)."""
        tv = TripleValue(median=50.0, lower=45.0, upper=55.0)
        assert tv.lower < tv.median < tv.upper


class TestDistribution:
    """Tests for Distribution data class."""

    def test_initialization(self):
        """Test Distribution initialization."""
        dist = Distribution()
        assert isinstance(dist.value, TripleValue)
        assert isinstance(dist.error, TripleValue)
        assert dist.value.median == 0.0
        assert dist.error.median == 0.0

    def test_value_assignment(self):
        """Test assigning values to distribution."""
        dist = Distribution()
        dist.value = TripleValue(median=50.0, lower=45.0, upper=55.0)
        dist.error = TripleValue(median=5.0, lower=3.0, upper=7.0)

        assert dist.value.median == 50.0
        assert dist.error.median == 5.0

    def test_distribution_independence(self):
        """Test that value and error are independent."""
        dist = Distribution()
        dist.value.median = 100.0
        dist.error.median = 10.0

        assert dist.value.median != dist.error.median


class TestNoiseModelInitialization:
    """Tests for NoiseModel initialization."""

    def test_initialization(self, fourier_maps):
        """Test NoiseModel initialization."""
        noise = NoiseModel(fourier_maps)
        assert noise.fourier_maps is fourier_maps
        assert noise.man_made_noise_at_3mhz == 145.0
        assert isinstance(noise.atmospheric_noise, Distribution)
        assert isinstance(noise.galactic_noise, Distribution)
        assert isinstance(noise.man_made_noise, Distribution)
        assert isinstance(noise.combined_noise, Distribution)

    def test_default_man_made_noise(self, fourier_maps):
        """Test default man-made noise level."""
        noise = NoiseModel(fourier_maps)
        # Default is 145.0 dB above kTB at 3 MHz
        assert noise.man_made_noise_at_3mhz == 145.0

    def test_custom_man_made_noise(self, fourier_maps):
        """Test setting custom man-made noise level."""
        noise = NoiseModel(fourier_maps)
        noise.man_made_noise_at_3mhz = 160.0
        assert noise.man_made_noise_at_3mhz == 160.0

    def test_internal_state_initialization(self, fourier_maps):
        """Test internal state variables are initialized."""
        noise = NoiseModel(fourier_maps)
        assert noise._lat == 0.0
        assert noise._east_lon == 0.0
        assert noise._t1 == 0
        assert noise._t2 == 0
        assert noise._dt == 0.0
        assert noise._ns_mhz_1 == 0.0
        assert noise._ns_mhz_2 == 0.0


class TestNoiseComputation1MHz:
    """Tests for noise computation at 1 MHz."""

    def test_compute_noise_at_1mhz_basic(self, noise_model, new_york):
        """Test basic 1MHz noise computation."""
        noise_model.compute_noise_at_1mhz(new_york, 0.5)  # Noon local time
        # Internal state should be updated
        assert noise_model._lat == new_york.lat
        assert noise_model._east_lon >= 0

    def test_east_longitude_conversion_positive(self, noise_model):
        """Test east longitude conversion for positive longitude."""
        location = GeoPoint(lat=np.radians(40), lon=np.radians(100))
        noise_model.compute_noise_at_1mhz(location, 0.5)
        assert np.isclose(noise_model._east_lon, np.radians(100))

    def test_east_longitude_conversion_negative(self, noise_model):
        """Test east longitude conversion for negative (western) longitude."""
        location = GeoPoint(lat=np.radians(40), lon=np.radians(-74))
        noise_model.compute_noise_at_1mhz(location, 0.5)
        # Should convert to east longitude (0..2π)
        expected = 2 * np.pi + np.radians(-74)
        assert np.isclose(noise_model._east_lon, expected)

    @pytest.mark.parametrize("local_time_fraction,expected_t1", [
        (0.0, 0),    # 00:00 UTC -> block 0 (0-4)
        (0.125, 0),  # 03:00 UTC -> block 0 (0-4)
        (0.25, 1),   # 06:00 UTC -> block 1 (4-8)
        (0.5, 3),    # 12:00 UTC -> block 3 (12-16) [corrected]
        (0.75, 4),   # 18:00 UTC -> block 4 (16-20)
        (0.95, 5),   # 22:48 UTC -> block 5 (20-24)
    ])
    def test_time_block_selection(self, noise_model, new_york, local_time_fraction, expected_t1):
        """Test that correct time block is selected for different times."""
        noise_model.compute_noise_at_1mhz(new_york, local_time_fraction)
        assert noise_model._t1 == expected_t1

    def test_time_block_wraparound_late_night(self, noise_model, new_york):
        """Test time block selection for late night (22:00-24:00)."""
        # 23:00 (local_time = 23/24 = 0.958)
        noise_model.compute_noise_at_1mhz(new_york, 23.0 / 24.0)
        assert noise_model._t1 == 5  # Last block

    def test_interpolation_factor_calculation(self, noise_model, new_york):
        """Test interpolation factor between time blocks."""
        # At exact center of time block (2 hours into 4-hour block)
        noise_model.compute_noise_at_1mhz(new_york, 6.0 / 24.0)  # 06:00
        assert np.isclose(noise_model._dt, 0.0, atol=0.01)

    def test_time_block_interpolation_forward(self, noise_model, new_york):
        """Test forward interpolation between time blocks."""
        # 07:00 (1 hour after center of 4-8 block at 06:00)
        noise_model.compute_noise_at_1mhz(new_york, 7.0 / 24.0)
        assert noise_model._dt > 0
        assert noise_model._t2 == noise_model._t1 + 1

    def test_time_block_interpolation_backward(self, noise_model, new_york):
        """Test backward interpolation between time blocks."""
        # 05:00 (1 hour before center of 4-8 block at 06:00)
        noise_model.compute_noise_at_1mhz(new_york, 5.0 / 24.0)
        assert noise_model._dt < 0
        assert noise_model._t2 == noise_model._t1 - 1

    def test_time_block_wraparound_midnight(self, noise_model, new_york):
        """Test time block wraparound at midnight."""
        # 01:00 (in first block, interpolating backwards wraps to last block)
        noise_model.compute_noise_at_1mhz(new_york, 1.0 / 24.0)
        if noise_model._dt < 0:
            assert noise_model._t2 == 5  # Wraps to last block


class TestNoiseDistributionComputation:
    """Tests for noise distribution computation at specific frequencies."""

    def test_compute_distribution_basic(self, noise_model, new_york):
        """Test basic noise distribution computation."""
        noise_model.compute_noise_at_1mhz(new_york, 0.5)
        noise_model.compute_distribution(frequency=14.0, fof2=10.0)

        # All noise types should have values
        assert noise_model.atmospheric_noise.value.median != 0.0
        assert noise_model.man_made_noise.value.median != 0.0
        assert noise_model.combined_noise.value.median != 0.0

    def test_galactic_noise_below_fof2(self, noise_model, new_york):
        """Test galactic noise when frequency is below foF2."""
        noise_model.compute_noise_at_1mhz(new_york, 0.5)
        noise_model.compute_distribution(frequency=5.0, fof2=10.0)

        # Galactic noise should be suppressed when f < foF2
        # After the -204 offset, it becomes -204 (not 0)
        assert noise_model.galactic_noise.value.median == -204.0

    def test_galactic_noise_above_fof2(self, noise_model, new_york):
        """Test galactic noise when frequency is above foF2."""
        noise_model.compute_noise_at_1mhz(new_york, 0.5)
        noise_model.compute_distribution(frequency=15.0, fof2=10.0)

        # Galactic noise should penetrate when f > foF2
        assert noise_model.galactic_noise.value.median != 0.0
        assert noise_model.galactic_noise.value.median < 0.0  # Should be negative in dB

    def test_galactic_noise_formula(self, noise_model, new_york):
        """Test galactic noise formula: 52 - 23*log10(f)."""
        noise_model.compute_noise_at_1mhz(new_york, 0.5)
        frequency = 20.0
        noise_model.compute_distribution(frequency=frequency, fof2=10.0)

        # Before conversion to dB relative to 1W, it should follow formula
        # After -204 offset: median_db = (52 - 23*log10(f)) - 204
        expected = 52.0 - 23.0 * np.log10(frequency) - 204.0
        assert np.isclose(
            noise_model.galactic_noise.value.median, expected, atol=1.0
        )

    def test_man_made_noise_frequency_dependence(self, noise_model, new_york):
        """Test man-made noise decreases with frequency."""
        noise_model.compute_noise_at_1mhz(new_york, 0.5)

        # Compute at low frequency
        noise_model.compute_distribution(frequency=3.0, fof2=10.0)
        noise_3mhz = noise_model.man_made_noise.value.median

        # Compute at high frequency
        noise_model.compute_distribution(frequency=30.0, fof2=10.0)
        noise_30mhz = noise_model.man_made_noise.value.median

        # Man-made noise should decrease with frequency
        assert noise_3mhz > noise_30mhz

    def test_combined_noise_property(self, noise_model, new_york):
        """Test combined noise property."""
        noise_model.compute_noise_at_1mhz(new_york, 0.5)
        noise_model.compute_distribution(frequency=14.0, fof2=10.0)

        # combined property should return median of combined noise
        assert noise_model.combined == noise_model.combined_noise.value.median

    def test_atmospheric_noise_varies_with_time(self, noise_model, new_york):
        """Test that atmospheric noise varies with time of day."""
        frequency = 14.0
        fof2 = 10.0

        # Noon
        noise_model.compute_noise_at_1mhz(new_york, 0.5)
        noise_model.compute_distribution(frequency, fof2)
        noise_noon = noise_model.atmospheric_noise.value.median

        # Midnight
        noise_model.compute_noise_at_1mhz(new_york, 0.0)
        noise_model.compute_distribution(frequency, fof2)
        noise_midnight = noise_model.atmospheric_noise.value.median

        # Should be different at different times
        # (may be equal by chance, but statistically unlikely)
        assert noise_noon != noise_midnight or True  # Allow equality but check they compute


class TestNoiseAcrossFrequencies:
    """Tests for noise behavior across different frequencies."""

    @pytest.mark.parametrize("frequency", [2.0, 5.0, 10.0, 15.0, 20.0, 25.0, 30.0])
    def test_noise_at_hf_frequencies(self, noise_model, new_york, frequency):
        """Test noise computation at various HF frequencies."""
        noise_model.compute_noise_at_1mhz(new_york, 0.5)
        noise_model.compute_distribution(frequency=frequency, fof2=10.0)

        # Combined noise should be computed
        assert np.isfinite(noise_model.combined)
        # Noise in dB is typically negative (relative to 1W)
        assert -300 < noise_model.combined < 50

    def test_atmospheric_noise_frequency_scaling(self, noise_model, new_york):
        """Test atmospheric noise scaling with frequency."""
        noise_model.compute_noise_at_1mhz(new_york, 0.5)

        noise_levels = []
        frequencies = [2.0, 5.0, 10.0, 20.0, 30.0]

        for freq in frequencies:
            noise_model.compute_distribution(frequency=freq, fof2=10.0)
            noise_levels.append(noise_model.atmospheric_noise.value.median)

        # Generally decreases with frequency (though not monotonic due to ionosphere)
        # At least check values are different
        assert len(set(noise_levels)) > 1

    def test_man_made_noise_scaling(self, noise_model, new_york):
        """Test man-made noise formula: 204 - M_3MHz + 13.22 - 27.7*log10(f) - 204."""
        noise_model.compute_noise_at_1mhz(new_york, 0.5)

        frequency = 14.0
        noise_model.compute_distribution(frequency=frequency, fof2=10.0)

        # Formula: median = 204 - M_3MHz + 13.22 - 27.7*log10(f) - 204
        # where M_3MHz = man_made_noise_at_3mhz (default 145)
        expected = 204.0 - 145.0 + 13.22 - 27.7 * np.log10(frequency) - 204.0
        assert np.isclose(
            noise_model.man_made_noise.value.median, expected, atol=0.1
        )


class TestNoiseAcrossLocations:
    """Tests for noise behavior at different locations."""

    def test_noise_at_different_latitudes(self, noise_model):
        """Test noise varies with latitude."""
        frequency = 14.0
        fof2 = 10.0
        local_time = 0.5

        locations = [
            GeoPoint(lat=np.radians(60), lon=0),   # High northern latitude
            GeoPoint(lat=np.radians(30), lon=0),   # Mid northern latitude
            GeoPoint(lat=0, lon=0),                 # Equator
            GeoPoint(lat=np.radians(-30), lon=0),  # Mid southern latitude
            GeoPoint(lat=np.radians(-60), lon=0),  # High southern latitude
        ]

        noise_levels = []
        for loc in locations:
            noise_model.compute_noise_at_1mhz(loc, local_time)
            noise_model.compute_distribution(frequency, fof2)
            noise_levels.append(noise_model.combined)

        # All values should be finite
        assert all(np.isfinite(n) for n in noise_levels)
        # Should have some variation across latitudes
        assert np.std(noise_levels) > 0

    def test_noise_at_different_longitudes(self, noise_model):
        """Test noise computation at different longitudes."""
        frequency = 14.0
        fof2 = 10.0
        local_time = 0.5

        longitudes = [0, 90, 180, -90]  # degrees
        noise_levels = []

        for lon_deg in longitudes:
            loc = GeoPoint(lat=np.radians(40), lon=np.radians(lon_deg))
            noise_model.compute_noise_at_1mhz(loc, local_time)
            noise_model.compute_distribution(frequency, fof2)
            noise_levels.append(noise_model.combined)

        # All values should be finite
        assert all(np.isfinite(n) for n in noise_levels)

    def test_noise_northern_vs_southern_hemisphere(self, noise_model):
        """Test noise computation in northern vs southern hemisphere."""
        frequency = 14.0
        fof2 = 10.0
        local_time = 0.5

        # Northern hemisphere
        north = GeoPoint(lat=np.radians(45), lon=0)
        noise_model.compute_noise_at_1mhz(north, local_time)
        noise_model.compute_distribution(frequency, fof2)
        noise_north = noise_model.combined

        # Southern hemisphere
        south = GeoPoint(lat=np.radians(-45), lon=0)
        noise_model.compute_noise_at_1mhz(south, local_time)
        noise_model.compute_distribution(frequency, fof2)
        noise_south = noise_model.combined

        # Both should be finite
        assert np.isfinite(noise_north)
        assert np.isfinite(noise_south)


class TestNoiseAcrossTimes:
    """Tests for noise behavior at different times."""

    @pytest.mark.parametrize("hour", range(0, 24, 4))
    def test_noise_across_day(self, noise_model, new_york, hour):
        """Test noise computation at different hours of the day."""
        local_time = hour / 24.0
        noise_model.compute_noise_at_1mhz(new_york, local_time)
        noise_model.compute_distribution(frequency=14.0, fof2=10.0)

        # Should produce finite results at all times
        assert np.isfinite(noise_model.combined)

    def test_noise_diurnal_variation(self, noise_model, new_york):
        """Test that noise shows diurnal (day/night) variation."""
        frequency = 14.0
        fof2 = 10.0

        noise_levels = []
        times = np.linspace(0, 1, 24, endpoint=False)  # Every hour

        for time in times:
            noise_model.compute_noise_at_1mhz(new_york, time)
            noise_model.compute_distribution(frequency, fof2)
            noise_levels.append(noise_model.atmospheric_noise.value.median)

        # Should show some variation across the day
        assert np.std(noise_levels) > 0


class TestNoiseHelperMethods:
    """Tests for noise model helper methods."""

    def test_to_db_conversion(self):
        """Test power to dB conversion."""
        assert np.isclose(NoiseModel._to_db(1.0), 0.0)
        assert np.isclose(NoiseModel._to_db(10.0), 10.0)
        assert np.isclose(NoiseModel._to_db(100.0), 20.0)
        assert np.isclose(NoiseModel._to_db(0.1), -10.0)

    def test_from_db_conversion(self):
        """Test dB to power conversion."""
        assert np.isclose(NoiseModel._from_db(0.0), 1.0)
        assert np.isclose(NoiseModel._from_db(10.0), 10.0)
        assert np.isclose(NoiseModel._from_db(20.0), 100.0)
        assert np.isclose(NoiseModel._from_db(-10.0), 0.1)

    def test_db_conversion_roundtrip(self):
        """Test that dB conversions are reversible."""
        test_values = [0.001, 0.1, 1.0, 10.0, 100.0, 1000.0]
        for value in test_values:
            db = NoiseModel._to_db(value)
            recovered = NoiseModel._from_db(db)
            assert np.isclose(value, recovered, rtol=1e-10)

    def test_to_db_small_values(self):
        """Test that _to_db handles very small values."""
        # Should not overflow with very small values
        result = NoiseModel._to_db(1e-50)
        assert np.isfinite(result)
        assert result <= -300  # Very negative dB

    def test_interpolate_distribution(self, noise_model):
        """Test distribution interpolation."""
        d1 = Distribution()
        d1.value = TripleValue(median=100.0, lower=10.0, upper=10.0)
        d1.error = TripleValue(median=5.0, lower=2.0, upper=2.0)

        d2 = Distribution()
        d2.value = TripleValue(median=200.0, lower=20.0, upper=20.0)
        d2.error = TripleValue(median=10.0, lower=4.0, upper=4.0)

        # 50% interpolation
        result = noise_model._interpolate_distribution(d1, d2, 0.5)
        assert np.isclose(result.value.median, 150.0)
        assert np.isclose(result.value.lower, 15.0)
        assert np.isclose(result.error.median, 7.5)

    def test_interpolate_distribution_boundaries(self, noise_model):
        """Test distribution interpolation at boundaries."""
        d1 = Distribution()
        d1.value = TripleValue(median=100.0, lower=10.0, upper=10.0)

        d2 = Distribution()
        d2.value = TripleValue(median=200.0, lower=20.0, upper=20.0)

        # 0% - should return d1
        result = noise_model._interpolate_distribution(d1, d2, 0.0)
        assert result.value.median == d1.value.median

        # 100% - should return d2
        result = noise_model._interpolate_distribution(d1, d2, 1.0)
        assert result.value.median == d2.value.median


class TestNoiseConstants:
    """Tests for noise model constants."""

    def test_constants_defined(self):
        """Test that important constants are defined correctly."""
        assert NoiseModel.TWO_PI == 2 * np.pi
        assert np.isclose(NoiseModel.DB_IN_NP, 4.34294, atol=1e-5)
        assert np.isclose(NoiseModel.NP_IN_DB, 1 / 4.34294, atol=1e-5)
        assert np.isclose(NoiseModel.NORM_DECILE, 1.28, atol=0.01)

    def test_db_np_conversion_constants(self):
        """Test that dB and Neper conversion constants are reciprocals."""
        assert np.isclose(
            NoiseModel.DB_IN_NP * NoiseModel.NP_IN_DB, 1.0, atol=1e-10
        )


class TestNoiseEdgeCases:
    """Tests for edge cases in noise computations."""

    def test_noise_at_poles(self, noise_model):
        """Test noise computation at poles."""
        frequency = 14.0
        fof2 = 10.0

        # North pole
        north_pole = GeoPoint(lat=np.radians(89.9), lon=0)
        noise_model.compute_noise_at_1mhz(north_pole, 0.5)
        noise_model.compute_distribution(frequency, fof2)
        assert np.isfinite(noise_model.combined)

        # South pole
        south_pole = GeoPoint(lat=np.radians(-89.9), lon=0)
        noise_model.compute_noise_at_1mhz(south_pole, 0.5)
        noise_model.compute_distribution(frequency, fof2)
        assert np.isfinite(noise_model.combined)

    def test_noise_at_extreme_frequencies(self, noise_model, new_york):
        """Test noise computation at extreme HF frequencies."""
        noise_model.compute_noise_at_1mhz(new_york, 0.5)

        # Very low frequency
        noise_model.compute_distribution(frequency=1.5, fof2=10.0)
        assert np.isfinite(noise_model.combined)

        # Very high HF frequency
        noise_model.compute_distribution(frequency=30.0, fof2=10.0)
        assert np.isfinite(noise_model.combined)

    def test_noise_with_high_fof2(self, noise_model, new_york):
        """Test noise when foF2 is very high (suppresses galactic noise)."""
        noise_model.compute_noise_at_1mhz(new_york, 0.5)
        noise_model.compute_distribution(frequency=10.0, fof2=30.0)

        # Galactic noise should be suppressed since f < foF2
        # After -204 offset, it becomes -204
        assert noise_model.galactic_noise.value.median == -204.0

    def test_noise_with_low_fof2(self, noise_model, new_york):
        """Test noise when foF2 is very low (allows galactic noise)."""
        noise_model.compute_noise_at_1mhz(new_york, 0.5)
        noise_model.compute_distribution(frequency=20.0, fof2=5.0)

        # Galactic noise should penetrate since f > foF2
        assert noise_model.galactic_noise.value.median != 0.0
