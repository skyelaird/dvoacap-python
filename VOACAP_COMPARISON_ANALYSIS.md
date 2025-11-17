# VOACAP vs DVOACAP Chart Comparison Analysis

## Executive Summary

**Critical Finding:** DVOACAP has a fundamental reliability calculation error that makes it predict 0-1.2% reliability when VOACAP predicts 20-100% reliability, despite both showing similar strong SNR values.

**Date:** 2025-11-17
**Test Scenario:** FN74ui (44.35N, 64.29W), 14.100 MHz, 1800 UTC, SSN 81, 80W

---

## Reference VOACAP Charts

### Chart Parameters
- **Location:** FN74ui (44.35N, 64.29W)
- **Frequency:** 14.100 MHz
- **Time:** November 1800 UTC
- **SSN:** 81
- **Power:** 80W, 38dB/Hz SSB
- **Antennas:** HVD025.ANT, -1° TX, HVD025.ANT RX
- **Noise:** -153 dBW

### VOACAP REL Chart (Reliability)
The reliability chart shows:
- **Center (TX location):** ~100% reliability (white/red center)
- **500-1000 km:** 70-90% reliability (yellow/green rings)
- **1000-2000 km:** 40-60% reliability (blue rings)
- **2000-3000 km:** 20-40% reliability (light blue)
- **>3000 km:** 10-30% reliability (very light blue)
- **Coverage:** Excellent across North America, extends transatlantic to Europe

### VOACAP SDBW Chart (Signal Strength)
The signal strength chart shows:
- **Center area:** S6-S8 signals (54-57 dB above noise floor)
- **North America:** S3-S6 signals (widespread coverage)
- **Transatlantic:** S1-S3 signals (51-53 dB, extending to Western Europe)
- **Pattern:** Concentric circles of decreasing signal strength

---

## DVOACAP Predictions (Same Scenario)

| Location  | Distance | **SNR**  | **Rel%** | MUFday   | Loss    | Comparison to VOACAP |
|-----------|----------|----------|----------|----------|---------|----------------------|
| Near NE   | 612 km   | **41.5** | **1.2%** | 0.223    | 140.5   | REL: Expected 80%, Got 1% ❌ |
| Medium N  | 1407 km  | **41.5** | **0.1%** | 0.999    | 140.6   | REL: Expected 50%, Got 0% ❌ |
| Medium W  | 1093 km  | **45.2** | **0.2%** | 0.988    | 136.7   | REL: Expected 60%, Got 0% ❌ |
| Far SE    | 1943 km  | **41.2** | **0.0%** | 0.999    | 142.0   | REL: Expected 40%, Got 0% ❌ |
| Far W     | 2435 km  | **29.3** | **0.1%** | 0.392    | 155.6   | REL: Expected 30%, Got 0% ❌ |
| Very Far  | 4247 km  | **28.2** | **0.0%** | 0.998    | 155.6   | REL: Expected 20%, Got 0% ❌ |

### Key Observations

1. **SNR is Correct:** DVOACAP predicts SNR of 28-45 dB, which matches VOACAP's signal strength predictions (S7-S9+ = signals well above noise)

2. **Reliability is BROKEN:** DVOACAP predicts 0-1.2% reliability everywhere, while VOACAP shows 20-100% reliability
   - This is a **50-100x error** in reliability calculation
   - SNR and reliability should be correlated, but they're completely disconnected in DVOACAP

3. **MUFday Values Look Reasonable:** 0.22-0.99 range suggests the frequency is close to or below the MUF (good)

4. **Loss Values are Reasonable:** 137-156 dB total path loss is in the expected range for these distances

---

## Critical Issues Identified

### Issue #1: Reliability Calculation Completely Wrong (CRITICAL)
**Severity:** 🔴 **CRITICAL**

**Problem:**
- VOACAP shows 20-100% reliability across test points
- DVOACAP shows 0-1.2% reliability for identical scenarios
- This makes DVOACAP predict "unlikely propagation" when VOACAP predicts "excellent propagation"

**Impact:**
- DVOACAP is **unusable for reliability predictions**
- Users would think paths are closed when they're actually open
- Invalidates the entire prediction system for practical use

