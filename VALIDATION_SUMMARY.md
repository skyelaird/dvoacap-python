# Validation & Debugging Tools - Summary

## What Was Created

I've built a comprehensive validation and debugging system to help you identify why your propagation results differ from VOACAP online.

### Files Created

1. **`validate_predictions.py`** (560 lines)
   - Main validation script comparing local vs VOACAP online
   - Side-by-side comparisons with tolerance checking
   - Detailed debugging mode for deep dives
   - JSON output for analysis

2. **`VALIDATION.md`** (650 lines)
   - Complete validation guide
   - Usage examples for all scenarios
   - Troubleshooting common issues
   - Interpreting results and failures

3. **`DEBUG_QUICKSTART.md`** (350 lines)
   - Quick start guide for immediate debugging
   - Step-by-step debugging workflow
   - Common issues and solutions
   - Command reference

4. **`VALIDATION_SUMMARY.md`** (this file)
   - Overview of the validation system

## How to Use

### 1. Quick Validation (Start Here)

Run a quick validation to identify problem areas:

```bash
cd /home/user/dvoacap-python
python3 validate_predictions.py --regions UK JA --bands 20m 15m
```

**What you'll see:**
- ✓ for predictions that match VOACAP online (within tolerance)
- ✗ for predictions that differ significantly
- Detailed metrics showing the differences

**Expected runtime:** ~30 seconds (includes 2-second delays for API rate limiting)

### 2. Debug Specific Mismatches

When you find a mismatch, get detailed internals:

```bash
python3 validate_predictions.py --debug UK 15m
```

**What you'll see:**
- Complete path geometry
- Ionospheric parameters
- Mode selection details
- Signal strength breakdown
- Noise calculations
- Side-by-side comparison with VOACAP
- Raw VOACAP response

### 3. Full Validation Suite

Test everything:

```bash
python3 validate_predictions.py
```

This tests:
- 4 regions (UK, Japan, Australia, Brazil)
- 4 bands (40m, 20m, 15m, 10m)
- Current UTC hour
- Total: 16 test cases

Results saved to `validation_results.json`

## Key Features

### Automatic Comparison

Compares three critical metrics:

| Metric | Tolerance | Why Important |
|--------|-----------|---------------|
| **Reliability** | ±15% | Overall circuit quality |
| **SNR** | ±5 dB | Signal reception quality |
| **MUF** | ±2 MHz | Ionospheric modeling accuracy |

### Smart Test Cases

Representative paths covering different propagation scenarios:

- **UK** (4,500 km) - Trans-Atlantic, typical DX
- **Japan** (10,500 km) - Long path over Pacific
- **Australia** (16,500 km) - Very long path, near antipodal
- **Brazil** (6,500 km) - Different hemisphere, equatorial crossing

### Detailed Debugging

Debug mode shows:
- Path distance and azimuth
- MUF calculations
- Mode selection (hops, layers, elevation angles)
- Signal components (power, loss, noise)
- All intermediate values
- VOACAP raw response for manual verification

### JSON Results

All results saved to `validation_results.json` with:
- Summary statistics (pass/fail rates)
- Per-test detailed results
- Comparison metrics
- Timestamp and configuration

## Understanding Results

### Good Match Example

```
20m (14.150 MHz): ✓ MATCH
    Local:  Rel= 75.0% SNR= 15.2dB Mode=2F2
    VOACAP: Rel= 78.0% SNR= 16.1dB
```

**Interpretation:** Within tolerance, normal variation

### Mismatch Example

```
15m (21.200 MHz): ✗ MISMATCH
    Local:  Rel= 45.0% SNR=  8.3dB MUF= 24.5MHz Mode=2F2
    VOACAP: Rel= 62.0% SNR= 12.1dB MUF= 26.2MHz
    → Reliability: local=45.0% vs VOACAP=62.0% (diff=17.0%)
    → SNR: local=8.3dB vs VOACAP=12.1dB (diff=3.8dB)
```

**Interpretation:** Significant difference, needs investigation

Possible causes:
- Different ionospheric model parameters
- Noise calculation differences
- MUF calculation variation

## What to Look For

### 1. Pattern Recognition

After running validation, analyze failures:

**By metric:**
- SNR failures → Check noise model
- Reliability failures → Check ionospheric parameters
- MUF failures → Check F2 layer calculations

**By band:**
- Low bands (40m) → D-layer absorption
- High bands (15m/10m) → F2 layer MUF
- All bands → Systematic issue

**By region:**
- Short paths → Path geometry, mode selection
- Long paths → Multi-hop calculations
- Specific region → Ionospheric model for that area

**By time:**
- Dawn/dusk → Terminator effects
- Noon → Absorption peaks
- Midnight → Low ionosphere

### 2. Typical Discrepancies

Based on VOACAP documentation, expect some variation:

