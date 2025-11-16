"""
Tests for DVOACAP geomagnetic field module.

This module tests magnetic latitude, gyrofrequency, and dip angle
calculations at various locations.
"""

import pytest
import math
import numpy as np

from dvoacap.geomagnetic import (
    GeographicPoint,
    GeomagneticParameters,
    SinCos,
    make_sincos_array,
    GeomagneticField,
    GeomagneticCalculator,
    TWO_PI,
    HALF_PI,
    RinD,
    MAG_POLE_LAT,
    MAG_POLE_LON,
    G,
    H,
    CT
)


class TestSinCos:
    """Tests for SinCos data class."""

    def test_initialization(self):
        """Test SinCos initialization."""
        sc = SinCos(sin=0.5, cos=0.866)
        assert sc.sin == 0.5
        assert sc.cos == 0.866

    def test_pythagorean_identity(self):
        """Test that sin² + cos² = 1 for valid SinCos objects."""
        angle = math.pi / 6
        sc = SinCos(sin=math.sin(angle), cos=math.cos(angle))
        assert math.isclose(sc.sin**2 + sc.cos**2, 1.0)


class TestMakeSincosArray:
    """Tests for make_sincos_array function."""

    def test_basic_array(self):
        """Test basic sin/cos array generation."""
        x = math.pi / 4
        arr = make_sincos_array(x, 4)

        assert len(arr) == 4
        # n=0: sin(0) = 0, cos(0) = 1
        assert math.isclose(arr[0].sin, 0.0)
        assert math.isclose(arr[0].cos, 1.0)

        # n=1: sin(π/4), cos(π/4)
        assert math.isclose(arr[1].sin, math.sin(x))
        assert math.isclose(arr[1].cos, math.cos(x))

    def test_array_length_7(self):
        """Test sin/cos array with length 7 (used in geomagnetic calculations)."""
        x = math.pi / 6
        arr = make_sincos_array(x, 7)

        assert len(arr) == 7

        # Verify all values satisfy Pythagorean identity
        for sc in arr:
            assert math.isclose(sc.sin**2 + sc.cos**2, 1.0, abs_tol=1e-10)

    def test_angle_multiples(self):
        """Test that array contains sin(nx) and cos(nx)."""
        x = math.pi / 3
        arr = make_sincos_array(x, 5)

        for n in range(5):
            expected_sin = math.sin(n * x)
            expected_cos = math.cos(n * x)
            assert math.isclose(arr[n].sin, expected_sin, abs_tol=1e-10)
            assert math.isclose(arr[n].cos, expected_cos, abs_tol=1e-10)

    def test_zero_angle(self):
        """Test sin/cos array for zero angle."""
        arr = make_sincos_array(0.0, 4)

        for sc in arr:
            assert math.isclose(sc.sin, 0.0)
            assert math.isclose(sc.cos, 1.0)

    def test_negative_angle(self):
        """Test sin/cos array for negative angle."""
        x = -math.pi / 4
        arr = make_sincos_array(x, 3)

        # Should work correctly with negative angles
        for n in range(3):
            assert math.isclose(arr[n].sin, math.sin(n * x), abs_tol=1e-10)
            assert math.isclose(arr[n].cos, math.cos(n * x), abs_tol=1e-10)

    def test_caching(self):
        """Test that function is cached."""
        x = math.pi / 5
        arr1 = make_sincos_array(x, 7)
        arr2 = make_sincos_array(x, 7)

        # Should return same object from cache
        assert arr1 is arr2