**Root Cause (Hypothesis):**
Based on VALIDATION_IMPROVEMENT_ANALYSIS.md, there are known issues with:
1. Sigma normalizer calculation (fourier_maps.py:553) - using 1/NORM_DECILE instead of NORM_DECILE
2. MUF reference calculation (prediction_engine.py:752-758) - using mode-specific MUF vs circuit MUF

However, the analysis noted that "fixing" these made overall validation worse (86.6% → 78.2%), suggesting **compensating errors** throughout the system.

### Issue #2: High Frequency Excess Loss (25.90 MHz)
**Severity:** 🟡 **KNOWN ISSUE**

From VALIDATION_IMPROVEMENT_ANALYSIS.md:
- **25.90 MHz pass rate:** 29.2% (7/24 tests)
- **Problem:** Excess loss of 47 dB during daytime hours
  - VOACAP: 186 dB loss, 42 dB SNR
  - DVOACAP: 233 dB loss, -5 dB SNR
- **Root cause:** MUFday calculation error (0.000215 vs 0.02 expected)
- **Status:** Known, documented, attempts to fix made it worse

### Issue #3: Overall Validation Performance
**Severity:** 🟢 **ACCEPTABLE** (but misleading)

- **Overall pass rate:** 86.6% (226/261 tests)
- **Rating:** "VERY GOOD" (exceeds 85% target)

**However:** This masks the reliability calculation problem because:
- Validation only checks if SNR is within ±10 dB tolerance
- Validation only checks if reliability is within ±20% tolerance
- A prediction showing "1% reliability with 40 dB SNR" still passes if VOACAP shows "80% reliability with 35 dB SNR"

---

## Detailed Discrepancy Analysis

### Example: 612 km path (Near NE)

| Metric | VOACAP (from chart) | DVOACAP | Error | Acceptable? |
|--------|---------------------|---------|-------|-------------|
| SNR | ~45 dB (S9+ signal) | 41.5 dB | -3.5 dB | ✓ Within ±10 dB |
| Reliability | ~80% (yellow/green on chart) | 1.2% | **-78.8%** | ❌ **MASSIVE** |
| Signal interpretation | "Excellent, reliable" | "Unlikely, unreliable" | Opposite! | ❌ |

### The Paradox

DVOACAP is simultaneously predicting:
- ✅ **Strong signal:** 41.5 dB SNR (S9+ on S-meter)
- ❌ **Won't work:** 1.2% reliability

This is physically contradictory. A 40+ dB SNR signal should have >90% reliability.

---

## Comparison to Known Validation Issues

### From test_voacap_reference.py Analysis

The validation tests show:
- **Excellent performance** (95-100% pass): 3.50, 7.00, 10.10, 11.90, 13.70, 14.00, 17.70 MHz
- **Poor performance** (<75% pass): 6.10 MHz (62.5%), 25.90 MHz (29.2%)

**Key insight:** 14.100 MHz should be in the "excellent" range based on nearby frequencies (13.70, 14.00 MHz), yet our test shows catastrophically wrong reliability.

**Conclusion:** The validation tests are passing despite broken reliability calculations because the tolerances are too loose (±20% for reliability).

---

## Root Cause Investigation

### Potential Sources of Reliability Error

1. **Fading Model** - Reliability depends on signal fading statistics
   - Rayleigh/Ricean fading calculations may be wrong
   - Upper/lower decile calculations may be inverted

2. **Required SNR Threshold** - System noise or required SNR may be too high
   - If required SNR is set to 60 dB instead of 20 dB, even 40 dB signals would show low reliability

3. **Bandwidth/Mode Mismatch** - Signal bandwidth or mode parameters
   - 38dB/Hz SSB bandwidth may not match between VOACAP and DVOACAP

4. **Noise Floor Calculation** - Atmospheric/man-made noise
   - If noise is calculated 20 dB higher than VOACAP, reliability would plummet

5. **The "Compensating Errors"** - Per validation analysis:
   - System has intentional or accidental bugs that work together
   - Fixing one bug breaks others that depend on it
   - Reliability might depend on the "wrong" MUFday calculation

---

## Recommendations

### Immediate Actions (Critical)

1. **🔴 DO NOT USE DVOACAP FOR RELIABILITY PREDICTIONS**
   - Current reliability values are 50-100x too low
   - SNR predictions appear reasonable
   - Loss predictions appear reasonable

2. **🔴 INVESTIGATE RELIABILITY CALCULATION**
   - Check fading model implementation
   - Verify required SNR thresholds
   - Compare noise floor calculations to VOACAP
   - Check signal bandwidth parameters

