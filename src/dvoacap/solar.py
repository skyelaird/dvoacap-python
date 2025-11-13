#!/usr/bin/env python3
"""
Solar Calculations Module for VOACAP
Ported from Sun.pas (DVOACAP)

Original Author: Alex Shovkoplyas, VE3NEA
Python Port: 2025

This module calculates solar position and local time for HF propagation modeling.
"""

import math
from dataclasses import dataclass
from typing import Tuple
from datetime import datetime


# ============================================================================
# Constants
# ============================================================================

TWO_PI = 2 * math.pi
HALF_PI = math.pi / 2
RinD = math.pi / 180  # radians in degree


# ============================================================================
# Solar Latitude Tables
# ============================================================================
# Solar declination angles for each month
# First value: beginning of month, Second value: end of month
# These represent the sub-solar point latitude throughout the year

SUN_LAT = {
    1:  (-23.05 * RinD, -17.31 * RinD),  # January
    2:  (-17.30 * RinD,  -7.89 * RinD),  # February
    3:  ( -7.88 * RinD,   4.21 * RinD),  # March
    4:  (  4.26 * RinD,  14.80 * RinD),  # April
    5:  ( 14.84 * RinD,  21.93 * RinD),  # May
    6:  ( 21.93 * RinD,  23.45 * RinD),  # June
    7:  ( 23.15 * RinD,  18.23 * RinD),  # July
    8:  ( 18.20 * RinD,   8.68 * RinD),  # August
    9:  (  8.55 * RinD,  -2.86 * RinD),  # September
    10: ( -2.90 * RinD, -14.16 * RinD),  # October
    11: (-14.20 * RinD, -21.68 * RinD),  # November
    12: (-21.66 * RinD, -23.45 * RinD),  # December
}


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class GeographicPoint:
    """Geographic location in radians"""
    latitude: float   # radians, positive north
    longitude: float  # radians, positive east
    
    @classmethod
    def from_degrees(cls, lat_deg: float, lon_deg: float) -> 'GeographicPoint':
        """Create point from degrees"""
        return cls(
            latitude=lat_deg * RinD,
            longitude=lon_deg * RinD
        )


# ============================================================================
# Solar Position Functions
# ============================================================================

def compute_zenith_angle(
    point: GeographicPoint,
    utc_fraction: float,
    month: int
) -> float:
    """
    Calculate solar zenith angle at a geographic point.
    
    The zenith angle is the angle between the sun and the local vertical.
    It's used to determine day/night terminator and ionospheric conditions.
    
    Args:
        point: Geographic location (latitude/longitude in radians)
        utc_fraction: UTC time as fraction of day (0.0 = midnight, 0.5 = noon)
        month: Month number (1-12)
        
    Returns:
        Solar zenith angle in radians (0 = directly overhead, π/2 = horizon)
        
    Note:
        - Uses simplified solar position model appropriate for HF propagation
        - Solar latitude varies throughout month (linear interpolation)
        - Solar longitude calculated from UTC time
        
    Example:
        >>> # Solar zenith at noon UTC on June 15 at equator
        >>> point = GeographicPoint(latitude=0, longitude=0)
        >>> zenith = compute_zenith_angle(point, 0.5, 6)  # 0.5 = noon UTC
        >>> print(f"Zenith angle: {math.degrees(zenith):.1f}°")
    """
    # Calculate sub-solar point (where sun is directly overhead)
    # Solar longitude moves 360° per day westward
    sun_lon = math.pi - utc_fraction * TWO_PI
    
    # Get solar declination (latitude) for this month
    # Choose beginning or end of month value based on which is closer
    sun_lat_start, sun_lat_end = SUN_LAT[month]

    if abs(point.latitude - sun_lat_start) > abs(point.latitude - sun_lat_end):
        sun_lat = sun_lat_start
    else:
        sun_lat = sun_lat_end

    # Calculate zenith angle using spherical trigonometry
    # This is the great circle angular distance between point and sub-solar point
    cos_zenith = (
        math.sin(point.latitude) * math.sin(sun_lat) +
        math.cos(point.latitude) * math.cos(sun_lat) *
        math.cos(point.longitude - sun_lon)
    )
    
    # Clamp to valid range to handle numerical precision issues
    cos_zenith = max(-1.0, min(1.0, cos_zenith))
    
    zenith_angle = math.acos(cos_zenith)
    
    return zenith_angle


def compute_local_time(utc_fraction: float, longitude: float) -> float:
    """
    Calculate local time from UTC and longitude.
    
    Args:
        utc_fraction: UTC time as fraction of day (0.0-1.0)
        longitude: Longitude in radians (positive east)
        
    Returns:
        Local time as fraction of day (0.0-1.0)
        
    Note:
        - VOACAP uses hours 1-24; 0h is never used
        - Returns 1.0 (not 0.0) for midnight to match VOACAP convention
        
    Example:
        >>> # Local time at 90°W when UTC is noon
        >>> lon = -90 * (math.pi / 180)
        >>> local = compute_local_time(0.5, lon)
        >>> print(f"Local time: {local * 24:.1f}h")
    """
    # Add longitude offset to UTC
    # Longitude in radians / (2π) gives fraction of day offset
    local_time = (utc_fraction + 1 + longitude / TWO_PI) % 1.0
    
    # VOACAP convention: use 1.0 instead of 0.0 for midnight
    if local_time < 1e-4:
        local_time = 1.0
        
    return local_time


# ============================================================================
# Helper Functions for Common Use Cases
# ============================================================================

