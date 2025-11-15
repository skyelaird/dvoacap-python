#!/usr/bin/env python3
"""
VE1ATM HF Propagation Prediction Generator
Uses DVOACAP-Python prediction engine for accurate HF band forecasts

This script generates 24-hour propagation predictions for VE1ATM's station
to major DX regions worldwide, using the complete DVOACAP prediction engine.
"""

import json
import sys
import numpy as np
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Tuple


# Custom JSON encoder to handle numpy types
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NumpyEncoder, self).default(obj)

# Add parent directory to path to import dvoacap
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from src.dvoacap.path_geometry import GeoPoint
    from src.dvoacap.prediction_engine import PredictionEngine
    from src.dvoacap.space_weather_sources import MultiSourceSpaceWeatherFetcher
    import requests
except ImportError as e:
    print(f"Error: Could not import DVOACAP modules: {e}")
    print("Make sure you're running from the dvoacap-python directory")
    sys.exit(1)


# =============================================================================
# VE1ATM Station Configuration
# =============================================================================

MY_QTH = {
    'call': 'VE1ATM',
    'lat': 44.374,  # FN74ui - Lunenburg, Nova Scotia
    'lon': -64.300,
    'grid': 'FN74ui',
    'antenna': 'DX Commander 7m Vertical',
    'location': GeoPoint.from_degrees(44.374, -64.300)
}

# HF Amateur bands (center frequencies in MHz)
BANDS = {
    '40m': 7.150,
    '30m': 10.125,
    '20m': 14.150,
    '17m': 18.118,
    '15m': 21.200,
    '12m': 24.940,
    '10m': 28.500
}

# Target DX regions
TARGET_REGIONS = {
    'EU': {'name': 'Europe', 'location': GeoPoint.from_degrees(50.0, 10.0)},
    'UK': {'name': 'United Kingdom', 'location': GeoPoint.from_degrees(54.0, -2.0)},
    'JA': {'name': 'Japan', 'location': GeoPoint.from_degrees(36.0, 138.0)},
    'VK': {'name': 'Australia', 'location': GeoPoint.from_degrees(-25.0, 135.0)},
    'ZL': {'name': 'New Zealand', 'location': GeoPoint.from_degrees(-41.0, 174.0)},
    'AF': {'name': 'Africa', 'location': GeoPoint.from_degrees(0.0, 20.0)},
    'SA': {'name': 'South America', 'location': GeoPoint.from_degrees(-15.0, -55.0)},
    'CA': {'name': 'Central America', 'location': GeoPoint.from_degrees(15.0, -90.0)},
    'AS': {'name': 'Asia', 'location': GeoPoint.from_degrees(30.0, 100.0)},
    'OC': {'name': 'Oceania', 'location': GeoPoint.from_degrees(-10.0, 150.0)},
}


# =============================================================================
# Solar Data Fetching
# =============================================================================

def fetch_solar_conditions() -> Dict:
    """
    Fetch current solar-terrestrial conditions from multiple international sources
    Returns dict with SFI, SSN, Kp, A-index

    Data sources (with automatic fallback):
    - Solar Flux Index (F10.7): NOAA SWPC, LISIRD, Space Weather Canada
    - Sunspot Number: SIDC/SILSO (Belgium), NOAA SWPC
    - Kp Index: GFZ Potsdam (Germany), NOAA SWPC
    - A Index: GFZ Potsdam (Germany), NOAA SWPC

    This function uses the MultiSourceSpaceWeatherFetcher which automatically
    tries multiple sources and falls back if primary sources are unavailable.
    """
    print("\n" + "=" * 70)
    print("Fetching Space Weather Data from International Sources")
    print("=" * 70)

    # Use the multi-source fetcher for increased reliability
    fetcher = MultiSourceSpaceWeatherFetcher(timeout=10, verbose=True)

    # Fetch data in legacy format for backward compatibility
    solar_data = fetcher.fetch_all_legacy_format()

    print()
    print(f"[OK] Solar conditions: SFI={solar_data['sfi']:.0f}, SSN={solar_data['ssn']:.0f}, "
          f"Kp={solar_data['kp']:.1f}, A={solar_data['a_index']:.1f}")
    print(f"     Overall source: {solar_data['source']}")
    print(f"     Detailed sources:")
    for param, source in solar_data.get('sources_detail', {}).items():
        print(f"       {param.upper()}: {source}")

    if solar_data.get('errors'):
        print(f"     Note: Some sources failed, see above for details")

    print("=" * 70)

    return solar_data


