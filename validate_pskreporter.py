#!/usr/bin/env python3
"""
PSKReporter Real-World Validation for DVOACAP

Validates DVOACAP predictions against actual propagation data from PSKReporter,
providing statistical analysis of prediction accuracy.

This implements Priority 4 (Weeks 7-8) from NEXT_STEPS.md.
"""

import sys
import json
import numpy as np
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
import argparse

# Add project root to path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import DVOACAP
from src.dvoacap.prediction_engine import PredictionEngine
from src.dvoacap.geomagnetic import GeographicPoint as GeoPoint

# Import PSKReporter API (from Dashboard)
dashboard_path = project_root / "Dashboard"
if str(dashboard_path) not in sys.path:
    sys.path.insert(0, str(dashboard_path))

from pskreporter_api import PSKReporterAPI


@dataclass
class ValidationSpot:
    """Single PSKReporter spot with prediction"""
    # PSKReporter data
    receiver_call: str
    receiver_grid: str
    receiver_country: str
    frequency_mhz: float
    actual_snr: int
    mode: str
    timestamp: str

    # Calculated data
    rx_lat: float
    rx_lon: float
    utc_fraction: float

    # Predicted data
    predicted_snr: Optional[float] = None
    predicted_reliability: Optional[float] = None
    predicted_sdbw: Optional[float] = None

    # Error metrics
    snr_error: Optional[float] = None  # predicted - actual
    abs_snr_error: Optional[float] = None


@dataclass
class ValidationStats:
    """Statistical summary of validation results"""
    total_spots: int
    valid_predictions: int
    failed_predictions: int

    # SNR error statistics (dB)
    mean_snr_error: float
    median_snr_error: float
    std_snr_error: float
    rmse_snr: float

    # Absolute error statistics
    mean_abs_error: float
    median_abs_error: float

    # Error percentiles
    snr_error_10th: float
    snr_error_90th: float

    # Accuracy metrics
    within_10db: float  # % of predictions within ±10 dB
    within_15db: float  # % of predictions within ±15 dB
    within_20db: float  # % of predictions within ±20 dB

    # Correlation
    correlation: float

    # Bias detection
    systematic_bias: float  # Average signed error

    # Per-band statistics
    band_stats: Dict[str, Dict] = None

    # Timestamp
    analysis_time: str = ""


