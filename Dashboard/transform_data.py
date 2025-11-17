#!/usr/bin/env python3
"""
Transform propagation_data.json to the format expected by dashboard.html

This script converts the raw prediction data structure to the enhanced format
that includes current_conditions, timeline_24h, and DXCC tracking.
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def transform_predictions(input_file: Path, output_file: Path, dxcc_file: Path):
    """
    Transform raw prediction data to dashboard-compatible format
    """
    print(f"Loading prediction data from {input_file}...")

    with open(input_file, 'r') as f:
        raw_data = json.load(f)

    # Load DXCC data if available
    dxcc_data = {}
    if dxcc_file.exists():
        print(f"Loading DXCC data from {dxcc_file}...")
        with open(dxcc_file, 'r') as f:
            dxcc_data = json.load(f)

    print("Transforming data structure...")

    # Build current conditions (using UTC hour 0 as baseline)
    current_hour = datetime.now().hour

    # Group predictions by region and hour
    predictions_by_hour = defaultdict(list)
    for pred in raw_data['predictions']:
        predictions_by_hour[pred['utc_hour']].append(pred)

    # Find the closest hour to current time
    available_hours = sorted(predictions_by_hour.keys())
    closest_hour = min(available_hours, key=lambda h: abs(h - current_hour))
    current_preds = predictions_by_hour[closest_hour]

    # Build current conditions bands structure
    current_bands = {}
    for band_name in raw_data['bands']:
        # Get frequency from first prediction
        freq = 0
        if band_name == '160m': freq = 1.900
        elif band_name == '80m': freq = 3.600
        elif band_name == '40m': freq = 7.150
        elif band_name == '30m': freq = 10.125
        elif band_name == '20m': freq = 14.150
        elif band_name == '17m': freq = 18.118
        elif band_name == '15m': freq = 21.200
        elif band_name == '12m': freq = 24.940
        elif band_name == '10m': freq = 28.500

        current_bands[band_name] = {
            'frequency': freq,
            'regions': {}
        }

    # Populate regions for each band
    for pred in current_preds:
        region_code = pred['region']
        region_name = pred['region_name']

        for band_name, band_data in pred['bands'].items():
            if band_data['status'] in ['GOOD', 'FAIR']:
                quality = band_data['status']
            elif band_data['status'] == 'POOR':
                quality = 'POOR'
            else:
                continue  # Skip CLOSED bands

            current_bands[band_name]['regions'][region_code] = {
                'name': region_name,
                'quality': quality,
                'reliability': band_data['reliability'],
                'snr_db': band_data['snr'],
                'distance_km': int(pred['distance_km']),
                'bearing': int(pred['azimuth']),
                'muf': pred['muf']
            }

    # Build timeline structure (24-72 hour forecast)
    timeline_hours = []
    for hour in sorted(predictions_by_hour.keys()):
        hour_data = {
            'time': f"2025-11-13T{hour:02d}:00:00Z",  # Use generated timestamp
            'hour_utc': hour,
            'bands': {}
        }

        # For each band, find which regions are open
        for band_name in raw_data['bands']:
            open_regions = []
            marginal_regions = []

            for pred in predictions_by_hour[hour]:
                band_pred = pred['bands'][band_name]
                if band_pred['status'] == 'GOOD':
                    open_regions.append(pred['region'])
                elif band_pred['status'] == 'FAIR':
                    marginal_regions.append(pred['region'])

            hour_data['bands'][band_name] = {
                'open': open_regions,
                'marginal': marginal_regions
            }

        timeline_hours.append(hour_data)

    # Build propagation charts data (hourly metrics for each band and region)
    prop_charts = {}
    for band_name in raw_data['bands']:
        prop_charts[band_name] = {
            'hours': [],
            'regions': {}
        }

        # For each hour, collect metrics for this band
        for hour in sorted(predictions_by_hour.keys()):
            prop_charts[band_name]['hours'].append(hour)

            # Collect metrics for each region
            for pred in predictions_by_hour[hour]:
                region_code = pred['region']
                region_name = pred['region_name']

                if region_code not in prop_charts[band_name]['regions']:
                    prop_charts[band_name]['regions'][region_code] = {
                        'name': region_name,
                        'reliability': [],
                        'snr': [],
                        'signal_dbw': [],
                        'signal_10': [],
                        'signal_90': [],
                        'muf_day': []
                    }

                band_data = pred['bands'][band_name]
                prop_charts[band_name]['regions'][region_code]['reliability'].append(band_data['reliability'])
                prop_charts[band_name]['regions'][region_code]['snr'].append(band_data['snr'])
                prop_charts[band_name]['regions'][region_code]['signal_dbw'].append(band_data['signal_dbw'])
                prop_charts[band_name]['regions'][region_code]['signal_10'].append(band_data['signal_10'])
                prop_charts[band_name]['regions'][region_code]['signal_90'].append(band_data['signal_90'])
                prop_charts[band_name]['regions'][region_code]['muf_day'].append(band_data['muf_day'])

    # Build the transformed structure
    transformed = {
        'predictions': {
            'current_conditions': {
                'generated': raw_data['generated'],
                'solar': {
                    'sfi': raw_data['solar_conditions']['sfi'],
                    'ssn': raw_data['solar_conditions']['ssn'],
                    'kp': raw_data['solar_conditions']['kp'],
                    'a_index': raw_data['solar_conditions']['a_index']
                },
                'bands': current_bands
            },
            'timeline_24h': {
                'hours': timeline_hours
            },
            'propagation_charts': prop_charts,
            'dxcc': dxcc_data if dxcc_data else {
                'dxcc_worked': [],
                'dxcc_confirmed_lotw': [],
                'dxcc_missing': [],
                'entity_names': {}
            }
        }
    }

    # Write output
    print(f"Writing transformed data to {output_file}...")
    with open(output_file, 'w') as f:
        json.dump(transformed, f, indent=2)

    print("✓ Transformation complete!")
    print(f"  - Bands: {len(current_bands)}")
    print(f"  - Timeline hours: {len(timeline_hours)}")
    print(f"  - Generated: {raw_data['generated']}")


def main():
    """Main entry point"""
    base_dir = Path(__file__).parent

    input_file = base_dir / 'propagation_data.json'
    output_file = base_dir / 'enhanced_predictions.json'
    dxcc_file = base_dir / 'dxcc_summary.json'

    if not input_file.exists():
        print(f"Error: {input_file} not found!")
        print("Run generate_predictions.py first to create the input data.")
        return 1

    transform_predictions(input_file, output_file, dxcc_file)
    return 0


if __name__ == '__main__':
    exit(main())
