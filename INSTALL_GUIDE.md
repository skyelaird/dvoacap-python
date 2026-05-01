# DVOACAP Installation Guide for Ham Radio Clubs

This guide is designed for ham radio club members who want to get started with DVOACAP for HF propagation prediction.

## Prerequisites

**Required:**
- **Python 3.11 or higher** ([Download from python.org](https://www.python.org/downloads/))
- Windows, macOS, or Linux

**That's it!** The installation scripts handle everything else.

## Installation Steps

### Step 1: Download the Scripts

Download these two files:

1. **[install_dvoacap.py](https://raw.githubusercontent.com/skyelaird/dvoacap-python/main/install_dvoacap.py)**
   - Right-click the link → Save Link As...
   - Or copy the URL and paste in your browser

2. **[validate_dvoacap.py](https://raw.githubusercontent.com/skyelaird/dvoacap-python/main/validate_dvoacap.py)**
   - Right-click the link → Save Link As...
   - Or copy the URL and paste in your browser

Save both files to the same folder (e.g., `Documents\DVOACAP\`)

### Step 2: Run the Installer

**On Windows:**
1. Open Command Prompt or PowerShell
2. Navigate to the folder with the scripts:
   ```cmd
   cd Documents\DVOACAP
   ```
3. Run the installer:
   ```cmd
   python install_dvoacap.py
   ```

**On macOS/Linux:**
1. Open Terminal
2. Navigate to the folder with the scripts:
   ```bash
   cd ~/Documents/DVOACAP
   ```
3. Run the installer:
   ```bash
   python3 install_dvoacap.py
   ```

### Step 3: Validate the Installation

After installation completes successfully, run:

```cmd
python validate_dvoacap.py
```

This will:
- ✅ Verify all components are installed correctly
- ✅ Load ionospheric maps
- ✅ Run a real propagation prediction
- ✅ Show you example results

## What You'll See

### During Installation (`install_dvoacap.py`):

```
============================================================
DVOACAP Installation Script
============================================================

Platform: Windows 10
Python: 3.12.0
Python Executable: C:\Users\YourName\AppData\Local\Programs\Python\Python312\python.exe

✓ Python version OK (3.11+)

============================================================
Step 1: Upgrading pip...
============================================================
✓ pip upgraded successfully

============================================================
Step 2: Installing DVOACAP...
============================================================
✓ DVOACAP installed successfully!

============================================================
Step 3: Verifying installation...
============================================================
Name: dvoacap
Version: 1.0.1
Summary: Python port of DVOACAP HF propagation prediction engine
✓ DVOACAP package verified

============================================================
Step 4: Testing import...
============================================================
✓ DVOACAP imported successfully (version 1.0.1)

============================================================
✓ INSTALLATION COMPLETE!
============================================================

Next steps:
1. Run validate_dvoacap.py to verify everything works
2. See examples at: https://github.com/skyelaird/dvoacap-python

Press Enter to exit...
```

### During Validation (`validate_dvoacap.py`):

```
============================================================
DVOACAP Validation Script
============================================================

This script will test your DVOACAP installation
and run a basic HF propagation prediction.

============================================================
[1/4] Testing package import...
============================================================
✓ Successfully imported dvoacap (version 1.0.1)

============================================================
[2/4] Testing core components...
============================================================
✓ Core components available:
  - FourierMaps (ionospheric data)
  - ControlPoint (location/time)
  - IonoPoint (geographic coordinates)
  - compute_iono_params (calculation engine)

============================================================
[3/4] Loading ionospheric maps...
============================================================
Loading CCIR/URSI coefficients...
✓ Ionospheric maps loaded successfully

Setting conditions:
  - Month: June
  - Sunspot Number (SSN): 100 (moderate solar activity)
  - UTC Time: 12:00 (noon)
✓ Conditions set successfully

============================================================
[4/4] Running HF propagation prediction...
============================================================
Computing ionospheric conditions at Halifax, Nova Scotia
Location: 44.65°N, 63.57°W

✓ Prediction calculation successful!

============================================================
IONOSPHERIC PREDICTION RESULTS
============================================================

Location: Halifax, Nova Scotia (44.65°N, 63.57°W)
Date: June
Time: 12:00 UTC (Noon)
Solar Activity: SSN 100 (moderate)

------------------------------------------------------------
IONOSPHERIC LAYERS:
------------------------------------------------------------
E  Layer: foE  =  3.45 MHz  at   110 km altitude
F1 Layer: foF1 =  5.23 MHz  at   200 km altitude
F2 Layer: foF2 =  8.67 MHz  at   300 km altitude
------------------------------------------------------------

What these numbers mean:
  • E Layer (110 km):  Supports frequencies up to 3.4 MHz
  • F1 Layer (200 km): Supports frequencies up to 5.2 MHz
  • F2 Layer (300 km): Supports frequencies up to 8.7 MHz

  Maximum Usable Frequency (MUF): ~26.0 MHz
  (for this location and time)

============================================================
✓ ALL TESTS PASSED!
============================================================

DVOACAP is installed correctly and ready to use.

For more examples and documentation, visit:
https://github.com/skyelaird/dvoacap-python
https://skyelaird.github.io/dvoacap-python/

Press Enter to exit...
```

## Troubleshooting

### "Python is not recognized"

**Problem:** Windows can't find Python in your PATH.

**Solutions:**
1. Reinstall Python and check "Add Python to PATH" during installation
2. Or use the full path to python.exe:
   ```cmd
   C:\Users\YourName\AppData\Local\Programs\Python\Python312\python.exe install_dvoacap.py
   ```

### "Python version 3.11+ required"

**Problem:** Your Python version is too old (3.10 or earlier).

**Solution:** 
- Download and install Python 3.11+ from [python.org](https://www.python.org/downloads/)
- Make sure to install the newer version

### Installation Fails with Permission Error

**Problem:** Don't have permission to install to system Python.

**Solution:** 
- The script automatically uses `--user` flag to install to your user directory
- If still failing, try running Command Prompt as Administrator (Windows) or use `sudo` (macOS/Linux)

### "Cannot import dvoacap" After Installation

**Problem:** Package installed but Python can't find it.

**Solutions:**
1. Close and reopen your terminal/command prompt
2. Make sure you're using the same Python that installed the package:
   ```cmd
   python -m pip show dvoacap
   ```
3. Try uninstalling and reinstalling:
   ```cmd
   pip uninstall dvoacap
   python install_dvoacap.py
   ```

## Next Steps After Installation

### 1. Try the Examples

The repository includes several example scripts:
```bash
git clone https://github.com/skyelaird/dvoacap-python.git
cd dvoacap-python/examples
python complete_prediction_example.py
```

### 2. Write Your First Prediction

Create a file called `my_first_prediction.py`:

```python
from dvoacap import FourierMaps, ControlPoint, IonoPoint, compute_iono_params
import math

# Your QTH coordinates (example: Halifax, NS)
my_lat = 44.65   # degrees North (negative for South)
my_lon = -63.57  # degrees East (negative for West)

# Load ionospheric data
maps = FourierMaps()
maps.set_conditions(
    month=6,           # June (1-12)
    ssn=100,          # Sunspot number (0-200+)
    utc_fraction=0.5   # 12:00 UTC (0.0-1.0)
)

# Create control point at your location
pnt = ControlPoint(
    location=IonoPoint.from_degrees(my_lat, my_lon),
    east_lon=my_lon * math.pi/180,
    distance_rad=0.0,
    local_time=0.5,
    zen_angle=0.3,
    zen_max=1.5,
    mag_lat=55.0 * math.pi/180,
    mag_dip=70.0 * math.pi/180,
    gyro_freq=1.4
)

# Calculate propagation conditions
compute_iono_params(pnt, maps)

# Display results
print(f"\nPropagation Conditions at Your QTH:")
print(f"E  layer: foE  = {pnt.e.fo:.2f} MHz at {pnt.e.hm:.0f} km")
print(f"F1 layer: foF1 = {pnt.f1.fo:.2f} MHz at {pnt.f1.hm:.0f} km")
print(f"F2 layer: foF2 = {pnt.f2.fo:.2f} MHz at {pnt.f2.hm:.0f} km")
print(f"\nEstimated MUF: {pnt.f2.fo * 3.0:.1f} MHz")
```

Run it:
```bash
python my_first_prediction.py
```

### 3. Set Up the Dashboard (Optional)

For a web-based interface with maps and visualizations:

```bash
git clone https://github.com/skyelaird/dvoacap-python.git
cd dvoacap-python/Dashboard
pip install -r requirements.txt
python server.py

# Open your browser to http://localhost:8000
```

See [Dashboard/README.md](Dashboard/README.md) for complete instructions.

## Resources

### Documentation
- **Main Repository:** https://github.com/skyelaird/dvoacap-python
- **Online Docs:** https://skyelaird.github.io/dvoacap-python/
- **PyPI Package:** https://pypi.org/project/dvoacap/

### Getting Help
- **Issues/Questions:** https://github.com/skyelaird/dvoacap-python/issues
- **Discussions:** GitHub Discussions tab
- **Original DVOACAP:** https://github.com/VE3NEA/DVOACAP

### Understanding the Results

**foE, foF1, foF2** = Critical frequencies (in MHz)
- The maximum frequency that can be reflected by each ionospheric layer
- Higher numbers = better propagation conditions

**Layer Heights** (in km)
- E Layer: ~110 km (daytime only, good for regional)
- F1 Layer: ~200 km (daytime only, merges with F2 at night)
- F2 Layer: ~300 km (day and night, best for DX)

**MUF (Maximum Usable Frequency)**
- Highest frequency that will propagate via ionosphere
- Typically 3-4× the critical frequency
- Changes with time of day, season, and solar activity

**SSN (Sunspot Number)**
- 0-30: Solar minimum (low bands work best)
- 50-100: Moderate (mid bands open)
- 100-200+: Solar maximum (high bands wide open)

## Ham Radio Use Cases

### Contest Planning
Predict which bands will be open to which regions at specific times.

### DX Chasing
Find the best time and frequency to work that rare DX entity.

### Emergency Communications
Plan backup frequencies and coverage areas for EMCOMM operations.

### Antenna Planning
Determine optimal antenna height and direction for your target regions.

### Band Analysis
Track propagation trends over the solar cycle for long-term planning.

## For Club Presentations

The repository includes:
- **PRESENTATION_GUIDE.md** - Complete 21-slide presentation outline
- Technical talking points
- Code examples with expected output
- Q&A preparation

This makes it easy to demonstrate DVOACAP to your club members!

---

**Questions?** Open an issue on GitHub or ask at your club meeting!

**73 de DVOACAP-Python Team**
