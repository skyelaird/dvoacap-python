#!/usr/bin/env python3
"""
Integration Example: PathGeometry with Existing Propagation System

This demonstrates how the ported PathGeometry module could be integrated
with the existing HF propagation prediction system to add more detailed
path analysis capabilities.
"""

from path_geometry import PathGeometry, GeoPoint, hop_distance, RinD, DinR, EarthR
from typing import Dict, List
import json


class EnhancedPathAnalysis:
    """Enhanced path analysis using PathGeometry"""
    
    def __init__(self, tx_location: tuple[float, float]):
        """
        Initialize with transmitter location
        
        Args:
            tx_location: (latitude, longitude) in degrees
        """
        self.tx_lat, self.tx_lon = tx_location
        self.tx_point = GeoPoint.from_degrees(self.tx_lat, self.tx_lon)
    
    def analyze_path(self, 
                     rx_location: tuple[float, float],
                     frequency_mhz: float,
                     elevation_deg: float = 10.0,
                     virtual_height_km: float = 300.0) -> Dict:
        """
        Analyze propagation path with detailed geometry
        
        Args:
            rx_location: (lat, lon) in degrees
            frequency_mhz: Frequency in MHz
            elevation_deg: Elevation angle in degrees
            virtual_height_km: Virtual reflection height in km
            
        Returns:
            Dictionary with detailed path analysis
        """
        # Create path geometry
        rx_lat, rx_lon = rx_location
        rx_point = GeoPoint.from_degrees(rx_lat, rx_lon)
        
        path = PathGeometry()
        path.set_tx_rx(self.tx_point, rx_point)
        
        # Calculate hop parameters
        elev_rad = elevation_deg * RinD
        hop_dist_rad = hop_distance(elev_rad, virtual_height_km)
        hop_dist_km = hop_dist_rad * EarthR
        hop_count = path.hop_count(elev_rad, virtual_height_km)
        
        # Calculate intermediate reflection points
        reflection_points = []
        for hop in range(1, hop_count + 1):
            dist = hop * hop_dist_rad
            if dist < path.dist:
                point = path.get_point_at_dist(dist)
                lat, lon = point.to_degrees()
                reflection_points.append({
                    'hop': hop,
                    'latitude': round(lat, 4),
                    'longitude': round(lon, 4),
                    'distance_km': round(dist * EarthR, 1)
                })
        
        # Calculate midpoint for ionospheric conditions
        midpoint = path.get_point_at_dist(path.dist / 2)
        mid_lat, mid_lon = midpoint.to_degrees()
        
        return {
            'path_geometry': {
                'distance_km': round(path.get_distance_km(), 1),
                'azimuth_tx_to_rx': round(path.get_azimuth_tr_degrees(), 1),
                'azimuth_rx_to_tx': round(path.get_azimuth_rt_degrees(), 1),
                'midpoint_lat': round(mid_lat, 4),
                'midpoint_lon': round(mid_lon, 4)
            },
            'propagation': {
                'frequency_mhz': frequency_mhz,
                'elevation_angle': elevation_deg,
                'virtual_height_km': virtual_height_km,
                'hop_distance_km': round(hop_dist_km, 1),
                'hop_count': hop_count
            },
            'reflection_points': reflection_points,
            'transmitter': {
                'latitude': self.tx_lat,
                'longitude': self.tx_lon,
                'callsign': 'VE1ATM'  # Could be configurable
            },
            'receiver': {
                'latitude': rx_lat,
                'longitude': rx_lon
            }
        }
    
    def analyze_multiple_targets(self, 
                                 targets: List[Dict],
                                 frequency_mhz: float) -> List[Dict]:
        """
        Analyze paths to multiple targets
        
        Args:
            targets: List of dicts with 'lat', 'lon', and optional 'name'
            frequency_mhz: Frequency in MHz
            
        Returns:
            List of path analyses
        """
        results = []
        
        for target in targets:
            rx_location = (target['lat'], target['lon'])
            analysis = self.analyze_path(rx_location, frequency_mhz)
            analysis['target_name'] = target.get('name', 'Unknown')
            results.append(analysis)
        
        return results


