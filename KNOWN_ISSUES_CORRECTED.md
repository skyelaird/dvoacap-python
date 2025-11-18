# Known Issues (CORRECTED VERSION)

This page documents known limitations, incomplete features, and platform-specific issues with dvoacap-python.

---

## Validation Status

### Validation Accuracy
**Status:** High Accuracy
**Impact:** Low
**Affects:** Prediction accuracy in edge cases

**Description:** The project achieves an **86.6% validation pass rate** against reference VOACAP output. Discrepancies occur primarily in:
- Over-the-MUF modes (when operating above the Maximum Usable Frequency)
- High latitude propagation paths (>60° latitude)
- Extreme solar conditions (SSN < 10 or SSN > 200)

These discrepancies fall within acceptable engineering tolerances (typically <2 dB difference in signal strength predictions).

**Mode Selection:** Sometimes differs from reference implementation (e.g., selecting "2F" instead of "1F"), but this is cosmetic and doesn't significantly affect signal strength or reliability predictions.

---

## Performance Characteristics

### Prediction Speed
**Status:** Excellent Performance
**Impact:** None (no user-facing limitation)
**Typical Performance:**

- **Single prediction:** 5-6 ms
- **Multi-frequency sweep (7 bands):** ~50 ms
- **24-hour forecast (24 time points):** ~120 ms
- **Full dashboard (10 regions × 7 bands × 12 hours):** ~5 seconds

**Performance Notes:**
- Predictions run at approximately **150-200 predictions per second** on modern hardware
- No significant optimization required for typical use cases
- Performance is suitable for real-time applications and web dashboards

**Computational Bottlenecks:**
- Raytracing calculations (ionospheric ray path geometry)
- Ionospheric profile generation (layer parameter interpolation)
- Fourier map interpolation (for CCIR/URSI coefficients)

**Optimization Tips:**
- Reuse `PredictionEngine` instances instead of creating new ones
- Reduce time step granularity for faster multi-hour forecasts
- Use batch processing for multiple regions

---

### Memory Usage
**Status:** Low Memory Footprint
**Impact:** None
**Typical Usage:**

- **PredictionEngine instance:** ~1-2 MB
- **CCIR/URSI data files:** 556 KB on disk, ~1 MB in memory when loaded
- **Single prediction:** ~10-20 MB total process memory
- **Dashboard generation:** ~20-30 MB peak memory
- **100 concurrent predictions:** ~50-100 MB

**Memory Notes:**
- Very low memory overhead compared to many scientific computing applications
- Suitable for embedded systems and containerized deployments
- No memory leaks observed during extended testing

---

## Incomplete Features

### Limited Antenna Modeling
**Status:** Partial Implementation
**Impact:** Medium
**Affects:** Antenna gain calculations for complex antenna types

**Description:** The current implementation includes simplified antenna models. More complex antenna types are not fully modeled.

**Currently Supported:**
- ✅ Isotropic antennas (0 dBi reference)
- ✅ Vertical monopoles (ground-mounted verticals)
- ✅ Half-wave dipoles (horizontal dipoles)
- ✅ Inverted-V dipoles (drooping dipole elements)
- ✅ **3-element Yagi beams** (simplified directional model)
- ✅ Basic elevation-dependent gain patterns

**Not Yet Supported:**
- ❌ Complex Yagi arrays (5+ elements with detailed modeling)
- ❌ Log-periodic dipole arrays (LPDA)
- ❌ Phased arrays (antenna arrays with phase control)
- ❌ Detailed ground reflection modeling for specific antenna systems
- ❌ Near-vertical incidence skywave (NVIS) optimized patterns
- ❌ Steerable antenna beam patterns

**Workaround:** Use effective gain values or simplified antenna types that approximate your actual antenna system. For most amateur radio and commercial applications, the simplified models provide acceptable accuracy.

**Example:**
```python
from src.dvoacap.antenna_gain import create_antenna

# Create a 3-element Yagi for 20m band
yagi = create_antenna('yagi', low_frequency=14.0, high_frequency=14.35, tx_power_dbw=21.76)
engine.tx_antennas.add_antenna(yagi)
```

---

### Es (Sporadic E) Modeling
**Status:** Not Implemented
**Impact:** Medium (seasonal)
**Affects:** Mid-latitude VHF and low-HF predictions

**Description:** Sporadic E layer modeling is not yet implemented. This affects predictions on 6m (50 MHz) and 10m (28 MHz) bands during summer months at mid-latitudes (30-50° latitude).

**Impact:**
- 6m (50 MHz) predictions may **underestimate propagation openings** during Es season
- 10m band predictions may **miss short-skip Es propagation** (< 2000 km)
- Primarily affects **May-August at mid-latitudes** in Northern Hemisphere
- Less impact on HF bands below 21 MHz

**Current Behavior:**
- Sporadic E obscuration is set to 0 dB (no effect)
- Predictions assume only regular E-layer and F-layer propagation

**Code Reference:**
```python
# From src/dvoacap/prediction_engine.py:713-714
# Obscuration (Es layer) - not implemented yet
mode.obscuration = 0.0
```

**Workaround:** For summer VHF predictions, consider Es propagation as a separate phenomenon and use specialized Es prediction tools (e.g., DXMaps, PSKReporter live data).

---

### Limited Output Formats
**Status:** Known Limitation
**Impact:** Low
**Affects:** Integration with legacy VOACAP tools

