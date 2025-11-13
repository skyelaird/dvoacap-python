#!/usr/bin/env python3
"""
Enhanced HF Propagation Dashboard with Real-Time Validation
Combines ITU-R predictions with PSKreporter actual reception data
"""

import json
import sys
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, List

# Import existing modules
sys.path.insert(0, str(Path(__file__).parent))

try:
    from pskreporter_api import PSKReporterAPI
    PSK_AVAILABLE = True
except ImportError:
    PSK_AVAILABLE = False
    print("Warning: PSKreporter integration not available")


def load_prediction_data(pred_file: Path) -> dict:
    """Load existing propagation predictions"""
    if pred_file.exists():
        with open(pred_file, 'r') as f:
            return json.load(f)
    return {}


def load_dxcc_data(dxcc_file: Path) -> dict:
    """Load DXCC entity data"""
    if dxcc_file.exists():
        with open(dxcc_file, 'r') as f:
            return json.load(f)
    return {}


def get_dxcc_from_country_name(country_name: str, dxcc_data: dict) -> Optional[str]:
    """
    Match PSKreporter country name to DXCC entity code
    """
    if not country_name or country_name == 'Unknown':
        return None
    
    # Direct name matches
    for entity_code, entity in dxcc_data.items():
        if entity['name'].lower() == country_name.lower():
            return entity_code
    
    # Handle common variations
    country_map = {
        'United States': '6',
        'England': '100',
        'Scotland': '103', 
        'Northern Ireland': '104',
        'Wales': '105',
        'Fed. Rep. of Germany': '140',
        'Germany': '140',
        'Hawaii': '382',
        'Alaska': '517',
        'Guantanamo Bay': '519'
    }
    
    if country_name in country_map:
        return country_map[country_name]
    
    # Partial match as fallback
    country_lower = country_name.lower()
    for entity_code, entity in dxcc_data.items():
        if country_lower in entity['name'].lower() or entity['name'].lower() in country_lower:
            return entity_code
    
    return None


def get_dxcc_from_grid(grid: str, dxcc_data: dict) -> Optional[str]:
    """
    Approximate DXCC entity from grid square (fallback method)
    """
    if not grid or len(grid) < 4:
        return None
    
    # Extract lat/lon from grid
    grid = grid.upper()
    lon = (ord(grid[0]) - ord('A')) * 20 - 180
    lat = (ord(grid[1]) - ord('A')) * 10 - 90
    
    if len(grid) >= 4:
        lon += int(grid[2]) * 2
        lat += int(grid[3])
    
    # Find closest DXCC entity
    min_dist = float('inf')
    closest_entity = None
    
    for entity_code, entity in dxcc_data.items():
        entity_lat = entity.get('lat', 0)
        entity_lon = entity.get('lon', 0)
        
        # Simple distance calculation
        dist = math.sqrt((lat - entity_lat)**2 + (lon - entity_lon)**2)
        
        if dist < min_dist:
            min_dist = dist
            closest_entity = entity_code
    
    return closest_entity


def map_region_to_dxcc_entities(region_code: str, dxcc_data: dict) -> List[str]:
    """
    Map region codes (EU, UK, JA, etc.) to DXCC entity codes
    """
    region_mappings = {
        'EU': ['100', '112', '116', '122', '126', '130', '136', '140', '145', '150', '154', '156', '160', '165', '175', '176', '182', '186', '187', '195', '196', '197', '199', '200', '201', '202'],  # Europe
        'UK': ['100', '103', '104', '105'],  # United Kingdom entities
        'JA': ['258'],  # Japan
        'VK': ['340'],  # Australia
        'ZL': ['343'],  # New Zealand
        'AF': ['274', '295', '296', '297', '298', '299'],  # Africa (major)
        'SA': ['62', '82', '84', '86'],  # South America (major)
        'CA': ['32', '35', '38', '40', '41', '42', '45'],  # Central America
        'AS': ['203', '232', '252', '255', '257'],  # Asia (major)
        'OC': ['340', '342', '343', '347']  # Oceania
    }
    
    return region_mappings.get(region_code, [])


