# Changelog

All notable changes to DVOACAP-Python will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.2] - 2026-05-01

### Fixed

- **Long-path signal/SNR calculation** - For HF paths longer than 7000 km, the engine was mixing in an unimplemented `_evaluate_long_model` stub that returned an empty `Prediction()`. The smooth-interpolation branch in `_combine_short_and_long` then pulled `power_dbw` toward 0 dBW and back-derived a nonsensically small `total_loss_db`, producing constant `-0.7 dBW` signal levels and SNRs of +150 dB or worse for any region beyond 7000 km, with reliability pinned at 100%. Paths beyond 10000 km returned all-zero predictions outright. Until a real long-path model exists, the short-path result is used at all distances. (#137)
- **TX power propagation to user-added antennas** - `params.tx_power` was stamped onto `current_antenna` once before the per-frequency loop, where `current_antenna` still pointed at the isotropic default. `select_antenna()` then swapped in the user antenna whose `tx_power_dbw` came from its constructor, leaving a 100 W radio configuration treated as 10 W (a 10 dB undercount). The assignment now happens inside the loop after antenna selection. (#137)
- **Dashboard buttons unresponsive** - A duplicate `const now` declaration inside `initializeDashboard()` (and again inside its `setInterval` callback) caused a `SyntaxError` that prevented the entire `<script>` block from parsing, leaving `triggerRefresh` and `showSettings` undefined when their `onclick` handlers fired. Renamed the duplicate locals to `currentHourInt` / `tickHour`. (#134, #135)
- **Gray-line terminator rendering** - `drawGrayLine()` swept a 2° lat/lon grid for points where `|solar altitude| < 6°`, then bucketed them into 5°-wide latitude bands and emitted one rectangle per (band, longitude segment), rendering the twilight zone as a visible staircase of 10°-tall blocks. Replaced with a closed-form analytic solve at every longitude, drawn as a single smooth polygon. (#136)

### Added

- **Regression tests for `PredictionEngine`** - Asserts long-distance predictions produce physically plausible signal levels and that `params.tx_power` reaches user-added antennas. (#137)

### Changed

- **Dashboard packaged as installable subpackage** - Moved from `Dashboard/` to `src/dvoacap/dashboard/`, added `dvoacap-dashboard` console-script entry point, and shipped HTML/JS/CSS with the package so `pip install dvoacap[dashboard]` followed by `dvoacap-dashboard` is sufficient. Backward-compatible `python Dashboard/server.py` shim retained. (#133)

## [1.0.1] - 2025-11-18

### 🚀 Performance Optimizations

This release delivers a **2.3x speedup** across all prediction benchmarks through algorithmic improvements and vectorization.

### Changed
- **Optimized ionospheric profile calculations** - Replaced linear search with binary search in height-to-density interpolation (O(n) → O(log n))
- **Vectorized Gaussian integration** - Replaced 40-iteration loop with NumPy vectorized operations in `get_virtual_height_gauss`
- **Vectorized oblique frequency computation** - Eliminated 1,200 nested loop iterations using NumPy broadcasting
- **Optimized Fourier series** - Replaced nested loops with NumPy dot products in `compute_fixed_map`
- **Updated Performance-Tips.md** - Documented new benchmark timings

### Performance Metrics
- Single prediction: 0.008s → 0.004s (2x faster)
- Multi-frequency (9 predictions): 0.111s → 0.048s (2.3x faster)
- 24-hour scan: 0.282s → 0.118s (2.4x faster)
- Area coverage (100 predictions): 0.82s → 0.35s (2.3x faster)
- Function call reduction: 68-71% fewer function calls

### Removed
- Obsolete debug scripts (debug_*.py, analyze_*.py)
- Obsolete test scripts (quick_*.py, simple_*.py)
- Old generator archive (Dashboard/archive/old_generators/)

## [1.0.0] - 2025-11-18

### 🎉 First Stable Release - Production Ready

This milestone marks the completion of all 5 implementation phases and achievement
of 86.6% validation accuracy, making DVOACAP-Python ready for production use.

### Added
- **NOTICE file** - Complete attribution chain for VOACAP → DVOACAP → dvoacap-python
- **LICENSE_NOTE.txt** - Explanation of MPL headers in Pascal reference files
- **RELEASE_NOTES_v1.0.0.md** - Comprehensive release documentation
- Performance profiling framework (`profile_performance.py`)
- 11 diverse test cases covering short/medium/long/polar/equatorial paths
- Solar minimum and solar maximum validation scenarios
- Multi-source space weather data fetching with international fallbacks
- Live Kp and A-index fetching from NOAA SWPC
- Systematic documentation maintenance with pre-commit hooks
- Comprehensive validation framework with regression baselines

### Changed
- **Version bumped to 1.0.0** - Production/Stable status
- **LICENSE updated** - Proper attribution to Joel Morin as Python port author
- **Development classifier** - Changed from Beta to Production/Stable
- **Author metadata** - Updated to "Joel Morin and Contributors"
- **Phase 5 status** - Marked as complete (100% progress)
- Improved validation pass rate to 86.6% (226/261 tests passing)
- Optimized prediction engine performance (0.009s per prediction)

### Fixed
- Licensing attribution corrected (was incorrectly attributed to Alex Shovkoplyas)
- Reliability calculation verified against FORTRAN RELBIL.FOR
- Absorption loss calculations corrected (677.2 coefficient)
- D-layer absorption coefficient corrections
- Signal distribution calculations validated

### Documentation
- Clarified MIT license compatibility (DVOACAP relicensed from MPL 1.1 to MIT in May 2025)
- Added complete attribution chain acknowledging all contributors
- Documented collaboration with Claude.ai in development process

## [0.9.0] - 2025-11-15

### Added
- Phase 5 signal prediction implementation
- Reference VOACAP validation test suite
- Dashboard with real-time predictions
- PSKReporter integration for real-world validation
- WSPR validation framework
- Comprehensive test coverage across 11 diverse scenarios

### Changed
- Achieved 86.6% validation pass rate (exceeds 85% target)
- Phase 5 validation complete with 83.8% baseline pass rate
- Documentation workflow improvements

### Fixed
- Reliability calculations match FORTRAN reference
- Absorption loss calculations corrected
- Mode selection logic verified

## [0.8.0] - 2025-11-01

### Added
- Phase 4 raytracing implementation (MUF, FOT, reflectrix, skip distance)
- Multi-hop propagation path calculation
- Reflection point determination
- Virtual height calculations

### Changed
- Improved ionospheric profile accuracy
- Enhanced layer parameter calculations

### Fixed
- MUF calculation edge cases
- Ray path geometry corrections

## [0.7.0] - 2025-10-15

### Added
- Phase 3 ionospheric profile implementation
- CCIR/URSI coefficient map integration
- Layer parameter calculations (foF2, foE, etc.)
- Electron density profile computation

### Changed
- Improved solar activity integration
- Enhanced geomagnetic field calculations

## [0.6.0] - 2025-10-01

### Added
- Phase 2 solar and geomagnetic field implementation
- Solar zenith angle calculations (<0.1° error validation)
- IGRF geomagnetic field model
- Local time computations

### Changed
- Path geometry calculations optimized
- Great circle distance accuracy improved

### Fixed
- Solar position edge cases near poles
- Time zone calculations

## [0.5.0] - 2025-09-15

### Added
- Phase 1 path geometry implementation
- Great circle path calculations (<0.01% error validation)
- Geographic coordinate transformations
- Distance and bearing computations

### Changed
- Initial project structure
- Core geometry algorithms

## [0.1.0] - 2025-08-01

### Added
- Initial project setup
- Basic module structure
- Development environment configuration
- Core dependencies (numpy, scipy, matplotlib)

---

## Release Notes Template

### Version X.Y.Z - YYYY-MM-DD

#### Highlights
- Brief summary of major changes
- Key features or bug fixes
- Performance improvements

#### Breaking Changes
- List any backward-incompatible changes
- Migration guide if needed

#### New Features
- Feature 1 description
- Feature 2 description

#### Improvements
- Improvement 1
- Improvement 2

#### Bug Fixes
- Bug fix 1
- Bug fix 2

#### Documentation
- Documentation updates
- New examples or guides

#### Contributors
- @contributor1
- @contributor2

---

## Version History

- **v0.9.0** - Phase 5 complete, 86.6% validation
- **v0.8.0** - Phase 4 raytracing
- **v0.7.0** - Phase 3 ionospheric profiles
- **v0.6.0** - Phase 2 solar/geomagnetic
- **v0.5.0** - Phase 1 path geometry
- **v0.1.0** - Initial release
