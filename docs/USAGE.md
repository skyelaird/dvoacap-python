# DVOACAP-Python Usage Guide

This guide provides comprehensive examples and patterns for using DVOACAP-Python in your applications.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Core Concepts](#core-concepts)
3. [Basic Usage Patterns](#basic-usage-patterns)
4. [Advanced Usage](#advanced-usage)
5. [API Reference](#api-reference)
6. [Common Use Cases](#common-use-cases)

---

## Quick Start

> **Interactive Dashboard:** If you prefer a web-based interface, check out the [Dashboard](../Dashboard/README.md) which provides a complete visualization system with maps, charts, and DXCC tracking.

### Installation

```bash
git clone https://github.com/skyelaird/dvoacap-python.git
cd dvoacap-python
pip install -e .
```

### Your First Prediction

```python
from dvoacap.prediction_engine import PredictionEngine
from dvoacap.path_geometry import GeoPoint
import numpy as np

# Create prediction engine
engine = PredictionEngine()

# Configure parameters
engine.params.ssn = 100.0  # Sunspot number
engine.params.month = 6  # June
engine.params.tx_power = 100.0  # watts
engine.params.tx_location = GeoPoint.from_degrees(39.95, -75.17)  # Philadelphia

# Run prediction
rx_location = GeoPoint.from_degrees(51.51, -0.13)  # London
engine.predict(rx_location=rx_location, utc_time=0.5, frequencies=[14.0, 21.0, 28.0])

# Get results
for freq, pred in zip([14.0, 21.0, 28.0], engine.predictions):
    print(f"{freq} MHz: SNR={pred.signal.snr_db:.1f} dB, "
          f"Reliability={pred.signal.reliability*100:.1f}%")
```

---

## Core Concepts

### Geographic Points

All locations are represented using `GeoPoint`:

```python
from dvoacap.path_geometry import GeoPoint

# Create from degrees (most common)
point = GeoPoint.from_degrees(latitude=40.0, longitude=-75.0)

# Create from radians
point = GeoPoint.from_radians(lat_rad=0.698, lon_rad=-1.309)

# Convert back to degrees
lat, lon = point.to_degrees()
```

### Path Geometry

Calculate great circle paths between locations:

```python
from dvoacap.path_geometry import PathGeometry, GeoPoint

# Create path
path = PathGeometry()
tx = GeoPoint.from_degrees(40.0, -75.0)  # Philadelphia
rx = GeoPoint.from_degrees(51.5, -0.1)   # London
path.set_tx_rx(tx, rx)

# Get path information
distance_km = path.get_distance_km()
azimuth_deg = path.get_azimuth_tr_degrees()
midpoint = path.get_point_at_dist(path.dist / 2)

print(f"Distance: {distance_km:.0f} km")
print(f"Azimuth: {azimuth_deg:.1f}°")
```

### Ionospheric Parameters

Model the ionosphere at any location and time:

```python
from dvoacap import FourierMaps, ControlPoint, GeographicPoint, compute_iono_params
import math

# Load ionospheric maps
maps = FourierMaps()
maps.set_conditions(month=6, ssn=100, utc_fraction=0.5)

# Create control point
pnt = ControlPoint(
    location=GeographicPoint.from_degrees(40.0, -75.0),
    east_lon=-75.0 * math.pi/180,
    distance_rad=0.0,
    local_time=0.5,
    zen_angle=0.3,
    zen_max=1.5,
    mag_lat=50.0 * math.pi/180,
    mag_dip=60.0 * math.pi/180,
    gyro_freq=1.2
)

# Compute ionospheric parameters
compute_iono_params(pnt, maps)

print(f"foE:  {pnt.e.fo:.2f} MHz at {pnt.e.hm:.0f} km")
print(f"foF2: {pnt.f2.fo:.2f} MHz at {pnt.f2.hm:.0f} km")
```

### MUF Calculations

Calculate Maximum Usable Frequency:

```python
from dvoacap.muf_calculator import MufCalculator

# Create MUF calculator
muf_calc = MufCalculator()

# Set up ionospheric profile and path
# (typically done automatically by PredictionEngine)

# Calculate MUF
muf_calc.calculate_muf()

print(f"MUF: {muf_calc.muf:.2f} MHz")
print(f"FOT (50%): {muf_calc.muf_info[2].fot:.2f} MHz")
print(f"HPF (90%): {muf_calc.muf_info[2].hpf:.2f} MHz")
```

---

## Basic Usage Patterns

### Single Path Prediction

```python
from dvoacap.prediction_engine import PredictionEngine
from dvoacap.path_geometry import GeoPoint

def predict_single_path(tx_lat, tx_lon, rx_lat, rx_lon, frequency, utc_hour=12):
    """Predict propagation for a single path"""

    engine = PredictionEngine()

    # Configure
    engine.params.ssn = 100.0
    engine.params.month = 6
    engine.params.tx_power = 100.0
    engine.params.tx_location = GeoPoint.from_degrees(tx_lat, tx_lon)

    # Run prediction
    rx_location = GeoPoint.from_degrees(rx_lat, rx_lon)
    engine.predict(rx_location=rx_location,
                   utc_time=utc_hour/24.0,
                   frequencies=[frequency])

    # Return results
    pred = engine.predictions[0]
    return {
        'frequency': frequency,
        'distance_km': engine.path.get_distance_km(),
        'azimuth': engine.path.get_azimuth_tr_degrees(),
        'muf': engine.muf_calculator.muf,
        'snr_db': pred.signal.snr_db,
        'reliability': pred.signal.reliability,
        'hop_count': pred.hop_count
    }

# Example usage
result = predict_single_path(40.0, -75.0, 51.5, -0.1, 14.0)
print(result)
```

### Multi-Frequency Scan

```python
def frequency_scan(tx_location, rx_location, freq_start=3, freq_end=30, freq_step=1):
    """Scan multiple frequencies to find best propagation"""

    engine = PredictionEngine()
    engine.params.ssn = 100.0
    engine.params.month = 6
    engine.params.tx_location = tx_location

    frequencies = list(range(freq_start, freq_end + 1, freq_step))
    engine.predict(rx_location=rx_location, utc_time=0.5, frequencies=frequencies)

    results = []
    for freq, pred in zip(frequencies, engine.predictions):
        results.append({
            'frequency': freq,
            'snr': pred.signal.snr_db,
            'reliability': pred.signal.reliability,
            'service_prob': pred.service_prob
        })

    # Find best frequency
    best = max(results, key=lambda x: x['reliability'])
    return results, best

# Example
tx = GeoPoint.from_degrees(40.0, -75.0)
rx = GeoPoint.from_degrees(51.5, -0.1)
all_freqs, best_freq = frequency_scan(tx, rx, 7, 30, 1)
print(f"Best frequency: {best_freq['frequency']} MHz "
      f"(SNR: {best_freq['snr']:.1f} dB)")
```

### Time-of-Day Analysis

```python
def analyze_by_time_of_day(tx_location, rx_location, frequency):
    """Analyze propagation across 24 hours"""

    engine = PredictionEngine()
    engine.params.ssn = 100.0
    engine.params.month = 6
    engine.params.tx_location = tx_location

    results = []
    for hour in range(24):
        utc_time = hour / 24.0
        engine.predict(rx_location=rx_location,
                      utc_time=utc_time,
                      frequencies=[frequency])

        pred = engine.predictions[0]
        results.append({
            'hour': hour,
            'utc_time': utc_time,
            'snr': pred.signal.snr_db,
            'reliability': pred.signal.reliability,
            'muf': engine.muf_calculator.muf
        })

    return results

# Example
tx = GeoPoint.from_degrees(40.0, -75.0)
rx = GeoPoint.from_degrees(51.5, -0.1)
hourly_data = analyze_by_time_of_day(tx, rx, 14.0)

# Print best times
good_times = [h for h in hourly_data if h['reliability'] > 0.7]
print(f"Good propagation hours (>70% reliability): "
      f"{[h['hour'] for h in good_times]}")
```

---

## Advanced Usage

### Custom Antenna Patterns

```python
from dvoacap.antenna_gain import AntennaModel
import numpy as np

class CustomDirectionalAntenna(AntennaModel):
    """Custom directional antenna model"""

    def __init__(self, gain_dbi=10.0, beamwidth_deg=45.0):
        self.gain_dbi = gain_dbi
        self.beamwidth_rad = np.deg2rad(beamwidth_deg)

    def get_gain_db(self, azimuth, elevation):
        """Calculate gain at given angles"""
        # Simple cosine pattern for example
        az_factor = np.cos(azimuth / 2) ** 2
        el_factor = np.cos(elevation - np.pi/4) ** 2
        return self.gain_dbi * az_factor * el_factor

# Use custom antenna
engine = PredictionEngine()
engine.params.tx_antenna = CustomDirectionalAntenna(gain_dbi=12.0, beamwidth_deg=60.0)
```

### Batch Processing Multiple Paths

```python
def batch_predict_paths(tx_location, rx_locations_dict, frequencies, output_file='predictions.json'):
    """Process multiple paths and save results"""
    import json

    engine = PredictionEngine()
    engine.params.ssn = 100.0
    engine.params.month = 6
    engine.params.tx_location = tx_location

    all_results = {}

    for name, rx_location in rx_locations_dict.items():
        print(f"Processing {name}...")

        try:
            engine.predict(rx_location=rx_location,
                          utc_time=0.5,
                          frequencies=frequencies)

            path_results = []
            for freq, pred in zip(frequencies, engine.predictions):
                path_results.append({
                    'frequency': freq,
                    'snr_db': pred.signal.snr_db,
                    'reliability': pred.signal.reliability,
                    'hop_count': pred.hop_count
                })

            all_results[name] = {
                'distance_km': engine.path.get_distance_km(),
                'azimuth': engine.path.get_azimuth_tr_degrees(),
                'predictions': path_results
            }
        except Exception as e:
            all_results[name] = {'error': str(e)}

    # Save to JSON
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2)

    return all_results

# Example
tx = GeoPoint.from_degrees(40.0, -75.0)
destinations = {
    'London': GeoPoint.from_degrees(51.5, -0.1),
    'Tokyo': GeoPoint.from_degrees(35.7, 139.7),
    'Sydney': GeoPoint.from_degrees(-33.9, 151.2)
}
results = batch_predict_paths(tx, destinations, [14.0, 21.0, 28.0])
```

### Solar Cycle Comparison

```python
def compare_solar_cycles(tx_location, rx_location, frequency):
    """Compare propagation at different solar cycle phases"""

    engine = PredictionEngine()
    engine.params.tx_location = tx_location
    engine.params.month = 6

    ssn_values = [10, 50, 100, 150, 200]  # Solar minimum to maximum
    results = {}

    for ssn in ssn_values:
        engine.params.ssn = ssn
        engine.predict(rx_location=rx_location,
                      utc_time=0.5,
                      frequencies=[frequency])

        pred = engine.predictions[0]
        results[ssn] = {
            'muf': engine.muf_calculator.muf,
            'snr': pred.signal.snr_db,
            'reliability': pred.signal.reliability
        }

    return results

# Example
tx = GeoPoint.from_degrees(40.0, -75.0)
rx = GeoPoint.from_degrees(51.5, -0.1)
solar_comparison = compare_solar_cycles(tx, rx, 14.0)

for ssn, data in solar_comparison.items():
    print(f"SSN {ssn:3d}: MUF={data['muf']:5.1f} MHz, "
          f"SNR={data['snr']:5.1f} dB, Rel={data['reliability']*100:4.1f}%")
```

---

## API Reference

### PredictionEngine

Main class for running propagation predictions.

```python
class PredictionEngine:
    def __init__(self):
        """Initialize prediction engine"""

    def predict(self, rx_location: GeoPoint, utc_time: float, frequencies: List[float]):
        """
        Run propagation prediction

        Args:
            rx_location: Receiver location (GeoPoint)
            utc_time: UTC time as fraction of day (0.0-1.0)
            frequencies: List of frequencies in MHz
        """

    # Main attributes
    params: VoacapParams      # Configuration parameters
    path: PathGeometry        # Path geometry
    muf_calculator: MufCalculator  # MUF calculations
    predictions: List[Prediction]  # Results for each frequency
```

### VoacapParams

Configuration parameters for predictions.

```python
class VoacapParams:
    ssn: float = 100.0              # Sunspot number
    month: int = 6                  # Month (1-12)
    tx_power: float = 100.0         # Transmit power (watts)
    tx_location: GeoPoint           # Transmitter location
    min_angle: float = 0.05         # Minimum elevation angle (radians)
    man_made_noise_at_3mhz: float = 145.0  # Man-made noise level
    required_snr: float = 10.0      # Required SNR (dB)
    required_reliability: float = 0.9  # Required reliability (0-1)
```

### GeoPoint

Represents a geographic location.

```python
class GeoPoint:
    @staticmethod
    def from_degrees(latitude: float, longitude: float) -> GeoPoint:
        """Create from degrees"""

    @staticmethod
    def from_radians(lat_rad: float, lon_rad: float) -> GeoPoint:
        """Create from radians"""

    def to_degrees(self) -> Tuple[float, float]:
        """Convert to (latitude, longitude) in degrees"""
```

---

## Common Use Cases

### Amateur Radio Contest Planning

```python
def contest_planner(home_location, contest_multipliers, frequency_band=14.0):
    """Plan operating strategy for contest multipliers"""

    engine = PredictionEngine()
    engine.params.ssn = 100.0
    engine.params.month = 11  # November contest season
    engine.params.tx_location = home_location

    # Analyze each multiplier
    targets = []
    for name, location in contest_multipliers.items():
        engine.predict(rx_location=location, utc_time=0.5, frequencies=[frequency_band])
        pred = engine.predictions[0]

        targets.append({
            'name': name,
            'azimuth': engine.path.get_azimuth_tr_degrees(),
            'distance': engine.path.get_distance_km(),
            'snr': pred.signal.snr_db,
            'reliability': pred.signal.reliability,
            'best_time': find_best_time(engine, location, frequency_band)
        })

    # Sort by reliability
    targets.sort(key=lambda x: x['reliability'], reverse=True)
    return targets
```

### Broadcast Coverage Analysis

```python
def coverage_analysis(tx_location, frequency, power_watts, target_grid):
    """Analyze broadcast coverage over geographic grid"""

    engine = PredictionEngine()
    engine.params.ssn = 100.0
    engine.params.month = 6
    engine.params.tx_power = power_watts
    engine.params.tx_location = tx_location

    coverage_map = {}

    for lat in range(target_grid['lat_min'], target_grid['lat_max'], target_grid['step']):
        for lon in range(target_grid['lon_min'], target_grid['lon_max'], target_grid['step']):
            rx = GeoPoint.from_degrees(lat, lon)

            try:
                engine.predict(rx_location=rx, utc_time=0.5, frequencies=[frequency])
                pred = engine.predictions[0]

                coverage_map[(lat, lon)] = {
                    'snr': pred.signal.snr_db,
                    'reliability': pred.signal.reliability
                }
            except:
                coverage_map[(lat, lon)] = None

    return coverage_map
```

### Emergency Communications Planning

```python
def emergency_comms_plan(disaster_location, relief_stations, available_frequencies):
    """Plan emergency communications network"""

    results = {}

    for station_name, station_loc in relief_stations.items():
        engine = PredictionEngine()
        engine.params.ssn = 50.0  # Conservative estimate
        engine.params.tx_location = station_loc
        engine.params.tx_power = 100.0

        engine.predict(rx_location=disaster_location,
                      utc_time=0.5,
                      frequencies=available_frequencies)

        # Find most reliable frequencies
        reliable_freqs = []
        for freq, pred in zip(available_frequencies, engine.predictions):
            if pred.signal.reliability > 0.7 and pred.signal.snr_db > 10:
                reliable_freqs.append({
                    'frequency': freq,
                    'snr': pred.signal.snr_db,
                    'reliability': pred.signal.reliability
                })

        results[station_name] = {
            'distance': engine.path.get_distance_km(),
            'azimuth': engine.path.get_azimuth_tr_degrees(),
            'reliable_frequencies': reliable_freqs
        }

    return results
```

---

## Error Handling

```python
try:
    engine = PredictionEngine()
    engine.predict(rx_location=rx, utc_time=0.5, frequencies=[14.0])
except ValueError as e:
    print(f"Invalid parameter: {e}")
except RuntimeError as e:
    print(f"Prediction failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Performance Tips

1. **Reuse PredictionEngine instances** - The engine can be reused for multiple predictions
2. **Batch frequency predictions** - Pass multiple frequencies in one call rather than multiple calls
3. **Cache FourierMaps** - The ionospheric maps are expensive to load
4. **Use appropriate SSN values** - Extreme values may cause convergence issues

---

## Next Steps

- See [INTEGRATION.md](INTEGRATION.md) for integrating with web applications and dashboards
- See [examples/](../examples/) for complete working examples
- Check the [API documentation](API.md) for detailed class references

---

For questions or issues, visit: https://github.com/skyelaird/dvoacap-python/issues
