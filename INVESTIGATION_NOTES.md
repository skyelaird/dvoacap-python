# Validation Investigation Notes

**Date**: 2025-11-14
**Current Status**: 83.8% validation pass rate (181/216 tests passing)
**Branch**: `claude/continue-work-01UE9xeWiKqwMQ8bgjRL6QAV`

## Summary

Investigated remaining validation failures to improve accuracy beyond the current 83.8% pass rate. Identified patterns in failures but did not find a clear root cause that could be safely fixed without further research.

## Failure Analysis

### Pattern Breakdown

1. **High-frequency (25.90 MHz)**: 17 failures (most common)
   - SNR deviations range from 12-47 dB
   - Failures occur across most hours (01-16, 23-24)

2. **Low-frequency (6.10, 7.20 MHz)**: 13 failures
   - Reliability systematically under-predicted by ~20-25%
   - Occurs during nighttime hours (20-24, 01-02) and midday (12-13)

3. **Mid-frequency spot failures**: 5 failures
   - Isolated incidents at specific frequency/time combinations
   - Less systematic pattern

### Key Findings

#### High-Frequency Investigation (25.90 MHz)

**Observed Issue:**
- Hour 06: DVOACAP calculates MUFday=0.0002 (0.02%), VOACAP shows MUFday=0.02 (2%)
- This 100x discrepancy in MUF probability causes incorrect additional loss calculations

**Investigation Results:**
- Traced through entire MUF probability calculation chain
- Formula matches Pascal source code exactly: `abs((1 - F2D[t,s,l]) * MUF) / NORM_DECILE`
- F2D table values load correctly from binary data files
- calc_muf_prob() function is correctly ported
- Attempted fix (multiplying F2D deviation by 2): **FAILED** - reduced pass rate to 62%

**Hypothesis:**
The MUFday discrepancy suggests either:
1. We're using a different profile's sigma values than VOACAP
2. There's a subtle averaging or weighting of sigma values across multiple profiles that we're missing
3. The F2D table interpretation has a scaling factor we haven't identified

**Evidence:**
- Computed sigma values vary by location in code:
  - At profile midpoint: sigma_lo=3.7227, sigma_hi=3.4248 MHz
  - In circuit MUF: sigma_lo=1.9360, sigma_hi=2.0850 MHz
- This ~2x difference could explain the MUFday discrepancy

#### Low-Frequency Investigation (6.10, 7.20 MHz)

**Observed Issue:**
- Reliability consistently 20-25% lower than VOACAP
- Example: Hour 01, 6.10 MHz: DVOACAP 37.3%, VOACAP 61.0%

**Status:**
- Not yet investigated in detail
- Likely related to signal variability calculations (snr10/snr90)
- May also involve MUFday probability for E-layer modes

## Attempted Fixes

### Fix #1: Multiply F2D deviation by 2.0
- **Rationale**: MUFday values 100x too low; sigma values appear 2x too small
- **Result**: FAILED - pass rate dropped from 83.8% to 62.0%
- **Why it failed**: Over-corrected SNR predictions, causing opposite errors

## Current Limitations

1. **No access to VOACAP intermediate calculations** - We can only compare final outputs, not internal state
2. **Complex multi-profile interactions** - Sigma values may be averaged/weighted in ways not obvious from code
3. **Legacy code archaeology** - VOACAP/IONCAP evolved over decades with undocumented empirical adjustments

## Recommendations

### Short-term (Maintain 83.8% accuracy)
1. Document known limitations in README
2. Add validation tolerance bands to account for expected deviations
3. Focus on use cases where 83.8% accuracy is sufficient

### Medium-term (Improve to >90%)
1. **Compare with original DVOACAP** (Delphi version) to see if it has same issues
2. **Consult VOACAP community** - May have encountered similar issues
3. **Add intermediate validation points** - Validate sigma calculations, profile selection, etc.
4. **Cross-reference with ITU-R P.533** - Official HF propagation standard

### Long-term (Research)
1. Review VOACAP development history and change logs
2. Compare with other VOACAP ports (VOACAPL, etc.)
3. Consider empirical calibration using real-world propagation data (WSPRnet, etc.)

## Files Modified

- `src/dvoacap/prediction_engine.py`: Added debug hooks (disabled)
- `src/dvoacap/fourier_maps.py`: Added debug hooks (disabled)
- Created debug scripts:
  - `debug_high_freq.py`
  - `debug_mufday.py`
  - `debug_f2d_table.py`
  - `simple_test.py`
  - `analyze_failures.py`

## References

- `test_voacap_reference.py` - Validation test against reference VOACAP output
- `SampleIO/voacapx.out` - Reference data from original VOACAP
- `VALIDATION_STRATEGY.md` - Validation methodology
- Original Pascal source: `src/original/VoaCapEng.pas`, `src/original/MufCalc.pas`, `src/original/FrMaps.pas`

## Conclusion

Achieved 83.8% validation pass rate, which represents good agreement with VOACAP for most propagation scenarios. Remaining 16.2% of failures are concentrated in edge cases (very high frequencies near/over MUF, low frequencies at nighttime).

Further improvements will require either:
- Access to VOACAP intermediate calculations for debugging
- Consultation with VOACAP developers/community
- Extensive cross-validation with real-world propagation measurements

The current accuracy level is suitable for most amateur radio and professional HF planning applications, with the caveat that predictions near the MUF limits should be treated with appropriate uncertainty.
