#!/usr/bin/env python3
"""
Enhanced HF Propagation Prediction Generator
Supports both ITU-R (fast) and VOACAP (accurate via proppy.net) modes
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime, timezone

# Import base generator
sys.path.insert(0, str(Path(__file__).parent))

try:
    from proppy_net_api import ProppyNetAPI
    VOACAP_AVAILABLE = True
except ImportError:
    VOACAP_AVAILABLE = False
    print("Note: proppy_net_api.py not found - VOACAP mode unavailable")

# Use existing generate_propagation for ITU-R predictions
try:
    # Load the existing generator functions
    exec(open('/mnt/project/generate_propagation.py').read())
except Exception as e:
    print(f"Error loading base prediction generator: {e}")
    sys.exit(1)


def enhance_with_voacap(predictions: dict, use_voacap: bool = False) -> dict:
    """
    Enhance ITU-R predictions with VOACAP data from proppy.net
    
    Args:
        predictions: Existing ITU-R predictions
        use_voacap: If True, fetch VOACAP predictions
        
    Returns:
        Enhanced predictions with both ITU-R and VOACAP data
    """
    
    if not use_voacap or not VOACAP_AVAILABLE:
        predictions['mode'] = 'ITU-R'
        predictions['voacap_available'] = VOACAP_AVAILABLE
        return predictions
    
    print("\n" + "=" * 60)
    print("VOACAP ACCURATE MODE via proppy.net")
    print("=" * 60)
    print("This will take 30-60 seconds...")
    print("Fetching professional-grade predictions from proppy.net")
    print()
    
    # Initialize proppy.net API
    station = predictions['current_conditions']['station']
    solar = predictions['current_conditions']['solar']
    
    api = ProppyNetAPI(
        tx_lat=station['lat'],
        tx_lon=station['lon'],
        tx_power=100  # 100W
    )
    
    # Get VOACAP predictions for each region
    for band_name, band_data in predictions['current_conditions']['bands'].items():
        freq_mhz = band_data['frequency']
        
        print(f"\n{band_name} ({freq_mhz} MHz):")
        
        for region_code, region_data in band_data['regions'].items():
            region_name = region_data['name']
            
            # Get target location (approximate region center)
            target_regions = {
                'EU': (50.0, 10.0),   # Central Europe
                'UK': (54.0, -2.0),   # UK center
                'JA': (36.0, 138.0),  # Japan
                'VK': (-25.0, 135.0), # Australia
                'ZL': (-41.0, 174.0), # New Zealand
                'AF': (0.0, 20.0),    # Central Africa
                'SA': (-15.0, -60.0), # South America
                'CA': (15.0, -85.0),  # Central America
                'AS': (30.0, 100.0),  # Asia
                'OC': (-10.0, 155.0)  # Oceania
            }
            
            if region_code not in target_regions:
                continue
            
            rx_lat, rx_lon = target_regions[region_code]
            
            # Get VOACAP prediction
            voacap = api.get_prediction(
                rx_lat=rx_lat,
                rx_lon=rx_lon,
                freq_mhz=freq_mhz,
                hour_utc=datetime.now(timezone.utc).hour,
                month=datetime.now(timezone.utc).month,
                ssn=int(solar['ssn'])
            )
            
            if voacap:
                # Store both ITU-R and VOACAP results
                region_data['itu_r'] = {
                    'reliability': region_data['reliability'],
                    'snr_db': region_data['snr_db'],
                    'quality': region_data['quality']
                }
                
                region_data['voacap'] = {
                    'reliability': voacap['reliability'],
                    'snr_db': voacap['snr_db'],
                    'quality': voacap['quality'],
                    'muf': voacap.get('muf', 0)
                }
                
                # Use VOACAP as primary prediction
                region_data['reliability'] = voacap['reliability']
                region_data['snr_db'] = voacap['snr_db']
                region_data['quality'] = voacap['quality']
                region_data['prediction_source'] = 'VOACAP'
                
                # Show comparison
                itu_rel = region_data['itu_r']['reliability']
                voa_rel = voacap['reliability']
                diff = voa_rel - itu_rel
                
                agree = "✓" if abs(diff) < 10 else "⚠"
                print(f"  {region_code:3s}: ITU-R {itu_rel:3d}% | VOACAP {voa_rel:3d}% | Δ{diff:+3d}% {agree}")
            else:
                region_data['prediction_source'] = 'ITU-R'
                print(f"  {region_code:3s}: VOACAP unavailable, using ITU-R")
    
    predictions['mode'] = 'VOACAP'
    predictions['voacap_available'] = True
    predictions['voacap_service'] = 'proppy.net'
    
    print()
    print("=" * 60)
    print("VOACAP predictions complete!")
    print("=" * 60)
    
    return predictions


def main():
    """Main entry point with argument parsing"""
    
    parser = argparse.ArgumentParser(
        description='VE1ATM HF Propagation Prediction Generator'
    )
    parser.add_argument(
        '--voacap',
        action='store_true',
        help='Use VOACAP accurate mode via proppy.net (slower but more accurate)'
    )
    
    args = parser.parse_args()
    
    # Generate base ITU-R predictions
    print("=== VE1ATM HF Propagation Prediction Generator ===")
    
    if args.voacap:
        print("Mode: VOACAP Accurate (via proppy.net)")
        if not VOACAP_AVAILABLE:
            print("\nError: proppy_net_api.py not found!")
            print("Make sure proppy_net_api.py is in the same directory.")
            sys.exit(1)
    else:
        print("Mode: ITU-R Quick (use --voacap for accurate mode)")
    
    print()
    
    # Fetch solar data
    solar_data = fetch_solar_data()
    print("Fetching current solar-terrestrial data...")
    print(f"  Solar Flux (SFI): {solar_data['sfi']}")
    print(f"  Sunspot Number: {solar_data['ssn']}")
    print(f"  Kp Index: {solar_data['kp']}")
    print(f"  A Index: {solar_data['a_index']}")
    
    # Generate ITU-R predictions
    print("Generating band condition predictions...")
    predictions = predict_band_conditions(solar_data)
    
    # Generate 72-hour timeline
    print("Generating 72-hour timeline...")
    timeline = generate_timeline(solar_data)
    predictions['timeline'] = timeline
    
    # Load DXCC data if available
    print("Loading DXCC tracking data...")
    dxcc_data = load_dxcc_data()
    if dxcc_data:
        predictions['dxcc'] = dxcc_data
    
    # Enhance with VOACAP if requested
    if args.voacap:
        predictions = enhance_with_voacap(predictions, use_voacap=True)
    else:
        predictions = enhance_with_voacap(predictions, use_voacap=False)
    
    # Save predictions
    output_file = Path('propagation_data.json')
    with open(output_file, 'w') as f:
        json.dump(predictions, f, indent=2)
    
    print(f"✓ Predictions generated and saved to: {output_file.absolute()}")
    
    # Print summary
    print("\n=== CURRENT BAND CONDITIONS SUMMARY ===")
    for band_name, band_data in predictions['current_conditions']['bands'].items():
        freq = band_data['frequency']
        regions = band_data['regions']
        
        # Find workable regions
        good_regions = []
        fair_regions = []
        
        for region_code, region_data in regions.items():
            if region_data['quality'] == 'GOOD':
                good_regions.append(f"{region_code} ({region_data['reliability']}%)")
            elif region_data['quality'] == 'FAIR':
                fair_regions.append(f"{region_code} ({region_data['reliability']}%)")
        
        print(f"{band_name} ({freq} MHz):")
        if good_regions:
            print(f"  GOOD: {', '.join(good_regions)}")
        if fair_regions:
            print(f"  FAIR: {', '.join(fair_regions)}")
        if not good_regions and not fair_regions:
            print(f"  No good paths currently")


if __name__ == '__main__':
    main()
