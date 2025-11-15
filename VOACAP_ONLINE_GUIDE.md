# Using VOACAP Online Service for Reference Data Generation

**Service URL:** https://www.voacap.com/hf/

This guide explains how to use the online VOACAP service to generate true reference outputs for validating DVOACAP-Python.

---

## Quick Start: Generate Reference Data for Test Cases

We have 10 test cases ready to run through VOACAP Online. Each has a pre-configured `.voa` input file in `SampleIO/`.

### Priority Test Cases (Run These First)

**Start with these 5 diverse scenarios:**

1. **Short Path** - `input_short_001_us_east.voa`
   - Philadelphia (39.95°N, 75.17°W) → Boston (42.36°N, 71.06°W)
   - Distance: 430 km, SSN: 100, Month: March
   - Frequencies: 3.5, 7.0, 14.0, 21.0, 28.0 MHz

2. **Medium Transatlantic** - `input_medium_001_transatlantic.voa`
   - Philadelphia → London (51.51°N, 0.13°W)
   - Distance: 5,570 km, SSN: 100, Month: June
   - Frequencies: 7.0, 10.1, 14.0, 18.1, 21.0, 24.9, 28.0 MHz

3. **Long Path** - `input_long_002_australia.voa`
   - London → Sydney (33.87°S, 151.21°E)
   - Distance: 17,015 km, SSN: 75, Month: September
   - Frequencies: 7.0, 14.0, 21.0 MHz

4. **Polar Path** - `input_polar_001_arctic.voa`
   - Anchorage (61.22°N, 149.90°W) → Oslo (59.91°N, 10.75°E)
   - Distance: 5,970 km, SSN: 50, Month: January
   - Frequencies: 7.0, 14.0, 21.0 MHz

5. **Equatorial Path** - `input_equatorial_001.voa`
   - Singapore (1.35°N, 103.82°E) → São Paulo (23.55°S, 46.63°W)
   - Distance: 15,830 km, SSN: 100, Month: June
   - Frequencies: 7.0, 14.0, 21.0, 28.0 MHz

---

## How to Use VOACAP Online

### Method 1: Copy-Paste Input File

1. Open a `.voa` file (e.g., `SampleIO/input_short_001_us_east.voa`)
2. Copy the entire contents
3. Go to https://www.voacap.com/hf/
4. Paste the contents into the input form
5. Submit the prediction
6. Save the output to `SampleIO/voacap_ref_<test_id>.out`

**Example `.voa` file format:**
```
LINEMAX   20
COEFFS    CCIR
TIME      4 24 6 12 18
MONTH     3 3
SUNSPOT   100 100
LABEL     Philadelphia to Boston (Short Path)
CIRCUIT   1 short_001_us_east
TRANSMIT  39.95 -75.17
RECEIVE   42.36 -71.06
SYSTEM    100  73  3.00
FREQUENCY 5 3.50 7.00 14.00 21.00 28.00
FPROB     1.00 0.10 0.90 0.10 0.90
METHOD    30
EXECUTE
QUIT
```

### Method 2: Manual Entry (Alternative)

If copy-paste doesn't work, manually enter:

**For "Philadelphia to Boston (Short Path)":**
- TX: 39.95°N, 75.17°W
- RX: 42.36°N, 71.06°W
- Month: March (3)
- SSN: 100
- UTC Hours: 0, 6, 12, 18
- Frequencies: 3.5, 7.0, 14.0, 21.0, 28.0 MHz
- TX Power: 100 kW (from SYSTEM line: 100)
- Required SNR: 73 dB
- Required Reliability: 90% (from SYSTEM line: 3.00 = 3 dB = 90%)
- Antennas: Isotropic (both TX and RX)
- Method: 30 (point-to-point)

---

## Saving VOACAP Output

### File Naming Convention

Save outputs with prefix `voacap_ref_` to distinguish from regression baselines:

```
SampleIO/voacap_ref_short_001.out           (TRUE VOACAP reference)
SampleIO/ref_short_001.out                   (regression baseline - DVOACAP-Python)
```

### Complete List of Files to Generate

**Priority 5** (most valuable for validation):
- `voacap_ref_short_001.out` - from `input_short_001_us_east.voa`
- `voacap_ref_medium_001.out` - from `input_medium_001_transatlantic.voa`
- `voacap_ref_long_002.out` - from `input_long_002_australia.voa`
- `voacap_ref_polar_001.out` - from `input_polar_001_arctic.voa`
- `voacap_ref_equatorial_001.out` - from `input_equatorial_001.voa`

**Additional 5** (for comprehensive coverage):
- `voacap_ref_short_002.out` - from `input_short_002_europe.voa`
- `voacap_ref_medium_002.out` - from `input_medium_002_us_japan.voa`
- `voacap_ref_long_001.out` - from `input_long_001_antipodal.voa`
- `voacap_ref_solar_min_001.out` - from `input_solar_min_001.voa`
- `voacap_ref_solar_max_001.out` - from `input_solar_max_001.voa`

