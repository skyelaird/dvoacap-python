#!/usr/bin/env python3
"""
HF Propagation Prediction Generator with DVOACAP Integration
Generates predictions using both ITU-R (quick) and DVOACAP (accurate) models
"""

import json
import math
import requests
import os
import sys
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Tuple
from pathlib import Path

# Check for DVOACAP availability
DVOACAP_AVAILABLE = False
try:
    from dvoacap_wrapper import DVOACAPEngine
    DVOACAP_AVAILABLE = True
    print("✓ DVOACAP engine available - accurate predictions enabled")
except ImportError:
    print("⚠  DVOACAP wrapper not found - using ITU-R model only")
    print("  Ensure dvoacap_wrapper.py and dvoa.dll are in the same directory")

# VE1ATM Station Parameters
MY_QTH = {
    'call': 'VE1ATM',
    'lat': 44.374,
    'lon': -64.300,
    'grid': 'FN74ui',
    'antenna': 'DX Commander 7m Vertical',
    'bands': ['40m', '30m', '20m', '17m', '15m', '12m', '10m']
}

# Band frequencies
BAND_FREQS = {
    '40m': 7.1,
    '30m': 10.125,
    '20m': 14.150,
    '17m': 18.118,
    '15m': 21.200,
    '12m': 24.940,
    '10m': 28.500
}

