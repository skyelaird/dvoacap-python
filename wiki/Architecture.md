# DVOACAP-Python Architecture

This page provides an overview of the DVOACAP-Python architecture, organized into 5 major phases that mirror the structure of radio wave propagation prediction.

## System Overview

DVOACAP-Python is structured as a modular pipeline where each phase builds upon the previous one:

```
Phase 1: Path Geometry
    ↓
Phase 2: Solar & Geomagnetic
    ↓
Phase 3: Ionospheric Profiles
    ↓
Phase 4: Raytracing
    ↓
Phase 5: Signal Predictions
```

## Phase 1: Path Geometry ✅ Complete

**Purpose:** Calculate geometric properties of the radio propagation path

**Module:** `path_geometry.py`

**Key Features:**
- Great circle path calculations
- Geodetic to geocentric coordinate conversions
- Path distance and bearing computation
- Path midpoint calculations
- Earth curvature modeling

**Key Classes:**
- `GeographicPoint` - Latitude/longitude coordinates
- `PathGeometry` - Path calculation utilities

**Key Functions:**
- `great_circle_distance()` - Distance between two points
- `path_bearing()` - Initial and final bearing
- `path_midpoint()` - Geographic midpoint
- `geodetic_to_geocentric()` - Coordinate system conversions

**Validation:**
- Distance error: < 0.01%
- Bearing error: < 0.01°
- Tested against reference VOACAP data

**Source Reference:** `PathGeom.pas` from original DVOACAP

---

## Phase 2: Solar & Geomagnetic ✅ Complete

**Purpose:** Calculate solar illumination and Earth's magnetic field properties

**Modules:**
- `solar.py` - Solar calculations
- `geomagnetic.py` - Magnetic field modeling

**Key Features:**

### Solar Module
- Solar zenith angle calculations
- Solar declination and right ascension
- Day of year conversions
- Local time calculations
- Sunrise/sunset times
- UTC to local time conversions

### Geomagnetic Module
- International Geomagnetic Reference Field (IGRF) model
- Magnetic latitude and dip angle
- Gyrofrequency calculations
- Magnetic field intensity
- Geographic to geomagnetic coordinate transformations

**Key Classes:**
- `SolarPosition` - Solar angle calculator
- `MagneticField` - IGRF magnetic field model

**Key Functions:**
- `compute_solar_zenith()` - Sun angle relative to location
- `compute_magnetic_latitude()` - Magnetic coordinates
- `compute_gyrofrequency()` - Electron gyrofrequency for ionosphere

**Validation:**
- Solar zenith angle: < 0.01° error
- Magnetic latitude: < 0.1° error
- Gyrofrequency: < 1% error

**Source Reference:** `Sun.pas`, `MagFld.pas` from original DVOACAP

---

## Phase 3: Ionospheric Profiles ✅ Complete

**Purpose:** Model ionospheric layer structure and electron density

**Modules:**
- `fourier_maps.py` - CCIR/URSI coefficient maps
- `ionospheric_profile.py` - Electron density profiles
- `layer_parameters.py` - Layer critical frequencies and heights

**Key Features:**

### Fourier Maps
- CCIR/URSI coefficient loading from data files
- Geographic interpolation using Fourier series
- Solar cycle variations (SSN-dependent)
- Seasonal and diurnal variations
- Variable maps: foF2, foE, M(3000)F2
- Fixed maps: foF1, hmF2, hmE

### Layer Parameters
- **E layer:** Solar-controlled critical frequency
- **F1 layer:** Daytime intermediate layer
- **F2 layer:** Primary long-distance reflection
- **Es (Sporadic E):** Unpredictable E-layer enhancement
- Layer peak heights (hm) and semi-thickness (ym)

### Ionospheric Profiles
- Electron density vs altitude
- True height and virtual height calculations
- Ionogram generation
- Multi-layer profile computation
- Quasi-parabolic layer modeling

**Key Classes:**
- `FourierMaps` - CCIR/URSI map manager
- `ControlPoint` - Point along propagation path
- `LayerInfo` - Layer parameters (fo, hm, ym)
- `IonosphericProfile` - Full vertical profile

