# DVOACAP-Python 📡

> Python port of DVOACAP (Digital Voice of America Coverage Analysis Program) - An HF radio propagation prediction engine

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![Progress](https://img.shields.io/badge/progress-36%25-orange)

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
from dvoacap.solar import SolarCalculator, GeographicPoint
from dvoacap.geomagnetic import GeomagneticCalculator
from datetime import datetime

# Define location
location = GeographicPoint.from_degrees(44.374, -64.300)  # Halifax, NS

# Calculate solar conditions
solar_calc = SolarCalculator()
time = datetime(2024, 6, 15, 12, 0)  # Noon UTC
zenith = solar_calc.calculate_zenith_angle(location, time)
print(f"Solar zenith angle: {math.degrees(zenith):.1f}°")

# Calculate geomagnetic parameters
geo_calc = GeomagneticCalculator()
params = geo_calc.calculate_parameters(location)
print(f"Magnetic latitude: {math.degrees(params.magnetic_latitude):.1f}°")
print(f"Gyrofrequency: {params.gyrofrequency:.3f} MHz")
```

See [examples/](examples/) for more detailed usage examples.

## 📊 Project Status

**Current Phase: 2 of 5 Complete (36%)**

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

### 🚧 In Progress

- **Phase 3: Ionospheric Profiles**
  - CCIR/URSI coefficient models
  - E/F layer critical frequencies
  - Layer height modeling
  - *Source: IonoProf.pas, LayrParm.pas, FrMaps.pas*

### 📅 Planned

- **Phase 4: Raytracing**
  - Ray path calculations
  - Skip distance computation
  - Multi-hop paths
  - *Source: Reflx.pas, MufCalc.pas*

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
│   ├── dvoacap/              # Main Python package
│   │   ├── __init__.py
│   │   ├── path_geometry.py  # Phase 1
│   │   ├── solar.py          # Phase 2
│   │   └── geomagnetic.py    # Phase 2
│   └── original/             # Reference Pascal source
│       └── *.pas
├── tests/                    # Test suite
│   └── test_*.py
├── examples/                 # Usage examples
│   ├── integration_example.py
│   └── phase2_integration_example.py
├── docs/                     # Documentation
│   └── *.pdf
├── DVoaData/                 # CCIR/URSI coefficient data
└── SampleIO/                 # Sample input/output files
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
