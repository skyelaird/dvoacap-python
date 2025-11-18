#!/usr/bin/env python3
"""
Generate VOACAP-style Propagation Maps with Maidenhead Grid

Creates signal strength (SDBW) and reliability (REL) maps for display
on the dashboard, aligned with Maidenhead grid squares.
"""

import sys
import json
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# Add parent directory to import dvoacap
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.dvoacap.path_geometry import GeoPoint
from src.dvoacap.prediction_engine import PredictionEngine
from Dashboard.mode_presets import MODE_PRESETS, apply_mode_preset


def maidenhead_to_latlon(grid: str) -> Tuple[float, float]:
    """
    Convert Maidenhead grid square to latitude/longitude.

    Args:
        grid: Maidenhead grid square (e.g., "FN74ui")

    Returns:
        tuple: (latitude, longitude) in degrees
    """
    grid = grid.upper()

    # Field (first 2 chars)
    lon = (ord(grid[0]) - ord('A')) * 20 - 180
    lat = (ord(grid[1]) - ord('A')) * 10 - 90

    # Square (next 2 digits)
    if len(grid) >= 4:
        lon += int(grid[2]) * 2
        lat += int(grid[3]) * 1

    # Subsquare (next 2 chars)
    if len(grid) >= 6:
        lon += (ord(grid[4]) - ord('A')) * (2/24)
        lat += (ord(grid[5]) - ord('A')) * (1/24)

    # Return center of grid square
    if len(grid) == 6:
        lon += (2/24) / 2
        lat += (1/24) / 2
    elif len(grid) == 4:
        lon += 1
        lat += 0.5
    else:
        lon += 10
        lat += 5

    return lat, lon


def generate_grid_squares(center_lat: float, center_lon: float,
                         range_deg: float = 50.0,
                         resolution: str = 'medium') -> List[Tuple[str, float, float]]:
    """
    Generate a grid of Maidenhead squares around a center point.

    Args:
        center_lat: Center latitude in degrees
        center_lon: Center longitude in degrees
        range_deg: Range in degrees (creates a square area)
        resolution: 'coarse' (field), 'medium' (square), 'fine' (subsquare)

    Returns:
        List of (grid_square, lat, lon) tuples
    """
    grid_squares = []

    # Determine grid size based on resolution
    if resolution == 'coarse':
        # Field level (20° x 10° squares)
        step_lon, step_lat = 10.0, 5.0  # Half-field for center points
    elif resolution == 'fine':
        # Subsquare level (5' x 2.5' squares)
        step_lon, step_lat = 1.0/12, 1.0/24
    else:  # medium (default)
        # Square level (2° x 1° squares)
        step_lon, step_lat = 1.0, 0.5

    # Generate grid points
    lat = center_lat - range_deg
    while lat <= center_lat + range_deg:
        lon = center_lon - range_deg
        while lon <= center_lon + range_deg:
            # Convert to Maidenhead (simplified - returns field for now)
            field_lon = int((lon + 180) / 20)
            field_lat = int((lat + 90) / 10)

            if 0 <= field_lon < 18 and 0 <= field_lat < 18:
                grid = chr(ord('A') + field_lon) + chr(ord('A') + field_lat)

                # Add square digits if medium or fine resolution
                if resolution in ['medium', 'fine']:
                    sq_lon = int(((lon + 180) % 20) / 2)
                    sq_lat = int(((lat + 90) % 10) / 1)
                    grid += str(sq_lon) + str(sq_lat)

                grid_squares.append((grid, lat, lon))

            lon += step_lon
        lat += step_lat

    return grid_squares


