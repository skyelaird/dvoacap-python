# Quick Start: Debug Propagation Discrepancies

Your propagation results don't match VOACAP online. Here's how to find out why.

## Step 1: Run Quick Validation (2 minutes)

Test a few key paths to see where discrepancies occur:

```bash
cd /home/user/dvoacap-python
python3 validate_predictions.py --regions UK JA --bands 20m 15m
```

**What this does:**
- Compares your local predictions vs VOACAP online (proppy.net)
- Tests UK and Japan paths on 20m and 15m bands
- Shows which predictions match (✓) and which don't (✗)
- Takes ~30 seconds with API delays

**Expected output:**
```
Region: United Kingdom (UK)
  20m (14.150 MHz): ✓ MATCH
      Local:  Rel= 75.0% SNR= 15.2dB Mode=2F2
      VOACAP: Rel= 78.0% SNR= 16.1dB

  15m (21.200 MHz): ✗ MISMATCH
      Local:  Rel= 45.0% SNR=  8.3dB MUF= 24.5MHz
      VOACAP: Rel= 62.0% SNR= 12.1dB MUF= 26.2MHz
      → Reliability: local=45.0% vs VOACAP=62.0% (diff=17.0%)
```

## Step 2: Deep Dive on Specific Mismatch

Found a mismatch? Get detailed debug info:

```bash
python3 validate_predictions.py --debug UK 15m
```

**What this shows:**
- Complete calculation breakdown
- Path geometry (distance, azimuth)
- Ionospheric parameters (MUF, virtual height)
- Mode selection (hops, layers, elevation angles)
- Signal components (power, loss, noise, SNR)
- Side-by-side comparison with VOACAP online
- Raw VOACAP response for manual inspection

**Look for these red flags:**

1. **Different modes selected**
   ```
   Local:  Mode=2F2  (2 hops, F2 layer)
   VOACAP: Mode=3F2  (3 hops, F2 layer)
   ```
   → Path geometry or elevation angle calculation issue

2. **Similar signal but different SNR**
   ```
   Local:  Signal=-95dBW  Noise=-102dBW  SNR=7dB
   VOACAP: Signal=-94dBW  Noise=-108dBW  SNR=14dB
   ```
   → Noise model discrepancy

3. **Very different MUF**
   ```
   Local:  MUF=24.5MHz
   VOACAP: MUF=28.2MHz
   ```
   → Ionospheric model or F2 critical frequency issue

4. **Large signal difference**
   ```
   Local:  Signal=-95dBW  Total loss=145dB
   VOACAP: Signal=-82dBW  Total loss=132dB
   ```
   → Absorption or loss calculation error

## Step 3: Test Across Multiple Times

Propagation varies by time of day. Test if discrepancies are consistent:

```bash
python3 validate_predictions.py --regions UK --bands 20m --hours 0 6 12 18
```

**What to look for:**
- Do mismatches occur at specific times? (dawn/dusk, noon, midnight)
- Are some hours consistently good and others consistently bad?
- Does the pattern make sense for ionospheric behavior?

## Step 4: Check Your Data Files

Verify coefficient files are intact:

```bash
cd /home/user/dvoacap-python
pytest tests/test_voacap_parser.py -v
```

**Should show:**
```
test_voacap_parser.py::test_all_months_load PASSED
test_voacap_parser.py::test_coefficient_shapes PASSED
test_voacap_parser.py::test_coefficient_ranges PASSED
```

If any fail, your coefficient files may be corrupted.

## Step 5: Compare Current Predictions

Check what your dashboard is currently showing:

```bash
python3 Dashboard/generate_predictions.py
cat Dashboard/propagation_data.json | python3 -m json.tool | head -100
```

Then compare with validation results:

```bash
cat validation_results.json | python3 -m json.tool | head -100
```

## Common Issues & Solutions

### Issue: Everything is way off (>90% failures)

**Likely cause:** Configuration mismatch

**Check:**
```python
python3 -c "
from src.dvoacap.prediction_engine import PredictionEngine
engine = PredictionEngine()
print(f'Month: {engine.params.month}')
print(f'SSN: {engine.params.ssn}')
print(f'TX Power: {engine.params.tx_power}W')
"
```

Make sure these match what VOACAP online is using.

### Issue: Only high bands fail (15m, 10m)

**Likely cause:** MUF/F2 layer calculation

**Debug:**
```bash
python3 validate_predictions.py --debug UK 10m
```

Look at the MUF values and F2 critical frequency.

### Issue: Only long paths fail (JA, VK)

**Likely cause:** Long path model or multi-hop geometry

**Debug:**
```bash
python3 validate_predictions.py --debug VK 20m
```

Check if it's using "short" or "long" method, and compare hop counts.

### Issue: SNR always lower than VOACAP

**Likely cause:** Noise model

**Debug:**
Look at the `noise_dbw` values in detailed output:
```bash
python3 validate_predictions.py --debug UK 20m | grep -i noise
```

### Issue: Proppy.net API errors

**Symptoms:**
```
Proppy.net API timeout - service may be busy
```

**Solutions:**
1. Check internet: `ping www.proppy.net`
2. Wait 1 minute and retry
3. Test fewer combinations: `--regions UK --bands 20m`

## Understanding Tolerance

The validation uses these tolerance thresholds:

| Metric | Tolerance | Why |
|--------|-----------|-----|
| Reliability | ±15% | VOACAP variability, coefficient rounding |
| SNR | ±5 dB | Noise model variations, decile calculations |
| MUF | ±2 MHz | Smoothing, interpolation differences |

**80%+ pass rate = Good** - Minor calculation differences are normal
**50-80% pass rate = Investigate** - Systematic issue in specific area
**<50% pass rate = Problem** - Major model or data issue

## Getting Help

When reporting issues, include:

1. **Validation summary:**
   ```bash
   python3 validate_predictions.py --quiet 2>&1 | tail -20
   ```

2. **Detailed debug of worst case:**
   ```bash
   python3 validate_predictions.py --debug <REGION> <BAND>
   ```

3. **Validation results file:**
   ```bash
   cat validation_results.json
   ```

4. **Your configuration:**
   - Month, SSN, TX power
   - Which paths/bands show largest errors
   - Any patterns you've noticed

## Next Steps

After validation, you can:

1. **Adjust tolerance** - Edit `tolerance` dict in `validate_predictions.py` if you have different accuracy requirements

2. **Add test cases** - Edit `TEST_CASES` to add more regions/paths

3. **Automate** - Add validation to CI/CD:
   ```bash
   python3 validate_predictions.py --regions UK --bands 20m --quiet
   ```
   (exits with code 1 if any failures)

4. **Compare with reference data** - Use `SampleIO/output.json` for offline testing

## Files Created

- `validate_predictions.py` - Main validation script
- `VALIDATION.md` - Detailed validation guide
- `validation_results.json` - Results from last run (auto-generated)
- `DEBUG_QUICKSTART.md` - This file

## Quick Commands Reference

```bash
# Quick test
python3 validate_predictions.py --regions UK --bands 20m

# Full validation (all regions/bands)
python3 validate_predictions.py

# Debug specific case
python3 validate_predictions.py --debug UK 15m

# Test multiple times
python3 validate_predictions.py --regions UK --bands 20m --hours 0 6 12 18

# Quiet mode (failures only)
python3 validate_predictions.py --quiet

# Check data files
pytest tests/test_voacap_parser.py

# Regenerate predictions
python3 Dashboard/generate_predictions.py
```
