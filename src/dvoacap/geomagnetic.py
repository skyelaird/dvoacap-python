#!/usr/bin/env python3
"""
Geomagnetic Field Calculations Module for VOACAP
Ported from MagFld.pas (DVOACAP)

Original Author: Alex Shovkoplyas, VE3NEA
Python Port: 2025

This module calculates geomagnetic field parameters for HF propagation modeling:
- Magnetic latitude
- Gyrofrequency
- Magnetic dip angle
"""

import math
from dataclasses import dataclass
from typing import List, Tuple
import numpy as np


# ============================================================================
# Constants
# ============================================================================

TWO_PI = 2 * math.pi
HALF_PI = math.pi / 2
RinD = math.pi / 180  # radians in degree
MAX_NON_POLE_LAT = 89.9 * RinD  # Maximum latitude before treating as pole

# Geomagnetic North Pole location (approximate)
MAG_POLE_LAT = 79.5 * RinD  # radians
MAG_POLE_LON = -69.0 * RinD  # radians

# Earth and height parameters for magnetic field calculation
EARTH_R_METERS = 6371200  # Earth radius in meters
HEIGHT_METERS = 300000    # Height for ionospheric calculation in meters
AR = EARTH_R_METERS / (EARTH_R_METERS + HEIGHT_METERS)  # Radius ratio


# ============================================================================
# Coefficient Arrays for Magnetic Field Model
# ============================================================================
# These are empirical coefficients from the International Geomagnetic
# Reference Field (IGRF) model, simplified for VOACAP

# CT coefficients for Schmidt semi-normalized associated Legendre functions
CT = np.array([
    [0,          0,          0,          0,          0,          0,          0],
    [0,          0,          0,          0,          0,          0,          0],
    [0.33333333, 0,          0,          0,          0,          0,          0],
    [0.26666667, 0.2,        0,          0,          0,          0,          0],
    [0.25714286, 0.22857142, 0.14285714, 0,          0,          0,          0],
    [0.25396825, 0.23809523, 0.19047619, 0.11111111, 0,          0,          0],
    [0.25252525, 0.24242424, 0.21212121, 0.16161616, 0.09090909, 0,          0]
], dtype=np.float32)

# G coefficients (cosine terms of spherical harmonic expansion)
G = np.array([
    [ 0,          0,         0,         0,         0,          0,        0],
    [ 0.304112,   0.021474,  0,         0,         0,          0,        0],
    [ 0.024035,  -0.051253, -0.013381,  0,         0,          0,        0],
    [-0.031518,   0.062130, -0.024898, -0.006496,  0,          0,        0],
    [-0.041794,  -0.045298, -0.021795,  0.007008, -0.002044,   0,        0],
    [ 0.016256,  -0.034407, -0.019447, -0.000608,  0.002775,   0.000697, 0],
    [-0.019523,  -0.004853,  0.003212,  0.021413,  0.001051,   0.000227, 0.001115]
], dtype=np.float32)

# H coefficients (sine terms of spherical harmonic expansion)
H = np.array([
    [0,  0.0,        0,          0,          0,          0,         0],
    [0, -0.057989,   0,          0,          0,          0,         0],
    [0,  0.033124,  -0.001579,   0,          0,          0,         0],
    [0,  0.014870,  -0.004075,   0.00021,    0,          0,         0],
    [0, -0.011825,   0.010006,   0.00043,    0.001385,   0,         0],
    [0, -0.000796,  -0.002,      0.004597,   0.002421,  -0.001218,  0],
    [0, -0.005758,  -0.008735,  -0.003406,  -0.000118,  -0.001116, -0.000325]
], dtype=np.float32)


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


@dataclass
class GeomagneticParameters:
    """Results of geomagnetic field calculations"""
    magnetic_latitude: float    # radians
    gyrofrequency: float       # MHz
    magnetic_dip: float        # radians (positive = downward in NH)
    field_x: float            # East component (for reference)
    field_y: float            # North component (for reference)
    field_z: float            # Vertical component (for reference)


# ============================================================================
# Sin/Cos Array Helper
# ============================================================================

@dataclass
class SinCos:
    """Paired sine and cosine values"""
    sin: float
    cos: float


