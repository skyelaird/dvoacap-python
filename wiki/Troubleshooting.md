# Troubleshooting Guide

Common issues and solutions when using DVOACAP-Python.

## Installation Issues

### ModuleNotFoundError: No module named 'dvoacap'

**Problem:** Python can't find the DVOACAP module after installation.

**Solutions:**

1. **Make sure you're in the repository directory:**
   ```bash
   cd dvoacap-python
   pip install -e .
   ```

2. **Check your Python environment:**
   ```bash
   which python3
   pip3 list | grep dvoacap
   ```

3. **Try reinstalling in user directory:**
   ```bash
   pip install -e . --user
   ```

4. **Verify you're using the correct Python:**
   ```bash
   python3 -c "import dvoacap; print(dvoacap.__version__)"
   ```

---

### Permission denied during installation

**Problem:** `pip install` fails with permission errors.

**Solution:** Install in user directory without sudo:
```bash
pip install -e . --user
```

**Never use sudo with pip** - this can break your system Python.

---

### NumPy or SciPy installation fails

**Problem:** `pip install` fails when installing numpy or scipy dependencies.

**Solutions:**

1. **Install dependencies separately first:**
   ```bash
   pip install numpy scipy
   pip install -e .
   ```

2. **On Ubuntu/Debian, install system packages:**
   ```bash
   sudo apt-get install python3-numpy python3-scipy
   pip install -e .
   ```

3. **On macOS with Homebrew:**
   ```bash
   brew install numpy scipy
   pip install -e .
   ```

4. **Use conda (alternative approach):**
   ```bash
   conda create -n dvoacap python=3.10
   conda activate dvoacap
   conda install numpy scipy matplotlib
   pip install -e .
   ```

---

### CCIR/URSI data files not found

**Problem:** `FileNotFoundError: DVoaData/CCIR*.asc not found`

**Solution:** Make sure the data files are present:
```bash
ls DVoaData/CCIR*.asc | wc -l  # Should show 168
ls DVoaData/URSI*.asc | wc -l  # Should show 168
```

If files are missing, clone the repository again:
```bash
git clone https://github.com/skyelaird/dvoacap-python.git
```

---

## Prediction Issues

### Predictions show 0% reliability

**Problem:** All predictions return 0% reliability regardless of path.

**Status:** Known bug in Phase 5 (see [Validation Status](Validation-Status))

**Workaround:** None currently - bug is being fixed

**Tracking:** See `NEXT_STEPS.md` Priority 1

---

### SNR values seem wrong

**Problem:** Signal-to-Noise Ratio predictions don't match expectations.

**Debugging steps:**

1. **Check input parameters:**
   ```python
   # Verify coordinates are correct
   print(f"TX: {tx_lat}, {tx_lon}")
   print(f"RX: {rx_lat}, {rx_lon}")

   # Check frequency is in MHz (not kHz!)
   print(f"Frequency: {frequency} MHz")
   ```

2. **Verify solar conditions:**
   ```python
   # SSN should be 0-200
   # Higher SSN = better HF propagation
   print(f"SSN: {ssn}")
   ```

3. **Check time of day:**
   ```python
   # UTC time affects ionosphere
   # Daytime vs nighttime matters
   print(f"UTC: {utc_time}")
   ```

4. **Run with debug logging:**
   ```bash
   python3 validate_predictions.py --debug <region> <band>
   ```

---

### MUF predictions are unrealistic

**Problem:** Maximum Usable Frequency values seem too high or too low.

**Typical MUF ranges:**
- **Low solar activity (SSN < 50):** 10-20 MHz
- **Medium solar activity (SSN 50-150):** 15-30 MHz
- **High solar activity (SSN > 150):** 20-40 MHz

**Debugging:**

1. **Check solar activity (SSN):**
   ```python
   # SSN must be 0-200
   # Current solar cycle (2025): ~100-150
   ```

2. **Verify time of day:**
   ```python
   # Daytime MUF is higher than nighttime
   # Use UTC, not local time
   ```

3. **Check path distance:**
   ```python
   # Short paths (< 1000 km): Lower MUF
   # Long paths (> 5000 km): Higher MUF
   ```

---

### AttributeError: 'ControlPoint' object has no attribute 'e'

**Problem:** Layer parameters not computed before use.