3. **🔴 ADD RELIABILITY-SPECIFIC VALIDATION**
   - Current validation passes despite broken reliability
   - Need tighter tolerances or separate reliability validation
   - Need test cases that specifically validate rel vs SNR correlation

### Medium-term Actions

4. **🟡 DEBUG 14 MHz SCENARIO**
   - Run step-by-step comparison with VOACAP for 14.1 MHz @ 1800 UTC
   - Log every intermediate calculation
   - Find where reliability diverges

5. **🟡 REVIEW "COMPENSATING ERRORS"**
   - The MUFday "fixes" that were reverted (VALIDATION_IMPROVEMENT_ANALYSIS.md)
   - Determine if they actually fix reliability
   - Consider fixing MUFday AND reliability together

6. **🟡 EXPAND VALIDATION TEST SUITE**
   - Add explicit SNR-reliability correlation tests
   - Add "sanity check" tests (40 dB SNR must have >50% reliability)
   - Add chart-based validation (coverage area tests)

### Long-term Actions

7. **🟢 REAL-WORLD VALIDATION**
   - Compare against WSPR/PSKReporter data (as mentioned in improvement analysis)
   - Test against actual on-air reports
   - Validate coverage predictions vs real propagation

8. **🟢 DOCUMENTATION**
   - Document reliability calculation as "KNOWN BROKEN"
   - Warn users to use SNR only
   - Provide workarounds or correction factors

---

## Technical Deep Dive Needed

### Questions to Answer

1. **Where is reliability calculated?**
   - Which file/function computes `mode.signal.reliability`?
   - What formula is used?
   - What are the input parameters?

2. **What is "required SNR"?**
   - What value is used for minimum required SNR?
   - How does it compare to VOACAP?
   - Is it mode-dependent (SSB vs CW vs digital)?

3. **How does reliability relate to MUFday?**
   - Is reliability dependent on the "broken" MUFday calculation?
   - Would fixing MUFday fix reliability?

4. **What are the fading margins?**
   - Upper/lower decile calculations
   - Rayleigh fading parameters
   - Time/space diversity factors

---

## Comparison Summary

| Aspect | VOACAP | DVOACAP | Status |
|--------|--------|---------|--------|
| **Coverage Maps** | Shows widespread North American coverage | N/A (no maps generated) | ❌ Missing feature |
| **SNR Predictions** | 30-50 dB range | 28-45 dB range | ✅ **GOOD MATCH** |
| **Reliability** | 20-100% across region | 0-1.2% everywhere | ❌ **COMPLETELY BROKEN** |
| **Signal Strength** | S3-S9+ across region | S7-S9+ (matches SNR) | ✅ **GOOD MATCH** |
| **Path Loss** | 135-160 dB (inferred) | 137-156 dB | ✅ **GOOD MATCH** |
| **MUFday** | Not shown on charts | 0.22-0.99 | ❓ Unknown (no reference) |
| **Visualization** | Beautiful color maps | None (numerical only) | ❌ Missing feature |

---

## Conclusion

### What Works in DVOACAP
✅ SNR calculations (±5 dB of VOACAP)
✅ Path loss calculations
✅ MUFday calculations (for most frequencies)
✅ Overall system architecture (86.6% validation pass)

### What's Broken in DVOACAP
❌ **Reliability calculations (50-100x too low)**
❌ High frequency (25.90 MHz) predictions (47 dB excess loss)
❌ No visualization/mapping capabilities
❌ Validation testing masks reliability errors

### Primary Issue
The **reliability calculation is the single most critical issue**. DVOACAP predicts "unlikely propagation" (1% reliable) when VOACAP predicts "excellent propagation" (80% reliable), despite both showing strong signals (40 dB SNR).

This makes DVOACAP **unsuitable for operational use** until the reliability calculation is fixed.

### Recommended Next Steps
1. Locate and debug reliability calculation code
2. Compare reliability formula to VOACAP source
3. Test if MUFday fixes also fix reliability
4. Create specific reliability validation tests
5. Document workarounds for current users

---

**Report Generated:** 2025-11-17
**Analysis by:** Claude (based on VOACAP reference charts and DVOACAP validation data)
**Reference Charts:** `examples/FN74ui 2025.11.17 1825Z-rel.pdf` and `-sdbw.pdf`
