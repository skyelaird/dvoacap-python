#!/usr/bin/env python3
"""
Test Suite for PathGeometry Module
Validates Python port against known values and edge cases
"""

import math
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dvoacap.path_geometry import (
    PathGeometry, GeoPoint,
    hop_distance, hop_length_3d, calc_elevation_angle,
    sin_of_incidence, cos_of_incidence,
    RinD, DinR, EarthR, HALF_PI
)


# ============================================================================
# GeoPoint Tests
# ============================================================================

def test_geo_point_conversion():
    """Test GeoPoint degree/radian conversion"""
    # Test conversion to/from degrees
    lat_deg, lon_deg = 45.0, -120.0
    point = GeoPoint.from_degrees(lat_deg, lon_deg)
    lat_back, lon_back = point.to_degrees()

    assert abs(lat_back - lat_deg) < 1e-10, "Latitude round-trip failed"
    assert abs(lon_back - lon_deg) < 1e-10, "Longitude round-trip failed"


# ============================================================================
# Path Calculations Tests
# ============================================================================

def test_short_path_calculations():
    """Test basic short-path calculations"""
    # Halifax to London (known values)
    tx = GeoPoint.from_degrees(44.65, -63.57)
    rx = GeoPoint.from_degrees(51.51, -0.13)

    path = PathGeometry()
    path.set_tx_rx(tx, rx)

    # Test distance (should be approximately 4622-4623 km)
    dist_km = path.get_distance_km()
    assert abs(dist_km - 4622.6) < 1.0, f"Halifax-London distance expected ~4622.6 km, got {dist_km:.1f} km"

    # Test azimuth Tx->Rx (should be approximately 57°)
    azim_tr = path.get_azimuth_tr_degrees()
    assert abs(azim_tr - 57.0) < 1.0, f"Halifax-London azimuth Tx->Rx expected ~57°, got {azim_tr:.1f}°"

    # Test azimuth Rx->Tx (should be approximately 286-287°)
    azim_rt = path.get_azimuth_rt_degrees()
    assert abs(azim_rt - 286.5) < 1.0, f"Halifax-London azimuth Rx->Tx expected ~286.5°, got {azim_rt:.1f}°"


def test_equator_paths():
    """Test paths along the equator"""
    # Path along equator from 0°E to 90°E
    tx = GeoPoint.from_degrees(0.0, 0.0)
    rx = GeoPoint.from_degrees(0.0, 90.0)

    path = PathGeometry()
    path.set_tx_rx(tx, rx)

    # Distance should be 1/4 of Earth's circumference
    expected_dist = 0.25 * 2 * math.pi * EarthR  # ~10018 km
    assert abs(path.get_distance_km() - expected_dist) < 1.0, \
        f"Equator 90° distance expected ~{expected_dist:.1f} km, got {path.get_distance_km():.1f} km"

    # Azimuth should be 90° (due east)
    assert abs(path.get_azimuth_tr_degrees() - 90.0) < 0.1, "Equator path azimuth should be 90°"


def test_meridian_paths():
    """Test paths along meridians"""
    # Path along prime meridian from 0°N to 45°N
    tx = GeoPoint.from_degrees(0.0, 0.0)
    rx = GeoPoint.from_degrees(45.0, 0.0)

    path = PathGeometry()
    path.set_tx_rx(tx, rx)

    # Distance should be 45° of great circle
    expected_dist = (45.0 * RinD) * EarthR  # ~5003 km
    assert abs(path.get_distance_km() - expected_dist) < 1.0, \
        f"Meridian 45° distance expected ~{expected_dist:.1f} km, got {path.get_distance_km():.1f} km"

    # Azimuth should be 0° (due north)
    assert abs(path.get_azimuth_tr_degrees() - 0.0) < 0.1, "Meridian path azimuth should be 0° (north)"


def test_antipodal_points():
    """Test antipodal points (opposite sides of Earth)"""
    # Test points on opposite sides of Earth
    tx = GeoPoint.from_degrees(0.0, 0.0)
    rx = GeoPoint.from_degrees(0.0, 180.0)

    path = PathGeometry()
    path.set_tx_rx(tx, rx)

    # Distance should be half Earth's circumference
    expected_dist = math.pi * EarthR  # ~20015 km
    assert abs(path.get_distance_km() - expected_dist) < 1.0, \
        f"Antipodal distance expected ~{expected_dist:.1f} km, got {path.get_distance_km():.1f} km"