# Target regions
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
        solar_url = "https://services.swpc.noaa.gov/json/solar-cycle/observed-solar-cycle-indices.json"
        
        response = requests.get(solar_url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            latest = data[-1]
            sfi = float(latest.get('f10.7', 150))
            ssn = float(latest.get('ssn', 100))
        else:
            sfi = 150
            ssn = 100
            
        try:
            kp_url = "https://services.swpc.noaa.gov/json/planetary_k_index_1m.json"
            kp_response = requests.get(kp_url, timeout=10)
            if kp_response.status_code == 200:
                kp_data = kp_response.json()
                kp = float(kp_data[-1].get('kp_index', 2.0))
            else:
                kp = 2.0
        except:
            kp = 2.0
            
        return {
            'sfi': sfi,
            'ssn': int(ssn),
            'kp': kp,
            'a_index': kp * 15,
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
    """Calculate great circle distance (km) and initial bearing"""
    lat1_r = math.radians(lat1)
    lat2_r = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    distance = 6371 * c
    
    y = math.sin(delta_lon) * math.cos(lat2_r)
    x = math.cos(lat1_r) * math.sin(lat2_r) - math.sin(lat1_r) * math.cos(lat2_r) * math.cos(delta_lon)
    bearing = (math.degrees(math.atan2(y, x)) + 360) % 360
    
    return distance, bearing

def calculate_muf_itur(distance_km: float, sfi: float, hour_utc: int, lat: float) -> float:
    """Calculate MUF using simplified ITU-R model (QUICK MODE)"""
    base_fof2 = 4.0 + (sfi - 70) / 30.0
    lst = (hour_utc + (lat / 15.0)) % 24
    diurnal_factor = 0.7 + 0.3 * math.cos(2 * math.pi * (lst - 14) / 24)
    fof2 = base_fof2 * diurnal_factor
    
    if distance_km < 2000:
        hop_angle = math.degrees(math.atan(distance_km / 600))
        muf_factor = 1 / math.cos(math.radians(hop_angle))
    else:
        hop_angle = math.degrees(math.atan(distance_km / 1200))
        muf_factor = 1 / math.cos(math.radians(hop_angle))
        muf_factor = min(muf_factor, 4.0)
    
    muf = fof2 * muf_factor
    return max(muf, 5.0)

def calculate_signal_quality_itur(freq_mhz: float, muf: float, distance_km: float, 
                                  kp: float, hour_utc: int) -> Dict:
    """Calculate signal quality using ITU-R model (QUICK MODE)"""
    fof_ratio = freq_mhz / muf
    optimal_ratio = 0.85
    
    if fof_ratio > 1.0:
        reliability = 0
        snr = -20
        quality = 'CLOSED'
    elif fof_ratio > 0.95:
        reliability = int(20 * (1.0 - fof_ratio) / 0.05)
        snr = -10 + (reliability / 2)
        quality = 'POOR'
    elif fof_ratio > 0.75:
        deviation = abs(fof_ratio - optimal_ratio)
        reliability = int(90 - (deviation * 200))
        snr = 10 + (reliability - 85) / 2
        quality = 'GOOD' if reliability > 70 else 'FAIR'
    elif fof_ratio > 0.5:
        reliability = int(70 - (0.75 - fof_ratio) * 100)
        snr = 5 + (reliability - 60) / 3
        quality = 'FAIR'
    else:
        reliability = int(30 - (0.5 - fof_ratio) * 60)
        snr = -5 + reliability / 5
        quality = 'POOR'
    
    if kp > 4:
        reliability = int(reliability * (1 - (kp - 4) * 0.15))
        snr -= (kp - 4) * 3
        if quality == 'GOOD':
            quality = 'FAIR'
    
    if 0 <= hour_utc <= 6 or 18 <= hour_utc <= 23:
        if freq_mhz < 10:
            reliability = min(100, int(reliability * 1.1))
            snr += 2
        elif freq_mhz > 21:
            reliability = int(reliability * 0.8)
            snr -= 3
    
    if distance_km > 8000:
        reliability = int(reliability * 0.9)
        snr -= 2
    
    reliability = max(0, min(100, reliability))
    
    return {
        'reliability': reliability,
        'snr_db': round(snr, 1),
        'quality': quality,
        'muf': round(muf, 1),
        'fof_ratio': round(fof_ratio, 2),
        'method': 'ITU-R'
    }

def run_dvoacap_prediction(engine: 'DVOACAPEngine', freq_mhz: float, 
                          tx_lat: float, tx_lon: float,
                          rx_lat: float, rx_lon: float, 
                          rx_label: str,
                          hour_utc: int,
                          solar_data: Dict) -> Dict:
    """Run DVOACAP prediction for a specific path (ACCURATE MODE)"""
    try:
        result = engine.predict_simple(
            tx_lat=tx_lat,
            tx_lon=tx_lon,
            rx_lat=rx_lat,
            rx_lon=rx_lon,
            frequency_mhz=freq_mhz,
            hour_utc=hour_utc,
            ssn=solar_data['ssn'],
            rx_label=rx_label
        )
        return result
        
    except Exception as e:
        print(f"DVOACAP prediction error for {rx_label}: {e}")
        return None

def predict_band_conditions(solar_data: Dict, use_dvoacap: bool = False, 
                           dvoacap_engine: 'DVOACAPEngine' = None) -> Dict:
    """Generate predictions for all bands (with optional DVOACAP)"""
    predictions = {
        'station': MY_QTH,
        'solar': solar_data,
        'generated': datetime.now(timezone.utc).isoformat(),
        'mode': 'DVOACAP' if use_dvoacap and DVOACAP_AVAILABLE else 'ITU-R',
        'dvoacap_available': DVOACAP_AVAILABLE,
        'bands': {}
    }
    
    current_hour = datetime.now(timezone.utc).hour
    
    print(f"\nGenerating predictions for {len(BAND_FREQS)} bands x {len(TARGET_REGIONS)} regions...")
    
    for band_name, freq in BAND_FREQS.items():
        print(f"  Processing {band_name} ({freq} MHz)...", end='')
        band_predictions = {
            'frequency': freq,
            'regions': {}
        }
        
        for region_code, region_info in TARGET_REGIONS.items():
            distance, bearing = calculate_distance_bearing(
                MY_QTH['lat'], MY_QTH['lon'],
                region_info['lat'], region_info['lon']
            )
            
            # Always calculate ITU-R (quick) prediction as baseline
            muf = calculate_muf_itur(distance, solar_data['sfi'], current_hour, region_info['lat'])
            quality_itur = calculate_signal_quality_itur(
                freq, muf, distance, solar_data['kp'], current_hour
            )
            
            region_data = {
                'name': region_info['name'],
                'distance_km': round(distance, 0),
                'bearing': round(bearing, 0),
                'itur': quality_itur
            }
            
            # If DVOACAP requested and available, run DVOACAP prediction
            if use_dvoacap and dvoacap_engine:
                dvoacap_result = run_dvoacap_prediction(
                    dvoacap_engine,
                    freq, 
                    MY_QTH['lat'], MY_QTH['lon'],
                    region_info['lat'], region_info['lon'],
                    region_code,
                    current_hour, 
                    solar_data
                )
                if dvoacap_result and dvoacap_result['method'] == 'VOACAP':
                    region_data['dvoacap'] = dvoacap_result
                    # Use DVOACAP results for display
                    region_data.update({
                        'reliability': dvoacap_result['reliability'],
                        'snr_db': dvoacap_result['snr_db'],
                        'quality': dvoacap_result['quality'],
                        'muf': dvoacap_result['muf'],
                        'method': 'VOACAP'
                    })
                else:
                    # Fall back to ITU-R
                    region_data.update(quality_itur)
            else:
                # Use ITU-R as default
                region_data.update(quality_itur)
            
            band_predictions['regions'][region_code] = region_data
        
        predictions['bands'][band_name] = band_predictions
        print(" ✓")
    
    return predictions

def predict_24_hour_timeline(solar_data: Dict) -> Dict:
    """Generate 72-hour timeline using ITU-R model"""
    timeline = {
        'generated': datetime.now(timezone.utc).isoformat(),
        'hours': []
    }
    
    current_time = datetime.now(timezone.utc)
    
    print("\nGenerating 72-hour timeline...")
    
    for hour_offset in range(72):
        prediction_time = current_time + timedelta(hours=hour_offset)
        hour_utc = prediction_time.hour
        
        hour_data = {
            'time': prediction_time.isoformat(),
            'hour_utc': hour_utc,
            'bands': {}
        }
        
        for band_name, freq in BAND_FREQS.items():
            band_status = {'open': [], 'marginal': [], 'closed': []}
            
            for region_code, region_info in TARGET_REGIONS.items():
                distance, _ = calculate_distance_bearing(
                    MY_QTH['lat'], MY_QTH['lon'],
                    region_info['lat'], region_info['lon']
                )
                
                muf = calculate_muf_itur(distance, solar_data['sfi'], hour_utc, region_info['lat'])
                quality = calculate_signal_quality_itur(freq, muf, distance, solar_data['kp'], hour_utc)
                
                if quality['reliability'] > 60:
                    band_status['open'].append(region_code)
                elif quality['reliability'] > 30:
                    band_status['marginal'].append(region_code)
                else:
                    band_status['closed'].append(region_code)
            
            hour_data['bands'][band_name] = band_status
        
        timeline['hours'].append(hour_data)
    
    print("  ✓ Timeline complete")
    
    return timeline

def load_dxcc_data() -> Dict:
    """Load DXCC worked/needed data"""
    try:
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
        
        print("  Note: dxcc_summary.json not found - DXCC tracking disabled")
        return {'dxcc_missing': [], 'dxcc_worked': []}
    except Exception as e:
        print(f"  Warning: Could not load DXCC data: {e}")
        return {'dxcc_missing': [], 'dxcc_worked': []}

def main():
    print("=== VE1ATM HF Propagation Prediction Generator ===")
    print(f"Mode: {'DVOACAP (Accurate)' if DVOACAP_AVAILABLE else 'ITU-R (Quick)'}\n")
    
    # Check for DVOACAP mode flag
    use_dvoacap = '--dvoacap' in sys.argv or '--accurate' in sys.argv
    
    dvoacap_engine = None
    if use_dvoacap:
        if not DVOACAP_AVAILABLE:
            print("⚠  DVOACAP mode requested but not available")
            print("  Falling back to ITU-R mode")
            print("  To enable DVOACAP:")
            print("    1. Ensure dvoacap_wrapper.py is in this directory")
            print("    2. Download dvoa.dll from: https://github.com/VE3NEA/DVOACAP")
            print("    3. Place dvoa.dll in this directory")
            print("    4. Re-run with --dvoacap flag\n")
            use_dvoacap = False
        else:
            try:
                print("Initializing DVOACAP engine...")
                dvoacap_engine = DVOACAPEngine("dvoa.dll")
                print("✓ DVOACAP engine ready\n")
            except Exception as e:
                print(f"✗ Could not initialize DVOACAP engine: {e}")
                print("  Falling back to ITU-R mode\n")
                use_dvoacap = False
    
    # Fetch solar data
    print("Fetching current solar-terrestrial data...")
    solar_data = fetch_solar_data()
    print(f"  Solar Flux (SFI): {solar_data['sfi']}")
    print(f"  Sunspot Number: {solar_data['ssn']}")
    print(f"  Kp Index: {solar_data['kp']}")
    print(f"  A Index: {solar_data['a_index']}")
    
    # Generate predictions
    predictions = predict_band_conditions(solar_data, use_dvoacap, dvoacap_engine)
    
    # Generate timeline
    timeline = predict_24_hour_timeline(solar_data)
    
    # Load DXCC data
    print("\nLoading DXCC tracking data...")
    dxcc_data = load_dxcc_data()
    
    # Combine all data
    output_data = {
        'current_conditions': predictions,
        'timeline_24h': timeline,
        'dxcc': dxcc_data
    }
    
    # Save to JSON
    script_dir = Path(__file__).parent
    output_file = script_dir / 'propagation_data.json'
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\n✓ Predictions generated and saved to: {output_file}")
    print(f"  Mode: {predictions['mode']}")
    
    # Print summary
    print("\n=== CURRENT BAND CONDITIONS SUMMARY ===")
    for band_name, band_data in predictions['bands'].items():
        print(f"\n{band_name} ({band_data['frequency']} MHz):")
        good_regions = []
        fair_regions = []
        for region, data in band_data['regions'].items():
            if data['quality'] in ['GOOD', 'FAIR']:
                method_tag = f" [{data.get('method', 'ITU-R')}]" if use_dvoacap else ""
                if data['quality'] == 'GOOD':
                    good_regions.append(f"{region} ({data['reliability']}%{method_tag})")
                else:
                    fair_regions.append(f"{region} ({data['reliability']}%{method_tag})")
        
        if good_regions:
            print(f"  GOOD: {', '.join(good_regions)}")
        if fair_regions:
            print(f"  FAIR: {', '.join(fair_regions)}")
        if not good_regions and not fair_regions:
            print(f"  No good paths currently")
    
    if use_dvoacap and dvoacap_engine:
        print("\n✓ DVOACAP accurate predictions generated!")
    elif DVOACAP_AVAILABLE:
        print("\n  Tip: Run with --dvoacap flag for accurate predictions")
    else:
        print("\n  Tip: Add dvoacap_wrapper.py and dvoa.dll for DVOACAP accurate mode")

if __name__ == '__main__':
    main()