def make_sincos_array(x: float, length: int) -> List[SinCos]:
    """
    Generate array of sin/cos pairs for multiple angles.
    
    This uses angle addition formulas to efficiently compute sin(n*x) and
    cos(n*x) for n = 0, 1, 2, ..., length-1
    
    Args:
        x: Base angle in radians
        length: Number of terms to generate
        
    Returns:
        List of SinCos objects containing sin(n*x) and cos(n*x)
        
    Note:
        Uses recurrence relation:
        sin((n+1)x) = sin(x)*cos(nx) + cos(x)*sin(nx)
        cos((n+1)x) = cos(x)*cos(nx) - sin(x)*sin(nx)
    """
    assert length > 1, "Length must be greater than 1"
    
    result = []
    
    # n = 0: sin(0) = 0, cos(0) = 1
    result.append(SinCos(sin=0.0, cos=1.0))
    
    # n = 1: sin(x), cos(x)
    result.append(SinCos(sin=math.sin(x), cos=math.cos(x)))
    
    # n >= 2: use recurrence relation
    for i in range(2, length):
        sin_val = result[1].sin * result[i-1].cos + result[1].cos * result[i-1].sin
        cos_val = result[1].cos * result[i-1].cos - result[1].sin * result[i-1].sin
        result.append(SinCos(sin=sin_val, cos=cos_val))
    
    return result


# ============================================================================
# Geomagnetic Field Calculator
# ============================================================================

