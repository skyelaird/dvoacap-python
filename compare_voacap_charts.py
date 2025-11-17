#!/usr/bin/env python3
"""Compare DVOACAP output to VOACAP reference charts
VOACAP scenario: FN74ui (44.35N, 64.29W), Nov. 1800 UTC, SSN 81, 14.100 MHz, 80W
"""

import sys
sys.path.insert(0, 'src')

import numpy as np
from dvoacap.prediction_engine import PredictionEngine
from dvoacap.path_geometry import GeoPoint

# VOACAP chart parameters
# FN74ui is 44.35N, 64.29W
tx_location = GeoPoint.from_degrees(44.35, -64.29)

# Test points at various distances/directions
# Near: 500 km, Medium: 1500 km, Far: 3000 km, Very Far: 5000 km
test_points = [
    ("Near NE", GeoPoint.from_degrees(49.0, -60.0)),      # ~500 km NE
    ("Medium N", GeoPoint.from_degrees(57.0, -64.0)),     # ~1400 km N
    ("Medium W", GeoPoint.from_degrees(44.0, -78.0)),     # ~1200 km W
    ("Far SE", GeoPoint.from_degrees(35.0, -45.0)),       # ~2000 km SE
    ("Far W", GeoPoint.from_degrees(44.0, -95.0)),        # ~2600 km W (to Great Lakes)
    ("Very Far E", GeoPoint.from_degrees(44.0, -10.0)),   # ~4500 km E (to Europe)
]

# Setup engine
engine = PredictionEngine()
engine.params.ssn = 81.0          # SSN from chart
engine.params.month = 11          # November
engine.params.tx_power = 80.0     # 80W
engine.params.tx_location = tx_location
engine.params.min_angle = np.deg2rad(3.0)
engine.params.required_snr = 10.0 # 10 dB SNR for SSB (VOACAP uses 73 for validation, but 10 is realistic)

# Time: 1800 UTC = 18/24 = 0.75
utc_time = 18.0 / 24.0
freq = 14.10  # MHz

print("=" * 80)
print("DVOACAP vs VOACAP Reference Chart Comparison")
print("=" * 80)
lat_deg, lon_deg = tx_location.to_degrees()
print(f"TX Location: FN74ui ({lat_deg:.2f}°N, {abs(lon_deg):.2f}°W)")
print(f"Frequency: {freq} MHz")
print(f"Time: 1800 UTC (November)")
print(f"SSN: {engine.params.ssn}")
print(f"TX Power: {engine.params.tx_power} W")
print("=" * 80)
print()

print(f"{'Location':<15} {'Distance':<10} {'SNR':<8} {'Rel%':<8} {'MUFday':<10} {'Loss':<8} {'Notes'}")
print("-" * 85)

for name, rx_loc in test_points:
    # Calculate distance using path geometry
    from dvoacap.path_geometry import PathGeometry
    path = PathGeometry()
    path.set_tx_rx(tx_location, rx_loc)
    distance_km = path.get_distance_km()

    # Run prediction
    try:
        engine.predict(rx_location=rx_loc, utc_time=utc_time, frequencies=[freq])

        if len(engine.predictions) > 0:
            pred = engine.predictions[0]

            # Get metrics from best mode
            best_snr = pred.signal.snr_db
            best_rel = pred.signal.reliability * 100
            best_muf = pred.signal.muf_day
            best_loss = pred.signal.total_loss_db

            # Interpret results
            notes = []
            if best_rel > 90:
                notes.append("Excellent")
            elif best_rel > 70:
                notes.append("Good")
            elif best_rel > 50:
                notes.append("Fair")
            elif best_rel > 10:
                notes.append("Poor")
            else:
                notes.append("Unlikely")

            if best_snr > 30:
                notes.append("S9+")
            elif best_snr > 10:
                notes.append("S7-S9")
            elif best_snr > 0:
                notes.append("S5-S7")
            elif best_snr > -10:
                notes.append("Weak")
            else:
                notes.append("Very weak")

            print(f"{name:<15} {distance_km:>7.0f} km {best_snr:>6.1f} dB {best_rel:>6.1f}% {best_muf:>9.6f} {best_loss:>6.1f} dB {', '.join(notes)}")
        else:
            print(f"{name:<15} {distance_km:>7.0f} km  No propagation predicted")

    except Exception as e:
        print(f"{name:<15} {distance_km:>7.0f} km  Error: {str(e)[:30]}")

print()
print("=" * 80)
print("INTERPRETATION vs VOACAP Charts:")
print("=" * 80)
print()
print("VOACAP REL Chart shows:")
print("  - Center (TX location): ~100% reliability")
print("  - 500-1000 km: 70-90% reliability (yellow/green)")
print("  - 1000-2000 km: 40-60% reliability (blue)")
print("  - 2000-3000 km: 20-40% reliability (light blue)")
print("  - >3000 km: 10-30% reliability (very light blue)")
print()
print("VOACAP SDBW Chart shows:")
print("  - Center area: S6-S8 signals (54-57 dB)")
print("  - North America: S3-S6 signals")
print("  - Transatlantic to Europe: S1-S3 signals (51-53 dB)")
print()

# Now run the debug script for high frequency issue
print()
print("=" * 80)
print("HIGH FREQUENCY ISSUE (25.90 MHz)")
print("=" * 80)
print()
print("Running comparison for known problem frequency...")
print()