def enhance_predictions_with_pskreporter(callsign: str, predictions: dict, 
                                        dxcc_data: dict) -> dict:
    """
    Enhance predictions with real PSKreporter data
    Returns enhanced prediction data with validation status
    """
    
    if not PSK_AVAILABLE:
        return {
            'enhanced': False,
            'reason': 'PSKreporter API not available',
            'predictions': predictions
        }
    
    print(f"\nFetching PSKreporter data for {callsign}...")
    
    psk = PSKReporterAPI(callsign)
    
    # Get recent activity
    coverage = psk.analyze_coverage(minutes=60)
    band_activity = psk.get_band_activity(minutes=60)
    
    print(f"  Found {coverage['total_spots']} spots from {coverage['unique_receivers']} receivers")
    print(f"  Active on: {', '.join([b for b, _ in coverage['bands']])}")
    
    # Map PSKreporter spots to DXCC entities
    dxcc_heard_by = {}  # entity_code -> list of receivers
    
    for band_name, spots in band_activity.items():
        for spot in spots:
            # Try country name first (most accurate)
            entity = None
            if spot.get('receiver_country'):
                entity = get_dxcc_from_country_name(spot['receiver_country'], dxcc_data)
            
            # Fall back to grid square if country name didn't work
            if not entity and spot.get('receiver_grid'):
                entity = get_dxcc_from_grid(spot['receiver_grid'], dxcc_data)
            
            if entity:
                if entity not in dxcc_heard_by:
                    dxcc_heard_by[entity] = []
                
                dxcc_heard_by[entity].append({
                    'band': band_name,
                    'receiver': spot['receiver_call'],
                    'grid': spot.get('receiver_grid', 'Unknown'),
                    'country': spot.get('receiver_country', 'Unknown'),
                    'snr': spot['snr'],
                    'time': spot['timestamp']
                })
    
    print(f"  Heard in {len(dxcc_heard_by)} DXCC entities")
    
    # Extract predictions from the actual data structure
    # predictions has: current_conditions.bands.{band}.regions.{region}
    region_predictions = {}
    if 'current_conditions' in predictions and 'bands' in predictions['current_conditions']:
        for band_name, band_data in predictions['current_conditions']['bands'].items():
            if 'regions' in band_data:
                for region_code, region_data in band_data['regions'].items():
                    if region_code not in region_predictions:
                        region_predictions[region_code] = {}
                    
                    # Consider it workable if reliability > 30% and quality is FAIR or better
                    workable = (region_data.get('reliability', 0) > 30 and 
                               region_data.get('quality') in ['FAIR', 'GOOD', 'EXCELLENT'])
                    
                    region_predictions[region_code][band_name] = {
                        'workable': workable,
                        'reliability': region_data.get('reliability', 0),
                        'quality': region_data.get('quality', 'UNKNOWN')
                    }
    
    print(f"  Loaded predictions for {len(region_predictions)} regions")
    
    # Enhance predictions with actual data
    enhanced = {
        'enhanced': True,
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'pskreporter_coverage': coverage,
        'region_validation': {},
        'dxcc_validation': {},
        'predictions': predictions
    }
    
    # Validate by region first
    for region_code, band_predictions in region_predictions.items():
        predicted_bands = [b for b, d in band_predictions.items() if d['workable']]
        
        # Get DXCC entities for this region
        region_entities = map_region_to_dxcc_entities(region_code, dxcc_data)
        
        # Check if any entity in this region was heard
        actual_bands = set()
        for entity_code in region_entities:
            if entity_code in dxcc_heard_by:
                actual_bands.update(r['band'] for r in dxcc_heard_by[entity_code])
        
        validation_status = 'unknown'
        if set(predicted_bands) & actual_bands:
            validation_status = 'confirmed'
        elif actual_bands and not predicted_bands:
            validation_status = 'unexpected'
        elif predicted_bands and not actual_bands:
            validation_status = 'unconfirmed'
        
        enhanced['region_validation'][region_code] = {
            'predicted_bands': predicted_bands,
            'actual_bands': sorted(list(actual_bands)),
            'validation_status': validation_status
        }
    
    # Also track by individual DXCC entity
    for entity_code in dxcc_heard_by:
        actual_bands = set(r['band'] for r in dxcc_heard_by[entity_code])
        enhanced['dxcc_validation'][entity_code] = {
            'entity_name': dxcc_data.get(entity_code, {}).get('name', 'Unknown'),
            'actual_bands': sorted(list(actual_bands)),
            'validation_status': 'unexpected',  # Will update if we find predictions
            'reception_reports': dxcc_heard_by[entity_code]
        }
    
    return enhanced


