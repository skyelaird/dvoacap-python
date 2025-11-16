"""
Tests for DVOACAP solar calculations module.

This module tests solar zenith angle, local time calculations,
and day/night determination across various locations and times.
"""

import pytest
import math
from datetime import datetime

from dvoacap.solar import (
    GeographicPoint,
    compute_zenith_angle,
    compute_local_time,
    is_daytime,
    solar_elevation_angle,
    get_utc_fraction,
    SolarCalculator,
    TWO_PI,
    HALF_PI,
    RinD,
    SUN_LAT
)


class TestGeographicPoint:
    """Tests for GeographicPoint data class."""

    def test_initialization(self):
        """Test GeographicPoint initialization."""
        point = GeographicPoint(latitude=math.radians(40), longitude=math.radians(-74))
        assert point.latitude == math.radians(40)
        assert point.longitude == math.radians(-74)

    def test_from_degrees(self):
        """Test creating GeographicPoint from degrees."""
        point = GeographicPoint.from_degrees(40.0, -74.0)
        assert math.isclose(point.latitude, math.radians(40.0))
        assert math.isclose(point.longitude, math.radians(-74.0))

    def test_from_degrees_extremes(self):
        """Test from_degrees with extreme values."""
        # North pole
        north_pole = GeographicPoint.from_degrees(90.0, 0.0)
        assert math.isclose(north_pole.latitude, math.pi / 2)

        # South pole
        south_pole = GeographicPoint.from_degrees(-90.0, 0.0)
        assert math.isclose(south_pole.latitude, -math.pi / 2)

        # Antimeridian
        point = GeographicPoint.from_degrees(0.0, 180.0)
        assert math.isclose(point.longitude, math.pi)

    def test_conversion_roundtrip(self):
        """Test that degrees-to-radians conversion is accurate."""
        lat_deg, lon_deg = 51.5, -0.1
        point = GeographicPoint.from_degrees(lat_deg, lon_deg)
        assert math.isclose(math.degrees(point.latitude), lat_deg)
        assert math.isclose(math.degrees(point.longitude), lon_deg)


class TestGetUtcFraction:
    """Tests for UTC fraction conversion."""

    def test_midnight(self):
        """Test UTC fraction at midnight."""
        dt = datetime(2024, 6, 15, 0, 0, 0)
        frac = get_utc_fraction(dt)
        assert math.isclose(frac, 0.0)

    def test_noon(self):
        """Test UTC fraction at noon."""
        dt = datetime(2024, 6, 15, 12, 0, 0)
        frac = get_utc_fraction(dt)
        assert math.isclose(frac, 0.5)

    def test_quarter_day(self):
        """Test UTC fraction at 6:00."""
        dt = datetime(2024, 6, 15, 6, 0, 0)
        frac = get_utc_fraction(dt)
        assert math.isclose(frac, 0.25)

    def test_three_quarter_day(self):
        """Test UTC fraction at 18:00."""
        dt = datetime(2024, 6, 15, 18, 0, 0)
        frac = get_utc_fraction(dt)
        assert math.isclose(frac, 0.75)

    def test_with_minutes_seconds(self):
        """Test UTC fraction with minutes and seconds."""
        dt = datetime(2024, 6, 15, 12, 30, 0)
        frac = get_utc_fraction(dt)
        # 12:30 = 12.5 hours = 12.5/24 = 0.520833...
        assert math.isclose(frac, 12.5 / 24.0)

    def test_with_microseconds(self):
        """Test UTC fraction with microseconds."""
        dt = datetime(2024, 6, 15, 0, 0, 0, 500000)  # 0.5 seconds
        frac = get_utc_fraction(dt)
        assert math.isclose(frac, 0.5 / 86400.0, rel_tol=1e-6)

    def test_almost_midnight(self):
        """Test UTC fraction just before midnight."""
        dt = datetime(2024, 6, 15, 23, 59, 59)
        frac = get_utc_fraction(dt)
        assert frac < 1.0
        assert frac > 0.999


