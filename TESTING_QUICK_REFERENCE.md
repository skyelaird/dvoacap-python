# DVOACAP-Python Testing Quick Reference

## Current State

- **7,101 lines** of source code across **14 modules**
- **1,002 lines** of tests covering only **3 modules** (~21% coverage)
- **pytest** is configured and ready to use
- **GitHub Actions** runs tests on Python 3.11, 3.12, 3.13

## Tests That Exist ✅

### 1. Path Geometry (test_path_geometry.py - 233 lines)
- GeoPoint conversions
- Great circle path calculations  
- Hop distance and elevation angle calculations
- Edge cases (poles, antipodal, close points)

### 2. VOACAP Parser (test_voacap_parser.py - 315 lines)  
- File I/O operations
- Data structure initialization
- Monthly data loading
- Enum validation

### 3. Ionospheric Profiles (test_ionospheric.py - 454 lines)
- FourierMaps configuration and computation
- IonosphericProfile creation
- Layer parameters
- **NOTE:** Not using pytest format - should be migrated

## Critical Testing Gaps 🚨 (Highest Priority)

### P1: Prediction Engine (1,257 lines)
The **core** module - needs comprehensive unit tests:
- Initialization and configuration
- Prediction workflow
- Signal/reliability/SNR calculations
- Multi-frequency handling

### P1: Reflectrix (558 lines)  
Complex raytracing calculations:
- Ray path calculations for E/F1/F2 layers
- Skip distance and multi-hop paths
- Over-the-MUF calculations

### P1: MUF Calculator (446 lines)
Maximum Usable Frequency calculations:
- Circuit MUF computation
- FOT and HPF calculations
- Profile selection algorithm

### P2: Noise Model (393 lines)
Critical for SNR calculations:
- Atmospheric, galactic, man-made noise
- Frequency-dependent scaling
- Distribution computations

### P2: Antenna Gain (302 lines)
Antenna models:
- IsotropicAntenna, HalfWaveDipole, VerticalMonopole
- Elevation/azimuth-dependent gains
- Frequency range validation

### P2: Solar Calculations (353 lines)
Zenith angle and local time:
- Zenith angle at various locations/times
- Day/night terminator
- Seasonal variations

### P3: Geomagnetic (482 lines)
Magnetic field calculations:
- Magnetic latitude
- Gyrofrequency  
- Dip angle
- Edge cases (poles, equator)

### P3: Layer Parameters (309 lines)
Incomplete - needs expansion:
- Edge cases and boundary conditions
- F1 layer nocturnal behavior
- Es layer variations

### P4: Space Weather Sources (590 lines)
Data fetching (lower priority):
- Fallback logic
- Error handling
- Data validation

## Running Tests

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=src/dvoacap --cov-report=html

# Run specific test file
python -m pytest tests/test_path_geometry.py -v

# Run specific test
python -m pytest tests/test_voacap_parser.py::TestVoacapParser::test_parse_coeff_file_exists -v
```

## Test Infrastructure

### Configured Tools
- pytest (>= 7.0)
- pytest-cov (>= 4.0) - for coverage reports
- pyproject.toml - test configuration
- .github/workflows/tests.yml - CI/CD pipeline

### Missing Infrastructure
- No conftest.py with shared fixtures
- No test data directory
- No coverage reports in CI/CD
- No testing documentation for developers

## Quick Wins (Easy to Implement)

1. **Migrate test_ionospheric.py** to pytest format
   - Add fixtures instead of manual setup
   - Use parametrize for multiple test cases
   - ~30 minutes

2. **Create conftest.py** with shared fixtures
   - GeoPoint, IonosphericProfile, Prediction objects
   - Common test data
   - ~30 minutes

3. **Add coverage to CI/CD**
   - Add --cov flag to pytest command
   - Generate HTML reports
   - ~15 minutes

4. **Move root-level tests** into tests/ directory
   - test_phase5_api.py, test_mode_selection.py, etc.
   - ~15 minutes

## Coverage Goals

- **Now:** ~21% (3 of 14 modules)
- **Short-term (P1):** 50% (add Prediction Engine, Reflectrix, MUF)
- **Medium-term (P2):** 75% (add all P2 priority modules)
- **Long-term:** 85%+ (comprehensive coverage)

## File Locations

- **Test directory:** `/home/user/dvoacap-python/tests/`
- **Source directory:** `/home/user/dvoacap-python/src/dvoacap/`
- **pytest config:** `pyproject.toml` (lines 92-97)
- **coverage config:** `pyproject.toml` (lines 99-111)
- **CI/CD:** `.github/workflows/tests.yml`

## Next Steps

1. **Read the full analysis:** `TEST_COVERAGE_ANALYSIS.md`
2. **Start with P1 modules** (highest impact)
3. **Use test_voacap_parser.py as template** (best example of pytest structure)
4. **Create conftest.py** for shared fixtures
5. **Add parametrized tests** for multiple scenarios

---

For detailed information, see **TEST_COVERAGE_ANALYSIS.md** in the repository.