---

## Integrating VOACAP References into Test Suite

### Option 1: Add as New Test Cases

Create new test case entries in `test_config.json`:

```json
{
  "id": "voacap_short_001",
  "name": "Philadelphia to Boston (VOACAP Reference)",
  "description": "TRUE VOACAP reference validation - short path",
  "tx_location": {"lat": 39.95, "lon": -75.17, "name": "Philadelphia, PA"},
  "rx_location": {"lat": 42.36, "lon": -71.06, "name": "Boston, MA"},
  "distance_km": 430,
  "month": 3,
  "ssn": 100,
  "frequencies_mhz": [3.5, 7.0, 14.0, 21.0, 28.0],
  "utc_hours": [0, 6, 12, 18],
  "reference_file": "SampleIO/voacap_ref_short_001.out",
  "status": "active"
}
```

### Option 2: Replace Regression Baselines

Update existing test cases to point to VOACAP references:

```json
{
  "id": "short_001_us_east",
  "reference_file": "SampleIO/voacap_ref_short_001.out",  // Changed from ref_short_001.out
  "status": "active"
}
```

### Option 3: Dual Validation (Recommended)

Keep both regression baselines AND VOACAP references:
- Regression baselines: Ensure no regressions in DVOACAP-Python
- VOACAP references: Measure actual accuracy against original VOACAP

---

## Running Validation with VOACAP References

Once you've saved VOACAP output files:

**Test specific VOACAP reference:**
```bash
# Update test_config.json to point to voacap_ref_*.out file
# Then run validation
python test_voacap_reference.py --test-cases voacap_short_001
```

**Compare accuracy:**
```bash
# Run with regression baseline
python test_voacap_reference.py --test-cases short_001_us_east

# Run with VOACAP reference
python test_voacap_reference.py --test-cases voacap_short_001

# Compare results
```

---

## Expected Results

### Current State (Regression Baselines)
- Pass rate: 86.6% (self-comparison)
- This is not "real" validation, just regression testing

### With VOACAP References
- Pass rate: **Unknown** (this is what we want to discover!)
- True accuracy measurement against original VOACAP
- Identify specific deviations and areas for improvement

**Hypothesis:**
- SNR: May see larger deviations (±10 dB tolerance should still pass most)
- Reliability: May see moderate deviations (±20% tolerance)
- MUF: Should be very close (<±2 MHz)
- Mode selection: Should match well

---

## Upload Instructions

### To GitHub

After generating VOACAP reference files:

```bash
cd /path/to/dvoacap-python

# Add VOACAP reference files
git add SampleIO/voacap_ref_*.out

# Update test config if needed
git add test_config.json

# Commit
git commit -m "Add true VOACAP reference outputs for validation"

# Push to branch
git push origin claude/expand-test-coverage-01CH5hpdPUHHPCcbWXMHtUoJ
```

### To Local Repo

Simply save the `.out` files directly to:
```
/home/user/dvoacap-python/SampleIO/voacap_ref_<test_id>.out
```

---

## Troubleshooting

### Common Issues

**Issue: Output format differs from expected**
- VOACAP Online may have different output format than desktop VOACAP
- Parser in `test_voacap_reference.py` may need adjustment
- Check the first few lines to ensure format matches `voacapx.out`

**Issue: Missing metrics in output**
- Ensure METHOD 30 is specified (point-to-point mode)
- Check that all required cards are present (SYSTEM, FREQUENCY, etc.)

**Issue: Different frequencies in output**
- VOACAP may add/remove frequencies based on MUF
- Check FREQUENCY line in input file

---

## Questions to Consider

1. **Which test cases to prioritize?**
   - Start with 5 diverse cases (short, medium, long, polar, equatorial)
   - Add solar variations (min/max) if time permits

2. **How to integrate results?**
   - Option A: Add as new test cases (keeps both)
   - Option B: Replace regression baselines (cleaner)
   - Option C: Dual validation (most thorough)

3. **What accuracy do we expect?**
   - Based on 83.8% pass rate with one true VOACAP reference
   - Likely 80-85% with diverse test cases
   - Some scenarios (polar, long paths) may have lower accuracy

---

## Next Steps

**Immediate (when VOACAP outputs are available):**
1. Save outputs to `SampleIO/voacap_ref_*.out`
2. Update `test_config.json` to add/modify test cases
3. Run validation: `python test_voacap_reference.py`
4. Analyze results and identify deviations
5. Document findings in validation report

**Analysis:**
1. Compare DVOACAP-Python vs VOACAP for each test case
2. Identify patterns in failures (specific frequencies, times, path types)
3. Prioritize improvements based on largest deviations
4. Update NEXT_STEPS.md with findings

---

**See Also:**
- `docs/Original_VOACAP_Manual.pdf` - Full VOACAP documentation
- `REGRESSION_BASELINE_APPROACH.md` - Current testing methodology
- `test_voacap_reference.py` - Validation test suite
- `test_config.json` - Test case definitions
