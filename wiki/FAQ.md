# Frequently Asked Questions (FAQ)

Common questions about DVOACAP-Python and HF propagation prediction.

## Table of Contents

- [General Questions](#general-questions)
- [Installation & Setup](#installation--setup)
- [Usage Questions](#usage-questions)
- [Accuracy & Validation](#accuracy--validation)
- [Performance](#performance)
- [Dashboard Questions](#dashboard-questions)
- [Development](#development)
- [Troubleshooting](#troubleshooting)

---

## General Questions

### What is DVOACAP-Python?

DVOACAP-Python is a Python port of the DVOACAP HF propagation prediction engine, originally written in Delphi/Pascal by Alex Shovkoplyas (VE3NEA). It implements the VOACAP ionospheric propagation model for predicting HF radio propagation conditions.

**Key Features:**
- Predicts MUF (Maximum Usable Frequency)
- Calculates signal strength and reliability
- Models E/F1/F2 ionospheric layers
- Performs raytracing through the ionosphere
- Provides SNR and service probability estimates

---

### What is VOACAP?

**VOACAP** (Voice of America Coverage Analysis Program) is a professional-grade HF propagation prediction tool developed by the Institute for Telecommunication Sciences (ITS) for Voice of America. It's based on decades of ionospheric research and is considered the gold standard for HF propagation prediction.

**DVOACAP** is a Delphi/Pascal port of VOACAP by VE3NEA, and **DVOACAP-Python** is a Python port of DVOACAP.

---

### Why Python instead of the original Fortran/Delphi?

**Advantages of the Python port:**
- ✅ **Accessibility:** Easier for modern developers to understand and use
- ✅ **Integration:** Works with Python scientific stack (NumPy, SciPy, Matplotlib)
- ✅ **Documentation:** Clear, modern documentation
- ✅ **Maintainability:** Easier to extend and modify
- ✅ **Cross-platform:** Works on Windows, macOS, Linux without compilation

**Trade-offs:**
- ⚠️ **Performance:** Python is slower than compiled Fortran/Pascal (but still usable)
- ⚠️ **Maturity:** VOACAP has 40+ years of validation; DVOACAP-Python is in active development

---

### How accurate is DVOACAP-Python?

**Current validation status:**
- **Phase 1-4 (Geometry, Solar, Ionosphere, Raytracing):** >95% validation pass rate
- **Phase 5 (Signal Predictions):** 83.8% validation pass rate

This means 83.8% of predictions match reference VOACAP output within acceptable tolerances. The remaining 16.2% show discrepancies being investigated and resolved.

See [Validation Status](Validation-Status) and [Known Issues](Known-Issues) for details.

---

### Can I trust DVOACAP-Python for critical applications?

**Short answer:** For most amateur radio use cases, yes.

**Detailed answer:**
- **Amateur radio planning:** ✅ Excellent
- **Contest planning:** ✅ Very good
- **DXpedition planning:** ✅ Good (cross-check with VOACAP Online)
- **Broadcast planning:** ⚠️ Use production VOACAP (Fortran version)
- **Military/critical comms:** ⚠️ Use validated production tools

**Recommendation:** For critical applications, validate predictions against operational data or cross-check with the original VOACAP.

---

### Is DVOACAP-Python free?

Yes! DVOACAP-Python is open source under the **MIT License**. You can use it freely for personal, commercial, or educational purposes.

---

### How does DVOACAP-Python compare to other propagation tools?

| Tool | Accuracy | Speed | Ease of Use | Cost |
|------|----------|-------|-------------|------|
| **VOACAP** (Fortran) | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | Free |
| **DVOACAP** (Delphi) | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | Free |
| **DVOACAP-Python** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Free |
| **VOACAP Online** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Free |
| **PropPy** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Free |
| **ITU-R P.533** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Free |

**DVOACAP-Python's niche:** Easy integration into Python applications with good accuracy.

---

## Installation & Setup

### What are the system requirements?

**Minimum:**
- Python 3.8 or higher
- 200 MB disk space
- 512 MB RAM

**Recommended:**
- Python 3.10 or higher
- 500 MB disk space (with dependencies)
- 1 GB RAM

**Operating Systems:**
- ✅ Linux (Ubuntu, Debian, Fedora, etc.)
- ✅ macOS (Intel and Apple Silicon)
- ✅ Windows 10/11

---

### How do I install DVOACAP-Python?

**Basic installation:**
```bash
git clone https://github.com/skyelaird/dvoacap-python.git
cd dvoacap-python
pip install -e .
```

**With dashboard:**
```bash
pip install -e ".[dashboard]"
```

**With all extras (development):**
```bash
pip install -e ".[all]"
```

See [Getting Started](Getting-Started) for detailed instructions.

---

### Do I need the original VOACAP installed?

**No!** DVOACAP-Python is a standalone implementation. You don't need VOACAP, DVOACAP, or any other external propagation software.

The only data files needed are the CCIR/URSI coefficient maps, which are included in the repository (`DVoaData/` directory).

---

### Can I install DVOACAP-Python with pip from PyPI?

**Not yet.** DVOACAP-Python is currently in active development and not published to PyPI. Install from source using:

```bash
pip install -e .
```

Once the project reaches v1.0, it will be published to PyPI for easier installation with:
```bash
pip install dvoacap  # Future release
```

---

## Usage Questions

### How do I run a basic prediction?

```python
from dvoacap import PredictionEngine
from dvoacap.path_geometry import GeoPoint
import numpy as np

# Create engine
engine = PredictionEngine()

# Configure
engine.params.ssn = 100.0
engine.params.month = 6
engine.params.tx_location = GeoPoint.from_degrees(40.0, -75.0)  # Philadelphia

# Run prediction
rx_location = GeoPoint.from_degrees(51.5, -0.1)  # London
engine.predict(rx_location=rx_location, utc_time=0.5, frequencies=[14.0])

# Get results
print(f"MUF: {engine.muf_calculator.muf:.2f} MHz")
print(f"SNR: {engine.predictions[0].signal.snr_db:.1f} dB")
```

See [Quick Examples](Quick-Examples) for more examples.

---

### What frequency range does DVOACAP-Python support?

**HF range:** 1.6 MHz - 30 MHz (160m through 10m bands)

**Tested bands:**
- 160m (1.8 MHz) ✅
- 80m (3.5 MHz) ✅
- 40m (7 MHz) ✅
- 30m (10 MHz) ✅
- 20m (14 MHz) ✅
- 17m (18 MHz) ✅
- 15m (21 MHz) ✅
- 12m (24 MHz) ✅
- 10m (28 MHz) ✅

**Note:** Frequencies > 30 MHz may work but are less validated.

---

### What solar and geomagnetic parameters do I need?

**Required parameters:**
- **Month:** 1-12
- **UTC time:** 0-24 hours

**Automatically fetched (when using Dashboard):**
- **SFI (Solar Flux Index):** Fetched live from NOAA SWPC (F10.7 cm flux)
- **SSN (Sunspot Number):** Fetched live from NOAA SWPC (observed solar cycle indices)
- **Kp index:** Fetched live from NOAA SWPC (planetary K-index)
- **A-index:** Fetched live from NOAA SWPC (predicted A-index)

**For manual API usage:**
- **SSN (Sunspot Number):** 0-300 (typical: 0-200)
- **Kp index:** 0-9 (typical: 0-5, defaults to 2 for quiet conditions)
- **A-index:** 0-400 (typical: 0-50, defaults to 10 for low absorption)

**Data Sources:**
- NOAA SWPC: https://www.swpc.noaa.gov/
- Dashboard auto-fetches from: https://services.swpc.noaa.gov/json/
- Manual fetch: See `Dashboard/generate_predictions.py` for implementation

---

### Can I predict long-path propagation?

**Yes!** The PathGeometry module supports both short-path and long-path calculations.

```python
from dvoacap.path_geometry import PathGeometry, GeoPoint

tx = GeoPoint.from_degrees(40.0, -75.0)
rx = GeoPoint.from_degrees(51.5, -0.1)

path = PathGeometry()
path.set_tx_rx(tx, rx)

# Short path (default)
short_distance = path.get_distance_km()
print(f"Short path: {short_distance:.0f} km")

# Long path
long_distance = (2 * 3.14159 * 6370) - short_distance
print(f"Long path: {long_distance:.0f} km")
```

---

### How do I specify antenna characteristics?

**Currently:** DVOACAP-Python uses simplified antenna models. You can specify:
- Transmit power (watts)
- Basic antenna gain patterns

**Future:** Full antenna modeling (Yagi, log-periodic, etc.) is planned.

---

## Accuracy & Validation

### Why is the validation pass rate only 83.8%?

The 83.8% pass rate for Phase 5 indicates that **83.8% of predictions match reference VOACAP within tolerances**. The remaining 16.2% show discrepancies due to:

1. **Numerical differences** - Python vs. Pascal floating-point operations
2. **Mode selection variations** - Different propagation mode choices
3. **Edge cases** - Extreme solar conditions, high latitudes, very short/long paths
4. **Over-the-MUF handling** - Different approaches when frequency > MUF

**Important:** Even "failed" test cases typically show SNR differences < 3 dB, which is operationally acceptable for amateur radio.

See [Known Issues](Known-Issues) for details.

---

### How do I validate predictions against real-world data?

**Methods:**
1. **Compare with operational results** - Check predictions against actual QSOs
2. **PSKreporter integration** - Compare with real-time reception reports
3. **Contest log analysis** - Analyze QSO logs vs. predictions
4. **Cross-check with VOACAP Online** - Verify against reference implementation

The dashboard includes optional PSKreporter validation.

---

## Performance

### Why are predictions slow?

DVOACAP predictions are **computationally intensive** because they perform full raytracing through a 3D ionospheric model.

**Typical times:**
- Single prediction: ~200-500 ms
- Full band sweep (7 frequencies): ~2-3 seconds
- 24-hour forecast (12 time points): ~25-35 seconds
- Full dashboard (10 regions × 7 bands): ~60-90 seconds

**Why it's slow:**
- Iterative raytracing (Phase 4)
- CCIR coefficient processing (Phase 3)
- Python overhead vs. compiled code

See [Performance Tips](Performance-Tips) for optimization strategies.

---

### Can I speed up predictions?

**Yes! Several approaches:**

1. **Reduce number of regions/frequencies:**
   ```python
   # Fewer regions = faster
   TARGET_REGIONS = {'EU': ..., 'JA': ...}  # Instead of 10 regions
   ```

2. **Increase time step:**
   ```python
   # Predict every 3 hours instead of 2
   utc_hours = [0, 3, 6, 9, 12, 15, 18, 21]
   ```

3. **Reuse PredictionEngine:**
   ```python
   engine = PredictionEngine()  # Create once
   # Reuse for multiple predictions
   ```

4. **Cache results:**
   Predictions for the same conditions are identical - cache and reuse.

See [Performance Tips](Performance-Tips) for details.

---

## Dashboard Questions

### How do I access the dashboard?

**Method 1: Flask Server (Recommended)**
```bash
cd Dashboard
python3 server.py

# Visit http://localhost:8000
```

**Method 2: Static Files**
```bash
cd Dashboard
python3 generate_predictions.py
open dashboard.html
```

See [Dashboard Guide](Dashboard-Guide) for complete setup.

---

### How often should I update predictions?

**Recommended update frequency:**
- **Normal conditions:** Every 2-4 hours
- **After solar events:** Immediately (flares, CMEs)
- **Before operating sessions:** Generate fresh predictions
- **Automated setup:** Every 2 hours via cron/scheduler

**Solar conditions change slowly** (hours to days), so updating every 2-4 hours is sufficient.

---

### Can I customize the dashboard for my station?

**Yes!** Edit `Dashboard/generate_predictions.py`:

```python
MY_QTH = {
    'call': 'YOUR_CALL',
    'lat': YOUR_LATITUDE,
    'lon': YOUR_LONGITUDE,
    'grid': 'YOUR_GRID',
    'antenna': 'Your Antenna Description',
}

TARGET_REGIONS = {
    # Add your target regions
}

BANDS = {
    # Configure your bands
}
```

See [Dashboard Guide](Dashboard-Guide) for details.

---

### Can multiple users share one dashboard?

**Current version:** No, the dashboard is single-user.

**Future plan:** A multi-user web service is planned. See `Dashboard/ISSUE_MULTI_USER_WEB_APP.md` for the roadmap.

---

## Development

### How can I contribute to DVOACAP-Python?

We welcome contributions! Areas needing help:

- **Validation:** Identify and fix failing test cases
- **Performance:** Optimize hot paths (Cython, Numba)
- **Features:** Es modeling, antenna patterns, output formats
- **Documentation:** Examples, tutorials, API docs
- **Testing:** Add test coverage

See [Contributing Guide](Contributing) for guidelines.

---

### What development tools do I need?

**Essential:**
- Python 3.8+
- pytest (testing)
- black (formatting)
- flake8 (linting)

**Install all dev tools:**
```bash
pip install -e ".[dev]"
```

See [Development Setup](Development-Setup) for complete setup.

---

### How do I run tests?

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=dvoacap tests/

# Run validation
python3 test_voacap_reference.py
```

See [Testing Guide](Testing-Guide) for details.

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'dvoacap'"

**Cause:** Package not installed or not in Python path.

**Solution:**
```bash
# From repository root
pip install -e .
```

---

### Dashboard shows "No data available"

**Cause:** Predictions haven't been generated.

**Solution:**
```bash
cd Dashboard
python3 generate_predictions.py
```

---

### Predictions fail with "Path not feasible"

**Cause:** The propagation path is not possible under current conditions (e.g., frequency too high, path too long).

**Solution:**
- Try a lower frequency
- Check MUF and use frequencies below FOT (Frequency of Optimum Traffic)
- Verify solar conditions are reasonable

---

### Tests fail after installation

**Cause:** Missing test dependencies or data files.

**Solution:**
```bash
# Install dev dependencies
pip install -e ".[dev]"

# Ensure you're in repository root
cd /path/to/dvoacap-python
pytest
```

---

### Dashboard "Refresh Predictions" button fails

**Cause:** Missing dependencies or import errors.

**Solution:**
```bash
# Install dashboard dependencies
pip install -e ".[dashboard]"

# Test generator directly
cd Dashboard
python3 generate_predictions.py
```

---

## Still Have Questions?

**Resources:**
- **[Wiki Home](Home)** - Main documentation
- **[Troubleshooting](Troubleshooting)** - Common issues and solutions
- **[GitHub Issues](https://github.com/skyelaird/dvoacap-python/issues)** - Report bugs or ask questions
- **[API Reference](API-Reference)** - Code documentation

**Contact:**
- Open an issue on GitHub
- Check existing issues for similar questions
- See README for project links

---

**73!** Happy HF propagation predicting! 📻