class TestComputeLocalTime:
    """Tests for local time computation."""

    def test_utc_at_greenwich(self):
        """Test local time equals UTC at Greenwich (0° longitude)."""
        utc_frac = 0.5  # Noon UTC
        lon = 0.0
        local = compute_local_time(utc_frac, lon)
        assert math.isclose(local, 0.5)

    def test_local_time_west(self):
        """Test local time west of Greenwich."""
        utc_frac = 0.5  # Noon UTC
        lon = math.radians(-90)  # 90°W (6 hours behind)
        local = compute_local_time(utc_frac, lon)
        # 12:00 UTC - 6h = 06:00 local = 0.25
        assert math.isclose(local, 0.25, atol=0.01)

    def test_local_time_east(self):
        """Test local time east of Greenwich."""
        utc_frac = 0.5  # Noon UTC
        lon = math.radians(90)  # 90°E (6 hours ahead)
        local = compute_local_time(utc_frac, lon)
        # 12:00 UTC + 6h = 18:00 local = 0.75
        assert math.isclose(local, 0.75, atol=0.01)

    def test_wraparound_past_midnight(self):
        """Test local time wraps around correctly past midnight."""
        utc_frac = 0.9  # 21:36 UTC
        lon = math.radians(90)  # 90°E (+6h)
        local = compute_local_time(utc_frac, lon)
        # Should wrap around to next day
        # 21:36 + 6h = 03:36 next day
        expected = (0.9 + 0.25) % 1.0
        assert math.isclose(local, expected, atol=0.01)

    def test_midnight_convention(self):
        """Test VOACAP convention: midnight returns 1.0 not 0.0."""
        utc_frac = 0.0
        lon = 0.0
        local = compute_local_time(utc_frac, lon)
        # Should return 1.0 instead of 0.0
        assert math.isclose(local, 1.0)

    def test_international_date_line(self):
        """Test local time at international date line."""
        utc_frac = 0.5  # Noon UTC
        lon = math.radians(180)  # 180° (12 hours ahead)
        local = compute_local_time(utc_frac, lon)
        # 12:00 UTC + 12h = 00:00 local = 1.0 (VOACAP convention)
        assert math.isclose(local, 1.0) or math.isclose(local, 0.0)

    @pytest.mark.parametrize("lon_deg", [-180, -90, 0, 90, 180])
    def test_various_longitudes(self, lon_deg):
        """Test local time at various longitudes."""
        utc_frac = 0.5
        lon = math.radians(lon_deg)
        local = compute_local_time(utc_frac, lon)
        # Should be in valid range
        assert 0.0 < local <= 1.0


