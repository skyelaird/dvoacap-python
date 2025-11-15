#!/usr/bin/env python3
"""
PathGeom - Path Geometry Module for VOACAP
Ported from PathGeom.pas (DVOACAP)

Original Author: Alex Shovkoplyas, VE3NEA
Python Port: 2025

This module handles 2D and 3D path geometry calculations for HF propagation:
- Great circle path calculations
- Azimuth calculations (transmitter to receiver and vice versa)
- Point-along-path calculations
- 3D hop geometry (elevation angles, hop distances, etc.)
"""

import math
from dataclasses import dataclass
from typing import Optional, Tuple


# ============================================================================
# Constants from VoaTypes.pas
# ============================================================================

# Mathematical constants
TWO_PI = 2 * math.pi
HALF_PI = math.pi / 2
RinD = math.pi / 180  # radians in degree
DinR = 180 / math.pi  # degrees in radian

# Physical constants
EarthR = 6370.0  # radius of the Earth in km
VofL = 299.79246  # velocity of light

# Minimum distances and tolerances
MIN_RXTX_DIST = 0.03 * RinD  # min distance between tx and rx, radians
MIN_RXTX_DIST2 = 0.000001
MAX_NON_POLE_LAT = 89.9 * RinD  # if higher lat, it is a pole
MIN_NON_POLE_COSLAT = 1e-7

MAX_ELEV_ANGLE = 89.99 * RinD
JUST_BELOW_MAX_ELEV = 89.9 * RinD


# ============================================================================
# Data Structures
# ============================================================================

@dataclass
class GeoPoint:
    """Geographic point with latitude and longitude in radians"""
    lat: float  # Latitude in radians
    lon: float  # Longitude in radians
    
    @classmethod
    def from_degrees(cls, lat_deg: float, lon_deg: float) -> 'GeoPoint':
        """Create GeoPoint from degrees"""
        return cls(lat=lat_deg * RinD, lon=lon_deg * RinD)
    
    def to_degrees(self) -> Tuple[float, float]:
        """Convert to degrees (lat, lon)"""
        return (self.lat * DinR, self.lon * DinR)
    
    def __repr__(self) -> str:
        lat_d, lon_d = self.to_degrees()
        return f"GeoPoint(lat={lat_d:.4f}°, lon={lon_d:.4f}°)"


# ============================================================================
# Utility Functions
# ============================================================================

def sign(x: float) -> float:
    """Return sign of x: 1 if x >= 0, else -1"""
    return 1.0 if x >= 0 else -1.0


def clamp_cosine(cos_val: float) -> float:
    """Clamp cosine value to [-1, 1] to avoid numerical errors"""
    if abs(cos_val) > 1:
        return sign(cos_val)
    return cos_val


# ============================================================================
# PathGeometry Class - 2D Path Calculations
# ============================================================================