def generate_propagation_map(
    tx_lat: float,
    tx_lon: float,
    frequency: float,
    mode: str,
    utc_hour: int,
    month: int,
    ssn: float,
    tx_power: float = 80.0,
    map_range_deg: float = 50.0,
    resolution: str = 'medium'
) -> Dict:
    """
    Generate a propagation map for a given set of parameters.

    Args:
        tx_lat: Transmitter latitude (degrees)
        tx_lon: Transmitter longitude (degrees)
        frequency: Frequency in MHz
        mode: Mode name (WSPR, FT8, CW, SSB, etc.)
        utc_hour: UTC hour (0-23)
        month: Month (1-12)
        ssn: Sunspot number
        tx_power: Transmit power in watts
        map_range_deg: Map range in degrees from TX location
        resolution: Grid resolution ('coarse', 'medium', 'fine')

    Returns:
        dict: Map data with grid squares and predictions
    """
    print(f"\n{'='*80}")
    print(f"Generating Propagation Map")
    print(f"{'='*80}")
    print(f"TX: {tx_lat:.2f}N, {tx_lon:.2f}W")
    print(f"Frequency: {frequency} MHz")
    print(f"Mode: {mode}")
    print(f"Time: Month {month}, {utc_hour:02d}00 UTC")
    print(f"SSN: {ssn}")
    print(f"Power: {tx_power} W")
    print(f"Map Range: ±{map_range_deg}°")
    print(f"Resolution: {resolution}")
    print()

    # Create prediction engine
    engine = PredictionEngine()
    engine.params.tx_location = GeoPoint.from_degrees(tx_lat, tx_lon)
    engine.params.tx_power = tx_power
    engine.params.ssn = ssn
    engine.params.month = month

    # Apply mode preset
    if not apply_mode_preset(engine, mode):
        print(f"Warning: Unknown mode '{mode}', using defaults")

    utc_time = utc_hour / 24.0

    # Generate grid squares
    print("Generating grid squares...")
    grid_squares = generate_grid_squares(tx_lat, tx_lon, map_range_deg, resolution)
    print(f"Grid squares to compute: {len(grid_squares)}")

    # Run predictions for each grid square
    predictions = []
    successful = 0
    failed = 0

    for i, (grid, lat, lon) in enumerate(grid_squares):
        if (i + 1) % 100 == 0:
            print(f"  Progress: {i+1}/{len(grid_squares)} ({(i+1)/len(grid_squares)*100:.1f}%)")

        try:
            rx_location = GeoPoint.from_degrees(lat, lon)
            engine.predict(rx_location=rx_location, utc_time=utc_time, frequencies=[frequency])

            if len(engine.predictions) > 0:
                pred = engine.predictions[0]
                distance_km = engine.path.dist * 6370

                predictions.append({
                    'grid': grid,
                    'lat': lat,
                    'lon': lon,
                    'distance_km': distance_km,
                    'snr_db': pred.signal.snr_db,
                    'reliability': pred.signal.reliability * 100,  # Convert to percentage
                    'signal_dbw': pred.signal.power_dbw,
                    'loss_db': pred.signal.total_loss_db,
                    'mode': pred.get_mode_name(engine.path.dist),
                    'hops': pred.hop_count
                })
                successful += 1
            else:
                failed += 1

        except Exception as e:
            # Skip grid squares where prediction fails
            failed += 1
            if failed <= 5:  # Only print first few errors
                print(f"    Warning: Prediction failed for {grid} ({lat:.1f}, {lon:.1f}): {e}")

    print(f"\nCompleted: {successful} successful, {failed} failed")

    # Compute statistics
    if predictions:
        snr_values = [p['snr_db'] for p in predictions]
        rel_values = [p['reliability'] for p in predictions]

        stats = {
            'snr': {
                'min': min(snr_values),
                'max': max(snr_values),
                'mean': np.mean(snr_values),
                'median': np.median(snr_values)
            },
            'reliability': {
                'min': min(rel_values),
                'max': max(rel_values),
                'mean': np.mean(rel_values),
                'median': np.median(rel_values)
            }
        }
    else:
        stats = None

    # Create map data structure
    map_data = {
        'metadata': {
            'generated': datetime.utcnow().isoformat() + 'Z',
            'tx_location': {
                'lat': tx_lat,
                'lon': tx_lon
            },
            'frequency_mhz': frequency,
            'mode': mode,
            'utc_hour': utc_hour,
            'month': month,
            'ssn': ssn,
            'tx_power': tx_power,
            'bandwidth_hz': engine.params.bandwidth_hz,
            'required_snr': engine.params.required_snr,
            'map_range_deg': map_range_deg,
            'resolution': resolution,
            'grid_count': len(grid_squares),
            'successful_predictions': successful,
            'failed_predictions': failed
        },
        'statistics': stats,
        'predictions': predictions
    }

    return map_data


def main():
    """Generate sample propagation maps for VE1ATM."""

    # VE1ATM station parameters
    TX_LAT = 44.374
    TX_LON = -64.300
    SSN = 77  # Will be replaced by live data in actual use
    MONTH = 11  # November
    POWER = 80  # Watts

    # Generate maps for different bands and modes
    test_configs = [
        {'freq': 14.100, 'mode': 'SSB', 'hour': 18, 'band': '20m'},
        {'freq': 14.074, 'mode': 'FT8', 'hour': 18, 'band': '20m'},
        {'freq': 7.074, 'mode': 'FT8', 'hour': 0, 'band': '40m'},
        {'freq': 21.074, 'mode': 'FT8', 'hour': 18, 'band': '15m'},
    ]

    output_dir = Path(__file__).parent / 'propagation_maps'
    output_dir.mkdir(exist_ok=True)

    for config in test_configs:
        print(f"\n{'#'*80}")
        print(f"# {config['band']} - {config['mode']} @ {config['hour']:02d}00 UTC")
        print(f"{'#'*80}")

        map_data = generate_propagation_map(
            tx_lat=TX_LAT,
            tx_lon=TX_LON,
            frequency=config['freq'],
            mode=config['mode'],
            utc_hour=config['hour'],
            month=MONTH,
            ssn=SSN,
            tx_power=POWER,
            map_range_deg=60.0,  # Larger area for better coverage
            resolution='medium'  # 2° x 1° grid squares
        )

        # Save to JSON
        filename = f"map_{config['band']}_{config['mode']}_{config['hour']:02d}00Z.json"
        output_file = output_dir / filename

        with open(output_file, 'w') as f:
            json.dump(map_data, f, indent=2)

        print(f"\nSaved to: {output_file}")

        if map_data['statistics']:
            print(f"\nStatistics:")
            print(f"  SNR: {map_data['statistics']['snr']['min']:.1f} to "
                  f"{map_data['statistics']['snr']['max']:.1f} dB "
                  f"(mean: {map_data['statistics']['snr']['mean']:.1f} dB)")
            print(f"  Reliability: {map_data['statistics']['reliability']['min']:.1f}% to "
                  f"{map_data['statistics']['reliability']['max']:.1f}% "
                  f"(mean: {map_data['statistics']['reliability']['mean']:.1f}%)")


if __name__ == '__main__':
    main()