**Solution:** Call `compute_iono_params()` first:
```python
from dvoacap import ControlPoint, FourierMaps, compute_iono_params

pnt = ControlPoint(...)  # Create control point
maps = FourierMaps()
maps.set_conditions(month=6, ssn=100, utc_fraction=0.5)

# MUST call this before accessing pnt.e, pnt.f1, pnt.f2
compute_iono_params(pnt, maps)

# Now you can access layer parameters
print(f"foE: {pnt.e.fo} MHz")
```

---

### ValueError: Invalid latitude/longitude

**Problem:** Coordinate validation fails.

**Solution:** Check coordinate ranges:
```python
# Latitude: -90 to +90 (south to north)
# Longitude: -180 to +180 (west to east)

# ✓ Correct
tx = GeographicPoint.from_degrees(40.0, -75.0)

# ✗ Wrong (longitude out of range)
tx = GeographicPoint.from_degrees(40.0, -275.0)

# ✗ Wrong (latitude out of range)
tx = GeographicPoint.from_degrees(140.0, -75.0)
```

---

## Dashboard Issues

### Dashboard won't start - "Address already in use"

**Problem:** Port 8000 is already in use by another process.

**Solutions:**

1. **Find and kill the process using port 8000:**
   ```bash
   lsof -i :8000
   kill <PID>
   ```

2. **Use a different port:**
   ```bash
   python3 server.py --port 8080
   ```

3. **Check for zombie processes:**
   ```bash
   ps aux | grep server.py
   kill -9 <PID>
   ```

---

### Dashboard shows "Failed to load predictions"

**Problem:** Prediction generation script failed.

**Debugging:**

1. **Check Flask server logs:**
   ```bash
   # Look for errors in terminal where server.py is running
   ```

2. **Test prediction generation manually:**
   ```bash
   cd Dashboard
   python3 generate_predictions.py
   ```

3. **Check file permissions:**
   ```bash
   ls -la predictions.json
   chmod 644 predictions.json
   ```

---

### Dashboard shows stale data

**Problem:** Predictions not updating when "Refresh" is clicked.

**Solutions:**

1. **Clear browser cache:**
   - Chrome/Firefox: Ctrl+Shift+R (hard reload)
   - Safari: Cmd+Shift+R

2. **Check server logs for errors:**
   ```bash
   # Look for generation failures in server output
   ```

3. **Manually regenerate predictions:**
   ```bash
   cd Dashboard
   python3 generate_predictions.py
   ```

4. **Verify Flask server is running:**
   ```bash
   curl http://localhost:8000/api/status
   ```

---

## Performance Issues

### Predictions are very slow (> 5 seconds)

**Problem:** Excessive computation time.

**Common causes:**

1. **First run after import loads CCIR/URSI files:**
   ```python
   # First prediction: ~2-3 seconds (loads data files)
   # Subsequent predictions: ~500ms
   ```

2. **Debug logging enabled:**
   ```bash
   # Remove --debug flag for faster execution
   python3 validate_predictions.py  # Fast
   python3 validate_predictions.py --debug  # Slow
   ```

3. **Large area coverage scans:**
   ```python
   # 100-point area scan takes ~30-60 seconds
   # This is normal
   ```

**Optimization tips:**

- Use NumPy arrays for batch predictions
- Reuse `FourierMaps` instance
- Cache ionospheric profiles for fixed locations
- Consider using `multiprocessing` for area scans

---

### High memory usage (> 1 GB)

**Problem:** Excessive memory consumption.

**Common causes:**

1. **Multiple `FourierMaps` instances:**
   ```python
   # ✗ Bad - creates multiple instances
   for i in range(100):
       maps = FourierMaps()  # Loads data each time!

   # ✓ Good - reuse single instance
   maps = FourierMaps()
   for i in range(100):
       maps.set_conditions(...)  # Reuses loaded data
   ```

2. **Large area coverage with many points:**
   ```python
   # Consider processing in batches
   # Or use generator pattern
   ```

**Memory usage guide:**
- CCIR/URSI data: ~30 MB
- Runtime working set: ~100-200 MB
- Area scan (100 points): ~500 MB

---

## Data Issues

### "CCIR coefficient file corrupted"

**Problem:** Data file checksum failure.

**Solution:** Re-download data files:
```bash
cd DVoaData
# Backup old files
mv CCIR*.asc backup/

# Re-clone repository
cd ..
git pull origin main
```