**Key Functions:**
- `set_conditions()` - Set month, SSN, UTC time
- `compute_iono_params()` - Compute all layer parameters
- `compute_profile()` - Generate electron density profile
- `true_height()` - Correct for ionospheric refraction

**Data Files:**
- `DVoaData/CCIR*.asc` - CCIR coefficients
- `DVoaData/URSI*.asc` - URSI coefficients

**Validation:**
- foF2: Validated against CCIR reference tables
- Layer heights: Reasonable physical ranges
- Profile structure: Matches reference ionograms

**Source Reference:** `IonoProf.pas`, `LayrParm.pas`, `FrMaps.pas` from original DVOACAP

---

## Phase 4: Raytracing ✅ Complete

**Purpose:** Calculate radio wave paths through the ionosphere

**Modules:**
- `muf_calculator.py` - Maximum Usable Frequency calculations
- `reflectrix.py` - Ray path calculations

**Key Features:**

### MUF Calculator
- **MUF (Maximum Usable Frequency):** Highest frequency that will refract back
- **FOT (Frequency of Optimum Traffic):** Typically 85% of MUF
- **HPF (High Probability Frequency):** Conservative estimate
- Circuit MUF for all layers (E, F1, F2)
- Profile selection from multiple sample areas
- Iterative refinement using Martyn's theorem
- Probability distribution calculations

### Reflectrix
- Ray path calculation for all ionospheric layers
- Elevation angle vs distance curves
- Skip distance computation
- Multi-hop path finding (1F, 2F, 3F, etc.)
- Mode interpolation
- Over-the-MUF mode handling
- Vertical incidence modes

**Propagation Modes:**
- `1E` - Single-hop E layer
- `1F1` - Single-hop F1 layer
- `1F2` - Single-hop F2 layer
- `2F2` - Two-hop F2 layer
- `3F2` - Three-hop F2 layer
- Mixed modes: `1E1F2`, etc.

**Key Classes:**
- `MufCalculator` - MUF computation
- `MufInfo` - MUF for a single layer
- `CircuitMuf` - Combined MUF for all layers
- `Reflectrix` - Ray path calculator
- `ModeInfo` - Propagation mode details

**Key Functions:**
- `compute_circuit_muf()` - MUF for entire circuit
- `compute_modes()` - Find all valid propagation modes
- `compute_skip_distance()` - Minimum distance for frequency
- `interpolate_mode()` - Mode parameters for specific distance

**Validation:**
- MUF calculations match reference VOACAP
- Skip distances validated
- Mode selection logic verified

**Source Reference:** `Reflx.pas`, `MufCalc.pas`, `ALLMODES.FOR` from original VOACAP

---

## Phase 5: Signal Predictions 🚧 In Progress (85%)

**Purpose:** Predict signal strength, noise levels, and reliability

**Modules:**
- `prediction_engine.py` - Main prediction engine
- `noise_model.py` - Atmospheric and man-made noise
- `antenna_gain.py` - Antenna pattern calculations

**Key Features:**

### Completed Components ✅
- **Noise modeling:**
  - Atmospheric noise (ITU-R P.372)
  - Galactic noise
  - Man-made noise (rural/suburban/urban)
  - Frequency-dependent noise calculations
- **Antenna gain:**
  - Dipole patterns
  - Vertical monopoles
  - Yagi/beam antennas
  - Elevation angle-dependent gain
- **Prediction engine framework:**
  - Mode selection
  - Path loss calculations
  - Power budget analysis

### In Progress ⚠️
- **Reliability calculation:** Currently showing 0% (debugging)
- **Signal distribution:** Decile calculations need verification
- **Absorption loss:** Recent fixes, ongoing validation
- **End-to-end integration:** Systematic testing

