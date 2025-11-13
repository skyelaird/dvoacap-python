#!/usr/bin/env python3
"""
HF Propagation Prediction Generator
Generates predictions based on current solar conditions for VE1ATM's QTH
Uses ITU-R based propagation models with real-time solar data
"""

import json
import math
import requests
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple
from pathlib import Path

# VE1ATM Station Parameters
MY_QTH = {
    'call': 'VE1ATM',
    'lat': 44.374,  # FN74ui
    'lon': -64.300,
    'grid': 'FN74ui',
    'antenna': 'DX Commander 7m Vertical',
    'bands': ['40m', '30m', '20m', '17m', '15m', '12m', '10m']
}

# Band frequencies (MHz) - use middle of band for calculations
BAND_FREQS = {
    '40m': 7.1,
    '30m': 10.125,
    '20m': 14.150,
    '17m': 18.118,
    '15m': 21.200,
    '12m': 24.940,
    '10m': 28.500
}

# Target regions for DXCC coverage - major areas
TARGET_REGIONS = {
    'EU': {'name': 'Europe', 'lat': 50.0, 'lon': 10.0, 'bearing': 45},
    'UK': {'name': 'United Kingdom', 'lat': 54.0, 'lon': -2.0, 'bearing': 40},
    'JA': {'name': 'Japan', 'lat': 36.0, 'lon': 138.0, 'bearing': 330},
    'VK': {'name': 'Australia', 'lat': -25.0, 'lon': 135.0, 'bearing': 240},
    'ZL': {'name': 'New Zealand', 'lat': -41.0, 'lon': 174.0, 'bearing': 230},
    'AF': {'name': 'Africa', 'lat': 0.0, 'lon': 20.0, 'bearing': 80},
    'SA': {'name': 'South America', 'lat': -15.0, 'lon': -55.0, 'bearing': 145},
    'CA': {'name': 'Central America', 'lat': 15.0, 'lon': -90.0, 'bearing': 190},
    'AS': {'name': 'Asia', 'lat': 30.0, 'lon': 100.0, 'bearing': 350},
    'OC': {'name': 'Oceania', 'lat': -10.0, 'lon': 150.0, 'bearing': 250},
}