class TestGeomagneticFieldXYZ:
    """Tests for GeomagneticField.compute_xyz method."""

    def test_initialization(self):
        """Test GeomagneticField initialization."""
        field = GeomagneticField()
        assert field.m_sin == math.sin(MAG_POLE_LAT)
        assert field.m_cos == math.cos(MAG_POLE_LAT)
        assert field.X == 0.0
        assert field.Y == 0.0
        assert field.Z == 0.0

    def test_compute_xyz_basic(self):
        """Test basic XYZ field computation."""
        field = GeomagneticField()
        X, Y, Z = field.compute_xyz(lat=math.radians(45), lon=math.radians(-75))

        # All components should be finite
        assert math.isfinite(X)
        assert math.isfinite(Y)
        assert math.isfinite(Z)

    def test_field_components_non_zero(self):
        """Test that field components are generally non-zero."""
        field = GeomagneticField()
        X, Y, Z = field.compute_xyz(lat=math.radians(40), lon=math.radians(-74))

        # At least one component should be significant
        total = math.sqrt(X**2 + Y**2 + Z**2)
        assert total > 0.1  # Normalized field strength

    def test_northern_hemisphere_z_component(self):
        """Test Z component in northern hemisphere."""
        field = GeomagneticField()
        _, _, Z = field.compute_xyz(lat=math.radians(45), lon=0)

        # Z component should be finite and non-zero
        assert math.isfinite(Z)
        assert Z != 0

    def test_southern_hemisphere_z_component(self):
        """Test Z component in southern hemisphere."""
        field = GeomagneticField()
        _, _, Z = field.compute_xyz(lat=math.radians(-45), lon=0)

        # Z component should be finite and non-zero
        assert math.isfinite(Z)
        assert Z != 0

    def test_pole_handling_north(self):
        """Test field computation near north pole."""
        field = GeomagneticField()
        # Should not crash or produce NaN
        X, Y, Z = field.compute_xyz(lat=math.radians(89.95), lon=0)

        assert math.isfinite(X)
        assert math.isfinite(Y)
        assert math.isfinite(Z)

    def test_pole_handling_south(self):
        """Test field computation near south pole."""
        field = GeomagneticField()
        X, Y, Z = field.compute_xyz(lat=math.radians(-89.95), lon=0)

        assert math.isfinite(X)
        assert math.isfinite(Y)
        assert math.isfinite(Z)

    def test_equator(self):
        """Test field computation at equator."""
        field = GeomagneticField()
        X, Y, Z = field.compute_xyz(lat=0, lon=0)

        # All components should be finite
        assert math.isfinite(X)
        assert math.isfinite(Y)
        assert math.isfinite(Z)

    @pytest.mark.parametrize("lat_deg", [-90, -45, 0, 45, 90])
    @pytest.mark.parametrize("lon_deg", [-180, -90, 0, 90, 180])
    def test_field_at_grid_points(self, lat_deg, lon_deg):
        """Test field computation at grid of locations."""
        field = GeomagneticField()
        lat = math.radians(lat_deg)
        lon = math.radians(lon_deg)

        X, Y, Z = field.compute_xyz(lat, lon)

        assert math.isfinite(X)
        assert math.isfinite(Y)
        assert math.isfinite(Z)


