# DVOACAP-Python 📡

> Python port of DVOACAP (Digital Voice of America Coverage Analysis Program) - An HF radio propagation prediction engine

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python Version](https://img.shields.io/badge/python-3.11%2B-blue)
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)
![Validation](https://img.shields.io/badge/validation-86.6%25-brightgreen)
[![CI](https://github.com/skyelaird/dvoacap-python/actions/workflows/validation.yml/badge.svg)](https://github.com/skyelaird/dvoacap-python/actions/workflows/validation.yml)

## 🎯 About

DVOACAP-Python is a modern Python port of the [DVOACAP](https://github.com/VE3NEA/DVOACAP) HF propagation prediction engine, originally written in Delphi/Pascal by Alex Shovkoplyas (VE3NEA). This project aims to provide an accessible, well-documented, and maintainable Python implementation of the VOACAP ionospheric propagation model.

**Original DVOACAP by:** Alex Shovkoplyas, VE3NEA
**Python Port:** Production Ready (v1.0.0, November 2025)

## ⚡ Quick Start

### Installation

Choose the installation option that fits your needs:

**Option 1: Core Library Only** (lightweight, for developers)
```bash
# Clone the repository
git clone https://github.com/skyelaird/dvoacap-python.git
cd dvoacap-python

# Install just the propagation engine
pip install -e .
```

**Option 2: With Dashboard** (includes Flask server and web UI)
```bash
# Clone the repository
git clone https://github.com/skyelaird/dvoacap-python.git
cd dvoacap-python

# Install library + dashboard dependencies
pip install -e ".[dashboard]"
```

**Option 3: Development Setup** (includes testing tools)
```bash
# Clone the repository
git clone https://github.com/skyelaird/dvoacap-python.git
cd dvoacap-python

# Install everything
pip install -e ".[all]"
```

### What's Included

| Installation | Core Library | Dashboard | Dev Tools |
|-------------|--------------|-----------|-----------|
| `pip install -e .` | ✅ | ❌ | ❌ |
| `pip install -e ".[dashboard]"` | ✅ | ✅ | ❌ |
| `pip install -e ".[dev]"` | ✅ | ❌ | ✅ |
| `pip install -e ".[all]"` | ✅ | ✅ | ✅ |

### Basic Usage

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

See [examples/](examples/) for more detailed usage examples.

## 📊 Interactive Dashboard

DVOACAP-Python includes a web-based dashboard for visualizing propagation predictions, DXCC tracking, and real-time band conditions.

### Features

- 🌍 **Interactive Propagation Map** - Visual display of MUF predictions across DX entities
- 📈 **Band Condition Meters** - Real-time signal quality indicators for 160m-10m
- 🏆 **DXCC Progress Tracking** - Monitor worked/confirmed entities by band and mode
- ⚡ **On-Demand Predictions** - One-click refresh with Flask server backend
- 📡 **Live Space Weather Data** - Real-time Kp/A-index, solar flux, and sunspot numbers from NOAA SWPC with international fallback sources
- 🎨 **Responsive Design** - Works on desktop and mobile devices

### Quick Start with Dashboard

**Option A: Flask Server (Recommended)**

```bash
cd Dashboard
pip install -r requirements.txt
python3 server.py

# Visit http://localhost:8000
# Click "⚡ Refresh Predictions" button to generate new predictions
```

The Flask server provides:
- API endpoints for prediction generation (`/api/generate`)
- Real-time progress monitoring (`/api/status`)
- Background processing (non-blocking)
- Automatic dashboard reload when complete

**Option B: Static Files**

```bash
cd Dashboard
python3 generate_predictions.py
open dashboard.html
```

### Configuration

Edit `Dashboard/dvoacap_wrapper.py` to customize:
- Your callsign and QTH coordinates
- Station power and antenna characteristics
- Target bands and DX entities
- Update frequency

### Dashboard Documentation

See [Dashboard/README.md](Dashboard/README.md) for complete setup instructions, configuration options, and API documentation.

### Future Plans

See [Dashboard/ISSUE_MULTI_USER_WEB_APP.md](Dashboard/ISSUE_MULTI_USER_WEB_APP.md) for the roadmap to expand the dashboard into a multi-user community service with:
- User authentication and accounts
- Per-user station configurations
- Database backend for historical tracking
- Public API endpoints
- Mobile app integration
- Community propagation reporting

## 📊 Project Status

**Status: v1.0.0 Production Release** - 86.6% validation accuracy across 11 diverse test paths

### ✅ Completed Modules

- **Phase 1: Path Geometry** ✓
  - Great circle calculations
  - Geodetic/geocentric conversions
  - Path midpoint calculations
  - Bearing calculations
  - *Source: PathGeom.pas*

- **Phase 2: Solar & Geomagnetic** ✓
  - Solar zenith angle calculations
  - Local time conversions
  - Magnetic field model (IGRF)
  - Gyrofrequency calculations
  - *Source: Sun.pas, MagFld.pas*

- **Phase 3: Ionospheric Profiles** ✓
  - CCIR/URSI coefficient models
  - E/F/F1/Es layer critical frequencies
  - Layer height modeling
  - Electron density profiles
  - Ionogram generation
  - True and virtual height calculations
  - *Source: IonoProf.pas, LayrParm.pas, FrMaps.pas*

- **Phase 4: Raytracing** ✓
  - MUF (Maximum Usable Frequency) calculations
  - FOT and HPF calculations
  - Ray path calculations (reflectrix)
  - Skip distance computation
  - Multi-hop path finding
  - Over-the-MUF mode handling
  - *Source: Reflx.pas, MufCalc.pas*

- **Phase 5: Signal Predictions** ✓
  - ✓ Noise modeling (atmospheric, galactic, man-made)
  - ✓ Antenna gain calculations
  - ✓ Prediction engine framework
  - ✓ Full end-to-end integration
  - ✓ **86.6% validation pass rate** across 11 diverse test cases
  - ✓ Real-world validation with PSKReporter/WSPR integration
  - *Source: VoaCapEng.pas, AntGain.pas, NoiseMdl.pas*

### 🚧 In Progress

- **Performance optimization and profiling** - Active development on this branch
  - Identifying and optimizing hot paths in prediction engine
  - Profiling Fourier map interpolation, ionospheric calculations, ray tracing
  - Target: <1s per prediction, <30s for 100-point area coverage

### 📅 Planned

- **PyPI public release** - Package ready (v1.0.0), pending publication decision
- **Comprehensive type hints** - Add type annotations throughout codebase
- **Sphinx API documentation** - Complete API reference with examples
- **Community engagement** - Forum presence, user support, integration examples

## 📚 Documentation

### User Guides
- **[Usage Guide](docs/USAGE.md)** - Comprehensive API usage patterns and examples
- **[Integration Guide](docs/INTEGRATION.md)** - Integrating with web apps, dashboards, and databases
- **[Quick Start](docs/QUICK_START%20v0.1.pdf)** - Getting started guide

### Technical Documentation
- **[Project Status](docs/PROJECT_STATUS.pdf)** - Detailed progress tracker
- **[Phase 1 Summary](docs/PATHGEOMETRY_PORT_SUMMARY.pdf)** - Path geometry implementation
- **[Phase 2 Summary](docs/PHASE2_COMPLETE.pdf)** - Solar & geomagnetic implementation
- **[Phase 3 Summary](docs/PHASE3_COMPLETE.md)** - Ionospheric profiles implementation
- **[Phase 4 Summary](docs/PHASE4_SUMMARY.md)** - Raytracing implementation

### Building Sphinx Documentation

The project includes comprehensive Sphinx documentation with API references. To build it:

**Prerequisites:**
```bash
pip install sphinx sphinx-rtd-theme
```

**Build on Linux/macOS:**
```bash
cd docs
make html
```

**Build on Windows:**

Option 1 - Using the batch file (PowerShell or CMD):
```powershell
cd docs
.\make.bat html
```

Option 2 - Using the PowerShell script:
```powershell
cd docs
.\make.ps1 html
```

Option 3 - Using sphinx-build directly:
```powershell
cd docs
sphinx-build -M html source build
```

The built documentation will be in `docs/build/html/index.html`.

See [docs/README.md](docs/README.md) for more details.

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_path_geometry.py -v

# Run with coverage
pytest --cov=dvoacap tests/
```

## 📦 Package Structure

```
dvoacap-python/
├── src/
│   ├── dvoacap/                    # Main Python package
│   │   ├── __init__.py
│   │   ├── path_geometry.py        # Phase 1
│   │   ├── solar.py                # Phase 2
│   │   ├── geomagnetic.py          # Phase 2
│   │   ├── fourier_maps.py         # Phase 3
│   │   ├── ionospheric_profile.py  # Phase 3
│   │   ├── layer_parameters.py     # Phase 3
│   │   ├── muf_calculator.py       # Phase 4
│   │   └── reflectrix.py           # Phase 4
│   └── original/                   # Reference Pascal source
│       └── *.pas
├── Dashboard/                      # Web-based visualization dashboard
│   ├── server.py                   # Flask API server
│   ├── dashboard.html              # Interactive dashboard UI
│   ├── generate_predictions.py     # Prediction generation script
│   ├── dvoacap_wrapper.py          # DVOACAP integration wrapper
│   ├── requirements.txt            # Server dependencies
│   ├── README.md                   # Dashboard documentation
│   └── ISSUE_MULTI_USER_WEB_APP.md # Multi-user service roadmap
├── tests/                          # Test suite
│   ├── test_path_geometry.py
│   ├── test_voacap_parser.py
│   └── test_ionospheric.py
├── examples/                       # Usage examples
│   ├── integration_example.py
│   ├── phase2_integration_example.py
│   ├── phase3_ionospheric_example.py
│   └── phase4_raytracing_example.py
├── docs/                           # Documentation
│   ├── USAGE.md
│   ├── INTEGRATION.md
│   └── *.pdf
├── DVoaData/                       # CCIR/URSI coefficient data
└── SampleIO/                       # Sample input/output files
```

## 🎓 Technical Background

### What is VOACAP?

VOACAP (Voice of America Coverage Analysis Program) is a professional-grade HF propagation prediction tool based on decades of ionospheric research. It predicts:

- **Maximum Usable Frequency (MUF)** - Highest frequency that will refract back to Earth
- **Signal Strength** - Expected field strength at receiver
- **Reliability** - Probability of successful communication
- **Path Geometry** - Ray paths through the ionosphere

### Why Python?

The original VOACAP is written in Fortran (1970s) and DVOACAP modernized it in Delphi/Pascal. This Python port aims to:

- ✅ Make the code accessible to modern developers
- ✅ Provide clear documentation and examples
- ✅ Enable integration with Python scientific stack (NumPy, SciPy, Matplotlib)
- ✅ Facilitate research and experimentation
- ✅ Maintain numerical accuracy of the original

## 🔬 Validation

### Component-Level Validation ✅

Individual modules validated against original VOACAP/DVOACAP:

- **Path Geometry:** < 0.01% distance error, < 0.01° bearing error
- **Solar Calculations:** < 0.01° zenith angle error
- **Geomagnetic Model:** < 0.1° magnetic latitude error
- **Ionospheric Profiles:** CCIR/URSI maps verified against reference data

### End-to-End Accuracy Validation 🔬

**Reference VOACAP Comparison:**
```bash
# Compare predictions against original VOACAP output
python3 test_voacap_reference.py
```

Validates full propagation predictions (SNR, reliability, MUF) against reference files from the original VOACAP engine. This ensures the integrated system produces accurate results, not just plausible-looking numbers.

**Functional Testing:**
```bash
# Verify engine produces valid output without crashing
python3 validate_predictions.py
```

Tests that predictions execute successfully and produce values in reasonable ranges across representative propagation paths.

**See [VALIDATION_STRATEGY.md](VALIDATION_STRATEGY.md)** for detailed validation methodology, test coverage status, and guidelines for interpreting results.

## 🤝 Contributing

Contributions are welcome! This is a large project with many modules still to port.

**Areas needing help:**
- Porting remaining Pascal modules
- Adding more comprehensive tests
- Improving documentation
- Performance optimization
- Validation against reference data

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📖 References

### Original Projects
- **DVOACAP** - https://github.com/VE3NEA/DVOACAP
- **VOACAP** - Developed by Voice of America / ITS
- **IONCAP** - Original ionospheric model

### Scientific Background
- ITU-R P.533: HF propagation prediction method
- CCIR Report 340: Ionospheric characteristics
- IPS Radio and Space Services documentation

## 📄 License

MIT License - See [LICENSE](LICENSE) for details

**Original DVOACAP License:** Mozilla Public License Version 1.1

## 🙏 Acknowledgments

- **Alex Shovkoplyas (VE3NEA)** - Original DVOACAP implementation
- **Voice of America / ITS** - Original VOACAP development
- Amateur radio and propagation modeling community

## 📧 Contact

- **Repository:** https://github.com/skyelaird/dvoacap-python
- **Issues:** https://github.com/skyelaird/dvoacap-python/issues
- **Original DVOACAP:** https://github.com/VE3NEA/DVOACAP

---

**Note:** This is an active development project. The API may change as we progress through implementation phases. Star ⭐ the repository to follow progress!

**Amateur Radio Operators:** This tool is designed for HF propagation prediction to help you make better contacts! 📻 73!
