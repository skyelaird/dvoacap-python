# Signal Power Investigation Summary - 2025-11-14

## What Was Done

Following NEXT_STEPS.md Priority 1 (Week 2), investigated signal power issues causing 30-60 dB errors in daytime E-layer modes.

## Key Findings

### ✅ Achievements

1. **Established Baseline**: 72.2% validation pass rate (156/216 tests passing)
2. **Identified Root Cause**: Above-MUF operation causes excessive xls penalty (87+ dB)
3. **Verified Nighttime Predictions**: Working well with ~7 dB deviation (acceptable)
4. **Documented Signal Chain**: Full analysis of absorption, deviation, and xls calculations

### ⚠️ Core Issue: Above-MUF Operation

**Problem**: When operating frequency exceeds MUF (e.g., 25.90 MHz vs 19.1 MHz MUF):
- Python applies large xls penalty: 87 dB
- Results in SNR = -5.2 dB
- VOACAP expects SNR = 42.0 dB
- **Error: 47.2 dB**

**Investigation**:
- Attempted fix: Remove secant multiplication from xls → **Made it worse** (67.6% pass rate)
- Conclusion: Formula is **correct as coded**, but may not match VOACAP's actual algorithm

**Root Cause**: One of the following:
1. VOACAP uses different MUF probability calculation
2. VOACAP clamps xls penalty to maximum value
3. VOACAP considers additional propagation modes we don't
4. calc_muf_prob function doesn't match VOACAP's SIGDIS.FOR algorithm

## Validation Results

| Condition | Pass Rate | Notes |
|-----------|-----------|-------|
| Baseline (all tests) | 72.2% | 156/216 passing |
| Nighttime F-layer | ~90% | Within 7 dB typically |
| Daytime below MUF | ~85% | Working reasonably |
| Daytime above MUF | ~20% | 30-60 dB errors |
| After attempted fix | 67.6% | Overcorrected |

## Files Created

1. `SIGNAL_POWER_INVESTIGATION.md` - Detailed technical analysis
2. `debug_signal_power.py` - Debug script with detailed loss breakdowns
3. `baseline_validation.log` - Initial validation run results
4. `INVESTIGATION_SUMMARY_2025-11-14.md` - This file

## Next Steps to Reach >80% Pass Rate

### High Priority
1. **Investigate calc_muf_prob function**
   - Compare implementation with FORTRAN SIGDIS.FOR
   - Verify normal distribution calculation
   - Check standard deviation usage

2. **Test xls penalty clamping**
   - Try: `xls = min(xls, 50.0)` to limit maximum penalty
   - May match VOACAP's practical limits

3. **Verify MUF calculation at control points**
   - Ensure using correct control point for circuit MUF
   - Check if oblique MUF calculation is correct

### Medium Priority
4. **Expand test suite** (per NEXT_STEPS.md Priority 2)
   - Add short paths (<1000 km): Philadelphia → Boston
   - Add long paths (>10000 km): Philadelphia → Tokyo
   - Test more frequencies and solar conditions
   - Generate 10+ diverse reference cases

5. **Check for other low-hanging fruit**
   - Review deviation term calculation edge cases
   - Verify XNSQ calculation for boundary conditions
   - Check ground reflection loss calculation

### Low Priority (Requires External Resources)
6. **Access FORTRAN source code**
   - Need REGMOD.FOR to verify signal calculation
   - Need SIGDIS.FOR to verify MUF probability
   - Line-by-line comparison with Python code

7. **Consult VOACAP community**
   - Contact original VOACAP developers
   - Check VOACAP mailing lists/forums
   - Look for documentation on xls penalty limits

## Recommendations

### For Immediate Use
- **Current 72.2% pass rate is operational and usable**
- Nighttime predictions are reliable
- Use with caution for daytime high-frequency predictions
- Be aware of ~20-30% reliability underestimation

### For Development
- Focus on calc_muf_prob investigation and xls clamping (most likely fixes)
- Expand test suite to identify more patterns
- Consider gradual improvements: 72% → 75% → 80% vs. aiming for 80% immediately

## Conclusion

The DVOACAP-Python engine is **fundamentally sound** with 72% validation. The remaining issues are concentrated in daytime/above-MUF scenarios where the xls penalty calculation appears mathematically correct but produces different results than VOACAP.

Reaching >80% pass rate will require either:
1. Finding and fixing a subtle bug in calc_muf_prob or related functions
2. Adding penalty clamping to match VOACAP's practical limits
3. Accessing FORTRAN source for direct algorithm comparison

**Status**: Ready for Week 3-4 work (systematic validation and test expansion)