class TestGeomagneticFieldCompute:
    """Tests for GeomagneticField.compute method."""

    def test_compute_returns_parameters(self):
        """Test that compute returns GeomagneticParameters."""
        field = GeomagneticField()
        location = GeographicPoint(latitude=math.radians(40), longitude=math.radians(-74))
        params = field.compute(location)

        assert isinstance(params, GeomagneticParameters)

    def test_magnetic_latitude_range(self):
        """Test magnetic latitude is in valid range."""
        field = GeomagneticField()
        location = GeographicPoint(latitude=math.radians(45), longitude=math.radians(-75))
        params = field.compute(location)

        # Magnetic latitude should be between -90 and +90 degrees
        assert -HALF_PI <= params.magnetic_latitude <= HALF_PI

    def test_gyrofrequency_positive(self):
        """Test gyrofrequency is positive."""
        field = GeomagneticField()
        location = GeographicPoint(latitude=math.radians(40), longitude=math.radians(-74))
        params = field.compute(location)

        # Gyrofrequency should always be positive
        assert params.gyrofrequency > 0

    def test_gyrofrequency_typical_range(self):
        """Test gyrofrequency is in typical range for Earth."""
        field = GeomagneticField()
        location = GeographicPoint(latitude=math.radians(40), longitude=math.radians(-74))
        params = field.compute(location)

        # Typical Earth gyrofrequency is around 0.5-2 MHz
        assert 0.1 < params.gyrofrequency < 5.0

    def test_magnetic_dip_northern_hemisphere(self):
        """Test magnetic dip in northern hemisphere."""
        field = GeomagneticField()
        location = GeographicPoint(latitude=math.radians(45), longitude=0)
        params = field.compute(location)

        # In northern hemisphere, dip is typically positive (downward)
        # But the modified dip formula can give various results
        assert math.isfinite(params.magnetic_dip)

    def test_magnetic_dip_southern_hemisphere(self):
        """Test magnetic dip in southern hemisphere."""
        field = GeomagneticField()
        location = GeographicPoint(latitude=math.radians(-45), longitude=0)
        params = field.compute(location)

        # Should be finite
        assert math.isfinite(params.magnetic_dip)

    def test_field_components_stored(self):
        """Test that field components are stored in parameters."""
        field = GeomagneticField()
        location = GeographicPoint(latitude=math.radians(40), longitude=math.radians(-74))
        params = field.compute(location)

        # Field components should match what compute_xyz returns
        X, Y, Z = field.compute_xyz(location.latitude, location.longitude)
        assert math.isclose(params.field_x, X, rel_tol=1e-5)
        assert math.isclose(params.field_y, Y, rel_tol=1e-5)
        assert math.isclose(params.field_z, Z, rel_tol=1e-5)

    def test_magnetic_latitude_near_magnetic_pole(self):
        """Test magnetic latitude near the magnetic north pole."""
        field = GeomagneticField()
        # Magnetic north pole is approximately at 79.5°N, 69°W
        location = GeographicPoint(latitude=MAG_POLE_LAT, longitude=MAG_POLE_LON)
        params = field.compute(location)

        # Near magnetic pole, magnetic latitude should be high
        assert abs(params.magnetic_latitude) > math.radians(70)

    def test_magnetic_latitude_at_equator(self):
        """Test magnetic latitude at geographic equator."""
        field = GeomagneticField()
        location = GeographicPoint(latitude=0, longitude=0)
        params = field.compute(location)

        # Magnetic latitude at equator should be relatively low
        # (though not necessarily zero due to magnetic pole offset)
        assert abs(params.magnetic_latitude) < math.radians(60)


class TestGeomagneticCalculator:
    """Tests for GeomagneticCalculator class."""

    def test_initialization(self):
        """Test GeomagneticCalculator initialization."""
        calc = GeomagneticCalculator()
        assert isinstance(calc.field, GeomagneticField)

    def test_calculate_parameters(self):
        """Test calculate_parameters method."""
        calc = GeomagneticCalculator()
        location = GeographicPoint.from_degrees(40.0, -74.0)
        params = calc.calculate_parameters(location)

        assert isinstance(params, GeomagneticParameters)
        assert math.isfinite(params.magnetic_latitude)
        assert math.isfinite(params.gyrofrequency)
        assert math.isfinite(params.magnetic_dip)

    def test_calculate_magnetic_latitude(self):
        """Test calculate_magnetic_latitude method."""
        calc = GeomagneticCalculator()
        mag_lat_deg = calc.calculate_magnetic_latitude(40.0, -74.0)

        # Should return degrees
        assert -90 <= mag_lat_deg <= 90
        assert math.isfinite(mag_lat_deg)

    def test_calculate_dip_angle(self):
        """Test calculate_dip_angle method."""
        calc = GeomagneticCalculator()
        dip_deg = calc.calculate_dip_angle(40.0, -74.0)

        # Dip angle can range from -90 to +90 degrees
        # (but modified formula can give different range)
        assert math.isfinite(dip_deg)

    def test_calculate_gyrofrequency(self):
        """Test calculate_gyrofrequency method."""
        calc = GeomagneticCalculator()
        gyro = calc.calculate_gyrofrequency(40.0, -74.0)

        assert gyro > 0
        assert 0.1 < gyro < 5.0  # Typical range

    def test_calculator_consistency(self):
        """Test that calculator methods give consistent results."""
        calc = GeomagneticCalculator()
        lat_deg, lon_deg = 51.5, -0.1

        # Get all parameters at once
        location = GeographicPoint.from_degrees(lat_deg, lon_deg)
        params = calc.calculate_parameters(location)

        # Get parameters individually
        mag_lat = calc.calculate_magnetic_latitude(lat_deg, lon_deg)
        dip = calc.calculate_dip_angle(lat_deg, lon_deg)
        gyro = calc.calculate_gyrofrequency(lat_deg, lon_deg)

        # Should match
        assert math.isclose(mag_lat, math.degrees(params.magnetic_latitude), rel_tol=1e-5)
        assert math.isclose(dip, math.degrees(params.magnetic_dip), rel_tol=1e-5)
        assert math.isclose(gyro, params.gyrofrequency, rel_tol=1e-5)


