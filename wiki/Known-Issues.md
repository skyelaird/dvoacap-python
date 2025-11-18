# Known Issues

Current limitations, bugs, and areas needing improvement in DVOACAP-Python.

## Table of Contents

- [Validation Issues](#validation-issues)
- [Performance Limitations](#performance-limitations)
- [Incomplete Features](#incomplete-features)
- [Platform-Specific Issues](#platform-specific-issues)
- [Documentation Gaps](#documentation-gaps)
- [Workarounds](#workarounds)

---

## Validation Issues

### Phase 5 Validation Pass Rate: 86.6%

**Status:** ✅ Complete (v1.0.1)
**Impact:** Low - Exceeds 85% target threshold
**Tracking:** [Validation Status](Validation-Status)

**Description:**
The Phase 5 signal prediction validation shows an 86.6% pass rate across 11 diverse test cases when compared against reference VOACAP output. This exceeds the 85% target threshold and approaches the 90% stretch goal. The remaining 13.4% show minor discrepancies within expected ionospheric model variability.

**Affected Areas:**
- Signal strength predictions (path loss calculations)
- SNR calculations at edge cases (very low or very high frequencies)
- Reliability calculations for marginal paths

**Known Failure Patterns:**
1. **Over-the-MUF modes** - Some discrepancies when frequency > 1.1 × MUF
2. **Short paths (< 500 km)** - Different ground wave vs. sky wave blending
3. **High latitude paths** - Geomagnetic field model differences
4. **Extreme solar conditions** - SSN > 200 or SSN < 10

**Workaround:**
For critical applications, validate predictions against operational data or cross-check with VOACAP Online.

**Resolution Plan:**
- Detailed error analysis of failing test cases
- Comparison with original Pascal source code for numerical differences
- Refinement of signal prediction algorithms

---

### Mode Selection Alignment

**Status:** Known Issue
**Impact:** Low
**Affects:** Mode naming (e.g., "1F", "2F", "3F")

**Description:**
Some predictions select different propagation modes (1F vs 2F) compared to reference VOACAP, even when the underlying signal predictions are correct.

**Example:**
```
DVOACAP:  7.0 MHz → 2F mode, SNR 12.3 dB
VOACAP:   7.0 MHz → 1F mode, SNR 12.1 dB
```

**Impact:**
This is cosmetic and doesn't affect the accuracy of signal strength, SNR, or reliability predictions. The mode name is a label for the propagation mechanism, not the prediction itself.

**Workaround:**
Focus on SNR and reliability values rather than mode names.

---

## Performance Limitations

### ~~Slow Prediction Generation~~ ✅ RESOLVED in v1.0.1

**Status:** ✅ Fixed - 2.3x faster in v1.0.1
**Previous Impact:** Medium
**Resolution:** Algorithmic optimizations and NumPy vectorization

**Description:**
**RESOLVED:** v1.0.1 delivers 2.3x performance improvement through:
- Binary search for height-to-density interpolation (O(n) → O(log n))
- Vectorized Gaussian integration (eliminated 40-iteration loop)
- Vectorized oblique frequency computation (eliminated 1,200 nested iterations)
- Optimized Fourier series with NumPy dot products

**Performance (v1.0.1):**
- Single prediction: ~4 ms (was ~8 ms in v1.0.0)
- Multi-frequency (9 predictions): ~48 ms (was ~111 ms in v1.0.0)
- 24-hour scan: ~118 ms (was ~282 ms in v1.0.0)
- Area scan (100 predictions): ~350 ms (was ~820 ms in v1.0.0)
- Dashboard generation (full): 20-30 seconds (was 60-90 seconds)
- 24-hour forecast (12 time points): ~25-35 seconds
- Full dashboard (10 regions × 7 bands × 12 hours): ~60-90 seconds

**Root Causes:**
1. Raytracing calculations (Phase 4) - iterative path finding
2. Ionospheric profile generation (Phase 3) - CCIR coefficient processing
3. Python overhead vs. compiled Pascal/Fortran

**Workarounds:**
- Reduce number of target regions
- Increase time step (predict every 3 hours instead of 2)
- Remove unused frequency bands
- Use caching for repeated predictions

**Future Improvements:**
- Cython/Numba optimization for hot paths
- Parallel processing for multiple regions
- Pre-computed lookup tables for common scenarios

See [Performance Tips](Performance-Tips) for optimization strategies.

---

### Memory Usage

**Status:** Low Priority
**Impact:** Low
**Affects:** Large batch operations

**Description:**
Each PredictionEngine instance loads CCIR/URSI coefficient maps (~50 MB) into memory. Running many concurrent instances can consume significant RAM.

**Typical Usage:**
- Single prediction: ~60 MB
- Dashboard generation: ~100 MB peak
- 100 concurrent predictions: ~1-2 GB

**Workaround:**
Reuse PredictionEngine instances and run predictions sequentially rather than in parallel.

---

## Incomplete Features

### Limited Antenna Modeling

**Status:** Partial Implementation
**Impact:** Medium
**Affects:** Antenna gain calculations

**Description:**
The current implementation uses simplified antenna models. More complex antenna types (Yagi, log-periodic, phased arrays) are not fully modeled.

**Currently Supported:**
- Isotropic antennas
- Vertical monopoles
- Simple dipoles
- Basic gain patterns

**Not Yet Supported:**
- Detailed Yagi modeling
- Log-periodic arrays
- Phased arrays
- Ground reflections for complex antenna systems

**Workaround:**
Use effective gain values rather than detailed antenna modeling.

**Future Plan:**
Implement comprehensive antenna modeling from VOACAP antenna database.

---

### Es (Sporadic E) Modeling

**Status:** Not Implemented
**Impact:** Medium (seasonal)
**Affects:** Mid-latitude 6m and 10m predictions

**Description:**
Sporadic E layer modeling is not yet implemented. This affects VHF/low-HF predictions during summer months at mid-latitudes.

**Impact:**
- 6m (50 MHz) predictions may underestimate openings
- 10m band predictions may miss short-skip Es propagation
- Primarily affects May-August at mid-latitudes

**Workaround:**
Use operational data (PSKreporter, DX clusters) to supplement predictions during Es season.

**Future Plan:**
Add Es modeling from VOACAP Es module.

---

### Limited Output Formats

**Status:** Low Priority
**Impact:** Low

**Description:**
DVOACAP-Python currently outputs to JSON and in-memory Python objects. It does not support VOACAP's native .VOA or .OUT file formats.

**Available:**
- Python dictionaries/objects
- JSON export
- Custom data structures

**Not Available:**
- VOACAP .VOA files
- ITU-R P.533 format
- CSV export (easy to add)

**Workaround:**
Convert JSON output to desired format using custom scripts.

---

## Platform-Specific Issues

### Windows Path Handling

**Status:** Known Issue
**Impact:** Low
**Affects:** Windows users

**Description:**
Some file path operations may fail on Windows due to path separator differences (`\` vs `/`).

**Affected:**
- CCIR data file loading (rare)
- Dashboard file paths (occasional)

**Workaround:**
Use `pathlib.Path` or ensure paths use `os.path.join()`.

**Status:**
Being addressed in ongoing development.

---

### macOS M1/M2 NumPy Issues

**Status:** Platform Limitation
**Impact:** Low
**Affects:** macOS Apple Silicon users

**Description:**
Some NumPy operations may trigger warnings or slowdowns on Apple Silicon Macs without optimized NumPy builds.

**Symptoms:**
- Warning messages about BLAS/LAPACK
- Slower-than-expected predictions

**Workaround:**
Install NumPy from conda-forge or use Miniforge:

```bash
# Install Miniforge (Apple Silicon optimized)
brew install miniforge
conda create -n dvoacap python=3.10
conda activate dvoacap
conda install numpy

# Install DVOACAP
pip install -e .
```

---

## Documentation Gaps

### Limited API Examples for Advanced Use Cases

**Status:** In Progress
**Impact:** Low

**Description:**
While basic usage is well-documented, advanced use cases (custom ionospheric profiles, manual raytracing, antenna pattern customization) lack comprehensive examples.

**Available:**
- Basic prediction examples
- Path geometry examples
- Dashboard integration

**Missing:**
- Custom ionospheric profile injection
- Manual raytracing step-by-step
- Antenna gain pattern customization
- Database integration patterns

**Future Plan:**
Expand wiki with advanced tutorials and use case examples.

---

### Sphinx Documentation Incomplete

**Status:** In Progress
**Impact:** Low

**Description:**
The Sphinx documentation build is functional but some modules lack comprehensive docstrings and examples.

**Status:**
Ongoing improvement as modules mature.

---

## Workarounds

### General Debugging Tips

**Enable verbose logging:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Validate inputs:**
```python
from dvoacap.path_geometry import GeoPoint

# Check valid coordinates
assert -90 <= lat <= 90
assert -180 <= lon <= 180

# Check valid frequencies
assert 1.0 <= frequency_mhz <= 30.0  # HF range
```

**Compare with reference:**
```bash
# Run validation tests
python3 test_voacap_reference.py
```

---

### Reporting Issues

If you encounter issues not listed here:

1. **Check existing issues:** [GitHub Issues](https://github.com/skyelaird/dvoacap-python/issues)
2. **Search the wiki:** [Home](Home), [Troubleshooting](Troubleshooting)
3. **Provide details:**
   - Python version
   - Operating system
   - DVOACAP version
   - Minimal reproducible example
   - Expected vs. actual behavior

**Create new issue:** [New Issue](https://github.com/skyelaird/dvoacap-python/issues/new)

---

## Issue Priority Levels

**High Priority:**
- Crashes or data corruption
- Security vulnerabilities
- Major validation failures (> 50% error rate)

**Medium Priority:**
- Validation discrepancies (current 16.2% failure rate)
- Performance issues affecting usability
- Missing features blocking common use cases

**Low Priority:**
- Cosmetic issues (mode naming)
- Documentation gaps
- Platform-specific quirks with workarounds
- Feature requests for edge cases

---

## Version History

### v1.0.1 (Current) - Production Ready
- ✅ **Performance optimized:** 2.3x faster than v1.0.0
- ✅ **Phase 5 complete:** 86.6% validation (exceeds 85% target)
- ✅ **All 5 phases validated** and production-ready
- ⚠️ Minor validation issues at edge cases (13.4%, documented above)

### v1.0.0 - Production Release
- ✅ Phase 5 signal predictions (86.6% validation across 11 test cases)
- ✅ All 5 phases complete and validated
- ✅ Real-world validation (WSPR/PSKReporter)

### v0.9.0
- ✅ Phase 5 initial implementation
- ✅ Reliability calculations verified

### v0.8.0
- ✅ Phase 4 raytracing complete
- ✅ MUF calculations validated

### v0.7.0
- ✅ Phase 3 ionospheric profiles complete
- ✅ CCIR/URSI maps validated

### v0.6.0
- ✅ Phase 2 solar/geomagnetic complete

### v0.5.0
- ✅ Phase 1 path geometry complete

---

## Next Steps

- **[Validation Status](Validation-Status)** - Detailed validation results
- **[Troubleshooting](Troubleshooting)** - Solutions to common problems
- **[Performance Tips](Performance-Tips)** - Optimize prediction speed
- **[Contributing](Contributing)** - Help fix issues

---

**Last Updated:** 2025-11-18
**Project Status:** v1.0.1 Production Ready - 86.6% validation accuracy, 2.3x performance boost