def fetch_solar_data() -> Dict:
    """Fetch current solar-terrestrial data from NOAA"""
    try:
        # NOAA Space Weather JSON endpoints
        solar_url = "https://services.swpc.noaa.gov/json/solar-cycle/observed-solar-cycle-indices.json"
        
        # Get latest solar cycle data
        response = requests.get(solar_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Get most recent entry
            latest = data[-1]
            sfi = float(latest.get('f10.7', 150))
            ssn = float(latest.get('ssn', 100))
        else:
            # Fallback values if API fails
            sfi = 150
            ssn = 100
            
        # Try to get current geomagnetic indices
        try:
            kp_url = "https://services.swpc.noaa.gov/json/planetary_k_index_1m.json"
            kp_response = requests.get(kp_url, timeout=10)
            if kp_response.status_code == 200:
                kp_data = kp_response.json()
                # Get latest Kp
                kp = float(kp_data[-1].get('kp_index', 2.0))
            else:
                kp = 2.0
        except:
            kp = 2.0
            
        return {
            'sfi': sfi,
            'ssn': ssn,
            'kp': kp,
            'a_index': kp * 15,  # Rough conversion
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        print(f"Warning: Could not fetch solar data: {e}")
        print("Using typical conditions...")
        return {
            'sfi': 150,
            'ssn': 100,
            'kp': 2.0,
            'a_index': 30,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'note': 'Using estimated values due to API unavailability'
        }

def calculate_distance_bearing(lat1, lon1, lat2, lon2) -> Tuple[float, float]:
    """Calculate great circle distance (km) and initial bearing between two points"""
    lat1_r = math.radians(lat1)
    lat2_r = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    # Haversine formula
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = 6371 * c  # Earth radius in km
    
    # Bearing calculation
    y = math.sin(delta_lon) * math.cos(lat2_r)
    x = math.cos(lat1_r) * math.sin(lat2_r) - math.sin(lat1_r) * math.cos(lat2_r) * math.cos(delta_lon)
    bearing = (math.degrees(math.atan2(y, x)) + 360) % 360
    
    return distance, bearing

def calculate_muf(distance_km: float, sfi: float, hour_utc: int, lat: float) -> float:
    """
    Calculate Maximum Usable Frequency using simplified ITU-R model
    Based on critical frequency and path geometry
    """
    # Base critical frequency (foF2) dependent on solar flux
    # Typical relationship: foF2 ≈ 3-12 MHz depending on conditions
    base_fof2 = 4.0 + (sfi - 70) / 30.0  # Scales with solar flux
    
    # Diurnal variation - peak around 14:00 local solar time
    # Approximate local solar time (very rough)
    lst = (hour_utc + (lat / 15.0)) % 24
    diurnal_factor = 0.7 + 0.3 * math.cos(2 * math.pi * (lst - 14) / 24)
    
    fof2 = base_fof2 * diurnal_factor
    
    # MUF calculation using path geometry
    # For distances, we need to consider number of hops
    if distance_km < 2000:
        # Single hop E or F layer
        hop_angle = math.degrees(math.atan(distance_km / 600))  # E layer ~110km
        muf_factor = 1 / math.cos(math.radians(hop_angle))
    else:
        # Multi-hop F layer
        hop_angle = math.degrees(math.atan(distance_km / 1200))  # F layer ~300km
        muf_factor = 1 / math.cos(math.radians(hop_angle))
        muf_factor = min(muf_factor, 4.0)  # Limit for very long paths
    
    muf = fof2 * muf_factor
    
    return max(muf, 5.0)  # Minimum realistic MUF

def calculate_signal_quality(freq_mhz: float, muf: float, distance_km: float, 
                            kp: float, hour_utc: int) -> Dict:
    """
    Calculate signal quality metrics
    Returns reliability percentage and SNR estimate
    """
    # Frequency as fraction of MUF
    fof_ratio = freq_mhz / muf
    
    # Optimal frequency is 85% of MUF
    optimal_ratio = 0.85
    
    if fof_ratio > 1.0:
        # Above MUF - very poor
        reliability = 0
        snr = -20
        quality = 'CLOSED'
    elif fof_ratio > 0.95:
        # Close to MUF - marginal
        reliability = int(20 * (1.0 - fof_ratio) / 0.05)
        snr = -10 + (reliability / 2)
        quality = 'POOR'
    elif fof_ratio > 0.75:
        # Good range
        deviation = abs(fof_ratio - optimal_ratio)
        reliability = int(90 - (deviation * 200))
        snr = 10 + (reliability - 85) / 2
        quality = 'GOOD' if reliability > 70 else 'FAIR'
    elif fof_ratio > 0.5:
        # Lower than optimal - more absorption
        reliability = int(70 - (0.75 - fof_ratio) * 100)
        snr = 5 + (reliability - 60) / 3
        quality = 'FAIR'
    else:
        # Too low - high absorption
        reliability = int(30 - (0.5 - fof_ratio) * 60)
        snr = -5 + reliability / 5
        quality = 'POOR'
    
    # Adjust for geomagnetic conditions
    if kp > 4:
        reliability = int(reliability * (1 - (kp - 4) * 0.15))
        snr -= (kp - 4) * 3
        if quality == 'GOOD':
            quality = 'FAIR'
    
    # Night time path absorption (gray line is best)
    if 0 <= hour_utc <= 6 or 18 <= hour_utc <= 23:
        # Better for lower bands, worse for higher bands
        if freq_mhz < 10:
            reliability = min(100, int(reliability * 1.1))
            snr += 2
        elif freq_mhz > 21:
            reliability = int(reliability * 0.8)
            snr -= 3
    
    # Distance factor - longer paths have more variability
    if distance_km > 8000:
        reliability = int(reliability * 0.9)
        snr -= 2
    
    reliability = max(0, min(100, reliability))
    
    return {
        'reliability': reliability,
        'snr_db': round(snr, 1),
        'quality': quality,
        'muf': round(muf, 1),
        'fof_ratio': round(fof_ratio, 2)
    }

def predict_band_conditions(solar_data: Dict) -> Dict:
    """Generate predictions for all bands to all target regions"""
    predictions = {
        'station': MY_QTH,
        'solar': solar_data,
        'generated': datetime.now(timezone.utc).isoformat(),
        'bands': {}
    }
    
    current_hour = datetime.now(timezone.utc).hour
    
    for band_name, freq in BAND_FREQS.items():
        band_predictions = {
            'frequency': freq,
            'regions': {}
        }
        
        for region_code, region_info in TARGET_REGIONS.items():
            distance, bearing = calculate_distance_bearing(
                MY_QTH['lat'], MY_QTH['lon'],
                region_info['lat'], region_info['lon']
            )
            
            muf = calculate_muf(distance, solar_data['sfi'], current_hour, region_info['lat'])
            
            quality = calculate_signal_quality(
                freq, muf, distance, solar_data['kp'], current_hour
            )
            
            band_predictions['regions'][region_code] = {
                'name': region_info['name'],
                'distance_km': round(distance, 0),
                'bearing': round(bearing, 0),
                **quality
            }
        
        predictions['bands'][band_name] = band_predictions
    
    return predictions

def predict_24_hour_timeline(solar_data: Dict) -> Dict:
    """Generate hour-by-hour predictions for next 72 hours (3 days)"""
    timeline = {
        'generated': datetime.now(timezone.utc).isoformat(),
        'hours': []
    }
    
    current_time = datetime.now(timezone.utc)
    
    # Generate 72 hours of predictions
    for hour_offset in range(72):
        prediction_time = current_time + timedelta(hours=hour_offset)
        hour_utc = prediction_time.hour
        
        hour_data = {
            'time': prediction_time.isoformat(),
            'hour_utc': hour_utc,
            'bands': {}
        }
        
        # Predict for key regions
        for band_name, freq in BAND_FREQS.items():
            band_status = {'open': [], 'marginal': [], 'closed': []}
            
            for region_code, region_info in TARGET_REGIONS.items():
                distance, _ = calculate_distance_bearing(
                    MY_QTH['lat'], MY_QTH['lon'],
                    region_info['lat'], region_info['lon']
                )
                
                muf = calculate_muf(distance, solar_data['sfi'], hour_utc, region_info['lat'])
                quality = calculate_signal_quality(freq, muf, distance, solar_data['kp'], hour_utc)
                
                if quality['reliability'] > 60:
                    band_status['open'].append(region_code)
                elif quality['reliability'] > 30:
                    band_status['marginal'].append(region_code)
                else:
                    band_status['closed'].append(region_code)
            
            hour_data['bands'][band_name] = band_status
        
        timeline['hours'].append(hour_data)
    
    return timeline

def load_dxcc_data() -> Dict:
    """Load DXCC worked/needed data"""
    try:
        # Try current directory first, then look in common locations
        script_dir = Path(__file__).parent
        possible_paths = [
            script_dir / 'dxcc_summary.json',
            Path('dxcc_summary.json'),
            Path.home() / 'dxcc_summary.json'
        ]
        
        for path in possible_paths:
            if path.exists():
                with open(path, 'r') as f:
                    return json.load(f)
        
        # If not found, return empty
        print("  Note: dxcc_summary.json not found - DXCC tracking disabled")
        return {'dxcc_missing': [], 'dxcc_worked': []}
    except Exception as e:
        print(f"  Warning: Could not load DXCC data: {e}")
        return {'dxcc_missing': [], 'dxcc_worked': []}

def main():
    print("=== VE1ATM HF Propagation Prediction Generator ===\n")
    
    # Fetch current solar conditions
    print("Fetching current solar-terrestrial data...")
    solar_data = fetch_solar_data()
    print(f"  Solar Flux (SFI): {solar_data['sfi']}")
    print(f"  Sunspot Number: {solar_data['ssn']}")
    print(f"  Kp Index: {solar_data['kp']}")
    print(f"  A Index: {solar_data['a_index']}")
    
    # Generate current conditions
    print("\nGenerating band condition predictions...")
    current_predictions = predict_band_conditions(solar_data)
    
    # Generate 24-hour timeline
    print("Generating 72-hour timeline...")
    timeline = predict_24_hour_timeline(solar_data)
    
    # Load DXCC data
    print("Loading DXCC tracking data...")
    dxcc_data = load_dxcc_data()
    
    # Combine all data
    output_data = {
        'current_conditions': current_predictions,
        'timeline_24h': timeline,
        'dxcc': dxcc_data
    }
    
    # Save to JSON for web interface - use current directory
    script_dir = Path(__file__).parent
    output_file = script_dir / 'propagation_data.json'
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n✓ Predictions generated and saved to: {output_file}")
    
    # Print summary
    print("\n=== CURRENT BAND CONDITIONS SUMMARY ===")
    for band_name, band_data in current_predictions['bands'].items():
        print(f"\n{band_name} ({band_data['frequency']} MHz):")
        good_regions = []
        fair_regions = []
        for region, data in band_data['regions'].items():
            if data['quality'] in ['GOOD', 'FAIR']:
                if data['quality'] == 'GOOD':
                    good_regions.append(f"{region} ({data['reliability']}%)")
                else:
                    fair_regions.append(f"{region} ({data['reliability']}%)")
        
        if good_regions:
            print(f"  GOOD: {', '.join(good_regions)}")
        if fair_regions:
            print(f"  FAIR: {', '.join(fair_regions)}")
        if not good_regions and not fair_regions:
            print(f"  No good paths currently")

if __name__ == '__main__':
    main()