class PathGeometry:
    """
    Handles great circle path geometry calculations between transmitter and receiver.
    
    This class computes:
    - Great circle distance
    - Azimuths (Tx->Rx and Rx->Tx)
    - Points along the path
    - Hop counts for given elevation angles
    """
    
    def __init__(self):
        self.tx: Optional[GeoPoint] = None
        self.rx: Optional[GeoPoint] = None
        self.dist: float = 0.0  # Great circle distance in radians
        self.azim_tr: float = 0.0  # Azimuth from Tx to Rx in radians
        self.azim_rt: float = 0.0  # Azimuth from Rx to Tx in radians
        self.d_lon: float = 0.0  # Longitude difference
        self.long_path: bool = False  # Use long path instead of short path
    
    def set_tx_rx(self, tx: GeoPoint, rx: GeoPoint) -> None:
        """
        Set transmitter and receiver locations and compute path parameters.
        
        Args:
            tx: Transmitter location (GeoPoint with lat/lon in radians)
            rx: Receiver location (GeoPoint with lat/lon in radians)
        """
        self.tx = GeoPoint(tx.lat, tx.lon)
        self.rx = GeoPoint(rx.lat, rx.lon)
        
        # Move Rx away from Tx a little bit if they're too close
        if max(abs(self.rx.lat - self.tx.lat), 
               abs(self.rx.lon - self.tx.lon)) <= MIN_RXTX_DIST:
            self.rx.lat = self.rx.lat - sign(self.rx.lat) * MIN_RXTX_DIST
        
        # At poles, force longitude = 0
        if abs(self.rx.lat) > MAX_NON_POLE_LAT:
            self.rx.lon = 0
        if abs(self.tx.lat) > MAX_NON_POLE_LAT:
            self.tx.lon = 0
        
        # Calculate longitude difference
        self.d_lon = self.tx.lon - self.rx.lon
        if abs(self.d_lon) > math.pi:
            self.d_lon = self.d_lon - sign(self.d_lon) * TWO_PI
        if self.long_path:
            self.d_lon = self.d_lon - sign(self.d_lon) * TWO_PI
        
        # Calculate great circle distance
        qcos = (math.sin(self.tx.lat) * math.sin(self.rx.lat) + 
                math.cos(self.tx.lat) * math.cos(self.rx.lat) * math.cos(self.d_lon))
        qcos = clamp_cosine(qcos)
        self.dist = max(MIN_RXTX_DIST2, math.acos(qcos))
        if self.long_path:
            self.dist = TWO_PI - self.dist
        
        # Calculate azimuth Tx -> Rx
        if math.cos(self.tx.lat) <= MIN_NON_POLE_COSLAT:
            # TX is near pole
            if self.tx.lat <= 0:
                self.azim_tr = 0
            else:
                self.azim_tr = math.pi
        else:
            qcos = ((math.sin(self.rx.lat) - math.sin(self.tx.lat) * math.cos(self.dist)) / 
                    (math.cos(self.tx.lat) * math.sin(self.dist)))
            qcos = clamp_cosine(qcos)
            self.azim_tr = math.acos(qcos)
        
        if self.d_lon > 0:
            self.azim_tr = TWO_PI - self.azim_tr
        
        # Calculate azimuth Rx -> Tx
        if math.cos(self.rx.lat) <= MIN_NON_POLE_COSLAT:
            # RX is near pole
            if self.rx.lat <= 0:
                self.azim_rt = 0
            else:
                self.azim_rt = math.pi
        else:
            qcos = ((math.sin(self.tx.lat) - math.sin(self.rx.lat) * math.cos(self.dist)) / 
                    (math.cos(self.rx.lat) * math.sin(self.dist)))
            qcos = clamp_cosine(qcos)
            self.azim_rt = math.acos(qcos)
        
        if self.d_lon < 0:
            self.azim_rt = TWO_PI - self.azim_rt
    
    def get_point_at_dist(self, dist: float) -> GeoPoint:
        """
        Get a point along the great circle path at a given distance from Tx.
        
        Args:
            dist: Distance from transmitter in radians
            
        Returns:
            GeoPoint at the specified distance along the path
        """
        if self.tx is None:
            raise ValueError("Transmitter location not set. Call set_tx_rx() first.")
        
        # Special case: TX near pole
        if math.cos(self.tx.lat) < MIN_NON_POLE_COSLAT:
            result_lat = self.tx.lat - sign(self.tx.lat) * abs(dist)
            if abs(result_lat) > HALF_PI:
                result_lat = sign(result_lat) * HALF_PI
            result_lon = self.rx.lon
            return GeoPoint(result_lat, result_lon)
        
        # Calculate latitude at distance
        qcos = (math.cos(dist) * math.sin(self.tx.lat) + 
                math.sin(dist) * math.cos(self.tx.lat) * math.cos(self.azim_tr))
        qcos = clamp_cosine(qcos)
        result_lat = HALF_PI - math.acos(qcos)
        
        # Special case: result near pole
        if math.cos(result_lat) <= MIN_NON_POLE_COSLAT:
            result_lon = self.tx.lon
            return GeoPoint(result_lat, result_lon)
        
        # Calculate longitude at distance
        qcos = ((math.cos(dist) - math.sin(result_lat) * math.sin(self.tx.lat)) / 
                (math.cos(result_lat) * math.cos(self.tx.lat)))
        qcos = clamp_cosine(qcos)
        result_lon = math.acos(qcos)
        
        if dist > math.pi:
            result_lon = TWO_PI - result_lon
        result_lon = self.tx.lon - sign(self.d_lon) * abs(result_lon)
        
        if abs(result_lon) > math.pi:
            result_lon = result_lon - sign(result_lon) * TWO_PI
        
        return GeoPoint(result_lat, result_lon)
    
    def hop_count(self, elev: float, height: float) -> int:
        """
        Calculate the number of hops required for given elevation angle and height.
        
        Args:
            elev: Elevation angle in radians
            height: Virtual height in km
            
        Returns:
            Number of hops required
        """
        return 1 + int(self.dist / hop_distance(elev, height))
    
    def get_distance_km(self) -> float:
        """Get great circle distance in kilometers"""
        return self.dist * EarthR
    
    def get_azimuth_tr_degrees(self) -> float:
        """Get azimuth from Tx to Rx in degrees"""
        return self.azim_tr * DinR
    
    def get_azimuth_rt_degrees(self) -> float:
        """Get azimuth from Rx to Tx in degrees"""
        return self.azim_rt * DinR


# ============================================================================
# 3D Path Calculations - Module-Level Functions
# ============================================================================

def hop_distance(elev: float, height: float) -> float:
    """
    Calculate the ground distance of one hop in radians.
    
    Args:
        elev: Elevation angle in radians
        height: Virtual height in km
        
    Returns:
        Hop distance in radians
    """
    result = math.cos(elev) * EarthR / (EarthR + height)
    result = 2 * (math.acos(result) - elev)
    return result


