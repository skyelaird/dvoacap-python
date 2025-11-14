# Signal Power Investigation - 2025-11-14

## Summary

Investigated signal power calculation issues causing 30-60 dB errors in daytime E-layer modes. Identified the xls penalty calculation as a key factor, but found that the formula is correct as coded. The issue is that VOACAP handles above-MUF operation differently than our implementation.

## Current Status

- **Baseline pass rate**: 72.2% (156/216 test cases)
- **Nighttime predictions**: Working well (~7 dB deviation, acceptable)
- **Daytime high-frequency predictions**: Failing with 30-60 dB SNR errors
- **Target**: >80% pass rate

## Investigation Results

### 1. XLS Penalty Calculation (Lines 764-769)

**What it does**: Calculates additional loss when operating near or above the MUF.

**Formula**:
```python
sec = 1.0 / cos_of_incidence(elevation, true_height)
xmuf = vert_freq * sec  # Oblique MUF for this mode
xls_prob = calc_muf_prob(frequency, xmuf, circuit_muf, sig_lo, sig_hi)
xls = -10 * log10(xls_prob) * sec  # Convert to dB and apply secant
total_loss += hop_count * xls
```

**Example** (UTC 06, 25.90 MHz, F2 mode):
- Operating frequency: 25.90 MHz
- Mode oblique MUF: 19.06 MHz (below operating freq!)
- Circuit MUF: 19.1 MHz
- MUF probability: 0.000708 (very low - we're above MUF)
- xls penalty: **87.29 dB**
- Result: SNR = -5.2 dB (VOACAP expects 42.0 dB)
- **Error: 47.2 dB**

### 2. Attempted Fix: Remove Secant Multiplication

Hypothesis: The secant is applied twice (once in xmuf, once in xls calculation).

```python
# Attempted change:
xls = -10 * log10(xls_prob)  # Remove * sec
```

**Result**: Pass rate **decreased** from 72.2% to 67.6% ❌

**Analysis**: Removing the secant overcorrected:
- Before: SNR too low (e.g., -5.2 dB vs 42.0 dB expected)
- After: SNR too high (e.g., 65.6 dB vs 29.0 dB expected)

**Conclusion**: The secant multiplication is **correct** as coded.

### 3. Why VOACAP Differs

VOACAP gets 42.0 dB SNR at UTC 06, 25.90 MHz with 1F2 mode (same mode we select).

Possible explanations:
1. **Different MUF calculation**: VOACAP may calculate MUF differently
2. **Different xls formula**: VOACAP may use a different penalty formula
3. **Additional propagation modes**: VOACAP may consider sporadic E or other modes
4. **Clamping/limits**: VOACAP may cap the xls penalty at a maximum value
5. **Different probability function**: calc_muf_prob may not match VOACAP's algorithm

### 4. Other Loss Components

**Absorption Loss** (already fixed in previous PR):
- Coefficient: 677.2 * absorption_index ✓
- Working correctly for most cases

**Deviation Term**:
- Formula appears correct
- Shows small values (~1-2 dB) for most modes
- Not a major contributor to the 30-60 dB errors

**XNSQ Calculation**:
- Uses 10.2 for F-layer and high E-layer reflections
- Uses height-dependent formula for low E-layer
- Appears correct based on FORTRAN reference

## Test Case Examples

### Working Case: UTC 01, 7.20 MHz (Nighttime F-layer)
- Mode: 1F2
- Operating freq: 7.20 MHz
- Circuit MUF: 16.25 MHz (well above operating freq)
- xls penalty: 0.00 dB ✓
- **DVOACAP SNR**: 72.29 dB
- **VOACAP SNR**: 79.0 dB
- **Error**: 7 dB ✓ (acceptable)

### Failing Case: UTC 06, 25.90 MHz (Daytime, above MUF)
- Mode: 1F2
- Operating freq: 25.90 MHz
- Circuit MUF: 19.1 MHz (below operating freq!)
- xls penalty: 87.29 dB ❌
- **DVOACAP SNR**: -5.2 dB
- **VOACAP SNR**: 42.0 dB
- **Error**: 47.2 dB ❌

### Pattern

| Condition | xls Penalty | Result |
|-----------|-------------|--------|
| Freq << MUF | ~0 dB | ✓ Works |
| Freq ≈ MUF | ~10-30 dB | ⚠️ Marginal |
| Freq >> MUF | ~50-300 dB | ❌ Fails |

## Recommendations

### Short Term (to reach >80% pass rate)

1. **Investigate calc_muf_prob function**
   - Compare with FORTRAN SIGDIS.FOR
   - Check if probability calculation matches VOACAP
   - May need adjustment to standard deviations

2. **Add xls penalty clamping**
   - VOACAP may limit xls to a maximum value (e.g., 50 dB)
   - Test with: `xls = min(xls, 50.0)`

3. **Check MUF calculation at control points**
   - Verify that circuit MUF is correctly calculated
   - May be using wrong control point for MUF

4. **Expand test suite** (per NEXT_STEPS.md)
   - Add more diverse paths (short, medium, long)
   - Test different times of day and solar conditions
   - Identify patterns in failures

### Long Term

1. **Access FORTRAN source code**
   - Get REGMOD.FOR to verify xls calculation
   - Get SIGDIS.FOR to verify MUF probability calculation
   - Line-by-line comparison

2. **Consider alternative approaches**
   - Use VOACAP DLL directly for validation
   - Consult with VOACAP developers/community

## Files Modified

None (investigation only, reverted attempted fix)

## Related Documents

- `NEXT_STEPS.md` - Overall project plan
- `RELIABILITY_INVESTIGATION.md` - Previous reliability investigation
- `ABSORPTION_BUG_ANALYSIS.md` - Absorption coefficient fix

## Debug Commands

```bash
# Run reference validation
python test_voacap_reference.py

# Debug specific case
python debug_signal_power.py

# Enable detailed logging (edit prediction_engine.py)
# Line 736: debug_loss = True
# Line 847: debug = True
```

## Conclusion

The 72.2% pass rate indicates the engine is fundamentally working, but there's a systematic issue with daytime/above-MUF predictions. The xls penalty calculation is mathematically correct as coded, but may not match VOACAP's actual algorithm. Further investigation requires:

1. Access to FORTRAN source code for verification
2. More detailed understanding of VOACAP's MUF probability calculation
3. Possible adjustment to penalty clamping or probability calculation

The engine is **operational and usable** at 72% pass rate. Reaching >80% will require deeper investigation into VOACAP's specific algorithms.