**Known Issues:**
- Reliability calculation bug (line 810+ in `prediction_engine.py`)
- Signal/noise distribution may have inverted deciles
- Absorption coefficient alignment fixed (PR #37)

**Key Classes:**
- `PredictionEngine` - Main engine
- `NoiseModel` - Noise calculations
- `AntennaPattern` - Gain patterns
- `PredictionResult` - Final output

**Key Functions:**
- `predict()` - Complete prediction
- `compute_signal_strength()` - Power budget
- `compute_reliability()` - Service probability
- `compute_noise()` - Background noise level

**Validation:**
- Component tests passing
- End-to-end validation in progress
- Reference comparison ongoing

**Source Reference:** `VoaCapEng.pas`, `AntGain.pas`, `NoiseMdl.pas`, `RELBIL.FOR`, `REGMOD.FOR` from original VOACAP

---

## Data Flow

### Typical Prediction Flow

```python
# 1. Define circuit
tx = GeographicPoint.from_degrees(40.0, -75.0)  # Philadelphia
rx = GeographicPoint.from_degrees(51.5, -0.1)   # London

# 2. Path geometry (Phase 1)
distance = great_circle_distance(tx, rx)
bearing = path_bearing(tx, rx)
midpoint = path_midpoint(tx, rx)

# 3. Solar & magnetic (Phase 2)
zenith = compute_solar_zenith(midpoint, utc_time)
mag_lat = compute_magnetic_latitude(midpoint)

# 4. Ionospheric profiles (Phase 3)
maps = FourierMaps()
maps.set_conditions(month=6, ssn=100, utc_fraction=0.5)
profile = compute_ionospheric_profile(midpoint, maps)

# 5. Raytracing (Phase 4)
muf_calc = MufCalculator(profile)
circuit_muf = muf_calc.compute_circuit_muf(distance)
modes = reflectrix.compute_modes(frequency, distance)

# 6. Signal prediction (Phase 5)
engine = PredictionEngine()
result = engine.predict(tx, rx, frequency, utc_time, ssn)
# Returns: SNR, reliability, MUF, FOT, signal strength
```

## Module Dependencies

```
path_geometry (standalone)
    ↓
solar, geomagnetic (depends on path_geometry)
    ↓
fourier_maps (standalone, loads data files)
    ↓
layer_parameters (depends on fourier_maps, solar, geomagnetic)
    ↓
ionospheric_profile (depends on layer_parameters)
    ↓
muf_calculator (depends on ionospheric_profile, path_geometry)
    ↓
reflectrix (depends on muf_calculator, ionospheric_profile)
    ↓
prediction_engine (depends on all previous modules)
```

## File Structure

```
src/dvoacap/
├── __init__.py
├── path_geometry.py        # Phase 1
├── solar.py                # Phase 2
├── geomagnetic.py          # Phase 2
├── fourier_maps.py         # Phase 3
├── layer_parameters.py     # Phase 3
├── ionospheric_profile.py  # Phase 3
├── muf_calculator.py       # Phase 4
├── reflectrix.py           # Phase 4
├── prediction_engine.py    # Phase 5
├── noise_model.py          # Phase 5
└── antenna_gain.py         # Phase 5

DVoaData/
├── CCIR*.asc              # CCIR ionospheric coefficients
├── URSI*.asc              # URSI ionospheric coefficients
└── *.dat                  # Other reference data

tests/
├── test_path_geometry.py
├── test_solar.py
├── test_ionospheric.py
└── test_voacap_reference.py
```

## Performance Characteristics

**Typical Prediction Times (on modern hardware):**
- Single-point prediction: ~500 ms
- Area coverage (100 points): ~30-60 seconds
- Full band scan (10 frequencies): ~5 seconds

**Memory Usage:**
- CCIR/URSI data files: ~30 MB
- Runtime working set: ~100-200 MB
- Peak usage during area scan: ~500 MB

**Optimization Opportunities:**
- Caching of Fourier map calculations
- NumPy vectorization of array operations
- Numba JIT compilation for hot paths
- Lazy-loading of coefficient files

## Next Steps

See the [Validation Status](Validation-Status) page for current testing state and the [Contributing Guide](Contributing) for how to help complete Phase 5.

## References

- [API Reference](API-Reference) - Detailed class and method documentation
- [Integration Guide](Integration-Guide) - Using DVOACAP in your applications
- [Validation Status](Validation-Status) - Testing and accuracy metrics
- Repository docs: [docs/PHASE*.md](https://github.com/skyelaird/dvoacap-python/tree/main/docs)

---

**Phase completion:** 4 of 5 complete (85% total)