class TestGeomagneticVariation:
    """Tests for geomagnetic variation with location."""

    def test_latitude_variation(self):
        """Test that parameters vary with latitude."""
        calc = GeomagneticCalculator()

        lats = [-60, -30, 0, 30, 60]
        mag_lats = []

        for lat in lats:
            mag_lat = calc.calculate_magnetic_latitude(lat, 0)
            mag_lats.append(mag_lat)

        # Should show variation
        assert len(set(mag_lats)) > 1
        assert max(mag_lats) - min(mag_lats) > 10  # At least 10° variation

    def test_longitude_variation(self):
        """Test that parameters vary with longitude."""
        calc = GeomagneticCalculator()

        lons = [-180, -90, 0, 90, 180]
        dips = []

        for lon in lons:
            dip = calc.calculate_dip_angle(45, lon)
            dips.append(dip)

        # Should show some variation (though may be less than latitude)
        assert len(set(dips)) > 1

    def test_gyrofrequency_polar_vs_equator(self):
        """Test gyrofrequency difference between pole and equator."""
        calc = GeomagneticCalculator()

        gyro_pole = calc.calculate_gyrofrequency(80, 0)
        gyro_equator = calc.calculate_gyrofrequency(0, 0)

        # Field is typically stronger at poles
        assert gyro_pole > gyro_equator


class TestGeomagneticConstants:
    """Tests for geomagnetic constants."""

    def test_constants_defined(self):
        """Test that constants are defined correctly."""
        assert TWO_PI == 2 * math.pi
        assert HALF_PI == math.pi / 2
        assert math.isclose(RinD, math.pi / 180)

    def test_magnetic_pole_location(self):
        """Test magnetic pole location is reasonable."""
        # Magnetic north pole should be in Arctic
        assert 75 * RinD < MAG_POLE_LAT < 85 * RinD
        # Longitude should be in valid range
        assert -math.pi <= MAG_POLE_LON <= math.pi

    def test_coefficient_arrays(self):
        """Test coefficient arrays have correct shape."""
        assert G.shape == (7, 7)
        assert H.shape == (7, 7)
        assert CT.shape == (7, 7)

        # Check arrays are non-trivial (have some non-zero values)
        assert np.any(G != 0)
        assert np.any(H != 0)
        assert np.any(CT != 0)


class TestGeomagneticEdgeCases:
    """Tests for edge cases in geomagnetic calculations."""

    def test_exactly_at_north_pole(self):
        """Test calculations at exact north pole."""
        calc = GeomagneticCalculator()
        params = calc.calculate_parameters(
            GeographicPoint(latitude=HALF_PI, longitude=0)
        )

        assert math.isfinite(params.magnetic_latitude)
        assert math.isfinite(params.gyrofrequency)
        assert math.isfinite(params.magnetic_dip)

    def test_exactly_at_south_pole(self):
        """Test calculations at exact south pole."""
        calc = GeomagneticCalculator()
        params = calc.calculate_parameters(
            GeographicPoint(latitude=-HALF_PI, longitude=0)
        )

        assert math.isfinite(params.magnetic_latitude)
        assert math.isfinite(params.gyrofrequency)
        assert math.isfinite(params.magnetic_dip)

    def test_near_pole_limit(self):
        """Test calculations near pole limit (89.9°)."""
        calc = GeomagneticCalculator()
        lat_limit = math.radians(89.9)

        # Just below limit
        params = calc.calculate_parameters(
            GeographicPoint(latitude=lat_limit - 0.01, longitude=0)
        )
        assert math.isfinite(params.gyrofrequency)

        # At limit
        params = calc.calculate_parameters(
            GeographicPoint(latitude=lat_limit, longitude=0)
        )
        assert math.isfinite(params.gyrofrequency)

        # Above limit (should be clamped)
        params = calc.calculate_parameters(
            GeographicPoint(latitude=lat_limit + 0.01, longitude=0)
        )
        assert math.isfinite(params.gyrofrequency)

    def test_date_line_crossing(self):
        """Test calculations crossing international date line."""
        calc = GeomagneticCalculator()

        # Just west of date line
        params_west = calc.calculate_parameters(
            GeographicPoint.from_degrees(45, 179.9)
        )

        # Just east of date line
        params_east = calc.calculate_parameters(
            GeographicPoint.from_degrees(45, -179.9)
        )

        # Should be similar but not identical
        assert abs(params_west.magnetic_latitude - params_east.magnetic_latitude) < math.radians(10)

    def test_known_locations(self):
        """Test geomagnetic parameters at known locations."""
        calc = GeomagneticCalculator()

        # New York City
        params_nyc = calc.calculate_parameters(GeographicPoint.from_degrees(40.7, -74.0))
        assert math.isfinite(params_nyc.gyrofrequency)
        assert 0.5 < params_nyc.gyrofrequency < 2.5

        # London
        params_london = calc.calculate_parameters(GeographicPoint.from_degrees(51.5, -0.1))
        assert math.isfinite(params_london.gyrofrequency)
        assert 0.5 < params_london.gyrofrequency < 2.5

        # Tokyo
        params_tokyo = calc.calculate_parameters(GeographicPoint.from_degrees(35.7, 139.7))
        assert math.isfinite(params_tokyo.gyrofrequency)
        assert 0.5 < params_tokyo.gyrofrequency < 2.5


