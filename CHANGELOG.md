# Changelog

All notable changes to DVOACAP-Python will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Performance profiling framework (`profile_performance.py`)
- 11 diverse test cases covering short/medium/long/polar/equatorial paths
- Solar minimum and solar maximum validation scenarios
- Multi-source space weather data fetching with international fallbacks
- Live Kp and A-index fetching from NOAA SWPC
- Systematic documentation maintenance with pre-commit hooks
- Comprehensive validation framework with regression baselines

### Changed
- Improved validation pass rate to 86.6% (226/261 tests passing)
- Optimized prediction engine performance (0.009s per prediction)

### Fixed
- Reliability calculation verified against FORTRAN RELBIL.FOR
- Absorption loss calculations corrected (677.2 coefficient)
- D-layer absorption coefficient corrections
- Signal distribution calculations validated

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