def generate_enhanced_predictions(callsign: str, log_file: Path, 
                                  tx_lat: float, tx_lon: float):
    """
    Generate enhanced predictions with PSKreporter validation
    """
    
    print("Enhanced HF Propagation Prediction System")
    print("=" * 60)
    print(f"Callsign: {callsign}")
    print(f"Location: {tx_lat:.4f}, {tx_lon:.4f}")
    print()
    
    # Load existing prediction data
    pred_file = Path('propagation_data.json')
    dxcc_file = Path('dxcc_entities.json')
    
    if not pred_file.exists():
        print("Error: propagation_data.json not found")
        print("Run generate_propagation.py first to create predictions")
        return False
    
    if not dxcc_file.exists():
        print("Error: dxcc_entities.json not found")
        print("Run generate_propagation.py first to create DXCC data")
        return False
    
    predictions = load_prediction_data(pred_file)
    dxcc_data = load_dxcc_data(dxcc_file)
    
    # Count regions in the actual data structure
    num_regions = 0
    if 'current_conditions' in predictions and 'bands' in predictions['current_conditions']:
        regions_found = set()
        for band_name, band_data in predictions['current_conditions']['bands'].items():
            if 'regions' in band_data:
                regions_found.update(band_data['regions'].keys())
        num_regions = len(regions_found)
    
    print("Loading ITU-R predictions...")
    print(f"  Predictions for {num_regions} regions")
    print()
    
    # Enhance with PSKreporter data
    enhanced = enhance_predictions_with_pskreporter(callsign, predictions, dxcc_data)
    
    # Save enhanced data
    output_file = Path('enhanced_predictions.json')
    with open(output_file, 'w') as f:
        json.dump(enhanced, f, indent=2)
    
    print()
    print("=" * 60)
    print(f"Enhanced predictions saved to: {output_file}")
    
    # Print validation summary
    if enhanced['enhanced']:
        region_counts = {
            'confirmed': 0,
            'unexpected': 0,
            'unconfirmed': 0
        }
        
        for region_code, validation in enhanced.get('region_validation', {}).items():
            status = validation['validation_status']
            if status in region_counts:
                region_counts[status] += 1
        
        print()
        print("Validation Summary:")
        print(f"  Regions predicted: {len(enhanced.get('region_validation', {}))}")
        print(f"  ✓ Confirmed: {region_counts['confirmed']} regions")
        print(f"  ⚡ Unexpected: {region_counts['unexpected']} regions")
        print(f"  ? Unconfirmed: {region_counts['unconfirmed']} regions")
    return True


if __name__ == '__main__':
    # VE1ATM configuration
    CALLSIGN = "VE1ATM"
    TX_LAT = 44.376
    TX_LON = -64.317
    LOG_FILE = Path('qso_log.adi')
    
    generate_enhanced_predictions(CALLSIGN, LOG_FILE, TX_LAT, TX_LON)
