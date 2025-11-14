#!/usr/bin/env python3
"""
Test Suite for PathGeometry Module
Validates Python port against known values and edge cases
"""

import math
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.dvoacap.path_geometry import (
    PathGeometry, GeoPoint,
    hop_distance, hop_length_3d, calc_elevation_angle,
    sin_of_incidence, cos_of_incidence,
    RinD, DinR, EarthR, HALF_PI
)


class TestPathGeometry:
    """Test suite for PathGeometry module"""
    
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
    
    def assert_close(self, actual, expected, tolerance, test_name):
        """Assert that actual value is close to expected value"""
        if abs(actual - expected) < tolerance:
            self.tests_passed += 1
            print(f"✓ {test_name}")
            return True
        else:
            self.tests_failed += 1
            print(f"✗ {test_name}")
            print(f"  Expected: {expected:.6f}, Got: {actual:.6f}, "
                  f"Diff: {abs(actual - expected):.6f}")
            return False
    
    def test_geo_point_conversion(self):
        """Test GeoPoint degree/radian conversion"""
        print("\n" + "=" * 70)
        print("Test: GeoPoint Conversion")
        print("=" * 70)
        
        # Test conversion to/from degrees
        lat_deg, lon_deg = 45.0, -120.0
        point = GeoPoint.from_degrees(lat_deg, lon_deg)
        lat_back, lon_back = point.to_degrees()
        
        self.assert_close(lat_back, lat_deg, 1e-10, "Latitude round-trip")
        self.assert_close(lon_back, lon_deg, 1e-10, "Longitude round-trip")
    
    def test_short_path_calculations(self):
        """Test basic short-path calculations"""
        print("\n" + "=" * 70)
        print("Test: Short Path Calculations")
        print("=" * 70)
        
        # Halifax to London (known values)
        tx = GeoPoint.from_degrees(44.65, -63.57)
        rx = GeoPoint.from_degrees(51.51, -0.13)
        
        path = PathGeometry()
        path.set_tx_rx(tx, rx)
        
        # Test distance (should be approximately 4622-4623 km)
        dist_km = path.get_distance_km()
        self.assert_close(dist_km, 4622.6, 1.0, 
                         f"Halifax-London distance (got {dist_km:.1f} km)")
        
        # Test azimuth Tx->Rx (should be approximately 57°)
        azim_tr = path.get_azimuth_tr_degrees()
        self.assert_close(azim_tr, 57.0, 1.0,
                         f"Halifax-London azimuth Tx->Rx (got {azim_tr:.1f}°)")
        
        # Test azimuth Rx->Tx (should be approximately 286-287°)
        azim_rt = path.get_azimuth_rt_degrees()
        self.assert_close(azim_rt, 286.5, 1.0,
                         f"Halifax-London azimuth Rx->Tx (got {azim_rt:.1f}°)")
    
    def test_equator_paths(self):
        """Test paths along the equator"""
        print("\n" + "=" * 70)
        print("Test: Equator Paths")
        print("=" * 70)
        
        # Path along equator from 0°E to 90°E
        tx = GeoPoint.from_degrees(0.0, 0.0)
        rx = GeoPoint.from_degrees(0.0, 90.0)
        
        path = PathGeometry()
        path.set_tx_rx(tx, rx)
        
        # Distance should be 1/4 of Earth's circumference
        expected_dist = 0.25 * 2 * math.pi * EarthR  # ~10018 km
        self.assert_close(path.get_distance_km(), expected_dist, 1.0,
                         f"Equator 90° distance (got {path.get_distance_km():.1f} km)")
        
        # Azimuth should be 90° (due east)
        self.assert_close(path.get_azimuth_tr_degrees(), 90.0, 0.1,
                         "Equator path azimuth")
    
    def test_meridian_paths(self):
        """Test paths along meridians"""
        print("\n" + "=" * 70)
        print("Test: Meridian Paths")
        print("=" * 70)
        
        # Path along prime meridian from 0°N to 45°N
        tx = GeoPoint.from_degrees(0.0, 0.0)
        rx = GeoPoint.from_degrees(45.0, 0.0)
        
        path = PathGeometry()
        path.set_tx_rx(tx, rx)
        
        # Distance should be 45° of great circle
        expected_dist = (45.0 * RinD) * EarthR  # ~5003 km
        self.assert_close(path.get_distance_km(), expected_dist, 1.0,
                         f"Meridian 45° distance (got {path.get_distance_km():.1f} km)")
        
        # Azimuth should be 0° (due north)
        self.assert_close(path.get_azimuth_tr_degrees(), 0.0, 0.1,
                         "Meridian path azimuth (north)")
    
    def test_antipodal_points(self):
        """Test antipodal points (opposite sides of Earth)"""
        print("\n" + "=" * 70)
        print("Test: Antipodal Points")
        print("=" * 70)
        
        # Test points on opposite sides of Earth
        tx = GeoPoint.from_degrees(0.0, 0.0)
        rx = GeoPoint.from_degrees(0.0, 180.0)
        
        path = PathGeometry()
        path.set_tx_rx(tx, rx)
        
        # Distance should be half Earth's circumference
        expected_dist = math.pi * EarthR  # ~20015 km
        self.assert_close(path.get_distance_km(), expected_dist, 1.0,
                         f"Antipodal distance (got {path.get_distance_km():.1f} km)")
    
    def test_point_along_path(self):
        """Test getting points along the path"""
        print("\n" + "=" * 70)
        print("Test: Points Along Path")
        print("=" * 70)
        
        # Simple test: path along equator
        tx = GeoPoint.from_degrees(0.0, 0.0)
        rx = GeoPoint.from_degrees(0.0, 90.0)
        
        path = PathGeometry()
        path.set_tx_rx(tx, rx)
        
        # Midpoint should be at (0°, 45°)
        midpoint = path.get_point_at_dist(path.dist / 2)
        mid_lat, mid_lon = midpoint.to_degrees()
        
        self.assert_close(mid_lat, 0.0, 0.1, 
                         f"Midpoint latitude (got {mid_lat:.1f}°)")
        self.assert_close(mid_lon, 45.0, 0.1,
                         f"Midpoint longitude (got {mid_lon:.1f}°)")
    
    def test_hop_distance_calculations(self):
        """Test hop distance calculations"""
        print("\n" + "=" * 70)
        print("Test: Hop Distance Calculations")
        print("=" * 70)
        
        # Test with common values
        elev = 10 * RinD  # 10 degrees
        height = 300  # km
        
        hop_dist = hop_distance(elev, height)
        hop_dist_km = hop_dist * EarthR
        
        # At 10° elevation and 300km height, hop should be ~2193 km
        self.assert_close(hop_dist_km, 2193, 5.0,
                         f"Hop distance at 10° (got {hop_dist_km:.1f} km)")
        
        # Test elevation angle calculation (reverse)
        calc_elev = calc_elevation_angle(hop_dist, height)
        self.assert_close(calc_elev, elev, 0.001,
                         f"Reverse elevation calculation (got {calc_elev*DinR:.2f}°)")
    
    def test_incidence_angles(self):
        """Test incidence angle calculations"""
        print("\n" + "=" * 70)
        print("Test: Incidence Angles")
        print("=" * 70)
        
        elev = 15 * RinD  # 15 degrees
        height = 250  # km
        
        sin_i = sin_of_incidence(elev, height)
        cos_i = cos_of_incidence(elev, height)
        
        # Verify sin² + cos² = 1
        sum_squares = sin_i**2 + cos_i**2
        self.assert_close(sum_squares, 1.0, 1e-6,
                         f"sin²+cos²=1 identity (got {sum_squares:.8f})")
        
        # For 15° elevation and 250km height, sin should be ~0.925
        self.assert_close(sin_i, 0.925, 0.01,
                         f"Sin of incidence (got {sin_i:.3f})")
    
    def test_3d_hop_length(self):
        """Test 3D hop length calculations"""
        print("\n" + "=" * 70)
        print("Test: 3D Hop Length")
        print("=" * 70)
        
        elev = 12 * RinD
        hop_dist = hop_distance(elev, 300)
        virt_height = 300
        
        length_3d = hop_length_3d(elev, hop_dist, virt_height)
        
        # 3D length should be greater than 2D ground distance
        length_2d = hop_dist * EarthR
        if length_3d > length_2d:
            self.tests_passed += 1
            print(f"✓ 3D length > 2D length ({length_3d:.1f} km > {length_2d:.1f} km)")
        else:
            self.tests_failed += 1
            print(f"✗ 3D length > 2D length: {length_3d:.1f} km NOT > {length_2d:.1f} km")
    
    def test_hop_count(self):
        """Test hop count calculations"""
        print("\n" + "=" * 70)
        print("Test: Hop Count")
        print("=" * 70)
        
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
        
        self.assert_close(hops, 5, 0.5,
                         f"Hop count for 90° path at 10° elevation (got {hops})")
    
    def test_near_pole_handling(self):
        """Test handling of paths near poles"""
        print("\n" + "=" * 70)
        print("Test: Near-Pole Handling")
        print("=" * 70)
        
        # Path near north pole
        tx = GeoPoint.from_degrees(85.0, 0.0)
        rx = GeoPoint.from_degrees(85.0, 90.0)
        
        path = PathGeometry()
        try:
            path.set_tx_rx(tx, rx)
            # Should complete without errors
            self.tests_passed += 1
            print(f"✓ Near-pole path calculation completed")
            print(f"  Distance: {path.get_distance_km():.1f} km")
        except Exception as e:
            self.tests_failed += 1
            print(f"✗ Near-pole path calculation failed: {e}")
    
    def test_close_points(self):
        """Test handling of very close Tx/Rx points"""
        print("\n" + "=" * 70)
        print("Test: Close Points Handling")
        print("=" * 70)
        
        # Points very close together
        tx = GeoPoint.from_degrees(45.0, -70.0)
        rx = GeoPoint.from_degrees(45.001, -70.001)
        
        path = PathGeometry()
        try:
            path.set_tx_rx(tx, rx)
            # Should handle close points without division by zero
            self.tests_passed += 1
            print(f"✓ Close points handled correctly")
            print(f"  Distance: {path.get_distance_km():.3f} km")
        except Exception as e:
            self.tests_failed += 1
            print(f"✗ Close points handling failed: {e}")
    
    def run_all_tests(self):
        """Run all tests and print summary"""
        print("\n" + "=" * 70)
        print("PathGeometry Module Test Suite")
        print("=" * 70)
        
        self.test_geo_point_conversion()
        self.test_short_path_calculations()
        self.test_equator_paths()
        self.test_meridian_paths()
        self.test_antipodal_points()
        self.test_point_along_path()
        self.test_hop_distance_calculations()
        self.test_incidence_angles()
        self.test_3d_hop_length()
        self.test_hop_count()
        self.test_near_pole_handling()
        self.test_close_points()
        
        # Print summary
        print("\n" + "=" * 70)
        print("Test Summary")
        print("=" * 70)
        total = self.tests_passed + self.tests_failed
        print(f"Total tests:  {total}")
        print(f"Passed:       {self.tests_passed} ({100*self.tests_passed/total:.1f}%)")
        print(f"Failed:       {self.tests_failed}")
        print("=" * 70)
        
        return self.tests_failed == 0


if __name__ == "__main__":
    tester = TestPathGeometry()
    success = tester.run_all_tests()
    
    if success:
        print("\n✓ All tests passed!")
        exit(0)
    else:
        print(f"\n✗ {tester.tests_failed} test(s) failed")
        exit(1)
