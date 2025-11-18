# Testing Guide

Comprehensive guide to running and writing tests for DVOACAP-Python.

## Table of Contents

- [Test Overview](#test-overview)
- [Running Tests](#running-tests)
- [Test Types](#test-types)
- [Writing Tests](#writing-tests)
- [Validation Testing](#validation-testing)
- [Coverage](#coverage)
- [Continuous Integration](#continuous-integration)
- [Debugging Tests](#debugging-tests)

---

## Test Overview

DVOACAP-Python uses **pytest** as its testing framework. The test suite includes:

- **Unit tests** - Individual function/class testing
- **Integration tests** - Multi-module interaction testing
- **Validation tests** - Comparison with reference VOACAP output
- **Regression tests** - Ensure bugs don't reappear

**Test Structure:**
```
dvoacap-python/
├── tests/                          # pytest test directory
│   ├── test_path_geometry.py       # Phase 1 tests
│   ├── test_ionospheric.py         # Phase 3 tests
│   └── test_voacap_parser.py       # VOACAP reference parser tests
├── test_voacap_reference.py        # Full validation suite
├── test_phase5_api.py              # Phase 5 API tests
├── test_mode_selection.py          # Mode selection tests
├── test_mode_alignment.py          # Mode alignment validation
└── test_high_freqs.py              # High frequency edge cases
```

---

## Running Tests

### Basic Test Execution

**Run all tests:**
```bash
# From repository root
pytest

# Should output:
# ======================== test session starts =========================
# collected 42 items
#
# tests/test_path_geometry.py ........                          [ 19%]
# tests/test_ionospheric.py ..............                      [ 52%]
# tests/test_voacap_parser.py ....................               [100%]
#
# ======================== 42 passed in 2.34s =========================
```

**Run with verbose output:**
```bash
pytest -v

# Shows each test individually:
# tests/test_path_geometry.py::test_distance_calculation PASSED    [ 2%]
# tests/test_path_geometry.py::test_azimuth_calculation PASSED     [ 4%]
# ...
```

---

### Running Specific Tests

**Run single test file:**
```bash
pytest tests/test_path_geometry.py
```

**Run specific test function:**
```bash
pytest tests/test_path_geometry.py::test_distance_calculation
```

**Run specific test class:**
```bash
pytest tests/test_ionospheric.py::TestIonosphericProfile
```

**Run tests matching a pattern:**
```bash
# Run all tests with "distance" in the name
pytest -k distance

# Run all tests with "muf" in the name
pytest -k muf
```

---

### Test Output Options

**Verbose output with details:**
```bash
pytest -v --tb=short
```

**Show print statements:**
```bash
pytest -s

# Or combine with verbose
pytest -sv
```

**Stop at first failure:**
```bash
pytest -x
```

**Run last failed tests only:**
```bash
pytest --lf
```

**Run failed tests first:**
```bash
pytest --ff
```

---

## Test Types

### Unit Tests

Test individual functions and classes in isolation.

**Example: Path Geometry Tests**
```python
# tests/test_path_geometry.py

import pytest
import math
from dvoacap.path_geometry import GeoPoint, PathGeometry

class TestGeoPoint:
    """Test GeoPoint class"""

    def test_from_degrees(self):
        """Test creating GeoPoint from degrees"""
        point = GeoPoint.from_degrees(40.0, -75.0)
        assert abs(point.lat - math.radians(40.0)) < 1e-9
        assert abs(point.lon - math.radians(-75.0)) < 1e-9

    def test_to_degrees(self):
        """Test converting GeoPoint to degrees"""
        point = GeoPoint.from_degrees(51.5, -0.1)
        lat, lon = point.to_degrees()
        assert abs(lat - 51.5) < 1e-9
        assert abs(lon - -0.1) < 1e-9

class TestPathGeometry:
    """Test PathGeometry class"""

    def test_distance_calculation(self):
        """Test great circle distance calculation"""
        tx = GeoPoint.from_degrees(40.0, -75.0)  # Philadelphia
        rx = GeoPoint.from_degrees(51.5, -0.1)   # London

        path = PathGeometry()
        path.set_tx_rx(tx, rx)

        # Expected distance ~5232 km
        distance_km = path.get_distance_km()
        assert 5200 < distance_km < 5260

    def test_azimuth_calculation(self):
        """Test azimuth calculation"""
        tx = GeoPoint.from_degrees(40.0, -75.0)
        rx = GeoPoint.from_degrees(51.5, -0.1)

        path = PathGeometry()
        path.set_tx_rx(tx, rx)

        azimuth_deg = path.get_azimuth_tr_degrees()
        # Expected azimuth ~52°
        assert 50 < azimuth_deg < 55
```

**Run unit tests:**
```bash
pytest tests/test_path_geometry.py -v
```

---

### Integration Tests

Test interactions between multiple modules.

**Example: Full Prediction Test**
```python
# test_phase5_api.py (simplified)

from dvoacap import PredictionEngine
from dvoacap.path_geometry import GeoPoint
import numpy as np

def test_full_prediction():
    """Test complete prediction pipeline"""
    engine = PredictionEngine()

    # Configure
    engine.params.ssn = 100.0
    engine.params.month = 6
    engine.params.tx_power = 100.0
    engine.params.tx_location = GeoPoint.from_degrees(40.0, -75.0)

    # Run prediction
    rx_location = GeoPoint.from_degrees(51.5, -0.1)
    frequencies = [7.0, 14.0, 21.0]

    engine.predict(
        rx_location=rx_location,
        utc_time=0.5,
        frequencies=frequencies
    )

    # Verify results
    assert engine.muf_calculator.muf > 0
    assert len(engine.predictions) == 3

    for pred in engine.predictions:
        assert pred.signal.snr_db is not None
        assert 0 <= pred.signal.reliability <= 1
```

**Run integration tests:**
```bash
pytest test_phase5_api.py -v
```

---

### Validation Tests

Compare DVOACAP output with reference VOACAP data.

**Full validation suite:**
```bash
# Run complete validation
python3 test_voacap_reference.py

# Sample output:
# ======================== Validation Results (v1.0.1) ===============
# Total test comparisons: 261 (11 test cases)
# Passed: 226 (86.6%)
# Failed: 35 (13.4%)
#
# Phase 1 (Path Geometry): 100% pass
# Phase 2 (Solar/Geomag): 100% pass
# Phase 3 (Ionospheric): 98.5% pass
# Phase 4 (MUF/Raytracing): 95.2% pass
# Phase 5 (Signal Predictions): 86.6% pass (exceeds 85% target)
# =====================================================================
```

**Run specific validation tests:**
```bash
# Test mode selection
pytest test_mode_selection.py -v

# Test high frequency edge cases
pytest test_high_freqs.py -v
```

See [Validation Status](Validation-Status) for detailed validation results.

---

## Writing Tests

### Test Structure

**Follow pytest conventions:**
```python
# tests/test_my_module.py

import pytest
from dvoacap.my_module import MyClass


class TestMyClass:
    """Tests for MyClass - use docstrings"""

    def setup_method(self):
        """Run before each test method"""
        self.obj = MyClass()

    def teardown_method(self):
        """Run after each test method"""
        pass

    def test_basic_functionality(self):
        """Test basic usage - clear description"""
        result = self.obj.method(42)
        assert result == 84

    def test_edge_case_negative_input(self):
        """Test behavior with negative input"""
        with pytest.raises(ValueError):
            self.obj.method(-1)

    @pytest.mark.parametrize("input,expected", [
        (1, 2),
        (2, 4),
        (3, 6),
        (10, 20),
    ])
    def test_multiple_inputs(self, input, expected):
        """Test with multiple parameter values"""
        assert self.obj.method(input) == expected
```

---

### Test Assertions

**Common assertions:**
```python
# Equality
assert result == expected

# Approximate equality (for floats)
import math
assert math.isclose(result, expected, rel_tol=1e-5)

# NumPy arrays
import numpy as np
np.testing.assert_allclose(result, expected, rtol=1e-5)

# Value ranges
assert 0 < result < 100

# Type checks
assert isinstance(result, float)

# Exception testing
with pytest.raises(ValueError):
    function_that_should_raise()

# Exception message matching
with pytest.raises(ValueError, match="invalid input"):
    function_that_should_raise()
```

---

### Fixtures

Use fixtures for reusable test data:

```python
# conftest.py or in test file

import pytest
from dvoacap import PredictionEngine
from dvoacap.path_geometry import GeoPoint

@pytest.fixture
def prediction_engine():
    """Create a configured prediction engine"""
    engine = PredictionEngine()
    engine.params.ssn = 100.0
    engine.params.month = 6
    engine.params.tx_power = 100.0
    engine.params.tx_location = GeoPoint.from_degrees(40.0, -75.0)
    return engine

@pytest.fixture
def sample_path():
    """Create a sample propagation path"""
    tx = GeoPoint.from_degrees(40.0, -75.0)
    rx = GeoPoint.from_degrees(51.5, -0.1)
    return tx, rx

# Use fixtures in tests
def test_with_fixtures(prediction_engine, sample_path):
    """Test using fixtures"""
    tx, rx = sample_path
    engine = prediction_engine

    engine.predict(rx_location=rx, utc_time=0.5, frequencies=[14.0])

    assert len(engine.predictions) == 1
```

---

### Parametrized Tests

Test multiple scenarios efficiently:

```python
@pytest.mark.parametrize("lat,lon,expected_hemisphere", [
    (40.0, -75.0, "Northern"),
    (-33.0, 151.0, "Southern"),
    (0.0, 0.0, "Equatorial"),
])
def test_hemisphere_detection(lat, lon, expected_hemisphere):
    """Test hemisphere detection for various locations"""
    point = GeoPoint.from_degrees(lat, lon)
    hemisphere = detect_hemisphere(point)
    assert hemisphere == expected_hemisphere
```

---

## Validation Testing

### Comparing with Reference VOACAP

**Test against reference output:**
```python
import json
from dvoacap import PredictionEngine
from dvoacap.path_geometry import GeoPoint

def test_against_voacap_reference():
    """Compare prediction with reference VOACAP output"""

    # Load reference data
    with open('SampleIO/voacap_reference/case_001.json', 'r') as f:
        reference = json.load(f)

    # Run DVOACAP prediction
    engine = PredictionEngine()
    engine.params.ssn = reference['ssn']
    engine.params.month = reference['month']
    engine.params.tx_location = GeoPoint.from_degrees(
        reference['tx_lat'], reference['tx_lon']
    )

    rx_location = GeoPoint.from_degrees(
        reference['rx_lat'], reference['rx_lon']
    )

    engine.predict(
        rx_location=rx_location,
        utc_time=reference['utc_time'],
        frequencies=[reference['frequency']]
    )

    # Compare results
    pred = engine.predictions[0]

    # Allow 10% tolerance
    assert abs(pred.signal.snr_db - reference['snr_db']) < 2.0
    assert abs(pred.signal.reliability - reference['reliability']) < 0.1
```

---

### Validation Tolerances

**Recommended tolerances for validation:**

| Parameter | Tolerance | Reason |
|-----------|-----------|--------|
| Distance | ±0.1 km | Great circle calculation |
| Azimuth | ±0.1° | Bearing calculation |
| foF2 | ±0.2 MHz | CCIR model differences |
| MUF | ±0.5 MHz | Raytracing variations |
| SNR | ±2.0 dB | Signal model differences |
| Reliability | ±10% | Statistical variations |

---

## Coverage

### Running Coverage Analysis

**Generate coverage report:**
```bash
# Run tests with coverage
pytest --cov=dvoacap tests/

# Sample output:
# ---------- coverage: platform linux, python 3.10.12 -----------
# Name                                Stmts   Miss  Cover
# -------------------------------------------------------
# src/dvoacap/__init__.py                12      0   100%
# src/dvoacap/path_geometry.py          156      8    95%
# src/dvoacap/ionospheric_profile.py    234     45    81%
# src/dvoacap/muf_calculator.py         189     23    88%
# src/dvoacap/prediction_engine.py      312     67    79%
# -------------------------------------------------------
# TOTAL                                1234    167    86%
```

**Generate HTML coverage report:**
```bash
pytest --cov=dvoacap --cov-report=html tests/

# Open in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

**Show missing lines:**
```bash
pytest --cov=dvoacap --cov-report=term-missing tests/
```

---

### Coverage Goals

**Target coverage levels:**
- **Overall:** >80%
- **Core modules (path_geometry, ionospheric):** >90%
- **Critical calculations (MUF, signal):** >85%
- **Utilities and helpers:** >70%

---

## Continuous Integration

### GitHub Actions

DVOACAP-Python uses GitHub Actions for CI/CD.

**Validation workflow:**
```yaml
# .github/workflows/validation.yml

name: Validation Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -e ".[dev]"

      - name: Run tests
        run: |
          pytest -v --cov=dvoacap tests/

      - name: Run validation
        run: |
          python3 test_voacap_reference.py
```

**View CI results:**
- Visit repository on GitHub
- Click "Actions" tab
- Select workflow run

---

## Debugging Tests

### Running Tests in Debug Mode

**Use pdb debugger:**
```python
# Add breakpoint in test
def test_my_function():
    result = my_function(42)
    import pdb; pdb.set_trace()  # Debugger will stop here
    assert result == 84
```

**Run with debugger:**
```bash
pytest tests/test_my_module.py -s

# When breakpoint hits:
# (Pdb) print(result)
# (Pdb) next  # Step to next line
# (Pdb) continue  # Continue execution
```

---

### Print Debugging

**Show print output:**
```bash
pytest -s tests/test_my_module.py
```

**Add debug output:**
```python
def test_my_function():
    result = my_function(42)
    print(f"DEBUG: result = {result}")
    assert result == 84
```

---

### Failed Test Inspection

**Show full traceback:**
```bash
pytest -v --tb=long
```

**Show local variables:**
```bash
pytest -v --tb=short --showlocals
```

---

## Best Practices

### Test Naming

**Use descriptive names:**
```python
# Good
def test_distance_calculation_for_transatlantic_path():
    """Test distance between Philadelphia and London"""
    pass

# Bad
def test1():
    pass
```

---

### Test Independence

**Each test should be independent:**
```python
# Good - each test sets up its own data
def test_feature_a():
    data = create_test_data()
    assert feature_a(data) == expected

def test_feature_b():
    data = create_test_data()
    assert feature_b(data) == expected

# Bad - tests depend on each other
def test_setup():
    global data
    data = create_test_data()

def test_feature():
    assert feature(data) == expected  # Depends on test_setup
```

---

### Fast Tests

**Keep tests fast:**
- Mock expensive operations
- Use small datasets
- Avoid network calls
- Target: <10 seconds for full test suite

---

### Test Documentation

**Use clear docstrings:**
```python
def test_muf_calculation_at_solar_maximum():
    """
    Test MUF calculation during solar maximum conditions.

    Verifies that MUF is calculated correctly when SSN=200,
    matching reference VOACAP output within 0.5 MHz tolerance.
    """
    pass
```

---

## Next Steps

- **[Development Setup](Development-Setup)** - Set up development environment
- **[Contributing](Contributing)** - Contribution guidelines
- **[Validation Status](Validation-Status)** - Current validation results
- **[API Reference](API-Reference)** - Code documentation

---

**Need help?** Check [Troubleshooting](Troubleshooting) or open an issue on [GitHub](https://github.com/skyelaird/dvoacap-python/issues).