**Normal (don't worry):**
- ±10% reliability variation
- ±3 dB SNR variation
- ±1 MHz MUF variation
- Different mode with similar performance

**Investigate:**
- >20% reliability difference
- >8 dB SNR difference
- >3 MHz MUF difference
- Consistently wrong on specific band/region

**Problem:**
- >50% test failures
- Systematic bias (always too high/low)
- Wrong mode selection on most tests
- MUF calculations way off

### 3. Debug Workflow

```
Run validation
    ↓
Identify failures
    ↓
Pattern analysis (which bands/regions/metrics?)
    ↓
Debug specific case with --debug
    ↓
Compare intermediate calculations
    ↓
Identify root cause
    ↓
Fix code or adjust tolerance
    ↓
Re-validate
```

## Common Issues

### Issue: "ModuleNotFoundError: No module named 'numpy'"

**Solution:**
```bash
pip install numpy requests --break-system-packages
```

### Issue: "Proppy.net API timeout"

**Solution:**
- Check internet connection
- Wait 30 seconds and retry
- Proppy.net may be experiencing high load
- Test fewer cases with `--regions UK --bands 20m`

### Issue: "All tests failing"

**Solution:**
1. Check your configuration matches VOACAP online:
   ```python
   python3 -c "from src.dvoacap.prediction_engine import PredictionEngine; e=PredictionEngine(); print(f'SSN={e.params.ssn}, Month={e.params.month}')"
   ```

2. Verify coefficient files:
   ```bash
   pytest tests/test_voacap_parser.py
   ```

3. Check basic prediction works:
   ```bash
   python3 Dashboard/generate_predictions.py
   ```

### Issue: "Permission denied"

**Solution:**
```bash
chmod +x validate_predictions.py
```

## Next Steps

1. **Run initial validation** to understand current state
   ```bash
   python3 validate_predictions.py --regions UK --bands 20m 15m
   ```

2. **Analyze results** - look for patterns in failures

3. **Debug worst case** - find the biggest discrepancy and debug it
   ```bash
   python3 validate_predictions.py --debug <REGION> <BAND>
   ```

4. **Compare calculations** - examine intermediate values to find where divergence occurs

5. **Investigate root cause** - check specific modules:
   - Ionospheric profile (`src/dvoacap/ionospheric_profile.py`)
   - MUF calculator (`src/dvoacap/muf_calculator.py`)
   - Noise model (`src/dvoacap/noise_model.py`)
   - Path geometry (`src/dvoacap/path_geometry.py`)

6. **Iterate** - fix issues and re-validate

## Files You'll Generate

When you run validation, these files are created:

- `validation_results.json` - Detailed results from last run
- (Optional) Custom test cases by editing `TEST_CASES` in `validate_predictions.py`

## Integration with Testing

Add to your CI/CD or test suite:

```bash
# In your test script
python3 validate_predictions.py --regions UK --bands 20m --quiet
if [ $? -eq 0 ]; then
    echo "Validation passed"
else
    echo "Validation failed - check validation_results.json"
    exit 1
fi
```

## Support

When reporting issues or asking for help, include:

1. Validation summary:
   ```bash
   python3 validate_predictions.py --quiet 2>&1 | tail -30
   ```

2. Specific debug output:
   ```bash
   python3 validate_predictions.py --debug UK 15m > debug_output.txt
   ```

3. Validation results file:
   ```bash
   cat validation_results.json
   ```

4. Your configuration (month, SSN, power, etc.)

## Documentation

- **Quick Start:** `DEBUG_QUICKSTART.md`
- **Full Guide:** `VALIDATION.md`
- **This Summary:** `VALIDATION_SUMMARY.md`

## Examples

### Example 1: Quick Check Before Release

```bash
# Test most common paths
python3 validate_predictions.py --regions UK JA --bands 20m 15m --quiet
```

### Example 2: Deep Investigation

```bash
# Full validation
python3 validate_predictions.py

# Analyze results
cat validation_results.json | python3 -m json.tool

# Debug worst case
python3 validate_predictions.py --debug JA 10m
```

### Example 3: Time-Based Testing

```bash
# Test different times of day
python3 validate_predictions.py --regions UK --bands 20m --hours 0 6 12 18
```

## Success Criteria

**Excellent:** >90% pass rate - Minor variations only
**Good:** 80-90% pass rate - Some systematic differences but acceptable
**Needs Work:** 50-80% pass rate - Significant issues in specific areas
**Problem:** <50% pass rate - Major model or implementation issues

## Credits

This validation system uses:
- **proppy.net** (G4FUI) for VOACAP online reference
- **VOACAP** ionospheric propagation model
- **DVOACAP-Python** local implementation

## Getting Started Now

Run this single command to start debugging:

```bash
cd /home/user/dvoacap-python
python3 validate_predictions.py --regions UK --bands 20m
```

This will show you immediately whether your predictions match VOACAP online for a UK path on 20m.

If it shows ✗ MISMATCH, run:

```bash
python3 validate_predictions.py --debug UK 20m
```

To see exactly where the calculations differ.

---

**Remember:** Some variation is normal. VOACAP is a complex model with many parameters. The goal is to identify *systematic* differences and ensure the implementation is fundamentally correct, not to match every decimal place.