class PSKReporterValidator:
    """
    Validates DVOACAP predictions against PSKReporter real-world data
    """

    # HF band definitions
    BANDS = {
        '160m': (1.8, 2.0),
        '80m': (3.5, 4.0),
        '60m': (5.3, 5.4),
        '40m': (7.0, 7.3),
        '30m': (10.1, 10.15),
        '20m': (14.0, 14.35),
        '17m': (18.068, 18.168),
        '15m': (21.0, 21.45),
        '12m': (24.89, 24.99),
        '10m': (28.0, 29.7),
    }

    def __init__(self, callsign: str, tx_lat: float, tx_lon: float):
        """
        Initialize validator

        Args:
            callsign: Your callsign (for PSKReporter lookups)
            tx_lat: Transmitter latitude (degrees)
            tx_lon: Transmitter longitude (degrees)
        """
        self.callsign = callsign
        self.tx_lat = tx_lat
        self.tx_lon = tx_lon

        # Initialize DVOACAP engine
        self.engine = PredictionEngine()
        self.engine.params.tx_location = GeoPoint(
            lat=np.deg2rad(tx_lat),
            lon=np.deg2rad(tx_lon)
        )

        # Initialize PSKReporter API
        self.psk_api = PSKReporterAPI(callsign)

        # Validation data
        self.spots: List[ValidationSpot] = []

    def maidenhead_to_latlon(self, grid: str) -> Tuple[float, float]:
        """
        Convert Maidenhead grid locator to lat/lon

        Args:
            grid: Maidenhead grid (e.g., 'FN20' or 'FN20xq')

        Returns:
            Tuple of (latitude, longitude) in degrees
        """
        grid = grid.upper().strip()

        if len(grid) < 4:
            raise ValueError(f"Grid '{grid}' too short (need at least 4 characters)")

        # Field (first 2 characters): 20° longitude, 10° latitude
        lon = (ord(grid[0]) - ord('A')) * 20 - 180
        lat = (ord(grid[1]) - ord('A')) * 10 - 90

        # Square (next 2 characters): 2° longitude, 1° latitude
        lon += (ord(grid[2]) - ord('0')) * 2
        lat += (ord(grid[3]) - ord('0')) * 1

        # Subsquare (optional): 5' longitude, 2.5' latitude
        if len(grid) >= 6:
            lon += (ord(grid[4]) - ord('A')) * (2.0 / 24.0)
            lat += (ord(grid[5]) - ord('A')) * (1.0 / 24.0)
            # Center of subsquare
            lon += 1.0 / 24.0
            lat += 1.0 / 48.0
        else:
            # Center of square
            lon += 1.0
            lat += 0.5

        return lat, lon

    def frequency_to_band(self, freq_mhz: float) -> str:
        """Convert frequency to band name"""
        for band, (low, high) in self.BANDS.items():
            if low <= freq_mhz <= high:
                return band
        return 'Other'

    def fetch_spots(self, minutes: int = 60, min_snr: int = -30) -> int:
        """
        Fetch recent PSKReporter spots

        Args:
            minutes: How far back to look
            min_snr: Minimum SNR threshold (filter out very weak spots)

        Returns:
            Number of spots fetched
        """
        print(f"Fetching PSKReporter spots for {self.callsign} (last {minutes} minutes)...")

        raw_spots = self.psk_api.get_recent_spots(minutes=minutes)

        if not raw_spots:
            print("No spots found")
            return 0

        print(f"Processing {len(raw_spots)} spots...")

        self.spots = []
        skipped = 0

        for spot in raw_spots:
            # Skip if no SNR data
            if spot['snr'] is None:
                skipped += 1
                continue

            # Skip very weak signals (likely unreliable)
            if spot['snr'] < min_snr:
                skipped += 1
                continue

            # Skip if grid is invalid
            grid = spot['receiver_grid']
            if grid == 'Unknown' or len(grid) < 4:
                skipped += 1
                continue

            # Convert grid to lat/lon
            try:
                rx_lat, rx_lon = self.maidenhead_to_latlon(grid)
            except Exception as e:
                print(f"Warning: Failed to parse grid '{grid}': {e}")
                skipped += 1
                continue

            # Parse timestamp to UTC fraction
            timestamp = datetime.fromisoformat(spot['timestamp'])
            utc_fraction = (timestamp.hour + timestamp.minute / 60.0 + timestamp.second / 3600.0) / 24.0

            # Create validation spot
            validation_spot = ValidationSpot(
                receiver_call=spot['receiver_call'],
                receiver_grid=grid,
                receiver_country=spot['receiver_country'],
                frequency_mhz=spot['frequency_mhz'],
                actual_snr=spot['snr'],
                mode=spot['mode'],
                timestamp=spot['timestamp'],
                rx_lat=rx_lat,
                rx_lon=rx_lon,
                utc_fraction=utc_fraction
            )

            self.spots.append(validation_spot)

        print(f"Fetched {len(self.spots)} valid spots ({skipped} skipped)")
        return len(self.spots)

    def run_predictions(self, verbose: bool = False) -> int:
        """
        Run DVOACAP predictions for all spots

        Args:
            verbose: Print progress for each prediction

        Returns:
            Number of successful predictions
        """
        if not self.spots:
            print("No spots to predict")
            return 0

        print(f"\nRunning DVOACAP predictions for {len(self.spots)} spots...")

        successful = 0
        failed = 0

        for i, spot in enumerate(self.spots):
            if verbose and (i % 10 == 0):
                print(f"  Progress: {i}/{len(self.spots)}")

            try:
                # Set up receiver location
                rx_location = GeoPoint(
                    lat=np.deg2rad(spot.rx_lat),
                    lon=np.deg2rad(spot.rx_lon)
                )

                # Run prediction for this frequency
                self.engine.predict(
                    rx_location=rx_location,
                    utc_time=spot.utc_fraction,
                    frequencies=[spot.frequency_mhz]
                )

                # Extract prediction results
                if self.engine.predictions and len(self.engine.predictions) > 0:
                    pred = self.engine.predictions[0]

                    spot.predicted_snr = pred.signal.snr_db if hasattr(pred.signal, 'snr_db') else None
                    spot.predicted_reliability = pred.reliability if hasattr(pred, 'reliability') else None
                    spot.predicted_sdbw = pred.signal.power_db if hasattr(pred.signal, 'power_db') else None

                    # Calculate error
                    if spot.predicted_snr is not None:
                        spot.snr_error = spot.predicted_snr - spot.actual_snr
                        spot.abs_snr_error = abs(spot.snr_error)
                        successful += 1
                    else:
                        failed += 1
                else:
                    failed += 1

            except Exception as e:
                if verbose:
                    print(f"  Warning: Prediction failed for {spot.receiver_call}: {e}")
                failed += 1

        print(f"Predictions complete: {successful} successful, {failed} failed")
        return successful

    def analyze_results(self) -> ValidationStats:
        """
        Compute statistical analysis of validation results

        Returns:
            ValidationStats object with comprehensive statistics
        """
        # Filter to spots with valid predictions
        valid_spots = [s for s in self.spots if s.predicted_snr is not None]

        if not valid_spots:
            print("No valid predictions to analyze")
            return ValidationStats(
                total_spots=len(self.spots),
                valid_predictions=0,
                failed_predictions=len(self.spots),
                mean_snr_error=0.0,
                median_snr_error=0.0,
                std_snr_error=0.0,
                rmse_snr=0.0,
                mean_abs_error=0.0,
                median_abs_error=0.0,
                snr_error_10th=0.0,
                snr_error_90th=0.0,
                within_10db=0.0,
                within_15db=0.0,
                within_20db=0.0,
                correlation=0.0,
                systematic_bias=0.0,
                analysis_time=datetime.now(timezone.utc).isoformat()
            )

        # Extract arrays
        errors = np.array([s.snr_error for s in valid_spots])
        abs_errors = np.array([s.abs_snr_error for s in valid_spots])
        actual_snrs = np.array([s.actual_snr for s in valid_spots])
        predicted_snrs = np.array([s.predicted_snr for s in valid_spots])

        # Compute statistics
        mean_error = float(np.mean(errors))
        median_error = float(np.median(errors))
        std_error = float(np.std(errors))
        rmse = float(np.sqrt(np.mean(errors ** 2)))

        mean_abs = float(np.mean(abs_errors))
        median_abs = float(np.median(abs_errors))

        error_10th = float(np.percentile(errors, 10))
        error_90th = float(np.percentile(errors, 90))

        # Accuracy thresholds
        within_10 = float(100.0 * np.sum(abs_errors <= 10) / len(abs_errors))
        within_15 = float(100.0 * np.sum(abs_errors <= 15) / len(abs_errors))
        within_20 = float(100.0 * np.sum(abs_errors <= 20) / len(abs_errors))

        # Correlation
        if len(actual_snrs) > 1 and np.std(actual_snrs) > 0 and np.std(predicted_snrs) > 0:
            correlation = float(np.corrcoef(actual_snrs, predicted_snrs)[0, 1])
        else:
            correlation = 0.0

        # Per-band analysis
        band_stats = {}
        for band_name in self.BANDS.keys():
            band_spots = [s for s in valid_spots if self.frequency_to_band(s.frequency_mhz) == band_name]
            if band_spots:
                band_errors = np.array([s.snr_error for s in band_spots])
                band_abs_errors = np.array([s.abs_snr_error for s in band_spots])
                band_stats[band_name] = {
                    'count': len(band_spots),
                    'mean_error': float(np.mean(band_errors)),
                    'median_error': float(np.median(band_errors)),
                    'rmse': float(np.sqrt(np.mean(band_errors ** 2))),
                    'mean_abs_error': float(np.mean(band_abs_errors)),
                    'within_15db': float(100.0 * np.sum(band_abs_errors <= 15) / len(band_abs_errors))
                }

        stats = ValidationStats(
            total_spots=len(self.spots),
            valid_predictions=len(valid_spots),
            failed_predictions=len(self.spots) - len(valid_spots),
            mean_snr_error=mean_error,
            median_snr_error=median_error,
            std_snr_error=std_error,
            rmse_snr=rmse,
            mean_abs_error=mean_abs,
            median_abs_error=median_abs,
            snr_error_10th=error_10th,
            snr_error_90th=error_90th,
            within_10db=within_10,
            within_15db=within_15,
            within_20db=within_20,
            correlation=correlation,
            systematic_bias=mean_error,
            band_stats=band_stats,
            analysis_time=datetime.now(timezone.utc).isoformat()
        )

        return stats

    def print_summary(self, stats: ValidationStats):
        """Print human-readable summary of validation results"""
        print("\n" + "=" * 70)
        print("PSKReporter Validation Summary")
        print("=" * 70)
        print(f"Callsign: {self.callsign}")
        print(f"TX Location: {self.tx_lat:.2f}°, {self.tx_lon:.2f}°")
        print(f"Analysis Time: {stats.analysis_time}")
        print()

        print(f"Total Spots: {stats.total_spots}")
        print(f"Valid Predictions: {stats.valid_predictions}")
        print(f"Failed Predictions: {stats.failed_predictions}")
        print()

        print("SNR Error Statistics (Predicted - Actual):")
        print(f"  Mean Error:       {stats.mean_snr_error:+7.2f} dB")
        print(f"  Median Error:     {stats.median_snr_error:+7.2f} dB")
        print(f"  Std Deviation:     {stats.std_snr_error:7.2f} dB")
        print(f"  RMSE:              {stats.rmse_snr:7.2f} dB")
        print(f"  10th Percentile:  {stats.snr_error_10th:+7.2f} dB")
        print(f"  90th Percentile:  {stats.snr_error_90th:+7.2f} dB")
        print()

        print("Absolute Error Statistics:")
        print(f"  Mean Absolute Error:   {stats.mean_abs_error:7.2f} dB")
        print(f"  Median Absolute Error: {stats.median_abs_error:7.2f} dB")
        print()

        print("Prediction Accuracy:")
        print(f"  Within ±10 dB:  {stats.within_10db:5.1f}%")
        print(f"  Within ±15 dB:  {stats.within_15db:5.1f}%")
        print(f"  Within ±20 dB:  {stats.within_20db:5.1f}%")
        print()

        print(f"Correlation Coefficient: {stats.correlation:+.3f}")
        print()

        if stats.systematic_bias > 5:
            print(f"⚠️  Systematic Bias Detected: {stats.systematic_bias:+.1f} dB (predictions too high)")
        elif stats.systematic_bias < -5:
            print(f"⚠️  Systematic Bias Detected: {stats.systematic_bias:+.1f} dB (predictions too low)")
        else:
            print(f"✓  No significant systematic bias ({stats.systematic_bias:+.1f} dB)")
        print()

        # Per-band statistics
        if stats.band_stats:
            print("Per-Band Analysis:")
            print(f"{'Band':<6} {'Spots':<6} {'Mean Err':<10} {'RMSE':<10} {'Within ±15dB':<12}")
            print("-" * 50)
            for band in ['160m', '80m', '40m', '30m', '20m', '17m', '15m', '12m', '10m']:
                if band in stats.band_stats:
                    bs = stats.band_stats[band]
                    print(f"{band:<6} {bs['count']:<6} {bs['mean_error']:+7.2f} dB  "
                          f"{bs['rmse']:7.2f} dB  {bs['within_15db']:5.1f}%")

        print("=" * 70)

    def save_results(self, output_file: Path, stats: ValidationStats):
        """Save detailed results to JSON"""
        output = {
            'metadata': {
                'callsign': self.callsign,
                'tx_location': {'lat': self.tx_lat, 'lon': self.tx_lon},
                'analysis_time': stats.analysis_time,
                'dvoacap_version': '0.5.0'
            },
            'statistics': asdict(stats),
            'spots': [asdict(spot) for spot in self.spots if spot.predicted_snr is not None]
        }

        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"\nDetailed results saved to: {output_file}")


