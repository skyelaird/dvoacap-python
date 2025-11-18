# DVOACAP-Python v1.0.1 Release Notes

**Release Date:** November 18, 2025
**Status:** Production/Stable

## 🎯 Overview

Version 1.0.1 is a performance-focused release that delivers a **2.3x speedup** across all prediction benchmarks while maintaining the 86.6% validation accuracy achieved in v1.0.0. This release focuses on algorithmic optimizations and vectorization improvements without any breaking changes to the API.

## 🚀 Performance Improvements

This release delivers significant performance gains through systematic optimization of core computational algorithms:

### Benchmark Results

| Operation | v1.0.0 | v1.0.1 | Speedup |
|-----------|--------|--------|---------|
| Single prediction | 0.008s | 0.004s | **2.0x** |
| Multi-frequency (9 predictions) | 0.111s | 0.048s | **2.3x** |
| 24-hour scan (24 predictions) | 0.282s | 0.118s | **2.4x** |
| Area coverage (100 predictions) | 0.820s | 0.350s | **2.3x** |

### Optimization Details

1. **Binary Search for Height-Density Interpolation**
   - Replaced linear search (O(n)) with binary search (O(log n))
   - Affects ionospheric profile calculations
   - Reduces function call overhead by 68-71%

2. **Vectorized Gaussian Integration**
   - Replaced 40-iteration explicit loop with NumPy vectorized operations
   - Applied to virtual height calculations (`get_virtual_height_gauss`)
   - Leverages NumPy's optimized C implementations

3. **Vectorized Oblique Frequency Computation**
   - Eliminated 1,200 nested loop iterations
   - Uses NumPy broadcasting for batch operations
   - Significant impact on multi-frequency predictions

4. **Optimized Fourier Series Calculations**
   - Replaced nested loops with NumPy dot products
   - Applied to `compute_fixed_map` function
   - Improves CCIR/URSI coefficient map computations

## 📦 What's Changed

### Changed
- Optimized ionospheric profile calculations with binary search
- Vectorized Gaussian integration in virtual height computations
- Vectorized oblique frequency calculations
- Optimized Fourier series computations with NumPy operations
- Updated performance documentation with new benchmarks

### Removed
- Obsolete debug scripts (debug_*.py, analyze_*.py)
- Obsolete test scripts (quick_*.py, simple_*.py)
- Old generator archive (Dashboard/archive/old_generators/)

### Fixed
- Version number consistency across package files

## 🔬 Validation Status

- **86.6% validation accuracy** maintained (same as v1.0.0)
- All 11 diverse test paths validated:
  - Short paths (150-500 km)
  - Medium paths (1,000-5,000 km)
  - Long paths (10,000+ km)
  - Polar propagation
  - Equatorial propagation
  - Solar minimum conditions
  - Solar maximum conditions

## 📥 Installation

### From PyPI (Recommended)

```bash
# Core library only
pip install dvoacap

# With dashboard
pip install dvoacap[dashboard]

# Full development installation
pip install dvoacap[all]
```

### From Source

```bash
git clone https://github.com/skyelaird/dvoacap-python.git
cd dvoacap-python
pip install -e .
```

## 🚀 Quick Start

```python
from dvoacap import FourierMaps, ControlPoint, IonoPoint, compute_iono_params
import math

# Load ionospheric maps
maps = FourierMaps()
maps.set_conditions(month=6, ssn=100, utc_fraction=0.5)

# Create control point
pnt = ControlPoint(
    location=IonoPoint.from_degrees(40.0, -75.0),
    east_lon=-75.0 * math.pi/180,
    distance_rad=0.0,
    local_time=0.5,
    zen_angle=0.3,
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

## 📊 Features

- **HF Propagation Prediction:** Maximum Usable Frequency (MUF), signal strength, reliability
- **Ionospheric Modeling:** E, F1, F2, and Es layer calculations with CCIR/URSI coefficients
- **Ray Tracing:** Multi-hop propagation path calculation
- **Solar & Geomagnetic:** Real-time space weather integration
- **Interactive Dashboard:** Web-based visualization with DXCC tracking
- **Validation:** 86.6% accuracy against reference VOACAP output

## 🔗 Links

- **Documentation:** https://skyelaird.github.io/dvoacap-python/
- **Repository:** https://github.com/skyelaird/dvoacap-python
- **Bug Tracker:** https://github.com/skyelaird/dvoacap-python/issues
- **PyPI Package:** https://pypi.org/project/dvoacap/
- **Original DVOACAP:** https://github.com/VE3NEA/DVOACAP

## 🙏 Acknowledgments

- **Alex Shovkoplyas (VE3NEA)** - Original DVOACAP implementation
- **Voice of America / ITS** - Original VOACAP development
- Amateur radio and propagation modeling community

## 📄 License

MIT License - See [LICENSE](LICENSE) for details

**Original DVOACAP:** Relicensed from Mozilla Public License v1.1 to MIT in May 2025

## 🎯 Coming Next

- Comprehensive type hints throughout codebase
- Enhanced Sphinx API documentation
- Community engagement and integration examples
- Performance profiling tools for user applications

---

**For Amateur Radio Operators:** This tool helps predict HF propagation for better DX contacts! 73! 📻
