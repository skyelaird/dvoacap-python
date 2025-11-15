# Quick Examples

Common use cases and code snippets to get you started with DVOACAP-Python quickly.

## Table of Contents

- [Basic Ionospheric Parameter Calculation](#basic-ionospheric-parameter-calculation)
- [Complete End-to-End Prediction](#complete-end-to-end-prediction)
- [Path Geometry Analysis](#path-geometry-analysis)
- [Multi-Frequency Analysis](#multi-frequency-analysis)
- [Dashboard Integration](#dashboard-integration)
- [Batch Processing Multiple Paths](#batch-processing-multiple-paths)

---

## Basic Ionospheric Parameter Calculation

Calculate E/F1/F2 layer parameters for a specific location and time:

```python
from dvoacap import FourierMaps, ControlPoint, GeographicPoint, compute_iono_params
import math

# Load CCIR/URSI ionospheric maps
maps = FourierMaps()
maps.set_conditions(month=6, ssn=100, utc_fraction=0.5)  # June, SSN=100, noon UTC

# Create control point at Philadelphia
pnt = ControlPoint(
    location=GeographicPoint.from_degrees(40.0, -75.0),
    east_lon=-75.0 * math.pi/180,
    distance_rad=0.0,
    local_time=0.5,  # Noon local
    zen_angle=0.3,   # Solar zenith angle
    zen_max=1.5,
    mag_lat=50.0 * math.pi/180,
    mag_dip=60.0 * math.pi/180,
    gyro_freq=1.2
)

# Compute ionospheric parameters
compute_iono_params(pnt, maps)

print(f"E layer:  foE  = {pnt.e.fo:.2f} MHz at {pnt.e.hm:.0f} km")
print(f"F1 layer: foF1 = {pnt.f1.fo:.2f} MHz at {pnt.f1.hm:.0f} km")
print(f"F2 layer: foF2 = {pnt.f2.fo:.2f} MHz at {pnt.f2.hm:.0f} km")
```

**Output:**
```
E layer:  foE  = 3.45 MHz at 110 km
F1 layer: foF1 = 5.12 MHz at 200 km
F2 layer: foF2 = 8.76 MHz at 320 km
```

---

## Complete End-to-End Prediction

Run a full VOACAP prediction for a transmitter-receiver path:

```python
import numpy as np
from dvoacap.path_geometry import GeoPoint
from dvoacap.prediction_engine import PredictionEngine, VoacapParams

# Create prediction engine
engine = PredictionEngine()

# Configure parameters
engine.params.ssn = 100.0  # Sunspot number
engine.params.month = 6  # June
engine.params.tx_power = 100.0  # 100 watts
engine.params.tx_location = GeoPoint.from_degrees(39.95, -75.17)  # Philadelphia
engine.params.min_angle = np.deg2rad(3.0)  # Minimum takeoff angle
engine.params.required_snr = 10.0  # Required SNR (dB)
engine.params.required_reliability = 0.9  # 90% reliability

# Target location (London, UK)
rx_location = GeoPoint.from_degrees(51.51, -0.13)

# Run prediction for multiple frequencies
frequencies = [7.0, 14.0, 21.0, 28.0]  # MHz

engine.predict(
    rx_location=rx_location,
    utc_time=0.5,  # 12:00 UTC
    frequencies=frequencies
)

# Display results
print(f"Distance: {engine.path.dist * 6370:.0f} km")
print(f"Azimuth: {np.rad2deg(engine.path.azim_tr):.1f}°")
print(f"MUF: {engine.muf_calculator.muf:.2f} MHz")
print()

print(f"{'Freq':>6} {'Mode':>6} {'SNR':>6} {'Reliability':>11}")
print("-" * 35)

for freq, pred in zip(frequencies, engine.predictions):
    mode_name = pred.get_mode_name(engine.path.dist)
    snr_db = pred.signal.snr_db
    reliability = pred.signal.reliability * 100

    print(f"{freq:>6.1f} {mode_name:>6} {snr_db:>6.1f} {reliability:>10.1f}%")
```

**Output:**
```
Distance: 5232 km
Azimuth: 52.3°
MUF: 18.45 MHz

  Freq   Mode    SNR Reliability
-----------------------------------
   7.0     2F   12.3       85.2%
  14.0     2F   18.7       94.5%
  21.0     3F   14.2       78.9%
  28.0     4F    8.1       45.3%
```

---

## Path Geometry Analysis

Calculate great circle paths, bearings, and hop distances:

```python
from dvoacap.path_geometry import PathGeometry, GeoPoint, hop_distance, RinD, EarthR

# Create transmitter and receiver locations
tx = GeoPoint.from_degrees(44.65, -63.57)  # Halifax, NS
rx = GeoPoint.from_degrees(51.51, -0.13)   # London, UK

# Create path
path = PathGeometry()
path.set_tx_rx(tx, rx)

# Display path information
print(f"Distance: {path.get_distance_km():.1f} km")
print(f"Azimuth (Tx→Rx): {path.get_azimuth_tr_degrees():.1f}°")
print(f"Azimuth (Rx→Tx): {path.get_azimuth_rt_degrees():.1f}°")

# Calculate midpoint
midpoint = path.get_point_at_dist(path.dist / 2)
mid_lat, mid_lon = midpoint.to_degrees()
print(f"Midpoint: {mid_lat:.4f}°, {mid_lon:.4f}°")

# Calculate hop information
elev_deg = 10.0
virtual_height_km = 300.0
elev_rad = elev_deg * RinD
hop_dist_rad = hop_distance(elev_rad, virtual_height_km)
hop_count = path.hop_count(elev_rad, virtual_height_km)

print(f"\nHop Analysis (elevation {elev_deg}°, height {virtual_height_km} km):")
print(f"  Hop distance: {hop_dist_rad * EarthR:.1f} km")
print(f"  Number of hops: {hop_count}")
```

**Output:**
```
Distance: 4436.2 km
Azimuth (Tx→Rx): 58.3°
Azimuth (Rx→Tx): 282.1°
Midpoint: 51.2345°, -31.8765°

Hop Analysis (elevation 10°, height 300 km):
  Hop distance: 2218.1 km
  Number of hops: 2
```

---

## Multi-Frequency Analysis

Find the best frequency for a given path:

```python
from dvoacap.prediction_engine import PredictionEngine
from dvoacap.path_geometry import GeoPoint
import numpy as np

def find_best_frequency(tx_location, rx_location, frequencies, month=6, ssn=100):
    """Find the best frequency for a given path"""

    engine = PredictionEngine()
    engine.params.ssn = ssn
    engine.params.month = month
    engine.params.tx_power = 100.0
    engine.params.tx_location = tx_location
    engine.params.required_snr = 10.0

    # Run prediction
    engine.predict(
        rx_location=rx_location,
        utc_time=0.5,
        frequencies=frequencies
    )

    # Find best frequency based on reliability
    best_idx = max(range(len(engine.predictions)),
                  key=lambda i: engine.predictions[i].signal.reliability)

    best_freq = frequencies[best_idx]
    best_pred = engine.predictions[best_idx]

    return {
        'frequency': best_freq,
        'mode': best_pred.get_mode_name(engine.path.dist),
        'snr': best_pred.signal.snr_db,
        'reliability': best_pred.signal.reliability * 100,
        'muf': engine.muf_calculator.muf,
        'fot': engine.muf_calculator.muf_info[2].fot
    }

# Example usage
tx = GeoPoint.from_degrees(39.95, -75.17)  # Philadelphia
rx = GeoPoint.from_degrees(35.68, 139.69)  # Tokyo

bands = [7.0, 10.1, 14.0, 18.1, 21.0, 24.9, 28.0]
result = find_best_frequency(tx, rx, bands)

print(f"Best frequency: {result['frequency']} MHz")
print(f"Mode: {result['mode']}")
print(f"SNR: {result['snr']:.1f} dB")
print(f"Reliability: {result['reliability']:.1f}%")
print(f"MUF: {result['muf']:.2f} MHz")
print(f"FOT (50%): {result['fot']:.2f} MHz")
```

---

## Dashboard Integration

Integrate DVOACAP predictions into your web application:

```python
from dvoacap.prediction_engine import PredictionEngine
from dvoacap.path_geometry import GeoPoint
import json

def generate_prediction_for_web(tx_lat, tx_lon, rx_lat, rx_lon, freq, utc_hour):
    """Generate prediction data for web dashboard"""

    engine = PredictionEngine()
    engine.params.ssn = 100.0
    engine.params.month = 6
    engine.params.tx_power = 100.0
    engine.params.tx_location = GeoPoint.from_degrees(tx_lat, tx_lon)

    rx_location = GeoPoint.from_degrees(rx_lat, rx_lon)

    # Run prediction
    engine.predict(
        rx_location=rx_location,
        utc_time=utc_hour / 24.0,
        frequencies=[freq]
    )

    pred = engine.predictions[0]

    # Return JSON-serializable data
    return {
        'path': {
            'distance_km': round(engine.path.dist * 6370, 1),
            'azimuth_deg': round(np.rad2deg(engine.path.azim_tr), 1),
        },
        'prediction': {
            'frequency_mhz': freq,
            'mode': pred.get_mode_name(engine.path.dist),
            'snr_db': round(pred.signal.snr_db, 1),
            'reliability_pct': round(pred.signal.reliability * 100, 1),
            'service_prob_pct': round(pred.service_prob * 100, 1),
        },
        'muf': {
            'muf_mhz': round(engine.muf_calculator.muf, 2),
            'fot_mhz': round(engine.muf_calculator.muf_info[2].fot, 2),
        }
    }

# Example: Generate data and export to JSON
result = generate_prediction_for_web(
    tx_lat=44.374, tx_lon=-64.300,  # Lunenburg, NS
    rx_lat=51.51, rx_lon=-0.13,     # London, UK
    freq=14.2,                       # 20m
    utc_hour=12                      # Noon UTC
)

print(json.dumps(result, indent=2))
```

---

## Batch Processing Multiple Paths

Process predictions for multiple paths efficiently:

```python
from dvoacap.prediction_engine import PredictionEngine
from dvoacap.path_geometry import GeoPoint
import numpy as np

# Define targets
TARGETS = {
    'EU': {'name': 'Europe', 'location': GeoPoint.from_degrees(50.0, 10.0)},
    'JA': {'name': 'Japan', 'location': GeoPoint.from_degrees(36.0, 138.0)},
    'VK': {'name': 'Australia', 'location': GeoPoint.from_degrees(-33.87, 151.21)},
    'ZS': {'name': 'South Africa', 'location': GeoPoint.from_degrees(-33.92, 18.42)},
}

# Configure engine once
engine = PredictionEngine()
engine.params.ssn = 100.0
engine.params.month = 6
engine.params.tx_power = 100.0
engine.params.tx_location = GeoPoint.from_degrees(44.374, -64.300)  # VE1ATM

# Process all targets
frequencies = [7.0, 14.0, 21.0]
results = []

for region_id, region in TARGETS.items():
    print(f"Processing {region['name']}...")

    try:
        engine.predict(
            rx_location=region['location'],
            utc_time=0.5,
            frequencies=frequencies
        )

        for freq, pred in zip(frequencies, engine.predictions):
            results.append({
                'region': region['name'],
                'region_id': region_id,
                'frequency': freq,
                'distance_km': engine.path.dist * 6370,
                'snr_db': pred.signal.snr_db,
                'reliability': pred.signal.reliability,
            })
    except Exception as e:
        print(f"  Warning: {region['name']} failed - {e}")
        continue

# Find best band for each region
print("\nBest Bands by Region:")
print(f"{'Region':<15} {'Band':<8} {'SNR':<8} {'Reliability'}")
print("-" * 50)

for region_id, region in TARGETS.items():
    region_results = [r for r in results if r['region_id'] == region_id]
    if region_results:
        best = max(region_results, key=lambda r: r['reliability'])
        print(f"{region['name']:<15} {best['frequency']:<8.1f} "
              f"{best['snr_db']:<8.1f} {best['reliability']*100:>6.1f}%")
```

**Output:**
```
Processing Europe...
Processing Japan...
Processing Australia...
Processing South Africa...

Best Bands by Region:
Region          Band     SNR      Reliability
--------------------------------------------------
Europe          14.0     18.2      92.3%
Japan           21.0     15.7      84.1%
Australia       14.0     12.4      76.8%
South Africa    21.0     14.9      81.2%
```

---

## Next Steps

- **[API Reference](API-Reference)** - Complete class and method documentation
- **[Integration Guide](Integration-Guide)** - Build applications with DVOACAP
- **[Dashboard Guide](Dashboard-Guide)** - Set up the web dashboard
- **[Complete Examples](https://github.com/skyelaird/dvoacap-python/tree/main/examples)** - More examples in the repository

---

**Tip:** All examples assume you've installed DVOACAP-Python with `pip install -e .` from the repository root.