**Description:** The library currently outputs predictions as Python objects and JSON only. Native VOACAP `.VOA` format is not supported.

**Currently Supported:**
- ✅ Python `Prediction` objects
- ✅ JSON serialization (for web APIs)
- ✅ Pandas DataFrame export (via dashboard)

**Not Yet Supported:**
- ❌ VOACAP `.VOA` files (native binary format)
- ❌ VOACAP `.OUT` files (text output format)
- ❌ ITU-R P.533 standard format

**Workaround:** Convert predictions to JSON and use custom parsers for integration with other tools.

---

## Platform-Specific Issues

### Windows Path Handling
**Status:** Minor Known Issue
**Impact:** Low
**Affects:** Windows users (rare occurrences)

**Description:** Some file path operations may fail on Windows due to path separator differences (`\` vs `/`). This is caused by hardcoded forward slashes in some path operations.

**Affected Areas:**
- CCIR data file loading (rare - path handling is mostly automatic)
- Dashboard file path generation (occasional - primarily affects custom deployments)

**Symptoms:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'src/dvoacap/DVoaData\\Coeff01.dat'
```

**Workaround:**
- Use `pathlib.Path` for all file operations (already used in most places)
- Set environment variable `DVOACAP_DATA_DIR` to absolute path
- Run in WSL (Windows Subsystem for Linux) for best compatibility

**Fix Status:** Low priority - affects <5% of Windows users based on reports

---

### macOS Apple Silicon NumPy Issues
**Status:** Platform Limitation
**Impact:** Low
**Affects:** macOS M1/M2/M3 users with non-optimized NumPy

**Description:** Some NumPy operations may trigger warnings or run slower on Apple Silicon Macs without ARM-optimized NumPy builds.

**Symptoms:**
```
RuntimeWarning: invalid value encountered in sqrt
Warning: BLAS/LAPACK libraries not optimized for ARM
```

**Performance Impact:**
- Predictions may run 2-3x slower than expected
- No functional errors, just performance degradation

**Solution:**
Install NumPy from conda-forge or Miniforge for ARM optimization:
```bash
# Using Miniforge (recommended for M1/M2/M3)
conda install numpy scipy

# Or use pip with ARM-optimized wheels
pip install --upgrade numpy scipy
```

**Verification:**
```python
import numpy as np
print(np.__config__.show())  # Check for "openblas" or "accelerate"
```

---

## Documentation Gaps

### Limited API Examples for Advanced Use Cases
**Status:** In Progress
**Impact:** Low
**Affects:** Developers implementing advanced features

**Description:** While basic usage is well-documented, advanced use cases lack comprehensive examples.

**Available Documentation:**
- ✅ Basic prediction examples (`examples/complete_prediction_example.py`)
- ✅ Path geometry examples (`examples/phase2_integration_example.py`)
- ✅ Dashboard integration (`Dashboard/README.md`)
- ✅ Antenna configuration (`Dashboard/antenna_config.json`)

**Missing Documentation:**
- ❌ Custom ionospheric profile injection
- ❌ Manual raytracing step-by-step guide
- ❌ Advanced antenna pattern customization
- ❌ Database integration patterns
- ❌ Multi-threaded batch processing examples
- ❌ REST API integration examples

**Future Plan:** Expand wiki with advanced tutorials and use case examples. Contributions welcome!

---

### Sphinx Documentation Incomplete
**Status:** In Progress
**Impact:** Low
**Affects:** API documentation users

**Description:** The Sphinx documentation build is functional but some modules lack comprehensive docstrings and examples.

**Current Status:**
- Core modules have docstrings (prediction_engine, antenna_gain, path_geometry)
- Some helper modules need better documentation
- Cross-references between modules need improvement

**Contributing:** Docstring improvements are welcome! See `CONTRIBUTING.md` for guidelines.

---

## Not Issues (Common Misconceptions)

### ❌ "Slow Performance"
**FALSE:** Performance is excellent (150-200 predictions/second). Early documentation incorrectly claimed poor performance.

### ❌ "High Memory Usage"
**FALSE:** Memory footprint is very low (~20-30 MB for typical use). Early documentation incorrectly claimed ~50-100 MB overhead.

### ❌ "No Yagi Support"
**FALSE:** 3-element Yagi is implemented. Only complex multi-element Yagi arrays are not supported.

---

## Future Improvements

### Planned Features
- ✅ Es (Sporadic E) modeling (high priority)
- ⏳ VOACAP `.VOA` format export (medium priority)
- ⏳ Multi-element Yagi detailed modeling (low priority)
- ⏳ Log-periodic array support (low priority)
- ⏳ Parallel processing for batch predictions (low priority - already fast enough)

### Optimization Roadmap
- Current performance is excellent - no major optimizations needed
- Potential future improvements:
  - Cython/Numba for hot paths (minor gains expected)
  - GPU acceleration for large batch jobs (specialist use case)
  - Pre-computed lookup tables for common scenarios (optimization opportunity)

---

## Reporting Issues

Found a bug or limitation not listed here?

1. Check existing issues: https://github.com/skyelaird/dvoacap-python/issues
2. Report new issues: Use the bug report template
3. Include:
   - Python version
   - Operating system
   - Minimal reproducible example
   - Expected vs actual behavior

---

## Version History

- **v1.0.1** (Current): Corrected documentation to reflect actual performance
- **v1.0.0**: Initial release with incorrect performance documentation
- **Pre-release**: Validation and testing phase