def main():
    """Main validation workflow"""
    parser = argparse.ArgumentParser(
        description='Validate DVOACAP predictions against PSKReporter real-world data'
    )
    parser.add_argument('--callsign', default='VE1ATM',
                       help='Your callsign (default: VE1ATM)')
    parser.add_argument('--tx-lat', type=float, default=44.65,
                       help='Transmitter latitude in degrees (default: 44.65)')
    parser.add_argument('--tx-lon', type=float, default=-63.59,
                       help='Transmitter longitude in degrees (default: -63.59)')
    parser.add_argument('--minutes', type=int, default=60,
                       help='How many minutes of PSKReporter data to fetch (default: 60)')
    parser.add_argument('--min-snr', type=int, default=-20,
                       help='Minimum SNR threshold in dB (default: -20)')
    parser.add_argument('--output', type=Path, default=Path('pskreporter_validation_results.json'),
                       help='Output JSON file (default: pskreporter_validation_results.json)')
    parser.add_argument('--verbose', action='store_true',
                       help='Print verbose output')

    args = parser.parse_args()

    print("=" * 70)
    print("DVOACAP PSKReporter Validation")
    print("Priority 4 (Weeks 7-8): Real-World Validation")
    print("=" * 70)
    print()

    # Initialize validator
    validator = PSKReporterValidator(
        callsign=args.callsign,
        tx_lat=args.tx_lat,
        tx_lon=args.tx_lon
    )

    # Fetch spots
    spot_count = validator.fetch_spots(minutes=args.minutes, min_snr=args.min_snr)

    if spot_count == 0:
        print("\nNo spots available for validation.")
        print("Try increasing --minutes or lowering --min-snr")
        return 1

    # Run predictions
    pred_count = validator.run_predictions(verbose=args.verbose)

    if pred_count == 0:
        print("\nNo successful predictions.")
        return 1

    # Analyze results
    stats = validator.analyze_results()

    # Print summary
    validator.print_summary(stats)

    # Save results
    validator.save_results(args.output, stats)

    # Assessment against targets from NEXT_STEPS.md
    print("\n" + "=" * 70)
    print("Assessment Against NEXT_STEPS.md Targets:")
    print("=" * 70)

    target_median_error = 15.0  # dB
    target_correlation = 0.5

    if stats.median_abs_error <= target_median_error:
        print(f"✓ Median SNR error: {stats.median_abs_error:.1f} dB (target: <{target_median_error} dB)")
    else:
        print(f"✗ Median SNR error: {stats.median_abs_error:.1f} dB (target: <{target_median_error} dB)")

    if stats.correlation >= target_correlation:
        print(f"✓ Correlation: {stats.correlation:.3f} (target: >{target_correlation})")
    else:
        print(f"✗ Correlation: {stats.correlation:.3f} (target: >{target_correlation})")

    print("=" * 70)

    return 0


if __name__ == '__main__':
    sys.exit(main())
