# D-Layer Absorption Bug Analysis

## Summary

Critical bug identified and partially fixed in D-layer absorption calculation. The absorption coefficient was incorrectly set to 67.72 instead of the correct VOACAP value of 677.2.

## Bug Details

### Location
`src/dvoacap/prediction_engine.py` line 652

### Original (Incorrect) Code
```python
# BUG FIX: Coefficient was 10x too high...
ac = 67.72 * self._absorption_index  # WRONG!
```

### Corrected Code
```python
# Coefficient from VOACAP REGMOD.FOR line 57: AC = 677.2 * ACAV
ac = 677.2 * self._absorption_index  # CORRECT
```

### Root Cause
The original code comment claimed the coefficient was "10x too high" and reduced it from 677.2 to 67.72. This was incorrect - the original VOACAP FORTRAN source (REGMOD.FOR line 57) clearly shows `AC = 677.2 * ACAV`.

## Impact

### Before Fix (UTC 11 Daytime):
- 7.20 MHz: SNR error +144.5 dB ❌ (unusable prediction)
- 9.70 MHz: SNR error +97.0 dB ❌ (unusable prediction)
- Absorption: ~6 dB/hop (should be ~100-150 dB/hop)

### After Fix (UTC 11 Daytime):
- 7.20 MHz: SNR error +38.0 dB ⚠️ (much improved but still high)
- 9.70 MHz: SNR error +59.4 dB ⚠️ (much improved but still high)
- Absorption: ~59 dB/hop (closer to expected ~100 dB/hop)

### Nighttime (UTC 01):
- 7.20-15.40 MHz: 2-7 dB errors ✓ (acceptable)
- Some degradation in lowest/highest frequencies

## Remaining Issues

Even after fixing the coefficient, daytime E-layer predictions still show 30-60 dB excess SNR. Possible causes:

1. **Deviation Term**: Currently showing -6.3 dB (negative), which reduces total loss. May need investigation.

2. **XNSQ Calculation**: For D-E modes, XNSQ is calculated based on reflection height. May need to use D-layer height (70 km) instead of reflection height (88 km).

3. **Mode Selection**: 9.70 MHz selects 2F2 mode instead of correct 2E mode at UTC 11.

4. **Low Frequency Anomaly**: 6.10 MHz shows 130 dB error at daytime (got worse after fix).

## FORTRAN Reference

From VOACAPW/REGMOD.FOR:
```fortran
C  D-E MODE
  106 CONTINUE
      IF(HTLOSS - HTMOD(IM,K) )  110,110,115
C.....XNSQ IS THE COLLISION FREQUENCY TERM
  110 XNSQ = 10.2
      GO TO 120
  115 HNUX= 61. + 3.*(HTMOD(IM,K) - 70.)/18.
      XNSQ=  XNUZ * EXP(- 2.*(HNUX-60.)/HNU)
  120 CONTINUE
      HEFF = AMIN1( 100.,HTMOD(IM,K))
      SINP = RZ*CDEL/(RZ+ HEFF)
      SECP = 1./SQRT(1. -SINP*SINP)
      ABPS(IM) = SECP* AC/(BC + XNSQ)
      XV = AMAX1( FVMOD(IM,K)/FI(1,K) , XVE)
      ADX =  AFE + BFE * ALOG(XV)
      ...
      ADV(IM) = SECP*AFMOD(IM,K)*((FVMOD(IM,K)+GYZ(L))**1.98 + XNSQ)
     A          / (BCX + XNSQ ) + ADX
```

## Test Results

### test_mode_selection.py Results:

**UTC 1.0 (Night):**
- 7.20 MHz 1F2: -3.7 dB SNR error, -15.0% rel error ✓
- 9.70 MHz 1F2: -2.4 dB SNR error, -8.2% rel error ✓

**UTC 11.0 (Daytime):**
- 7.20 MHz 2E: +38.0 dB SNR error, 0% rel error ⚠️
- 9.70 MHz 2F2: +59.4 dB SNR error, 0% rel error ⚠️ (wrong mode)

### test_voacap_reference.py Results:
- Total: 18 comparisons
- Passed: 6 (33%)
- Failed: 12 (67%)

## Next Steps

1. ✅ Fix absorption coefficient (677.2) - DONE
2. ⚠️ Investigate remaining 30-60 dB error in daytime E-layer modes
3. ⚠️ Fix mode selection (9.70 MHz should be 2E, not 2F2)
4. ⚠️ Investigate deviation term negative values
5. ⚠️ Investigate low-frequency (6.10 MHz) anomaly

## Files Modified

- `src/dvoacap/prediction_engine.py` (line 649-652)