# =============================================================================
# Prediction Generation
# =============================================================================

def generate_prediction(
    engine: PredictionEngine,
    region_code: str,
    region_info: Dict,
    utc_hour: int,
    frequencies: List[float]
) -> Dict:
    """
    Generate propagation prediction for a specific region at a specific hour

    Returns dict with band-by-band predictions
    """
    utc_fraction = utc_hour / 24.0

    try:
        # Run prediction
        engine.predict(
            rx_location=region_info['location'],
            utc_time=utc_fraction,
            frequencies=frequencies
        )

        # Extract predictions for each band
        band_predictions = {}
        for band_name, freq in BANDS.items():
            # Find the prediction for this frequency
            pred_idx = None
            for i, f in enumerate(frequencies):
                if abs(f - freq) < 0.1:  # Match within 100 kHz
                    pred_idx = i
                    break

            if pred_idx is not None and pred_idx < len(engine.predictions):
                pred = engine.predictions[pred_idx]

                # Determine status based on reliability and SNR
                reliability = pred.signal.reliability * 100
                snr = pred.signal.snr_db

                if reliability >= 60 and snr >= 10:
                    status = 'GOOD'
                elif reliability >= 30 or snr >= 3:
                    status = 'FAIR'
                elif reliability > 0:
                    status = 'POOR'
                else:
                    status = 'CLOSED'

                band_predictions[band_name] = {
                    'status': status,
                    'reliability': round(reliability, 1),
                    'snr': round(snr, 1),
                    'mode': pred.get_mode_name(engine.path.dist),
                    'hops': pred.hop_count,
                    'elevation': round(np.rad2deg(pred.tx_elevation), 1),
                    # Enhanced data for prop charts
                    'muf_day': round(pred.signal.muf_day * 100, 1),  # MUF probability as %
                    'signal_dbw': round(pred.signal.power_dbw, 1),   # Median signal power
                    'signal_10': round(pred.signal.power10, 1),      # Lower decile (weak)
                    'signal_90': round(pred.signal.power90, 1),      # Upper decile (strong)
                    'snr_10': round(pred.signal.snr10, 1),           # Lower decile SNR
                    'snr_90': round(pred.signal.snr90, 1),           # Upper decile SNR
                }
            else:
                # No prediction available
                band_predictions[band_name] = {
                    'status': 'CLOSED',
                    'reliability': 0,
                    'snr': -999,
                    'mode': 'N/A',
                    'hops': 0,
                    'elevation': 0,
                    'muf_day': 0,
                    'signal_dbw': -999,
                    'signal_10': -999,
                    'signal_90': -999,
                    'snr_10': -999,
                    'snr_90': -999,
                }

        # Calculate path info
        distance_km = engine.path.dist * 6370
        azimuth_deg = np.rad2deg(engine.path.azim_tr)

        return {
            'region': region_code,
            'region_name': region_info['name'],
            'utc_hour': utc_hour,
            'distance_km': round(distance_km, 0),
            'azimuth': round(azimuth_deg, 1),
            'muf': round(engine.circuit_muf.muf, 2) if engine.circuit_muf else 0,
            'bands': band_predictions
        }

    except Exception as e:
        print(f"  [WARNING] Error predicting {region_code} at {utc_hour:02d}00 UTC: {e}")
        # Return empty prediction with all enhanced fields
        return {
            'region': region_code,
            'region_name': region_info['name'],
            'utc_hour': utc_hour,
            'distance_km': 0,
            'azimuth': 0,
            'muf': 0,
            'bands': {band: {'status': 'ERROR', 'reliability': 0, 'snr': -999,
                            'mode': 'N/A', 'hops': 0, 'elevation': 0,
                            'muf_day': 0, 'signal_dbw': -999, 'signal_10': -999,
                            'signal_90': -999, 'snr_10': -999, 'snr_90': -999}
                     for band in BANDS.keys()}
        }


