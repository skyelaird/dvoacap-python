# DVOACAP-Python Validation Strategy

## Executive Summary

**Critical Issue Identified:** While DVOACAP-Python successfully produces propagation predictions (outputs numerical values), **we have not yet validated that these predictions are accurate** against a known reference implementation.

This document outlines the validation strategy to ensure DVOACAP-Python produces correct HF propagation predictions, not just plausible-looking numbers.

---

## The Validation Gap

### What We Have Been Doing (Insufficient)

1. **Component-level validation** ✓
   - Path geometry calculations match reference (< 0.01% error)
   - Solar calculations validated
   - Geomagnetic model validated
   - Ionospheric coefficient maps loaded correctly

2. **Sanity checking** ✓
   - `validate_predictions.py` checks if values are in reasonable ranges:
     - Reliability: 0-100%
     - SNR: -50 to +100 dB
     - MUF: 0-100 MHz
   - **This only proves the engine runs without crashing, not that it's correct**

### What We Need (Critical)

**End-to-end accuracy validation** against ground truth:
- Compare full propagation predictions against reference VOACAP output
- Verify SNR, reliability, MUF, signal strength, path loss match within tolerances
- Test across multiple paths, frequencies, times, and conditions

**Why This Matters:**
- Individual components can be correct but integration can fail
- Subtle bugs in coordinate systems, unit conversions, or formula implementations
- Without validation, we're just generating plausible noise

---

## Validation Approaches

### 1. Reference Implementation Comparison (PRIMARY)

**Status:** ✅ **Now Implemented** (see `test_voacap_reference.py`)

**Method:**
- Compare DVOACAP-Python output against reference files from original VOACAP
- Use `SampleIO/voacapx.out` - output from original Voacapwin.exe
- Test case: Tangier → Belgrade, June 1994, SSN=100, multiple frequencies

**Acceptance Criteria:**
- SNR: Within ±10 dB of reference
- Reliability: Within ±20% of reference
- MUF day factor: Within ±0.2 of reference
- Pass rate: >80% of test cases within tolerances

**Usage:**
```bash
# Run full reference validation
python3 test_voacap_reference.py

# Test specific hours
python3 test_voacap_reference.py --hours 12 18

# Test specific frequencies
python3 test_voacap_reference.py --freqs 14.15 21.2
```

**Advantages:**
- Deterministic - same inputs always produce same results
- No external dependencies
- Fast execution
- Reference data already in repository

**Limitations:**
- Limited to test cases we have reference data for
- Doesn't validate against real-world propagation
- Reference VOACAP itself has limitations/assumptions

### 2. Real-World Measurement Validation (FUTURE)

**Status:** ⏳ Not yet implemented

**Method:**
- Compare predictions against actual HF propagation measurements
- Data sources:
  - **WSPRnet** - Weak Signal Propagation Reporter Network
  - **PSKReporter** - PSK and other digital mode reports
  - **Reverse Beacon Network** - CW and digital mode reception reports

**Example Implementation:**
```python
# Fetch WSPR spots for a time period
wspr_spots = fetch_wspr_spots(
    tx_call="VE1ATM",
    start_time="2025-01-01 00:00",
    end_time="2025-01-01 23:59"
)

# For each spot, run DVOACAP prediction
for spot in wspr_spots:
    prediction = engine.predict(
        rx_location=spot.rx_location,
        freq=spot.frequency,
        utc_time=spot.time
    )

    # Compare predicted vs actual SNR
    snr_error = abs(prediction.snr - spot.snr)

    # Track statistics
    ...
```

**Acceptance Criteria:**
- Median SNR error: <10 dB
- Predicted reliability correlates with reception success rate
- MUF predictions align with highest observable frequency

**Advantages:**
- Validates against reality
- Large dataset available
- Tests real-world conditions

**Challenges:**
- Noisy data (antenna variations, QRM, propagation anomalies)
- Need statistical approach (not deterministic)
- External API dependencies
- Time-consuming data collection

### 3. Cross-Validation with Other Models (FUTURE)

**Status:** ⏳ Not yet implemented

**Candidate Models:**
- **ITU-R P.533** (soundbytes.asia/proppy) - Web interface only, no API
- **VOACAP Online** (voacap.com) - Prohibits automated access
- **Local VOACAPL** (jawatson/voacapl) - Requires installation

**Note:** As of 2025, no public VOACAP APIs allow automated access. Options:
1. Contact voacap.com for API permission (research/educational use)
2. Install VOACAPL locally and run comparison tests
3. Manual spot-checks via web interfaces

---

## Validation Workflow for Development

### For New Features/Bug Fixes

1. **Run unit tests**
   ```bash
   pytest tests/
   ```

2. **Run reference validation**
   ```bash
   python3 test_voacap_reference.py
   ```
   - Must pass with >80% accuracy
   - Any regression is a blocking issue

3. **Run functional validation**
   ```bash
   python3 validate_predictions.py --regions UK JA VK --bands 20m 15m
   ```
   - Ensures engine produces valid output
   - Checks for crashes/errors

4. **Manual spot-checks**
   - Compare a few predictions against online VOACAP (voacap.com)
   - Verify results "make sense" for known propagation conditions

### For Claude.ai Sessions

**Before making changes:**
```bash
# Establish baseline
python3 test_voacap_reference.py > baseline.txt
```

**After making changes:**
```bash
# Check for regressions
python3 test_voacap_reference.py > after.txt
diff baseline.txt after.txt
```

**Red flags:**
- Pass rate decreases
- New systematic errors (all SNR too high/low)
- Predictions fail for previously working cases

---

## Current Validation Status