class GeomagneticField:
    """
    Calculate geomagnetic field parameters using spherical harmonic model.
    
    This implements a simplified IGRF (International Geomagnetic Reference Field)
    model truncated to degree 6 for computational efficiency.
    """
    
    def __init__(self):
        """Initialize geomagnetic field calculator"""
        self.m_sin = math.sin(MAG_POLE_LAT)
        self.m_cos = math.cos(MAG_POLE_LAT)
        
        # Working arrays for associated Legendre functions
        self.P = np.zeros((7, 7), dtype=np.float32)
        self.DP = np.zeros((7, 7), dtype=np.float32)
        
        # Field components
        self.X = 0.0  # East component
        self.Y = 0.0  # North component
        self.Z = 0.0  # Vertical component (positive down)
    
    def compute_xyz(self, lat: float, lon: float) -> Tuple[float, float, float]:
        """
        Compute X, Y, Z components of magnetic field vector.
        
        Args:
            lat: Latitude in radians
            lon: Longitude in radians (east positive)
            
        Returns:
            Tuple of (X, Y, Z) field components
            
        Note:
            - X: East component
            - Y: North component  
            - Z: Vertical component (positive downward)
            - Uses spherical harmonic expansion to degree 6
        """
        # Handle polar regions where cos(lat) → 0
        if lat > MAX_NON_POLE_LAT:
            lat = MAX_NON_POLE_LAT
            lon = 0
        elif lat < -MAX_NON_POLE_LAT:
            lat = -MAX_NON_POLE_LAT
            lon = 0
        
        # Compute sin and cos of latitude
        C = math.sin(lat)  # sin(colatitude) = cos(latitude) in standard coords
        S = math.cos(lat)  # cos(colatitude) = sin(latitude) in standard coords
        
        # Generate sin/cos array for longitude multiples
        W = make_sincos_array(lon, 7)
        
        # Initialize
        pwr_ar = AR * AR  # (R / (R+h))^2
        self.P[0, 0] = 1
        self.DP[0, 0] = 0
        self.Z = 0
        self.Y = 0
        self.X = 0
        
        # Spherical harmonic expansion to degree 6
        for n in range(1, 7):
            sum_z = 0.0
            sum_y = 0.0
            sum_x = 0.0
            
            for m in range(0, n + 1):
                # Compute associated Legendre functions P_n^m and derivatives
                if m == n:
                    # Diagonal terms
                    self.P[n, n] = S * self.P[n-1, n-1]
                    self.DP[n, n] = S * self.DP[n-1, n-1] + C * self.P[n-1, n-1]
                elif n == 1:
                    # First degree
                    self.P[1, 0] = C
                    self.DP[1, 0] = -S
                else:
                    # Recurrence relation for P_n^m
                    self.P[n, m] = C * self.P[n-1, m] - CT[n, m] * self.P[n-2, m]
                    self.DP[n, m] = (C * self.DP[n-1, m] - S * self.P[n-1, m] - 
                                     CT[n, m] * self.DP[n-2, m])
                
                # Combine with G and H coefficients
                temp = G[n, m] * W[m].cos + H[n, m] * W[m].sin
                sum_z += self.P[n, m] * temp
                sum_y += self.DP[n, m] * temp
                sum_x += m * self.P[n, m] * (-G[n, m] * W[m].sin + H[n, m] * W[m].cos)
            
            # Accumulate field components with appropriate powers of (R/(R+h))
            pwr_ar *= AR
            self.Z -= pwr_ar * (n + 1) * sum_z
            self.Y -= pwr_ar * sum_y
            self.X += pwr_ar * sum_x
        
        # Normalize X by cos(lat) to get east component
        if abs(S) > 1e-10:
            self.X /= S
        
        return self.X, self.Y, self.Z
    
    def compute(self, location: GeographicPoint) -> GeomagneticParameters:
        """
        Compute all geomagnetic parameters for a location.
        
        Args:
            location: Geographic point (lat/lon in radians)
            
        Returns:
            GeomagneticParameters with all calculated values
            
        Note:
            Calculates:
            - Magnetic latitude (for ionospheric modeling)
            - Gyrofrequency (electron gyrofrequency in MHz)
            - Magnetic dip angle (inclination)
        """
        # Compute field vector components
        X, Y, Z = self.compute_xyz(location.latitude, location.longitude)
        
        # Calculate field magnitudes
        mag_2 = math.sqrt(X**2 + Y**2)  # Horizontal component
        mag_3 = math.sqrt(X**2 + Y**2 + Z**2)  # Total field strength
        
        # Calculate magnetic latitude
        # This is the angle to the magnetic equator
        q_cos = (self.m_sin * math.sin(location.latitude) + 
                 self.m_cos * math.cos(location.latitude) * 
                 math.cos(location.longitude - MAG_POLE_LON))
        
        # Clamp to valid range
        if abs(q_cos) > 1:
            q_cos = math.copysign(1.0, q_cos)
        
        mag_lat = HALF_PI - math.acos(q_cos)
        
        # Calculate gyrofrequency (MHz)
        # This is the electron gyrofrequency = (e * B) / (2π * m_e)
        # The factor 2.8 includes all the physical constants
        gyro_freq = 2.8 * mag_3
        
        # Calculate modified magnetic dip
        # This is the angle the field makes with horizontal
        # Modified version used in ionospheric calculations
        gob = max(0.000001, math.cos(location.latitude))
        mag_dip = math.atan(math.atan(-Z / mag_2) / math.sqrt(gob))
        
        return GeomagneticParameters(
            magnetic_latitude=mag_lat,
            gyrofrequency=gyro_freq,
            magnetic_dip=mag_dip,
            field_x=X,
            field_y=Y,
            field_z=Z
        )


# ============================================================================
# High-Level Interface
# ============================================================================