def example_usage():
    """Demonstrate enhanced path analysis"""
    
    print("=" * 70)
    print("Enhanced Path Analysis - Integration Example")
    print("=" * 70)
    print()
    
    # Initialize with VE1ATM location (Halifax, NS)
    analyzer = EnhancedPathAnalysis((44.65, -63.57))
    
    # Define some interesting DX targets
    targets = [
        {'name': 'London, UK (G)', 'lat': 51.51, 'lon': -0.13},
        {'name': 'Tokyo, Japan (JA)', 'lat': 35.68, 'lon': 139.65},
        {'name': 'Sydney, Australia (VK)', 'lat': -33.87, 'lon': 151.21},
        {'name': 'Moscow, Russia (UA)', 'lat': 55.75, 'lon': 37.62},
    ]
    
    frequency = 14.2  # 20m band
    
    print(f"Analyzing paths from VE1ATM on {frequency} MHz")
    print()
    
    # Analyze paths
    results = analyzer.analyze_multiple_targets(targets, frequency)
    
    # Display results
    for result in results:
        print("-" * 70)
        print(f"Target: {result['target_name']}")
        print("-" * 70)
        
        geom = result['path_geometry']
        prop = result['propagation']
        
        print(f"  Distance:         {geom['distance_km']:>10.1f} km")
        print(f"  Azimuth (Tx->Rx): {geom['azimuth_tx_to_rx']:>10.1f}°")
        print(f"  Midpoint:         {geom['midpoint_lat']:>10.4f}°, "
              f"{geom['midpoint_lon']:>10.4f}°")
        print()
        print(f"  Hop count:        {prop['hop_count']:>10}")
        print(f"  Hop distance:     {prop['hop_distance_km']:>10.1f} km")
        
        if result['reflection_points']:
            print(f"\n  Reflection Points:")
            for point in result['reflection_points']:
                print(f"    Hop {point['hop']}: "
                      f"{point['latitude']:8.4f}°, {point['longitude']:9.4f}° "
                      f"({point['distance_km']:7.1f} km from Tx)")
        print()
    
    # Save one detailed analysis as JSON
    detailed = analyzer.analyze_path(
        (51.51, -0.13),  # London
        frequency,
        elevation_deg=12.0,
        virtual_height_km=280.0
    )
    
    print("=" * 70)
    print("Detailed JSON Export (London path):")
    print("=" * 70)
    print(json.dumps(detailed, indent=2))


def integration_with_existing_system():
    """
    Example of how this could integrate with the existing
    generate_propagation.py system
    """
    print()
    print("=" * 70)
    print("Integration Pattern with Existing System")
    print("=" * 70)
    print()
    
    code_example = """
# In generate_propagation.py, add this import:
from path_geometry import PathGeometry, GeoPoint

# When generating predictions, enhance with geometry:
def enhance_prediction_with_geometry(prediction, tx_location, rx_location):
    '''Add detailed path geometry to prediction'''
    
    tx = GeoPoint.from_degrees(tx_location['lat'], tx_location['lon'])
    rx = GeoPoint.from_degrees(rx_location['lat'], rx_location['lon'])
    
    path = PathGeometry()
    path.set_tx_rx(tx, rx)
    
    # Add to prediction
    prediction['path_geometry'] = {
        'distance_km': path.get_distance_km(),
        'azimuth': path.get_azimuth_tr_degrees(),
        'midpoint': path.get_point_at_dist(path.dist / 2).to_degrees()
    }
    
    return prediction

# Then in your main prediction loop:
for region in regions:
    prediction = calculate_propagation(region)
    prediction = enhance_prediction_with_geometry(
        prediction, 
        {'lat': 44.65, 'lon': -63.57},  # VE1ATM
        region['location']
    )
    predictions.append(prediction)
"""
    
    print(code_example)
    
    print("\nBenefits of integration:")
    print("  • Accurate azimuth calculations for antenna pointing")
    print("  • Midpoint calculations for ionospheric predictions")
    print("  • Hop analysis for multipath understanding")
    print("  • Reflection point mapping")
    print("  • Support for long path calculations")
    print()


if __name__ == "__main__":
    example_usage()
    integration_with_existing_system()
