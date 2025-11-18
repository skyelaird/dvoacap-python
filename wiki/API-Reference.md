# API Reference

Complete API reference for DVOACAP-Python. Classes and methods are organized by phase.

## Quick Links

- [Phase 1: Path Geometry](#phase-1-path-geometry)
- [Phase 2: Solar & Geomagnetic](#phase-2-solar--geomagnetic)
- [Phase 3: Ionospheric Profiles](#phase-3-ionospheric-profiles)
- [Phase 4: Raytracing](#phase-4-raytracing)
- [Phase 5: Signal Predictions](#phase-5-signal-predictions)
- [Utilities](#utilities)

---

## Phase 1: Path Geometry

### `GeographicPoint`

Represents a geographic location with latitude and longitude.

**Constructor:**
```python
GeographicPoint(lat: float, lon: float)
GeographicPoint.from_degrees(lat_deg: float, lon_deg: float)
```

**Attributes:**
- `lat` (float) - Latitude in radians
- `lon` (float) - Longitude in radians

**Example:**
```python
from dvoacap import PathPoint

# Create point from degrees
philadelphia = PathPoint.from_degrees(40.0, -75.0)
```

### `PathGeometry`

Utilities for great circle path calculations.

**Static Methods:**
```python
PathGeometry.distance(p1: GeographicPoint, p2: GeographicPoint) -> float
PathGeometry.bearing(p1: GeographicPoint, p2: GeographicPoint) -> float
PathGeometry.midpoint(p1: GeographicPoint, p2: GeographicPoint) -> GeographicPoint
```

**Parameters:**
- `p1`, `p2` - Geographic points (start and end)
- **Returns:** Distance in km, bearing in radians, or midpoint

**Example:**
```python
from dvoacap import PathGeometry, PathPoint

tx = PathPoint.from_degrees(40.0, -75.0)  # Philadelphia
rx = PathPoint.from_degrees(51.5, -0.1)   # London

distance_km = PathGeometry.distance(tx, rx)
bearing_rad = PathGeometry.bearing(tx, rx)
midpoint = PathGeometry.midpoint(tx, rx)
```

---

## Phase 2: Solar & Geomagnetic

### `SolarCalculator`

Calculates solar position and illumination.

**Methods:**
```python
SolarCalculator.compute_zenith_angle(
    location: GeographicPoint,
    utc_time: datetime
) -> float

SolarCalculator.compute_local_time(
    location: GeographicPoint,
    utc_time: datetime
) -> float

SolarCalculator.is_daytime(
    location: GeographicPoint,
    utc_time: datetime
) -> bool
```

**Parameters:**
- `location` - Geographic point
- `utc_time` - UTC datetime
- **Returns:** Zenith angle (radians), local time fraction (0-1), or boolean

**Example:**
```python
from dvoacap import SolarCalculator, SolarPoint
from datetime import datetime

location = SolarPoint.from_degrees(40.0, -75.0)
utc = datetime(2025, 6, 15, 12, 0)

zenith = SolarCalculator.compute_zenith_angle(location, utc)
is_day = SolarCalculator.is_daytime(location, utc)
```

### `GeomagneticCalculator`

Calculates Earth's magnetic field parameters.

**Methods:**
```python
GeomagneticCalculator.compute_field(
    location: GeographicPoint,
    altitude_km: float,
    date: datetime
) -> GeomagneticParameters
```

**Returns:** `GeomagneticParameters` with:
- `mag_lat` - Magnetic latitude (radians)
- `mag_dip` - Magnetic dip angle (radians)
- `gyro_freq` - Gyrofrequency (MHz)
- `field_intensity` - Total field strength (nT)

**Example:**
```python
from dvoacap import GeomagneticCalculator, GeoPoint
from datetime import datetime

location = GeoPoint.from_degrees(40.0, -75.0)
params = GeomagneticCalculator.compute_field(
    location,
    altitude_km=300,
    date=datetime(2025, 6, 15)
)

print(f"Magnetic latitude: {params.mag_lat:.2f} rad")
print(f"Gyrofrequency: {params.gyro_freq:.2f} MHz")
```

---

## Phase 3: Ionospheric Profiles

### `FourierMaps`

CCIR/URSI ionospheric coefficient maps.

**Constructor:**
```python
FourierMaps(data_dir: str = "DVoaData")
```

**Methods:**
```python
def set_conditions(
    self,
    month: int,          # 1-12
    ssn: float,          # Sunspot number (0-200)
    utc_fraction: float  # 0-1 (0 = midnight, 0.5 = noon)
)

def compute_var_map(
    self,
    lat: float,    # Latitude in radians
    lon: float,    # Longitude in radians
    kind: VarMapKind
) -> Distribution  # Returns median, upper decile, lower decile
```

**VarMapKind enum:**
- `VarMapKind.F2` - F2 layer critical frequency
- `VarMapKind.ER` - E layer critical frequency
- `VarMapKind.FM3` - M(3000)F2 propagation factor

**Example:**
```python
from dvoacap import FourierMaps, VarMapKind

maps = FourierMaps()
maps.set_conditions(month=6, ssn=100, utc_fraction=0.5)

# Get foF2 at Philadelphia
fof2 = maps.compute_var_map(
    lat=40.0 * 3.14159/180,
    lon=-75.0 * 3.14159/180,
    kind=VarMapKind.F2
)

print(f"foF2: {fof2.median:.2f} MHz")
```

### `ControlPoint`

Point along propagation path with ionospheric parameters.

**Attributes:**
- `location` - Geographic point
- `e` - E layer info (LayerInfo)
- `f1` - F1 layer info
- `f2` - F2 layer info
- `es` - Sporadic E info

**LayerInfo fields:**
- `fo` - Critical frequency (MHz)
- `hm` - Peak height (km)
- `ym` - Semi-thickness (km)

**Example:**
```python
from dvoacap import ControlPoint, FourierMaps, compute_iono_params
import math

maps = FourierMaps()
maps.set_conditions(month=6, ssn=100, utc_fraction=0.5)

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

compute_iono_params(pnt, maps)

print(f"E layer:  foE  = {pnt.e.fo:.2f} MHz at {pnt.e.hm:.0f} km")
print(f"F2 layer: foF2 = {pnt.f2.fo:.2f} MHz at {pnt.f2.hm:.0f} km")
```

### `IonosphericProfile`

Electron density profile vs altitude.

**Methods:**
```python
def compute_profile(
    self,
    control_point: ControlPoint,
    altitude_km: float
) -> float  # Returns electron density (electrons/cm³)
```

**Example:**
```python
from dvoacap import IonosphericProfile

profile = IonosphericProfile(control_point)

# Get electron density at 300 km
density = profile.compute_profile(control_point, 300)
print(f"Electron density at 300 km: {density:.2e} e/cm³")
```

---

## Phase 4: Raytracing

### `MufCalculator`

Maximum Usable Frequency calculations.

**Constructor:**
```python
MufCalculator(profile: IonosphericProfile)
```

**Methods:**
```python
def compute_circuit_muf(
    self,
    distance_km: float,
    min_elevation_deg: float = 3.0
) -> CircuitMuf
```

**CircuitMuf attributes:**
- `muf` - Maximum Usable Frequency (MHz)
- `fot` - Frequency of Optimum Traffic (MHz)
- `hpf` - High Probability Frequency (MHz)
- `e_muf` - E layer MUF
- `f1_muf` - F1 layer MUF
- `f2_muf` - F2 layer MUF

**Example:**
```python
from dvoacap import MufCalculator

calc = MufCalculator(ionospheric_profile)
circuit = calc.compute_circuit_muf(distance_km=5000)

print(f"MUF: {circuit.muf:.2f} MHz")
print(f"FOT: {circuit.fot:.2f} MHz (optimum)")
print(f"HPF: {circuit.hpf:.2f} MHz (high reliability)")
```

### `Reflectrix`

Ray path calculations through ionosphere.

**Constructor:**
```python
Reflectrix(profile: IonosphericProfile)
```

**Methods:**
```python
def compute_modes(
    self,
    frequency_mhz: float,
    distance_km: float
) -> List[ModeInfo]

def compute_skip_distance(
    self,
    frequency_mhz: float,
    layer: str  # 'E', 'F1', 'F2'
) -> float
```

**ModeInfo attributes:**
- `mode` - Mode name (e.g., '1F2', '2F2')
- `hops` - Number of hops
- `layer` - Reflection layer ('E', 'F1', 'F2')
- `elevation_angle` - Takeoff angle (degrees)
- `virtual_height` - Virtual reflection height (km)

**Example:**
```python
from dvoacap import Reflectrix

reflx = Reflectrix(ionospheric_profile)

# Find all modes for 14 MHz, 5000 km path
modes = reflx.compute_modes(frequency_mhz=14.0, distance_km=5000)

for mode in modes:
    print(f"Mode {mode.mode}: {mode.hops} hops, "
          f"takeoff {mode.elevation_angle:.1f}°")

# Get skip distance for F2 layer at 28 MHz
skip = reflx.compute_skip_distance(frequency_mhz=28.0, layer='F2')
print(f"Skip distance: {skip:.0f} km")
```

---

## Phase 5: Signal Predictions

### `NoiseModel`

Atmospheric, galactic, and man-made noise calculations.

**Constructor:**
```python
NoiseModel(
    frequency_mhz: float,
    location: GeographicPoint,
    utc_time: datetime,
    noise_type: str = "rural"  # 'rural', 'suburban', 'urban'
)
```

**Methods:**
```python
def compute_noise(self) -> Distribution
```

**Returns:** `Distribution` with median, upper, lower decile noise levels (dB)

**Example:**
```python
from dvoacap import NoiseModel, GeoPoint
from datetime import datetime

location = GeoPoint.from_degrees(40.0, -75.0)
noise = NoiseModel(
    frequency_mhz=14.2,
    location=location,
    utc_time=datetime(2025, 6, 15, 12, 0),
    noise_type="suburban"
)

levels = noise.compute_noise()
print(f"Noise level: {levels.median:.1f} dB")
```

### `AntennaModel`

Base class for antenna gain patterns.

**Subclasses:**
- `IsotropicAntenna` - 0 dBi gain in all directions
- `HalfWaveDipole` - Dipole pattern (2.15 dBi gain)
- `VerticalMonopole` - Vertical antenna pattern
- Custom antennas via subclassing

**Methods:**
```python
def compute_gain(
    self,
    elevation_angle_deg: float,
    azimuth_deg: float = 0
) -> float  # Returns gain in dBi
```

**Example:**
```python
from dvoacap import HalfWaveDipole

dipole = HalfWaveDipole(height_m=10, orientation_deg=0)
gain = dipole.compute_gain(elevation_angle_deg=15)
print(f"Gain at 15°: {gain:.1f} dBi")
```

### `PredictionEngine`

Main prediction engine for complete propagation predictions.

**Constructor:**
```python
PredictionEngine()
```

**Methods:**
```python
def predict(
    self,
    tx_lat: float,           # Degrees
    tx_lon: float,           # Degrees
    rx_lat: float,           # Degrees
    rx_lon: float,           # Degrees
    frequency: float,        # MHz
    utc_time: datetime,
    ssn: float = 100,        # Sunspot number
    tx_power: float = 100,   # Watts
    tx_antenna_gain: float = 0,  # dBi
    rx_antenna_gain: float = 0   # dBi
) -> Prediction
```

**Prediction attributes:**
- `muf` - Maximum Usable Frequency (MHz)
- `fot` - Frequency of Optimum Traffic (MHz)
- `snr` - Signal-to-Noise Ratio (dB)
- `signal_strength` - Field strength (dBµV/m)
- `reliability` - Service probability (%)
- `mode` - Best propagation mode
- `distance_km` - Path distance

**Example:**
```python
from dvoacap import PredictionEngine
from datetime import datetime

engine = PredictionEngine()

result = engine.predict(
    tx_lat=40.0, tx_lon=-75.0,  # Philadelphia
    rx_lat=51.5, rx_lon=-0.1,   # London
    frequency=14.2,              # 20m band
    utc_time=datetime(2025, 6, 15, 12, 0),
    ssn=100,
    tx_power=100,
    tx_antenna_gain=2.0
)

print(f"Distance: {result.distance_km:.0f} km")
print(f"MUF: {result.muf:.2f} MHz")
print(f"SNR: {result.snr:.1f} dB")
print(f"Reliability: {result.reliability:.0f}%")
print(f"Best mode: {result.mode}")
```

---

## Utilities

### `Distribution`

Represents statistical distribution with median and deciles.

**Attributes:**
- `median` - Median value (50th percentile)
- `upper` - Upper decile (90th percentile)
- `lower` - Lower decile (10th percentile)

**Example:**
```python
from dvoacap import Distribution

dist = Distribution(median=10.0, upper=15.0, lower=5.0)
print(f"Range: {dist.lower:.1f} to {dist.upper:.1f} dB")
```

### Version Information

```python
from dvoacap import get_version_info, get_phase_status

version = get_version_info()
print(f"DVOACAP-Python v{version['version']}")
print(f"Progress: {version['progress']}")

status = get_phase_status()
for phase, desc in status.items():
    print(f"{phase}: {desc}")
```

---

## Complete Example: End-to-End Prediction

```python
from dvoacap import PredictionEngine
from datetime import datetime

# Initialize engine
engine = PredictionEngine()

# Configure transmitter and receiver
tx_lat, tx_lon = 40.0, -75.0  # Philadelphia
rx_lat, rx_lon = 51.5, -0.1   # London

# Run prediction for 20m band
result = engine.predict(
    tx_lat=tx_lat,
    tx_lon=tx_lon,
    rx_lat=rx_lat,
    rx_lon=rx_lon,
    frequency=14.2,
    utc_time=datetime(2025, 6, 15, 12, 0),
    ssn=100,
    tx_power=100,
    tx_antenna_gain=2.0,
    rx_antenna_gain=0.0
)

# Display results
print(f"Philadelphia → London Propagation Prediction")
print(f"=============================================")
print(f"Distance:     {result.distance_km:>8.0f} km")
print(f"Frequency:    {14.2:>8.1f} MHz")
print(f"MUF:          {result.muf:>8.2f} MHz")
print(f"FOT:          {result.fot:>8.2f} MHz")
print(f"SNR:          {result.snr:>8.1f} dB")
print(f"Reliability:  {result.reliability:>8.0f} %")
print(f"Best Mode:    {result.mode}")
```

**Expected Output:**
```
Philadelphia → London Propagation Prediction
=============================================
Distance:        5120 km
Frequency:       14.2 MHz
MUF:            18.50 MHz
FOT:            15.72 MHz
SNR:            25.3 dB
Reliability:       85 %
Best Mode:      2F2
```

---

## Type Hints

DVOACAP-Python includes type hints throughout the codebase:

```python
from typing import List, Tuple, Optional
from datetime import datetime
from dvoacap import GeographicPoint, ModeInfo, Distribution

def my_function(
    location: GeographicPoint,
    frequency: float,
    utc: datetime
) -> Tuple[float, List[ModeInfo]]:
    # Your code here
    pass
```

---

## See Also

- [Architecture](Architecture) - System design and module structure
- [Getting Started](Getting-Started) - Installation and basic usage
- [Integration Guide](Integration-Guide) - Building applications with DVOACAP
- [Examples Repository](https://github.com/skyelaird/dvoacap-python/tree/main/examples) - More code examples

---

**API Status:** v1.0.0 Production Ready. API is stable.