class GeomagneticCalculator:
    """
    High-level interface for geomagnetic calculations.
    
    This class provides convenient methods for computing geomagnetic
    parameters needed in HF propagation modeling.
    """
    
    def __init__(self):
        """Initialize geomagnetic calculator"""
        self.field = GeomagneticField()
    
    def calculate_parameters(
        self,
        location: GeographicPoint
    ) -> GeomagneticParameters:
        """
        Calculate all geomagnetic parameters for a location.
        
        Args:
            location: Geographic point
            
        Returns:
            GeomagneticParameters with calculated values
        """
        return self.field.compute(location)
    
    def calculate_magnetic_latitude(
        self,
        lat_deg: float,
        lon_deg: float
    ) -> float:
        """
        Calculate magnetic latitude in degrees.
        
        Args:
            lat_deg: Geographic latitude in degrees
            lon_deg: Geographic longitude in degrees
            
        Returns:
            Magnetic latitude in degrees
        """
        location = GeographicPoint.from_degrees(lat_deg, lon_deg)
        params = self.field.compute(location)
        return math.degrees(params.magnetic_latitude)
    
    def calculate_dip_angle(
        self,
        lat_deg: float,
        lon_deg: float
    ) -> float:
        """
        Calculate magnetic dip angle in degrees.
        
        Args:
            lat_deg: Geographic latitude in degrees
            lon_deg: Geographic longitude in degrees
            
        Returns:
            Magnetic dip angle in degrees (positive = downward in NH)
        """
        location = GeographicPoint.from_degrees(lat_deg, lon_deg)
        params = self.field.compute(location)
        return math.degrees(params.magnetic_dip)
    
    def calculate_gyrofrequency(
        self,
        lat_deg: float,
        lon_deg: float
    ) -> float:
        """
        Calculate electron gyrofrequency in MHz.
        
        Args:
            lat_deg: Geographic latitude in degrees
            lon_deg: Geographic longitude in degrees
            
        Returns:
            Gyrofrequency in MHz
        """
        location = GeographicPoint.from_degrees(lat_deg, lon_deg)
        params = self.field.compute(location)
        return params.gyrofrequency


# ============================================================================
# Demo / Testing
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("DVOACAP Geomagnetic Field Calculations - Phase 2")
    print("=" * 70)
    
    # Test locations
    test_locations = [
        ("Halifax, NS", 44.374, -64.300),
        ("London, UK", 51.5, -0.1),
        ("Equator", 0.0, 0.0),
        ("North Pole", 85.0, 0.0),
        ("Tokyo, Japan", 35.7, 139.7),
        ("Sydney, Australia", -33.9, 151.2),
    ]
    
    calc = GeomagneticCalculator()
    
    print("\nGeomagnetic Parameters at Various Locations:")
    print("-" * 70)
    print(f"{'Location':<20} {'MagLat':>8} {'Dip':>8} {'Gyro':>8}")
    print(f"{'':20} {'(deg)':>8} {'(deg)':>8} {'(MHz)':>8}")
    print("-" * 70)
    
    for name, lat, lon in test_locations:
        location = GeographicPoint.from_degrees(lat, lon)
        params = calc.calculate_parameters(location)
        
        print(f"{name:<20} "
              f"{math.degrees(params.magnetic_latitude):>8.2f} "
              f"{math.degrees(params.magnetic_dip):>8.2f} "
              f"{params.gyrofrequency:>8.3f}")
    
    # Detailed output for Halifax
    print(f"\n{'-' * 70}")
    print("Detailed Output for Halifax:")
    print("-" * 70)
    
    halifax = GeographicPoint.from_degrees(44.374, -64.300)
    params = calc.calculate_parameters(halifax)
    
    print(f"  Geographic Latitude:  {math.degrees(halifax.latitude):.3f}°")
    print(f"  Geographic Longitude: {math.degrees(halifax.longitude):.3f}°")
    print(f"\n  Magnetic Latitude:    {math.degrees(params.magnetic_latitude):.3f}°")
    print(f"  Magnetic Dip Angle:   {math.degrees(params.magnetic_dip):.3f}°")
    print(f"  Gyrofrequency:        {params.gyrofrequency:.3f} MHz")
    print(f"\n  Field Components:")
    print(f"    X (East):           {params.field_x:.6f}")
    print(f"    Y (North):          {params.field_y:.6f}")
    print(f"    Z (Down):           {params.field_z:.6f}")
    
    # Test high-level interface
    print(f"\n{'-' * 70}")
    print("High-Level Interface Test:")
    print("-" * 70)
    
    mag_lat = calc.calculate_magnetic_latitude(44.374, -64.300)
    dip = calc.calculate_dip_angle(44.374, -64.300)
    gyro = calc.calculate_gyrofrequency(44.374, -64.300)
    
    print(f"  Magnetic Latitude: {mag_lat:.2f}°")
    print(f"  Dip Angle:         {dip:.2f}°")
    print(f"  Gyrofrequency:     {gyro:.3f} MHz")
    
    print("\n" + "=" * 70)
    print("✓ Phase 2 Geomagnetic Module Complete!")
    print("=" * 70)
