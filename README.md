# DVOACAP-Python 📡

> Python port of DVOACAP (Digital Voice of America Coverage Analysis Program) - An HF radio propagation prediction engine

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![Progress](https://img.shields.io/badge/progress-80%25-green)

## 🎯 About

DVOACAP-Python is a modern Python port of the [DVOACAP](https://github.com/VE3NEA/DVOACAP) HF propagation prediction engine, originally written in Delphi/Pascal by Alex Shovkoplyas (VE3NEA). This project aims to provide an accessible, well-documented, and maintainable Python implementation of the VOACAP ionospheric propagation model.

**Original DVOACAP by:** Alex Shovkoplyas, VE3NEA  
**Python Port:** In Progress (2025)

## ⚡ Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/skyelaird/dvoacap-python.git
cd dvoacap-python

# Install in development mode
pip install -e .
```

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

## 📊 Project Status

**Current Phase: 4 of 5 Complete (80%)**

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

### 🚧 In Progress

- None currently

### 📅 Planned

- **Phase 5: Signal Predictions**
  - MUF/FOT/LUF calculations
  - Signal strength prediction
  - Reliability estimates
  - *Source: VoaCapEng.pas*

## 📚 Documentation

- **[Quick Start](docs/QUICK_START%20v0.1.pdf)** - Getting started guide
- **[Project Status](docs/PROJECT_STATUS.pdf)** - Detailed progress tracker
- **[Phase 1 Summary](docs/PATHGEOMETRY_PORT_SUMMARY.pdf)** - Path geometry implementation
- **[Phase 2 Summary](docs/PHASE2_COMPLETE.pdf)** - Solar & geomagnetic implementation
- **[Phase 3 Summary](docs/PHASE3_COMPLETE.pdf)** - Ionospheric profiles implementation
- **[Phase 4 Summary](docs/PHASE4_COMPLETE.pdf)** - Raytracing implementation (to be created)

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

All modules are validated against the original VOACAP/DVOACAP:

- **Path Geometry:** < 0.01% distance error, < 0.01° bearing error
- **Solar Calculations:** < 0.01° zenith angle error
- **Geomagnetic Model:** < 0.1° magnetic latitude error
- **Ionospheric Profiles:** CCIR/URSI maps verified against reference data

## 🤝 Contributing

Contributions are welcome! This is a large project with many modules still to port.

**Areas needing help:**
- Porting remaining Pascal modules
- Adding more comprehensive tests
- Improving documentation
- Performance optimization
- Validation against reference data

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines (coming soon).

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