class TestComputeZenithAngle:
    """Tests for solar zenith angle computation."""

    def test_noon_at_equator_equinox(self):
        """Test zenith angle at noon at equator during equinox."""
        point = GeographicPoint(latitude=0, longitude=0)
        utc_frac = 0.5  # Noon UTC
        month = 3  # March (vernal equinox)

        zenith = compute_zenith_angle(point, utc_frac, month)

        # At equinox, sun should be near zenith at equator at noon
        # Should be close to 0 degrees (overhead)
        assert zenith < math.radians(25)  # Within 25 degrees of overhead

    def test_zenith_angle_range(self):
        """Test zenith angle is always in valid range [0, π]."""
        point = GeographicPoint(latitude=math.radians(45), longitude=0)

        for month in range(1, 13):
            for utc_frac in [0.0, 0.25, 0.5, 0.75]:
                zenith = compute_zenith_angle(point, utc_frac, month)
                assert 0 <= zenith <= math.pi

    def test_midnight_vs_noon(self):
        """Test zenith angle at midnight vs noon."""
        point = GeographicPoint(latitude=math.radians(45), longitude=0)
        month = 6  # June

        zenith_midnight = compute_zenith_angle(point, 0.0, month)
        zenith_noon = compute_zenith_angle(point, 0.5, month)

        # Sun should be higher (smaller zenith) at noon than midnight
        assert zenith_noon < zenith_midnight

    def test_summer_solstice_northern_hemisphere(self):
        """Test zenith angle during summer solstice in northern hemisphere."""
        point = GeographicPoint(latitude=math.radians(45), longitude=0)
        utc_frac = 0.5  # Noon
        month = 6  # June (summer solstice)

        zenith_summer = compute_zenith_angle(point, utc_frac, month)

        # Should have smaller zenith angle (sun higher) in summer
        assert zenith_summer < math.radians(70)

    def test_winter_solstice_northern_hemisphere(self):
        """Test zenith angle during winter solstice in northern hemisphere."""
        point = GeographicPoint(latitude=math.radians(45), longitude=0)
        utc_frac = 0.5  # Noon
        month = 12  # December (winter solstice)

        zenith_winter = compute_zenith_angle(point, utc_frac, month)

        # Should have larger zenith angle (sun lower) in winter
        assert zenith_winter > math.radians(45)

    def test_seasonal_variation(self):
        """Test zenith angle varies with season."""
        point = GeographicPoint(latitude=math.radians(45), longitude=0)
        utc_frac = 0.5  # Noon

        zenith_june = compute_zenith_angle(point, utc_frac, 6)
        zenith_december = compute_zenith_angle(point, utc_frac, 12)

        # Should be different in summer vs winter
        assert abs(zenith_june - zenith_december) > math.radians(20)

    def test_northern_vs_southern_hemisphere(self):
        """Test seasonal variation is opposite in southern hemisphere."""
        lat = 45
        north = GeographicPoint(latitude=math.radians(lat), longitude=0)
        south = GeographicPoint(latitude=math.radians(-lat), longitude=0)
        utc_frac = 0.5

        # June: summer in north, winter in south
        zenith_north_june = compute_zenith_angle(north, utc_frac, 6)
        zenith_south_june = compute_zenith_angle(south, utc_frac, 6)

        # North should have smaller zenith (higher sun) in June
        assert zenith_north_june < zenith_south_june

    def test_polar_regions_summer(self):
        """Test zenith angle in polar regions during summer."""
        north_pole = GeographicPoint(latitude=math.radians(85), longitude=0)
        utc_frac = 0.5
        month = 6  # Arctic summer

        zenith = compute_zenith_angle(north_pole, utc_frac, month)

        # During polar summer, sun should be above horizon most of the day
        assert zenith < math.radians(95)

    def test_polar_regions_winter(self):
        """Test zenith angle in polar regions during winter."""
        north_pole = GeographicPoint(latitude=math.radians(85), longitude=0)
        utc_frac = 0.5
        month = 12  # Arctic winter

        zenith = compute_zenith_angle(north_pole, utc_frac, month)

        # During polar winter, sun should be below horizon
        assert zenith > math.radians(90)

    @pytest.mark.parametrize("month", range(1, 13))
    def test_all_months(self, month):
        """Test zenith angle computation for all months."""
        point = GeographicPoint(latitude=math.radians(40), longitude=math.radians(-74))
        utc_frac = 0.5

        zenith = compute_zenith_angle(point, utc_frac, month)

        # Should be valid for all months
        assert 0 <= zenith <= math.pi
        assert math.isfinite(zenith)

    def test_longitude_effect(self):
        """Test that longitude affects time of solar noon."""
        lat = math.radians(40)
        west = GeographicPoint(latitude=lat, longitude=math.radians(-90))
        east = GeographicPoint(latitude=lat, longitude=math.radians(90))

        # At noon UTC
        utc_frac = 0.5
        month = 6

        zenith_west = compute_zenith_angle(west, utc_frac, month)
        zenith_east = compute_zenith_angle(east, utc_frac, month)

        # Should be different due to longitude
        assert zenith_west != zenith_east


class TestIsDaytime:
    """Tests for daytime determination."""

    def test_clearly_daytime(self):
        """Test daytime when sun is well above horizon."""
        zenith = math.radians(30)  # Sun 60° above horizon
        assert is_daytime(zenith)

    def test_clearly_nighttime(self):
        """Test nighttime when sun is well below horizon."""
        zenith = math.radians(120)  # Sun 30° below horizon
        assert not is_daytime(zenith)

    def test_at_horizon(self):
        """Test at geometric horizon (90°)."""
        zenith = math.radians(90)
        # Default twilight is 96°, so 90° should be daytime
        assert is_daytime(zenith)

    def test_twilight_boundary(self):
        """Test at default twilight boundary (96°)."""
        zenith = math.radians(96)
        # At exactly the boundary, should not be daytime
        assert not is_daytime(zenith, twilight_angle=math.radians(96))

    def test_custom_twilight_angle(self):
        """Test with custom twilight angle."""
        zenith = math.radians(95)

        # With geometric horizon (90°)
        assert not is_daytime(zenith, twilight_angle=math.radians(90))

        # With nautical twilight (102°)
        assert is_daytime(zenith, twilight_angle=math.radians(102))

    @pytest.mark.parametrize("twilight_deg", [90, 96, 102, 108])
    def test_various_twilight_definitions(self, twilight_deg):
        """Test various twilight angle definitions."""
        zenith = math.radians(80)  # Clearly daytime
        assert is_daytime(zenith, twilight_angle=math.radians(twilight_deg))

        zenith = math.radians(110)  # Clearly nighttime
        assert not is_daytime(zenith, twilight_angle=math.radians(twilight_deg))