class TestGeomagneticDipAngle:
    """Tests specifically for magnetic dip angle calculations."""

    def test_dip_angle_northern_latitudes(self):
        """Test dip angle variation across northern latitudes."""
        calc = GeomagneticCalculator()

        dip_angles = []
        for lat in range(0, 91, 15):
            dip = calc.calculate_dip_angle(lat, 0)
            dip_angles.append(dip)
            assert math.isfinite(dip)

        # Should show variation with latitude
        assert len(set(dip_angles)) > 1

    def test_dip_angle_southern_latitudes(self):
        """Test dip angle variation across southern latitudes."""
        calc = GeomagneticCalculator()

        dip_angles = []
        for lat in range(0, -91, -15):
            dip = calc.calculate_dip_angle(lat, 0)
            dip_angles.append(dip)
            assert math.isfinite(dip)

        # Should show variation with latitude
        assert len(set(dip_angles)) > 1

    def test_dip_angle_signs(self):
        """Test dip angle signs in different hemispheres."""
        calc = GeomagneticCalculator()

        # The modified dip formula can give different signs
        # Just test that values are finite and reasonable
        dip_north = calc.calculate_dip_angle(60, 0)
        dip_south = calc.calculate_dip_angle(-60, 0)

        assert math.isfinite(dip_north)
        assert math.isfinite(dip_south)
        # Signs may or may not be opposite due to modified formula


class TestGeomagneticRobustness:
    """Tests for robustness of geomagnetic calculations."""

    def test_repeated_calculations(self):
        """Test that repeated calculations give same results."""
        calc = GeomagneticCalculator()
        location = GeographicPoint.from_degrees(40.0, -74.0)

        params1 = calc.calculate_parameters(location)
        params2 = calc.calculate_parameters(location)

        assert params1.magnetic_latitude == params2.magnetic_latitude
        assert params1.gyrofrequency == params2.gyrofrequency
        assert params1.magnetic_dip == params2.magnetic_dip

    @pytest.mark.parametrize("lat,lon", [
        (0, 0),
        (45, -75),
        (51.5, -0.1),
        (35.7, 139.7),
        (-33.9, 151.2),
        (60, 30),
        (-45, -60),
    ])
    def test_various_locations_robust(self, lat, lon):
        """Test robustness at various real-world locations."""
        calc = GeomagneticCalculator()
        params = calc.calculate_parameters(GeographicPoint.from_degrees(lat, lon))

        # All values should be finite
        assert math.isfinite(params.magnetic_latitude)
        assert math.isfinite(params.gyrofrequency)
        assert math.isfinite(params.magnetic_dip)
        assert math.isfinite(params.field_x)
        assert math.isfinite(params.field_y)
        assert math.isfinite(params.field_z)

        # Gyrofrequency should be positive and reasonable
        assert 0.1 < params.gyrofrequency < 5.0