def generate_24hour_forecast() -> Dict:
    """
    Generate complete 24-hour propagation forecast for all regions
    """
    print("=" * 80)
    print("VE1ATM HF Propagation Prediction Generator")
    print("Using DVOACAP-Python Full Prediction Engine")
    print("=" * 80)
    print()

    # Get solar conditions
    solar = fetch_solar_conditions()

    # Initialize prediction engine
    print("\n[OK] Initializing DVOACAP prediction engine...")
    engine = PredictionEngine()

    # Configure engine
    now = datetime.now(timezone.utc)
    engine.params.ssn = solar['ssn']
    engine.params.month = now.month
    engine.params.tx_power = 100.0  # 100W
    engine.params.tx_location = MY_QTH['location']
    engine.params.min_angle = np.deg2rad(3.0)  # 3° minimum takeoff angle
    engine.params.required_snr = 10.0  # 10 dB SNR for good copy
    engine.params.required_reliability = 0.9

    print(f"[OK] Configuration: Month={now.month}, SSN={solar['ssn']:.0f}, TX Power=100W")

    # Generate predictions
    frequencies = list(BANDS.values())
    all_predictions = []

    # Generate hourly predictions for detailed prop charts (v1.0 enhancement)
    utc_hours = range(0, 24, 1)  # Changed from 2-hour to 1-hour intervals

    print(f"\n[OK] Generating predictions for {len(TARGET_REGIONS)} regions, {len(utc_hours)} time points...")
    print()

    for utc_hour in utc_hours:
        print(f"  Processing {utc_hour:02d}00 UTC...", end=' ')
        hour_count = 0

        for region_code, region_info in TARGET_REGIONS.items():
            pred = generate_prediction(engine, region_code, region_info, utc_hour, frequencies)
            all_predictions.append(pred)
            hour_count += 1

        print(f"[OK] {hour_count} regions")

    # Build output structure
    # Create JSON-safe station info (exclude GeoPoint object)
    station_info = {k: v for k, v in MY_QTH.items() if k != 'location'}

    output = {
        'generated': datetime.now(timezone.utc).isoformat(),
        'station': station_info,
        'solar_conditions': solar,
        'bands': list(BANDS.keys()),
        'regions': {code: info['name'] for code, info in TARGET_REGIONS.items()},
        'predictions': all_predictions
    }

    return output


# =============================================================================
# Main
# =============================================================================

def main():
    """Main entry point"""

    # Generate predictions
    data = generate_24hour_forecast()

    # Save to JSON
    output_file = Path(__file__).parent / 'propagation_data.json'
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2, cls=NumpyEncoder)

    print()
    print("=" * 80)
    print(f"[OK] Predictions saved to: {output_file}")
    print("=" * 80)

    # Transform data to dashboard-compatible format
    print()
    print("[OK] Transforming data for dashboard...")
    try:
        import subprocess
        transform_script = Path(__file__).parent / 'transform_data.py'
        result = subprocess.run(
            [sys.executable, str(transform_script)],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
    except Exception as e:
        print(f"[WARNING] Could not transform data: {e}")
        print("Dashboard may not display correctly without enhanced_predictions.json")

    print()
    print("Summary:")
    print(f"  * Total predictions: {len(data['predictions'])}")
    print(f"  * Regions covered: {len(TARGET_REGIONS)}")
    print(f"  * Bands: {', '.join(BANDS.keys())}")
    print(f"  * Generated: {data['generated']}")
    print()
    print("Next steps:")
    print("  1. Start the server: python3 server.py")
    print("  2. Open http://localhost:8000 in your browser")
    print("  3. View the updated predictions with live refresh capability")
    print()


if __name__ == "__main__":
    main()