def is_daytime(zenith_angle: float, twilight_angle: float = 96 * RinD) -> bool:
    """
    Determine if it's daytime at a location.
    
    Args:
        zenith_angle: Solar zenith angle in radians
        twilight_angle: Angle defining day/night boundary (default: 96°)
                       90° = geometric horizon
                       96° = civil twilight (typical for HF propagation)
                       102° = nautical twilight
                       
    Returns:
        True if daytime, False if nighttime
    """
    return zenith_angle < twilight_angle


def solar_elevation_angle(zenith_angle: float) -> float:
    """
    Convert zenith angle to elevation angle.
    
    Args:
        zenith_angle: Solar zenith angle in radians
        
    Returns:
        Solar elevation angle in radians (positive above horizon)
    """
    return HALF_PI - zenith_angle


def get_utc_fraction(dt: datetime) -> float:
    """
    Convert datetime to UTC fraction of day.
    
    Args:
        dt: datetime object (assumed to be UTC)
        
    Returns:
        Fraction of day (0.0 = midnight, 0.5 = noon, 1.0 = midnight next day)
        
    Example:
        >>> from datetime import datetime
        >>> dt = datetime(2024, 6, 15, 12, 0)  # Noon UTC
        >>> frac = get_utc_fraction(dt)
        >>> print(f"UTC fraction: {frac}")  # Should be 0.5
    """
    seconds_since_midnight = (
        dt.hour * 3600 + 
        dt.minute * 60 + 
        dt.second + 
        dt.microsecond / 1e6
    )
    return seconds_since_midnight / 86400.0


# ============================================================================
# High-Level Interface
# ============================================================================

class SolarCalculator:
    """
    High-level interface for solar position calculations.
    
    This class provides convenient methods for common solar calculations
    needed in HF propagation modeling.
    """
    
    def __init__(self):
        """Initialize solar calculator"""
        pass
    
    def calculate_zenith_angle(
        self,
        location: GeographicPoint,
        time: datetime
    ) -> float:
        """
        Calculate solar zenith angle at a location and time.
        
        Args:
            location: Geographic point (lat/lon in radians)
            time: UTC datetime
            
        Returns:
            Solar zenith angle in radians
        """
        utc_frac = get_utc_fraction(time)
        month = time.month
        return compute_zenith_angle(location, utc_frac, month)
    
    def is_daytime_at(
        self,
        location: GeographicPoint,
        time: datetime,
        twilight_deg: float = 96.0
    ) -> bool:
        """
        Determine if it's daytime at a location and time.
        
        Args:
            location: Geographic point
            time: UTC datetime
            twilight_deg: Twilight angle in degrees (default: 96°)
            
        Returns:
            True if daytime, False if nighttime
        """
        zenith = self.calculate_zenith_angle(location, time)
        return is_daytime(zenith, twilight_deg * RinD)
    
    def calculate_local_time(
        self,
        longitude_deg: float,
        utc_time: datetime
    ) -> float:
        """
        Calculate local time at a longitude.
        
        Args:
            longitude_deg: Longitude in degrees (positive east)
            utc_time: UTC datetime
            
        Returns:
            Local time as fraction of day
        """
        utc_frac = get_utc_fraction(utc_time)
        lon_rad = longitude_deg * RinD
        return compute_local_time(utc_frac, lon_rad)


# ============================================================================
# Demo / Testing
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("DVOACAP Solar Calculations - Phase 2")
    print("=" * 70)
    
    # Test data: Halifax to London path at noon UTC
    halifax = GeographicPoint.from_degrees(44.374, -64.300)
    london = GeographicPoint.from_degrees(51.5, -0.1)
    
    test_time = datetime(2024, 6, 15, 12, 0)  # June 15, noon UTC
    utc_frac = get_utc_fraction(test_time)
    
    print(f"\nTest Scenario:")
    print(f"  Date/Time: {test_time} UTC")
    print(f"  UTC fraction: {utc_frac:.4f}")
    
    # Calculate for Halifax
    zenith_hfx = compute_zenith_angle(halifax, utc_frac, 6)
    local_hfx = compute_local_time(utc_frac, halifax.longitude)
    
    print(f"\nHalifax (44.4°N, 64.3°W):")
    print(f"  Solar zenith angle: {math.degrees(zenith_hfx):.1f}°")
    print(f"  Solar elevation: {math.degrees(solar_elevation_angle(zenith_hfx)):.1f}°")
    print(f"  Local time: {local_hfx * 24:.2f}h")
    print(f"  Daytime: {is_daytime(zenith_hfx)}")
    
    # Calculate for London
    zenith_lon = compute_zenith_angle(london, utc_frac, 6)
    local_lon = compute_local_time(utc_frac, london.longitude)
    
    print(f"\nLondon (51.5°N, 0.1°W):")
    print(f"  Solar zenith angle: {math.degrees(zenith_lon):.1f}°")
    print(f"  Solar elevation: {math.degrees(solar_elevation_angle(zenith_lon)):.1f}°")
    print(f"  Local time: {local_lon * 24:.2f}h")
    print(f"  Daytime: {is_daytime(zenith_lon)}")
    
    # Test high-level interface
    print(f"\n{'-' * 70}")
    print("High-Level Interface Test:")
    print("-" * 70)
    
    calc = SolarCalculator()
    
    zenith_test = calc.calculate_zenith_angle(halifax, test_time)
    print(f"Halifax zenith (high-level): {math.degrees(zenith_test):.1f}°")
    print(f"Is daytime: {calc.is_daytime_at(halifax, test_time)}")
    
    local_test = calc.calculate_local_time(-64.3, test_time)
    print(f"Local time: {local_test * 24:.2f}h")
    
    print("\n" + "=" * 70)
    print("✓ Phase 2 Solar Module Complete!")
    print("=" * 70)
