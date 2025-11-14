# DVOACAP-Python Validation Analysis
## Date: 2025-11-14

## Executive Summary

**Current Status:** 72.2% validation pass rate (156/216 tests)
**Target:** >80% pass rate with expanded test coverage
**Priority:** Expand test suite to cover diverse propagation scenarios

---

## Baseline Validation Results

### Test Configuration
- **Reference Path:** Tangier (35.80°N, 5.90°W) → Belgrade (44.90°N, 20.50°E)
- **Distance:** ~2440 km (medium path)
- **Month:** June 1994
- **SSN:** 100 (moderate solar activity)
- **Frequencies:** 6.07, 7.20, 9.70, 11.85, 13.70, 15.35, 17.73, 21.65, 25.89 MHz
- **UTC Hours:** 1-24 (all hours)
- **Total Tests:** 216 comparisons

### Pass/Fail Summary
```
Total comparisons: 216
Passed:            156 (72.2%)
Failed:            60 (27.8%)
```

### Failure Analysis by Frequency

| Frequency | Pass Rate | Primary Issue |
|-----------|-----------|---------------|
| 6.07 MHz  | 50.0% (12/24) | Reliability underestimated by ~25-30% |
| 7.20 MHz  | 50.0% (12/24) | Reliability underestimated by ~20-25% |
| 9.70 MHz  | 87.5% (21/24) | Generally good |
| 11.85 MHz | 95.8% (23/24) | Excellent |
| 13.70 MHz | 91.7% (22/24) | Good |
| 15.35 MHz | 87.5% (21/24) | Generally good |
| 17.73 MHz | 100% (24/24) | Perfect |
| 21.65 MHz | 95.8% (23/24) | Excellent |
| 25.89 MHz | 41.7% (10/24) | Large SNR deviations (10-47 dB) |

### Failure Analysis by Time of Day

**Night (17:00-05:00 UTC):**
- Pass rate: 81.5% (88/108 tests)
- Issues: Low frequency reliability underestimation

**Day (06:00-16:00 UTC):**
- Pass rate: 63.0% (68/108 tests)
- Issues: D-layer absorption, high frequency SNR errors

### Key Patterns Identified

1. **Low Frequency Failures (6-7 MHz)**
   - Systematic reliability underestimation (~25-30%)
   - SNR generally within tolerance
   - MUF day factor accurate
   - **Root cause:** Likely E-layer or D-layer absorption calculation

2. **High Frequency Failures (25.9 MHz)**
   - Large SNR deviations (10-47 dB)
   - Near the MUF (~26 MHz)
   - **Root cause:** Near-MUF signal calculations, mode selection

3. **Daytime Failures (06:00-16:00)**
   - More failures during daylight
   - Affects low frequencies most
   - **Root cause:** D-layer absorption modeling

4. **Mid-Range Success (9.7-21.6 MHz)**
   - 90-100% pass rate
   - Core calculations working well

---

## Current Test Coverage Gaps

### Path Distance Coverage
- ✅ Medium paths (2000-5000 km): 1 path tested
- ❌ Short paths (<1000 km): Not tested
- ❌ Long paths (>10000 km): Not tested
- ❌ Antipodal paths (~20000 km): Not tested

### Geographic Coverage
- ✅ Europe → Europe: 1 path
- ❌ North America → Europe: Not tested
- ❌ Trans-Pacific: Not tested
- ❌ Equatorial paths: Not tested
- ❌ Polar paths: Not tested

### Solar Condition Coverage
- ✅ SSN=100 (moderate): Tested
- ❌ SSN=10 (solar minimum): Not tested
- ❌ SSN=200 (solar maximum): Not tested

### Seasonal Coverage
- ✅ June (summer): Tested
- ❌ December (winter): Not tested
- ❌ March/September (equinox): Not tested

### Frequency Coverage
- ✅ HF bands 40m-10m: Well covered
- ❌ 160m, 80m (1.8-3.8 MHz): Not tested
- ❌ 6m (50 MHz): Not tested
- ❌ Edge cases (<3 MHz, >30 MHz): Not tested

