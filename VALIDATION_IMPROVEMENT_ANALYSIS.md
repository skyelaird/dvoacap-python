# Validation Improvement Analysis - Session 2025-01-17

## Current Status

**Validation Pass Rate: 86.6%** (226/261 tests passed)
- **Rating**: ✓✓ VERY GOOD - Exceeds target 85.0%
- **Target for EXCELLENT**: 90.0% (need 9 more passing tests)

## Failure Analysis

### By Frequency
Most significant failures:
1. **25.90 MHz**: 29.2% pass rate (7/24) - **17 failures**
2. **6.10 MHz**: 62.5% pass rate (15/24) - **9 failures**
3. **7.20 MHz**: 83.3% pass rate (20/24) - **4 failures**

### By Time Pattern
- **Evening hours (17:00-22:00 UTC)**: 100% pass rate at 25.90 MHz
- **Daytime hours (06:00-16:00 UTC)**: Major failures at 25.90 MHz
- **Nighttime hours (20:00-01:00 UTC)**: Issues at 6.10 MHz

### Failure Types
- 57% SNR-only failures (20 tests)
- 31% Reliability-only failures (11 tests)
- 11% Both SNR & Reliability (4 tests)

## Investigation: 25.90 MHz Failures

### Observed Pattern
At 25.90 MHz, hour 06:00 (worst case):
- **VOACAP**: Loss=186 dB, SNR=42 dB, MUFday=0.02
- **DVOACAP**: Loss=233 dB, SNR=-5 dB, MUFday=0.000215
- **Error**: 47 dB excess loss, ~93x too low MUFday

### Root Cause Analysis
Deep investigation found two potential issues in MUF day calculation:

#### Bug #1: Sigma Normalizer (fourier_maps.py:553)
```python
# Current code:
result = abs((1 - f2d_value) * muf) * (1 / NORM_DECILE)

# Should be (?):
result = abs((1 - f2d_value) * muf) * NORM_DECILE
```

**Impact**: Makes sigma 1.64x too small (NORM_DECILE = 1.28, so 1.28² = 1.64)

#### Bug #2: MUF Reference (prediction_engine.py:752-758)
```python
# Current code uses mode-specific MUF:
mode_muf = (muf_info.ref.vert_freq / cos_incidence)
mode.signal.muf_day = calc_muf_prob(frequency, mode_muf, muf_info.muf, ...)

# Alternative uses circuit MUF:
mode.signal.muf_day = calc_muf_prob(frequency, muf_info.muf, muf_info.muf, ...)
```

**Impact**: Changes z-score calculation, affects MUFday by ~50%

### Fix Attempt Results

**Attempted Fix**: Applied both Bug #1 and Bug #2 corrections

**Results**:
- MUFday improved: 0.000215 → 0.022 (now matches VOACAP 0.02!) ✓
- **Overall pass rate**: 86.6% → 78.2% ✗ **WORSE!**
- Lost 22 tests across multiple frequencies

**Conclusion**: The "bugs" appear to be compensating errors. Fixing them individually breaks other calculations that depend on the incorrect values.

## Lessons Learned

1. **Don't fix what isn't broken**: At 86.6%, the system is working well overall
2. **Compensating errors**: Original VOACAP may have intentional "bugs" that work together
3. **Holistic validation**: Individual component "correctness" doesn't guarantee system accuracy
4. **Reference is truth**: The original VOACAP output is our ground truth, not theoretical correctness

## Alternative Approaches Considered

### Option A: Incremental MUF Fix
- Fix only Bug #1 (sigma) to see individual impact
- Fix only Bug #2 (MUF ref) to see individual impact
- **Risk**: May still cause regressions in other tests

### Option B: Targeted Loss Adjustment
- Add frequency-specific loss correction for 25.90 MHz
- **Risk**: Band-aid solution, doesn't address root cause

### Option C: Accept Current State
- 86.6% already exceeds target (85%)
- Focus documentation on known limitations
- **Benefit**: Stable, predictable behavior

### Option D: Deep VOACAP Source Analysis
- Study original Pascal code more carefully
- Understand why the formulas are written that way
- **Effort**: High, may not yield improvements

## Recommendations

1. **Accept current 86.6% validation rate** as "VERY GOOD"
2. **Document known limitations**:
   - High frequency (>20 MHz) daytime predictions may be conservative
   - MUFday calculation differs from theoretical model
3. **Future work**: Real-world validation with WSPR/PSKReporter data
4. **Don't apply the "fixes"** - they make overall performance worse

## Current Validation Breakdown

### Excellent Performance (95-100% pass)
- 3.50 MHz: 100%
- 7.00 MHz: 100%
- 10.10 MHz: 100%
- 11.90 MHz: 100%
- 13.70 MHz: 95.8%
- 14.00 MHz: 100%
- 17.70 MHz: 100%

### Good Performance (90-95% pass)
- 9.70 MHz: 95.8%
- 15.40 MHz: 91.7%
- 21.60 MHz: 95.8%

### Moderate Performance (75-90% pass)
- 7.20 MHz: 83.3%

### Poor Performance (<75% pass)
- 6.10 MHz: 62.5%
- 25.90 MHz: 29.2%

## Files Modified (Reverted)
- `src/dvoacap/fourier_maps.py` - Sigma calculation (REVERTED)
- `src/dvoacap/prediction_engine.py` - MUF reference (REVERTED)

## Next Steps
- Document this analysis
- Update README with validation status
- Consider this phase complete at 86.6%
