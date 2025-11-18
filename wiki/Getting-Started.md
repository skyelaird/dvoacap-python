# Getting Started with DVOACAP-Python

> **🎉 v1.0.1 Release - Production Ready with 2.3x Performance Boost!**
> DVOACAP-Python has reached production-ready status with comprehensive HF propagation prediction capabilities validated against VOACAP reference data. Version 1.0.1 delivers a 2.3x speedup through algorithmic optimizations.

This guide will help you install DVOACAP-Python and run your first propagation prediction.

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- git (for cloning the repository)

## Installation Options

Choose the installation option that fits your needs:

### Option 1: Core Library Only (Lightweight)

For developers who want just the propagation engine without the web dashboard:

```bash
# Clone the repository
git clone https://github.com/skyelaird/dvoacap-python.git
cd dvoacap-python

# Install just the propagation engine
pip install -e .
```

**Includes:**
- Core propagation prediction engine
- All ionospheric data files (CCIR/URSI maps)
- Basic command-line tools

**Disk space:** ~50 MB

### Option 2: With Dashboard (Recommended for Most Users)

Includes the Flask server and web-based visualization dashboard:

```bash
# Clone the repository
git clone https://github.com/skyelaird/dvoacap-python.git
cd dvoacap-python

# Install library + dashboard dependencies
pip install -e ".[dashboard]"
```

**Includes:**
- Everything from Option 1
- Flask web server
- Interactive dashboard UI
- Real-time visualization tools

**Disk space:** ~60 MB

### Option 3: Development Setup (For Contributors)

Includes all dependencies plus testing and development tools:

```bash
# Clone the repository
git clone https://github.com/skyelaird/dvoacap-python.git
cd dvoacap-python

# Install everything
pip install -e ".[all]"
```

**Includes:**
- Everything from Options 1 and 2
- pytest and testing tools
- Development utilities
- Code quality tools

**Disk space:** ~70 MB

## Verification

Verify your installation:

```bash
# Test the installation
python -c "from dvoacap import FourierMaps; print('DVOACAP installed successfully!')"

# Run basic tests (development installation only)
pytest tests/test_path_geometry.py -v
```

## Your First Prediction

### Basic Example: Ionospheric Parameters

This example computes ionospheric parameters at a single location:

```python
from dvoacap import FourierMaps, ControlPoint, IonoPoint, compute_iono_params
import math

# Load CCIR/URSI ionospheric maps
maps = FourierMaps()
maps.set_conditions(month=6, ssn=100, utc_fraction=0.5)  # June, SSN=100, noon UTC

# Create control point at Philadelphia
pnt = ControlPoint(
    location=IonoPoint.from_degrees(40.0, -75.0),
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

# Display results
print(f"E layer:  foE  = {pnt.e.fo:.2f} MHz at {pnt.e.hm:.0f} km")
print(f"F1 layer: foF1 = {pnt.f1.fo:.2f} MHz at {pnt.f1.hm:.0f} km")
print(f"F2 layer: foF2 = {pnt.f2.fo:.2f} MHz at {pnt.f2.hm:.0f} km")
```

**Expected output:**
```
E layer:  foE  = 3.45 MHz at 110 km
F1 layer: foF1 = 5.20 MHz at 200 km
F2 layer: foF2 = 8.50 MHz at 300 km
```

### Advanced Example: Path Prediction

Predict propagation between two locations:

```python
from dvoacap import PredictionEngine
from datetime import datetime

# Initialize prediction engine
engine = PredictionEngine()

# Configure prediction
result = engine.predict(
    tx_lat=40.0,  # Philadelphia
    tx_lon=-75.0,
    rx_lat=51.5,  # London
    rx_lon=-0.1,
    frequency=14.2,  # 20m band
    utc_time=datetime(2025, 6, 15, 12, 0),  # Noon UTC
    ssn=100,  # Solar activity
    tx_power=100,  # Watts
    tx_antenna_gain=2.0  # dBi
)

# Display results
print(f"MUF: {result.muf:.2f} MHz")
print(f"Signal strength: {result.snr:.1f} dB")
print(f"Reliability: {result.reliability:.0f}%")
print(f"Best frequency: {result.fot:.2f} MHz")
```

## Using the Dashboard

If you installed with dashboard support, start the web interface:

```bash
cd Dashboard
pip install -r requirements.txt
python3 server.py
```

Then open your browser to: [http://localhost:8000](http://localhost:8000)

**Dashboard Features:**
- Interactive propagation map
- Real-time band condition meters
- DXCC tracking
- Solar data integration
- One-click prediction updates

See the [Dashboard Guide](Dashboard-Guide) for complete documentation.

## Common Installation Issues

### Issue: "ModuleNotFoundError: No module named 'dvoacap'"

**Solution:**
```bash
# Make sure you're in the repository directory
cd dvoacap-python

# Reinstall in editable mode
pip install -e .
```

### Issue: "Permission denied" when installing

**Solution:**
```bash
# Install in user directory (no sudo required)
pip install -e . --user
```

### Issue: "numpy" or "scipy" installation fails

**Solution:**
```bash
# Install numpy and scipy separately first
pip install numpy scipy

# Then install DVOACAP
pip install -e .
```

### Issue: Dashboard won't start

**Solution:**
```bash
# Make sure Flask is installed
pip install flask

# Check if port 8000 is available
lsof -i :8000

# Use a different port if needed
python3 server.py --port 8080
```

## Next Steps

Now that you have DVOACAP-Python installed:

1. **[API Reference](API-Reference)** - Learn about core classes and methods
2. **[Architecture](Architecture)** - Understand the 5-phase structure
3. **[Integration Guide](Integration-Guide)** - Build applications with DVOACAP
4. **[Dashboard Guide](Dashboard-Guide)** - Customize the web interface
5. **[Examples Repository](https://github.com/skyelaird/dvoacap-python/tree/main/examples)** - More code examples

## Getting Help

- **Issues:** [github.com/skyelaird/dvoacap-python/issues](https://github.com/skyelaird/dvoacap-python/issues)
- **Discussions:** [github.com/skyelaird/dvoacap-python/discussions](https://github.com/skyelaird/dvoacap-python/discussions)
- **Troubleshooting:** [Troubleshooting Guide](Troubleshooting)

---

**Ready to make some predictions!** 📡 73!