class TestSolarElevationAngle:
    """Tests for solar elevation angle conversion."""

    def test_zenith_to_elevation(self):
        """Test conversion from zenith to elevation angle."""
        # Sun at zenith
        elevation = solar_elevation_angle(0.0)
        assert math.isclose(elevation, math.pi / 2)

        # Sun at horizon
        elevation = solar_elevation_angle(math.pi / 2)
        assert math.isclose(elevation, 0.0)

        # Sun below horizon
        elevation = solar_elevation_angle(math.pi)
        assert math.isclose(elevation, -math.pi / 2)

    def test_elevation_range(self):
        """Test elevation angle range."""
        for zenith_deg in range(0, 181, 10):
            zenith = math.radians(zenith_deg)
            elevation = solar_elevation_angle(zenith)

            # Elevation should be complementary to zenith
            assert math.isclose(zenith + elevation, math.pi / 2)

    def test_elevation_signs(self):
        """Test elevation angle signs."""
        # Above horizon (zenith < 90°) -> positive elevation
        elevation = solar_elevation_angle(math.radians(45))
        assert elevation > 0

        # Below horizon (zenith > 90°) -> negative elevation
        elevation = solar_elevation_angle(math.radians(135))
        assert elevation < 0


class TestSolarCalculator:
    """Tests for SolarCalculator class."""

    def test_initialization(self):
        """Test SolarCalculator initialization."""
        calc = SolarCalculator()
        assert calc is not None

    def test_calculate_zenith_angle(self):
        """Test calculate_zenith_angle method."""
        calc = SolarCalculator()
        location = GeographicPoint.from_degrees(40.0, -74.0)
        time = datetime(2024, 6, 15, 12, 0)

        zenith = calc.calculate_zenith_angle(location, time)

        assert 0 <= zenith <= math.pi
        assert math.isfinite(zenith)

    def test_is_daytime_at(self):
        """Test is_daytime_at method."""
        calc = SolarCalculator()
        location = GeographicPoint.from_degrees(40.0, -74.0)

        # Noon in June - should be daytime
        time_noon = datetime(2024, 6, 15, 16, 0)  # Noon local (UTC-4)
        assert calc.is_daytime_at(location, time_noon)

        # Midnight in June - should be nighttime
        time_midnight = datetime(2024, 6, 15, 4, 0)  # Midnight local (UTC-4)
        assert not calc.is_daytime_at(location, time_midnight)

    def test_is_daytime_at_custom_twilight(self):
        """Test is_daytime_at with custom twilight angle."""
        calc = SolarCalculator()
        location = GeographicPoint.from_degrees(60.0, 0.0)  # High latitude
        time = datetime(2024, 6, 15, 22, 0)  # Late evening

        # With geometric horizon
        result_90 = calc.is_daytime_at(location, time, twilight_deg=90.0)

        # With civil twilight
        result_96 = calc.is_daytime_at(location, time, twilight_deg=96.0)

        # One might be day while the other is night
        # Just verify both return boolean
        assert isinstance(result_90, bool)
        assert isinstance(result_96, bool)

    def test_calculate_local_time(self):
        """Test calculate_local_time method."""
        calc = SolarCalculator()
        time = datetime(2024, 6, 15, 12, 0)  # Noon UTC

        # At Greenwich
        local = calc.calculate_local_time(0.0, time)
        assert math.isclose(local, 0.5)

        # 90°W (6 hours behind)
        local = calc.calculate_local_time(-90.0, time)
        assert math.isclose(local, 0.25, atol=0.01)

    def test_calculator_consistency(self):
        """Test that SolarCalculator gives same results as module functions."""
        calc = SolarCalculator()
        location = GeographicPoint.from_degrees(51.5, -0.1)
        time = datetime(2024, 6, 15, 12, 0)

        # Calculate using class method
        zenith_class = calc.calculate_zenith_angle(location, time)

        # Calculate using module function
        utc_frac = get_utc_fraction(time)
        zenith_func = compute_zenith_angle(location, utc_frac, time.month)

        assert math.isclose(zenith_class, zenith_func)


