#!/usr/bin/env python3
"""
DVOACAP Phase 1 + Phase 2 Integration Example

Demonstrates how path geometry, solar, and geomagnetic calculations
work together for HF propagation prediction.
"""

import math
from datetime import datetime

# Import Phase 1 modules (you'll need to have these)
# from path_geometry import PathGeometry, GeographicPoint

# Import Phase 2 modules
from solar import SolarCalculator, GeographicPoint as SolarPoint
from geomagnetic import GeomagneticCalculator, GeographicPoint as GeoPoint


def analyze_propagation_path():
    """
    Analyze HF propagation conditions along a path.
    
    This example shows how to use Phase 1 (path geometry) and Phase 2
    (solar/geomagnetic) together to characterize propagation conditions.
    """
    print("=" * 70)
    print("DVOACAP Phase 1 + Phase 2 Integration Example")
    print("=" * 70)
    
    # Define path endpoints
    halifax_lat, halifax_lon = 44.374, -64.300  # VE1ATM
    london_lat, london_lon = 51.5, -0.1
    
    print(f"\nPath Analysis:")
    print(f"  From: Halifax, NS ({halifax_lat}°N, {abs(halifax_lon)}°W)")
    print(f"  To:   London, UK ({london_lat}°N, {abs(london_lon)}°W)")
    
    # Phase 1: Path Geometry (simplified for this example)
    # In real code, use PathGeometry class
    print(f"\n{'Path Geometry (Phase 1):'}")
    print("-" * 70)
    
    # Calculate great circle distance (simplified)
    R = 6371  # Earth radius in km
    lat1, lon1 = math.radians(halifax_lat), math.radians(halifax_lon)
    lat2, lon2 = math.radians(london_lat), math.radians(london_lon)
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = R * c
    
    print(f"  Great circle distance: {distance:.0f} km")
    
    # Calculate midpoint (simplified)
    Bx = math.cos(lat2) * math.cos(dlon)
    By = math.cos(lat2) * math.sin(dlon)
    mid_lat = math.atan2(math.sin(lat1) + math.sin(lat2),
                         math.sqrt((math.cos(lat1) + Bx)**2 + By**2))
    mid_lon = lon1 + math.atan2(By, math.cos(lat1) + Bx)
    
    mid_lat_deg = math.degrees(mid_lat)
    mid_lon_deg = math.degrees(mid_lon)
    
    print(f"  Path midpoint: {mid_lat_deg:.2f}°N, {abs(mid_lon_deg):.2f}°W")
    
    # Phase 2: Solar Conditions
    print(f"\n{'Solar Conditions (Phase 2):'}")
    print("-" * 70)
    
    # Test at different times
    test_times = [
        ("Midnight UTC", datetime(2024, 6, 15, 0, 0)),
        ("06:00 UTC", datetime(2024, 6, 15, 6, 0)),
        ("Noon UTC", datetime(2024, 6, 15, 12, 0)),
        ("18:00 UTC", datetime(2024, 6, 15, 18, 0)),
    ]
    
    solar_calc = SolarCalculator()
    midpoint_solar = SolarPoint(latitude=mid_lat, longitude=mid_lon)
    
    print(f"\n  Conditions at path midpoint on June 15, 2024:")
    print(f"  {'Time':<15} {'Zenith':>8} {'Elevation':>10} {'Status':>10}")
    print(f"  {'':<15} {'(deg)':>8} {'(deg)':>10} {'':<10}")
    print(f"  {'-'*15} {'-'*8} {'-'*10} {'-'*10}")
    
    for time_label, time in test_times:
        zenith = solar_calc.calculate_zenith_angle(midpoint_solar, time)
        elevation = math.degrees(math.pi/2 - zenith)
        is_day = solar_calc.is_daytime_at(midpoint_solar, time)
        status = "DAY" if is_day else "NIGHT"
        
        print(f"  {time_label:<15} {math.degrees(zenith):>8.1f} {elevation:>10.1f} {status:>10}")
    
    # Phase 2: Geomagnetic Conditions
    print(f"\n{'Geomagnetic Conditions (Phase 2):'}")
    print("-" * 70)
    
    geo_calc = GeomagneticCalculator()
    
    # Calculate for transmitter, midpoint, receiver
    locations = [
        ("Halifax (TX)", halifax_lat, halifax_lon),
        ("Midpoint", mid_lat_deg, mid_lon_deg),
        ("London (RX)", london_lat, london_lon),
    ]
    
    print(f"\n  {'Location':<15} {'MagLat':>10} {'Dip':>10} {'Gyro':>10}")
    print(f"  {'':<15} {'(deg)':>10} {'(deg)':>10} {'(MHz)':>10}")
    print(f"  {'-'*15} {'-'*10} {'-'*10} {'-'*10}")
    
    for name, lat, lon in locations:
        location = GeoPoint.from_degrees(lat, lon)
        params = geo_calc.calculate_parameters(location)
        
        print(f"  {name:<15} "
              f"{math.degrees(params.magnetic_latitude):>10.2f} "
              f"{math.degrees(params.magnetic_dip):>10.2f} "
              f"{params.gyrofrequency:>10.3f}")
    
    # Propagation Assessment
    print(f"\n{'Propagation Assessment:'}")
    print("-" * 70)
    
    # Check noon conditions at midpoint
    noon_time = datetime(2024, 6, 15, 12, 0)
    noon_zenith = solar_calc.calculate_zenith_angle(midpoint_solar, noon_time)
    midpoint_geo = GeoPoint.from_degrees(mid_lat_deg, mid_lon_deg)
    geo_params = geo_calc.calculate_parameters(midpoint_geo)
    
    print(f"\n  Conditions at midpoint (noon UTC):")
    print(f"    Solar zenith angle: {math.degrees(noon_zenith):.1f}°")
    print(f"    Solar elevation: {math.degrees(math.pi/2 - noon_zenith):.1f}°")
    print(f"    Day/Night: {'Daytime' if solar_calc.is_daytime_at(midpoint_solar, noon_time) else 'Nighttime'}")
    print(f"    Magnetic latitude: {math.degrees(geo_params.magnetic_latitude):.1f}°")
    print(f"    Magnetic dip: {math.degrees(geo_params.magnetic_dip):.1f}°")
    print(f"    Gyrofrequency: {geo_params.gyrofrequency:.3f} MHz")
    
    print(f"\n  Propagation characteristics:")
    
    # D-layer absorption (depends on solar zenith angle)
    if solar_calc.is_daytime_at(midpoint_solar, noon_time):
        d_layer_factor = math.cos(noon_zenith)**0.5
        print(f"    D-layer absorption: Moderate (factor: {d_layer_factor:.3f})")
    else:
        print(f"    D-layer absorption: Minimal (nighttime)")
    
    # Magnetic effects
    mag_lat = math.degrees(geo_params.magnetic_latitude)
    if abs(mag_lat) > 60:
        print(f"    Magnetic effects: High (high-latitude path)")
    elif abs(mag_lat) < 20:
        print(f"    Magnetic effects: Low (equatorial path)")
    else:
        print(f"    Magnetic effects: Moderate (mid-latitude path)")
    
    # Recommended frequencies (simplified)
    print(f"\n  Approximate frequency recommendations:")
    if solar_calc.is_daytime_at(midpoint_solar, noon_time):
        print(f"    Best bands: 20m, 17m, 15m (14-21 MHz)")
        print(f"    Marginal: 30m (10 MHz) - higher absorption")
        print(f"    Poor: 40m, 80m - excessive D-layer absorption")
    else:
        print(f"    Best bands: 40m, 30m (7-10 MHz)")
        print(f"    Good: 20m (14 MHz)")
        print(f"    Marginal: Higher bands - insufficient ionization")
    
    print("\n" + "=" * 70)
    print("✓ Integration Example Complete!")
    print("=" * 70)
    print("\nThis demonstrates how Phase 1 (path geometry) and Phase 2")
    print("(solar/geomagnetic) work together to characterize HF propagation.")
    print("\nNext: Phase 3 will add ionospheric layer modeling to predict")
    print("actual MUF, FOT, and signal strength!")


if __name__ == '__main__':
    analyze_propagation_path()