def hop_length_3d(elev: float, hop_dist: float, virt_height: float) -> float:
    """
    Calculate the 3D length of a hop path.
    
    Args:
        elev: Elevation angle in radians
        hop_dist: Hop distance (ground) in radians
        virt_height: Virtual reflection height in km
        
    Returns:
        3D hop path length in km
    """
    result = (2 * (virt_height + EarthR * (1 - math.cos(0.5 * hop_dist))) / 
              math.sin(0.5 * hop_dist + elev))
    return result


def calc_elevation_angle(hop_dist: float, height: float) -> float:
    """
    Calculate elevation angle from hop distance and height.
    
    Args:
        hop_dist: Hop distance in radians
        height: Virtual height in km
        
    Returns:
        Elevation angle in radians
    """
    half = 0.5 * hop_dist
    result = (math.cos(half) - EarthR / (EarthR + height)) / math.sin(half)
    result = math.atan(result)
    return result


def sin_of_incidence(elev: float, height: float) -> float:
    """
    Calculate sine of incidence angle at ionosphere.
    
    Args:
        elev: Elevation angle in radians
        height: Height in km
        
    Returns:
        Sin of incidence angle
    """
    return EarthR * math.cos(elev) / (EarthR + height)


def cos_of_incidence(elev: float, height: float) -> float:
    """
    Calculate cosine of incidence angle at ionosphere.
    
    Args:
        elev: Elevation angle in radians
        height: Height in km
        
    Returns:
        Cos of incidence angle
    """
    sin_i = sin_of_incidence(elev, height)
    result = math.sqrt(max(1e-6, 1 - sin_i**2))
    return result


# ============================================================================
# Example/Test Code
# ============================================================================

def example_usage():
    """Demonstrate usage of the PathGeometry module"""
    
    print("=" * 70)
    print("PathGeometry Module - Example Usage")
    print("=" * 70)
    print()
    
    # Create transmitter and receiver locations
    # Example: Halifax, NS (44.65°N, 63.57°W) to London, UK (51.51°N, 0.13°W)
    tx = GeoPoint.from_degrees(44.65, -63.57)
    rx = GeoPoint.from_degrees(51.51, -0.13)
    
    print(f"Transmitter: {tx}")
    print(f"Receiver:    {rx}")
    print()
    
    # Create path geometry object
    path = PathGeometry()
    path.set_tx_rx(tx, rx)
    
    # Display path parameters
    print("Path Parameters:")
    print(f"  Distance:        {path.get_distance_km():.1f} km")
    print(f"  Azimuth (Tx->Rx): {path.get_azimuth_tr_degrees():.1f}°")
    print(f"  Azimuth (Rx->Tx): {path.get_azimuth_rt_degrees():.1f}°")
    print()
    
    # Calculate hop parameters for different elevation angles
    print("Hop Analysis:")
    print(f"{'Elev (°)':<10} {'Height (km)':<15} {'Hop Dist (km)':<15} {'Hop Count':<12}")
    print("-" * 52)
    
    test_elevations = [5, 10, 15, 20]  # degrees
    test_height = 300  # km
    
    for elev_deg in test_elevations:
        elev_rad = elev_deg * RinD
        hop_dist_rad = hop_distance(elev_rad, test_height)
        hop_dist_km = hop_dist_rad * EarthR
        hops = path.hop_count(elev_rad, test_height)
        print(f"{elev_deg:<10} {test_height:<15} {hop_dist_km:<15.1f} {hops:<12}")
    
    print()
    
    # Calculate points along the path
    print("Points Along Path:")
    print(f"{'Distance (%)':<15} {'Latitude (°)':<15} {'Longitude (°)':<15}")
    print("-" * 45)
    
    for pct in [0, 25, 50, 75, 100]:
        dist_rad = (pct / 100.0) * path.dist
        point = path.get_point_at_dist(dist_rad)
        lat_d, lon_d = point.to_degrees()
        print(f"{pct:<15} {lat_d:<15.4f} {lon_d:<15.4f}")
    
    print()
    
    # 3D path calculations
    print("3D Path Calculations:")
    elev = 10 * RinD  # 10 degrees
    hop_dist_rad = hop_distance(elev, test_height)
    hop_length = hop_length_3d(elev, hop_dist_rad, test_height)
    sin_i = sin_of_incidence(elev, test_height)
    cos_i = cos_of_incidence(elev, test_height)
    
    print(f"  Elevation angle:      {10}°")
    print(f"  Virtual height:       {test_height} km")
    print(f"  Hop distance (3D):    {hop_length:.1f} km")
    print(f"  Sin of incidence:     {sin_i:.4f}")
    print(f"  Cos of incidence:     {cos_i:.4f}")
    print()
    
    # Test reverse calculation
    print("Reverse Calculation Test:")
    calc_elev = calc_elevation_angle(hop_dist_rad, test_height)
    print(f"  Original elevation:   {10}°")
    print(f"  Calculated from hop:  {calc_elev * DinR:.1f}°")
    print()
    
    print("=" * 70)


if __name__ == "__main__":
    example_usage()
