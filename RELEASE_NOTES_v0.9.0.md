# DVOACAP-Python v0.9.0 - Beta Release

## 🎉 What's New

DVOACAP-Python is now feature-complete with **86.6% validation accuracy** against reference VOACAP data!

This beta release marks a major milestone: the core propagation engine is complete and ready for early adopters, developers, and testers.

## 📦 Installation

### For Developers and Library Users:
```bash
pip install dvoacap
```

### For Dashboard Users (includes web interface):
```bash
pip install dvoacap[dashboard]
```

### Using Docker:
```bash
docker pull skyelaird/dvoacap-dashboard:0.9.0
docker run -p 8000:8000 skyelaird/dvoacap-dashboard:0.9.0
```

## ✨ Core Features

### Complete Propagation Engine (Phases 1-5)

✅ **Phase 1: Path Geometry**
- Great circle path calculations
- Control point determination
- Distance and bearing computations

✅ **Phase 2: Solar & Geomagnetic**
- Solar position calculations
- Sunspot number integration
- Geomagnetic field modeling

✅ **Phase 3: Ionospheric Modeling**
- CCIR/URSI coefficient loading
- Ionospheric profile generation
- Critical frequency calculations
- F2 layer foF2 and M(3000)F2 modeling

✅ **Phase 4: MUF Calculations**
- Maximum Usable Frequency (MUF) computation
- Frequency of Optimum Traffic (FOT) determination
- Multi-hop propagation support
- Layer-specific MUF calculations

✅ **Phase 5: Signal Predictions**
- Signal power calculations
- D-layer and E-layer absorption
- Antenna gain modeling
- Noise floor integration
- Signal-to-Noise Ratio (SNR) predictions
- Reliability calculations

### Production-Ready Library

- 📘 Clean Python API for programmatic access
- 📊 All required CCIR/URSI ionospheric data files included
- 🧪 Comprehensive test suite with 86.6% validation rate
- 📚 Example code and documentation
- 🔄 Compatible with Python 3.11, 3.12, 3.13

### Interactive Dashboard

- 🌐 Flask web server with real-time predictions
- ☀️ Space weather integration (NOAA SWPC)
- 🌍 DXCC entity tracking
- 🐳 Docker support for easy deployment
- 📡 Point-to-point propagation analysis

## 📊 Validation Results

- **226 of 261 tests passing (86.6% accuracy)**
- Validated against reference VOACAP outputs
- Real-world validation with PSKReporter data
- Comprehensive test coverage across 11 diverse scenarios:
  - Short paths (US East Coast, Europe)
  - Medium paths (Transatlantic, US-Japan)
  - Long paths (Antipodal, Australia)
  - Equatorial paths
  - Polar/Arctic paths
  - Solar maximum conditions
  - Solar minimum conditions

### Known Differences from Reference

The 35 failing tests show consistent patterns:
- Most failures are in low-reliability scenarios (<10%)
- Some discrepancies in E-layer absorption calculations
- Minor differences in auroral zone modeling
- See [PHASE5_VALIDATION_REPORT.md](PHASE5_VALIDATION_REPORT.md) for details

## 📚 Documentation

- **[README.md](README.md)** - Project overview and quick start
- **[PYPI_RELEASE_GUIDE.md](PYPI_RELEASE_GUIDE.md)** - Release process documentation
- **[PYPI_SETUP_GUIDE.md](PYPI_SETUP_GUIDE.md)** - Step-by-step PyPI setup
- **[V1_RELEASE_PLAN.md](V1_RELEASE_PLAN.md)** - Roadmap for v1.0.0
- **[PHASE5_VALIDATION_REPORT.md](PHASE5_VALIDATION_REPORT.md)** - Detailed validation results
- **Wiki** - Comprehensive guides and API reference

## 🔮 What's Coming in v1.0 (December 2025)

### Dashboard Enhancements
- Enhanced propagation charts (REL/SDBW/SNR over 24 hours)
- Propagation wheel visualization
- Mini planner for DXCC targeting
- Best frequency recommendations
- Improved UI/UX

### Library Improvements
- Performance optimizations
- Complete API documentation
- Additional usage examples
- Enhanced error handling

See [V1_RELEASE_PLAN.md](V1_RELEASE_PLAN.md) for the complete roadmap.

## 🚀 Quick Start

### Basic Usage

```python
from dvoacap import ControlPoint, FourierMaps, IonosphericProfile, MufCalculator

# Define transmitter and receiver
tx = ControlPoint(latitude=40.0, longitude=-75.0)  # Philadelphia
rx = ControlPoint(latitude=51.5, longitude=-0.1)   # London

# Set ionospheric conditions
fourier_maps = FourierMaps()
fourier_maps.set_conditions(
    month=6,           # June
    ssn=100,           # Sunspot number
    utc_fraction=12.0  # Noon UTC
)

# Calculate ionospheric profile at midpoint
profile = IonosphericProfile()
profile.calculate_profile(
    control_point=tx.midpoint(rx),
    fourier_maps=fourier_maps
)

# Calculate MUF
muf_calc = MufCalculator()
muf = muf_calc.calculate_muf(tx, rx, profile)
print(f"MUF: {muf:.2f} MHz")
```

### Running the Dashboard

```bash
# Install with dashboard dependencies
pip install dvoacap[dashboard]

# Run the server
cd Dashboard
python server.py

# Open browser to http://localhost:8000
```

## 📦 What's Included

### Python Package (`dvoacap`)
- 14 core modules implementing full propagation engine
- 24 ionospheric data files (CCIR/URSI coefficients)
- Type hints for better IDE support
- Comprehensive docstrings

### Dashboard Application
- Flask web server
- React-based frontend (planned for v1.0)
- RESTful API endpoints
- Docker deployment support

## 🙏 Acknowledgments

- **Alex Shovkoplyas (VE3NEA)** - Original DVOACAP Delphi implementation
- **NOAA Space Weather Prediction Center** - Real-time space weather data
- **Amateur radio community** - Testing, feedback, and validation data
- **PSKReporter** - Real-world propagation validation data

## 📝 Release Notes

### Changed
- Fixed license metadata format in pyproject.toml (SPDX expression)
- Improved package building and distribution

### Added
- Comprehensive PyPI release workflow (GitHub Actions)
- Detailed PyPI setup guide
- Release automation documentation

### Technical Details
- Source Distribution: 1.4 MB (includes all data files)
- Wheel Package: 528 KB
- Python Version: ≥3.11
- Dependencies: numpy>=1.20.0
- Optional Dependencies: flask, flask-cors, requests (for dashboard)

## 🐛 Known Issues

- Dashboard UI is functional but basic (v1.0 will have major improvements)
- Some edge cases in E-layer absorption modeling
- Performance could be optimized for batch calculations
- See [Known-Issues](wiki/Known-Issues.md) in the wiki for complete list

## 🔗 Links

- **PyPI Package:** https://pypi.org/project/dvoacap/
- **Documentation:** https://github.com/skyelaird/dvoacap-python/wiki
- **Bug Reports:** https://github.com/skyelaird/dvoacap-python/issues
- **Original DVOACAP:** https://github.com/VE3NEA/DVOACAP

## 💬 Feedback Welcome!

This is a beta release. Your feedback is valuable:
- Report bugs via GitHub Issues
- Suggest features via Discussions
- Share your use cases
- Contribute code via Pull Requests

---

**73 de VE1ATM** 📻

Happy propagation predictions!