### ✅ Validated Components
- Path geometry (great circle, bearings, distances)
- Solar position calculations
- Geomagnetic field model (IGRF)
- Ionospheric coefficient map loading (CCIR/URSI)

### ⚠️  Partially Validated
- Ionospheric profile calculations
  - Individual layer parameters computed
  - Not validated end-to-end with ray tracing

### ❌ Not Yet Validated (Critical Gaps)
- **Full end-to-end propagation predictions**
  - SNR calculations
  - Signal strength predictions
  - Path loss modeling
  - Reliability calculations
- **Signal integration**
  - Antenna gain application
  - Noise modeling
  - Required SNR checking

### 📊 Test Coverage

| Module | Unit Tests | Integration Tests | Reference Validation |
|--------|-----------|-------------------|---------------------|
| path_geometry | ✅ | ✅ | ✅ |
| solar | ✅ | ✅ | ✅ |
| geomagnetic | ✅ | ✅ | ✅ |
| ionospheric_profile | ✅ | ⚠️ | ❌ |
| muf_calculator | ⚠️ | ⚠️ | ❌ |
| prediction_engine | ❌ | ⚠️ | **⏳ Now Available** |
| signal | ❌ | ❌ | ❌ |

**Legend:**
- ✅ Comprehensive coverage
- ⚠️ Partial coverage
- ❌ No coverage
- ⏳ Implementation in progress

---

## Interpreting Validation Results

### Reference Validation (`test_voacap_reference.py`)

**What "PASS" means:**
- Predictions are within ±10 dB SNR of reference VOACAP
- Predictions are within ±20% reliability of reference
- >80% of test cases pass these tolerances

**What "PASS" does NOT mean:**
- Predictions are perfect
- Real-world accuracy is guaranteed
- VOACAP reference itself is perfect

**VOACAP has limitations:**
- Ionospheric model is statistical (CCIR coefficients)
- Doesn't account for sporadic E, aurora, etc.
- Antenna modeling is simplified
- No terrain/obstruction effects

### Expected Deviations

**Normal variations (acceptable):**
- SNR: ±5 dB typical
- Reliability: ±10% typical
- Slightly different mode selection (1F2 vs 2F2)

**Red flags (investigate):**
- Systematic bias (all predictions too high/low)
- SNR errors >15 dB
- Reliability errors >30%
- Predictions failing where reference succeeds

---

## Reference Data Inventory

### Current Reference Files

| File | Description | Path Coverage | Frequency Range | Time Coverage |
|------|-------------|---------------|-----------------|---------------|
| `SampleIO/voacapx.out` | Original VOACAP output | Tangier → Belgrade (~2440km) | 6-26 MHz | 24 hours |
| `SampleIO/input.json` | Input parameters for above | Single path | 9 frequencies | June, SSN=100 |

### Additional Reference Data Needed

**To improve validation coverage:**

1. **Short paths** (<1000 km)
   - Different propagation modes (E, F1, F2)
   - NVIS conditions

2. **Long paths** (>10,000 km)
   - Multi-hop propagation
   - Antipodal cases

3. **Different solar conditions**
   - Low SSN (sunspot minimum)
   - High SSN (sunspot maximum)
   - Different months/seasons

4. **Different frequencies**
   - HF bands: 160m, 80m, 40m, 30m, 20m, 17m, 15m, 12m, 10m
   - Edge cases: very low (<5 MHz), very high (>25 MHz)

**How to generate reference data:**
1. Install original VOACAP or VOACAPL
2. Run predictions with known inputs
3. Save output files to `SampleIO/`
4. Update `test_voacap_reference.py` to parse new formats

---

## Recommendations for Future Work

### Immediate Priorities (P0)

1. **Run reference validation** ✅ Now available
   ```bash
   python3 test_voacap_reference.py
   ```

2. **Fix any critical errors** found by reference validation
   - Focus on systematic biases first
   - Document known limitations

3. **Add more reference test cases**
   - Generate VOACAP output for different paths
   - Include edge cases

### Short-term (P1)

4. **Implement real-world validation**
   - WSPRnet comparison tool
   - Statistical analysis of prediction accuracy

5. **Expand test coverage**
   - Unit tests for signal module
   - Integration tests for full predictions

### Long-term (P2)

6. **Continuous validation**
   - Automated daily comparisons against WSPRnet
   - Trend analysis over time

7. **Cross-model validation**
   - Compare against ITU P.533 (if API available)
   - Benchmark against other implementations

---

## For Future Claude Sessions

**When you start a session on this repository:**

1. **Check current validation status:**
   ```bash
   python3 test_voacap_reference.py --quiet
   ```

2. **Understand what "working" means:**
   - ✅ Produces output ≠ Produces *correct* output
   - Reference validation is the truth

3. **Before claiming success:**
   - Run reference validation
   - Compare against baseline
   - Document any deviations

4. **When making changes:**
   - Test before and after
   - Don't break what works
   - If validation degrades, investigate why

**Key files:**
- `test_voacap_reference.py` - Truth test (compare against VOACAP)
- `validate_predictions.py` - Sanity test (does it run without crashing)
- `SampleIO/voacapx.out` - Reference ground truth
- `VALIDATION_STRATEGY.md` - This document

---

## Summary

**The Question:** Does DVOACAP-Python produce accurate HF propagation predictions?

**Previous Answer:** "It outputs numbers" ❌ Insufficient

**New Answer:** "Run `test_voacap_reference.py` to compare against reference VOACAP" ✅

**Validation is not optional.** Without validation against ground truth, we're just generating plausible-looking random numbers. This repository now has the tools to validate properly - use them.

---

*Last updated: 2025-01-14*
*Validation framework created to address accuracy verification gap*