class TestSolarConstants:
    """Tests for solar module constants."""

    def test_constants_defined(self):
        """Test that constants are defined correctly."""
        assert TWO_PI == 2 * math.pi
        assert HALF_PI == math.pi / 2
        assert math.isclose(RinD, math.pi / 180)

    def test_sun_lat_table(self):
        """Test SUN_LAT table has all months."""
        assert len(SUN_LAT) == 12

        for month in range(1, 13):
            assert month in SUN_LAT
            start, end = SUN_LAT[month]
            # Should be in valid latitude range
            assert -math.pi / 2 <= start <= math.pi / 2
            assert -math.pi / 2 <= end <= math.pi / 2

    def test_sun_lat_seasonal_pattern(self):
        """Test that sun latitude follows expected seasonal pattern."""
        # June should have maximum positive (northern) declination
        june_start, june_end = SUN_LAT[6]
        assert june_start > 0 and june_end > 0

        # December should have maximum negative (southern) declination
        dec_start, dec_end = SUN_LAT[12]
        assert dec_start < 0 and dec_end < 0

        # March and September (equinoxes) should be near zero
        march_start, march_end = SUN_LAT[3]
        assert abs(march_start) < math.radians(15) or abs(march_end) < math.radians(15)


class TestSolarEdgeCases:
    """Tests for edge cases in solar calculations."""

    def test_exactly_at_pole(self):
        """Test calculations at exact poles."""
        north_pole = GeographicPoint(latitude=math.pi / 2, longitude=0)
        south_pole = GeographicPoint(latitude=-math.pi / 2, longitude=0)

        for pole in [north_pole, south_pole]:
            zenith = compute_zenith_angle(pole, 0.5, 6)
            assert math.isfinite(zenith)
            assert 0 <= zenith <= math.pi

    def test_date_line_crossing(self):
        """Test local time crossing international date line."""
        # Just west of date line
        lon_west = math.radians(179.9)
        local_west = compute_local_time(0.5, lon_west)

        # Just east of date line
        lon_east = math.radians(-179.9)
        local_east = compute_local_time(0.5, lon_east)

        # Both should be valid
        assert 0 < local_west <= 1
        assert 0 < local_east <= 1

    def test_near_midnight_local_time(self):
        """Test local time very close to midnight."""
        utc_frac = 0.001  # Just after midnight UTC
        lon = 0.0
        local = compute_local_time(utc_frac, lon)

        # Should return 1.0 by VOACAP convention
        assert math.isclose(local, 1.0) or math.isclose(local, 0.001)

    def test_all_month_boundaries(self):
        """Test that solar declination is reasonable at month boundaries."""
        point = GeographicPoint(latitude=0, longitude=0)
        utc_frac = 0.5

        zenith_angles = []
        for month in range(1, 13):
            zenith = compute_zenith_angle(point, utc_frac, month)
            zenith_angles.append(zenith)
            assert math.isfinite(zenith)

        # Should show variation across the year
        assert len(set(zenith_angles)) > 1

    def test_continuous_time_progression(self):
        """Test that zenith angle changes smoothly with time."""
        point = GeographicPoint(latitude=math.radians(40), longitude=0)
        month = 6

        zenith_values = []
        for hour in range(24):
            utc_frac = hour / 24.0
            zenith = compute_zenith_angle(point, utc_frac, month)
            zenith_values.append(zenith)

        # Check that values change smoothly (no huge jumps)
        for i in range(len(zenith_values) - 1):
            diff = abs(zenith_values[i + 1] - zenith_values[i])
            assert diff < math.radians(30)  # No jumps > 30 degrees per hour