def test_point_along_path():
    """Test getting points along the path"""
    # Simple test: path along equator
    tx = GeoPoint.from_degrees(0.0, 0.0)
    rx = GeoPoint.from_degrees(0.0, 90.0)

    path = PathGeometry()
    path.set_tx_rx(tx, rx)

    # Midpoint should be at (0°, 45°)
    midpoint = path.get_point_at_dist(path.dist / 2)
    mid_lat, mid_lon = midpoint.to_degrees()

    assert abs(mid_lat - 0.0) < 0.1, f"Midpoint latitude expected ~0°, got {mid_lat:.1f}°"
    assert abs(mid_lon - 45.0) < 0.1, f"Midpoint longitude expected ~45°, got {mid_lon:.1f}°"


# ============================================================================
# Hop Distance Tests
# ============================================================================

def test_hop_distance_calculations():
    """Test hop distance calculations"""
    # Test with common values
    elev = 10 * RinD  # 10 degrees
    height = 300  # km

    hop_dist = hop_distance(elev, height)
    hop_dist_km = hop_dist * EarthR

    # At 10° elevation and 300km height, hop should be ~2193 km
    assert abs(hop_dist_km - 2193) < 5.0, f"Hop distance at 10° expected ~2193 km, got {hop_dist_km:.1f} km"

    # Test elevation angle calculation (reverse)
    calc_elev = calc_elevation_angle(hop_dist, height)
    assert abs(calc_elev - elev) < 0.001, \
        f"Reverse elevation calculation expected {elev*DinR:.2f}°, got {calc_elev*DinR:.2f}°"


def test_incidence_angles():
    """Test incidence angle calculations"""
    elev = 15 * RinD  # 15 degrees
    height = 250  # km

    sin_i = sin_of_incidence(elev, height)
    cos_i = cos_of_incidence(elev, height)

    # Verify sin² + cos² = 1
    sum_squares = sin_i**2 + cos_i**2
    assert abs(sum_squares - 1.0) < 1e-6, f"sin²+cos²=1 identity failed, got {sum_squares:.8f}"

    # For 15° elevation and 250km height, sin should be ~0.925
    assert abs(sin_i - 0.925) < 0.01, f"Sin of incidence expected ~0.925, got {sin_i:.3f}"


def test_3d_hop_length():
    """Test 3D hop length calculations"""
    elev = 12 * RinD
    hop_dist = hop_distance(elev, 300)
    virt_height = 300

    length_3d = hop_length_3d(elev, hop_dist, virt_height)

    # 3D length should be greater than 2D ground distance
    length_2d = hop_dist * EarthR
    assert length_3d > length_2d, f"3D length ({length_3d:.1f} km) should be > 2D length ({length_2d:.1f} km)"


def test_hop_count():
    """Test hop count calculations"""
    # Create a path of known distance
    tx = GeoPoint.from_degrees(0.0, 0.0)
    rx = GeoPoint.from_degrees(0.0, 90.0)  # ~10,018 km

    path = PathGeometry()
    path.set_tx_rx(tx, rx)

    # At 10° elevation and 300km height, hop distance is ~2193 km
    # So for ~10,018 km path, we should need ~5 hops
    elev = 10 * RinD
    height = 300
    hops = path.hop_count(elev, height)

    assert abs(hops - 5) < 0.5, f"Hop count for 90° path at 10° elevation expected ~5, got {hops}"


# ============================================================================
# Edge Case Tests
# ============================================================================

def test_near_pole_handling():
    """Test handling of paths near poles"""
    # Path near north pole
    tx = GeoPoint.from_degrees(85.0, 0.0)
    rx = GeoPoint.from_degrees(85.0, 90.0)

    path = PathGeometry()
    # Should complete without errors
    path.set_tx_rx(tx, rx)

    # Just verify we got a reasonable distance
    dist = path.get_distance_km()
    assert 0 < dist < 20000, f"Near-pole path distance should be reasonable, got {dist:.1f} km"


def test_close_points():
    """Test handling of very close Tx/Rx points"""
    # Points very close together (0.001 degree apart)
    tx = GeoPoint.from_degrees(45.0, -70.0)
    rx = GeoPoint.from_degrees(45.001, -70.001)

    path = PathGeometry()
    # Should handle close points without division by zero
    path.set_tx_rx(tx, rx)

    # Distance should be small but positive
    # 0.001 degrees at this latitude is about 0.11 km per degree, but diagonal
    # so actual distance is a few km
    dist = path.get_distance_km()
    assert 0 < dist < 5, f"Close points distance should be < 5 km, got {dist:.3f} km"