---

### Unexpected results for specific paths

**Problem:** Certain paths produce unusual predictions.

**Debugging workflow:**

1. **Verify against original VOACAP:**
   - Use [VOACAP Online](https://www.voacap.com/hf/)
   - Compare MUF, SNR, reliability
   - Document differences

2. **Check path geometry:**
   ```python
   from dvoacap import PathGeometry, PathPoint

   tx = PathPoint.from_degrees(tx_lat, tx_lon)
   rx = PathPoint.from_degrees(rx_lat, rx_lon)

   distance = PathGeometry.distance(tx, rx)
   bearing = PathGeometry.bearing(tx, rx)

   print(f"Distance: {distance:.1f} km")
   print(f"Bearing: {bearing:.1f}°")
   ```

3. **Verify ionospheric parameters:**
   ```python
   from dvoacap import compute_iono_params, FourierMaps

   maps = FourierMaps()
   maps.set_conditions(month, ssn, utc_fraction)
   compute_iono_params(control_point, maps)

   print(f"foF2: {control_point.f2.fo:.2f} MHz")
   print(f"MUF: {circuit_muf.muf:.2f} MHz")
   ```

4. **Open issue on GitHub with:**
   - Path details (TX, RX coordinates)
   - Frequency, time, SSN
   - Expected vs actual results
   - Debug output

---

## Testing Issues

### pytest fails with import errors

**Problem:** Tests can't import dvoacap module.

**Solution:** Install in editable mode first:
```bash
cd dvoacap-python
pip install -e ".[dev]"
pytest tests/
```

---

### Reference validation tests fail

**Problem:** `test_voacap_reference.py` shows mismatches.

**Status:** Expected during Phase 5 debugging

**Context:**
- Phase 5 reliability bug causes validation failures
- Tests will pass once bug is fixed
- See [Validation Status](Validation-Status) for details

---

## Common Error Messages

### "Division by zero in MUF calculation"

**Cause:** Invalid ionospheric parameters (foF2 = 0)

**Solution:** Check solar/geomagnetic conditions are set correctly

---

### "No valid modes found for frequency X MHz"

**Cause:** Frequency is above MUF or below LUF

**Solution:** Check frequency is within propagation window:
```python
# Use FOT (typically 85% of MUF) for best results
if frequency > circuit_muf.muf:
    print("Frequency too high - above MUF")
elif frequency < 2.0:  # Typical lower limit
    print("Frequency too low - absorption too high")
```

---

### "Path distance exceeds maximum"

**Cause:** Antipodal path (distance > 20,000 km)

**Solution:** VOACAP is designed for typical radio paths. Very long paths may have limitations.

---

## Getting Help

If you encounter an issue not listed here:

1. **Check existing issues:** [github.com/skyelaird/dvoacap-python/issues](https://github.com/skyelaird/dvoacap-python/issues)

2. **Search discussions:** [github.com/skyelaird/dvoacap-python/discussions](https://github.com/skyelaird/dvoacap-python/discussions)

3. **Open a new issue with:**
   - Python version (`python3 --version`)
   - DVOACAP version (`python3 -c "import dvoacap; print(dvoacap.__version__)"`)
   - Operating system
   - Complete error message
   - Minimal code to reproduce

4. **For urgent bugs:**
   - Label as "bug"
   - Include detailed reproduction steps
   - Attach debug output if available

---

## Known Issues

See [Validation Status](Validation-Status) for current known bugs and their status.

**Critical Issues:**
- Reliability calculation returns 0% (debugging in progress)
- Signal/noise distribution may have inverted deciles

**Tracking:** [NEXT_STEPS.md](https://github.com/skyelaird/dvoacap-python/blob/main/NEXT_STEPS.md)

---

## Useful Debug Commands

```bash
# Quick validation
python3 validate_predictions.py --regions UK --bands 20m

# Deep debug
python3 validate_predictions.py --debug UK 20m

# Run tests
pytest tests/ -v

# Run specific test
pytest tests/test_path_geometry.py -v

# Check module import
python3 -c "from dvoacap import FourierMaps; print('OK')"

# Get version info
python3 -c "import dvoacap; print(dvoacap.get_version_info())"

# List installed modules
pip list | grep dvoacap
```

---

**Last Updated:** 2025-11-18

**Still having issues?** Open an issue on GitHub!