---

## Proposed Test Expansion Plan

### Phase 1: Diverse Path Distances (Priority: Critical)

Generate reference data for:

1. **Short Path (<1000 km)**
   - Example: Philadelphia (39.95°N, 75.17°W) → Boston (42.36°N, 71.06°W)
   - Distance: ~430 km
   - NVIS and single-hop E propagation
   - Frequencies: 3.5, 7, 14, 21 MHz

2. **Long Path (>10000 km)**
   - Example: Philadelphia → Tokyo (35.68°N, 139.69°E)
   - Distance: ~10,900 km
   - Multi-hop F2 propagation
   - Frequencies: 7, 14, 21, 28 MHz

3. **Very Long Path (Antipodal)**
   - Example: Philadelphia → Perth (31.95°S, 115.86°E)
   - Distance: ~18,700 km
   - Maximum hops, near-antipodal effects
   - Frequencies: 14, 21, 28 MHz

### Phase 2: Solar Condition Variations (Priority: High)

Generate reference data for existing paths with:

1. **Solar Minimum (SSN=10)**
   - Lower MUF
   - Different mode selection
   - Tangier → Belgrade path

2. **Solar Maximum (SSN=200)**
   - Higher MUF
   - Enhanced F2 layer
   - Tangier → Belgrade path

### Phase 3: Seasonal Variations (Priority: Medium)

Generate reference data for:

1. **Winter Solstice (December)**
   - Different ionospheric conditions
   - Tangier → Belgrade path
   - SSN=100

2. **Equinox (March)**
   - Equinoctial enhancements
   - Tangier → Belgrade path
   - SSN=100

### Phase 4: Edge Cases (Priority: Low)

1. **Very Low Frequencies (<5 MHz)**
   - Absorption-dominated
   - Different propagation modes

2. **Very High Frequencies (>28 MHz)**
   - Near upper HF limit
   - Sporadic E, TEP

3. **Polar Paths**
   - High latitude effects
   - Aurora zone

---

## Implementation Plan

### Step 1: Generate Reference Data

For each test case, run original VOACAP or VOACAPL and save:
- Input parameters (JSON format)
- Raw output (voacapx.out format)
- Store in `SampleIO/reference_<testname>/`

**Tools needed:**
- VOACAPL installation (Linux-compatible VOACAP)
- OR access to online VOACAP API
- OR manual runs of Voacapwin.exe

### Step 2: Create Parametrized Test Framework

Expand `test_voacap_reference.py` to support:

```python
# Define test cases
TEST_CASES = [
    {
        'name': 'tangier_belgrade',
        'tx': (35.80, -5.90),
        'rx': (44.90, 20.50),
        'distance_km': 2440,
        'month': 6,
        'ssn': 100,
        'reference_file': 'SampleIO/voacapx.out'
    },
    {
        'name': 'philadelphia_boston',
        'tx': (39.95, -75.17),
        'rx': (42.36, -71.06),
        'distance_km': 430,
        'month': 6,
        'ssn': 100,
        'reference_file': 'SampleIO/reference_short_path/voacapx.out'
    },
    # ... more test cases
]

@pytest.mark.parametrize("test_case", TEST_CASES)
def test_path_validation(test_case):
    """Validate prediction for specific path"""
    # Run validation
    # Compare against reference
    # Assert within tolerances
```

### Step 3: Extend Unit Tests

Create comprehensive unit tests for:

1. **Signal Module** (`src/dvoacap/signal.py`)
   - Signal power calculations
   - Noise calculations
   - SNR calculations
   - Reliability calculations

2. **MUF Calculator** (`src/dvoacap/muf_calculator.py`)
   - MUF calculations for different layers
   - FOT calculations
   - Mode selection logic

3. **Absorption Model** (`src/dvoacap/ionospheric_profile.py`)
   - D-layer absorption
   - E-layer absorption
   - F-layer absorption

### Step 4: CI/CD Integration

Create `.github/workflows/validation.yml`:

```yaml
name: DVOACAP Validation

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install numpy scipy matplotlib pytest
      - name: Run unit tests
        run: pytest tests/ -v
      - name: Run reference validation
        run: python3 test_voacap_reference.py
      - name: Check pass rate
        run: |
          PASS_RATE=$(python3 -c "import json; data=json.load(open('validation_reference_results.json')); print(data['summary']['pass_rate'])")
          echo "Pass rate: $PASS_RATE%"
          if (( $(echo "$PASS_RATE < 80" | bc -l) )); then
            echo "❌ Validation pass rate below 80%"
            exit 1
          fi
          echo "✅ Validation passed"
```

---

## Success Criteria

### Short-term (Week 1-2)
- ✅ Baseline validation established (72.2%)
- 🔄 Test expansion plan created
- ⏳ 3+ new reference paths generated
- ⏳ Parametrized test framework implemented

### Medium-term (Week 3-4)
- ⏳ 10+ diverse test cases
- ⏳ >80% overall pass rate
- ⏳ Unit test coverage >70%
- ⏳ CI/CD validation automated

### Long-term (Week 5-8)
- ⏳ Comprehensive test suite (30+ cases)
- ⏳ >85% pass rate
- ⏳ Known limitations documented
- ⏳ Real-world WSPR validation

---

## Next Actions

### Immediate (Today)
1. ✅ Create this analysis document
2. Create parametrized test framework
3. Document test case generation process

### This Week
4. Generate 3-5 new reference test cases:
   - Short path (Philadelphia → Boston)
   - Long path (Philadelphia → Tokyo)
   - Different SSN (Tangier → Belgrade, SSN=50)

5. Implement parametrized tests
6. Run expanded validation suite

### Next Week
7. Generate remaining test cases (10+ total)
8. Add unit tests for signal and MUF modules
9. Set up CI/CD automation
10. Create comprehensive validation report

---

## Known Issues to Track

From baseline validation, prioritize fixing:

1. **Low frequency reliability** (6-7 MHz)
   - Underestimated by ~25-30%
   - Affects nighttime predictions
   - Location: Reliability calculation in prediction_engine.py

2. **High frequency SNR** (25.9 MHz)
   - Deviations up to 47 dB
   - Near-MUF conditions
   - Location: Signal power calculations, mode selection

3. **Daytime D-layer absorption**
   - More failures during day (06:00-16:00 UTC)
   - Affects low frequencies
   - Location: Ionospheric absorption calculations

---

## Resources

### Reference Files
- Baseline: `SampleIO/voacapx.out`
- Results: `validation_reference_results.json`
- Test script: `test_voacap_reference.py`

### Documentation
- Validation strategy: `VALIDATION_STRATEGY.md`
- Next steps plan: `NEXT_STEPS.md`
- FORTRAN analysis: `FORTRAN_ANALYSIS_AND_RECOMMENDATIONS.md`

### Tools
- Test script: `test_voacap_reference.py`
- Functional validation: `validate_predictions.py`
- Unit tests: `tests/test_*.py`

---

## Appendix: Detailed Failure Breakdown

### Low Frequency Failures (6.07 MHz)

**Failed Hours:** 1, 2, 3, 5, 7, 8, 9, 20, 21, 22, 23, 24 (12 failures)
**Pattern:** Mostly nighttime and early morning hours
**Error:** Reliability underestimated by 20-30%
**SNR:** Generally within tolerance (±10 dB)

### High Frequency Failures (25.89 MHz)

**Failed Hours:** 1, 2, 3, 4, 6, 7, 8, 9, 10, 12, 13, 14, 15, 16, 24 (14 failures)
**Pattern:** All times of day
**Error:** Large SNR deviations (10-47 dB)
**Reliability:** Often within tolerance

### Daytime Failures (06:00-16:00 UTC)

**Most affected frequencies:** 6.07 MHz, 7.20 MHz, 25.89 MHz
**Total daytime tests:** 108
**Daytime failures:** 40
**Daytime pass rate:** 63.0%

---

**Last Updated:** 2025-11-14
**Next Review:** After test expansion implementation
