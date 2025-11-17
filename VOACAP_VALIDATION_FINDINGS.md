# VOACAP Reference Maps Validation - Key Findings

## Executive Summary

Analysis of VOACAP reference maps uploaded for FN74ui station reveals several parameter mismatches between VOACAP.com reference maps and our DVOACAP-Python implementation.

**Date:** 2025-11-17
**Reference Maps:** `examples/FN74ui 2025.11.17-*.pdf` (REL and SDBW maps for WSPR, FT8, CW, SSB)

---

## VOACAP Reference Parameters

### Common Parameters (All Modes)
From the PDF map headers:

- **Location:** FN74ui (44.35N, 64.29W) ✅ **MATCHES**
- **Time:** November, 1800 UTC ✅ **MATCHES**
- **SSN:** 77 ✅ **MATCHES**
- **Frequency:** 14.100 MHz ✅ **MATCHES**
- **Power:** 80 W ✅ **MATCHES**
- **TX Antenna:** HVD025.ANT, -1° takeoff angle
- **RX Antenna:** HVD025.ANT
- **Noise:** -150 dBW
- **Generated:** www.voacap.com, 2025-11-17

### Mode-Specific Bandwidth Parameters

| Mode | Bandwidth (dB/Hz) | Typical Required SNR | VOACAP Maps |
|------|------------------|---------------------|-------------|
| **WSPR** | 3 dB/Hz | ~-28 dB | ✅ Available |
| **CW** | 13 dB/Hz | ~5-8 dB | ✅ Available |
| **FT8** | 19 dB/Hz | ~-21 dB | ✅ Available |
| **SSB** | 38 dB/Hz | ~10-15 dB | ✅ Available |

---

## Critical Differences Found

### 1. Missing Bandwidth Parameter ⚠️

**Issue:** DVOACAP-Python does NOT have a bandwidth parameter

- **VOACAP uses:** Mode-specific bandwidth values (3, 13, 19, 38 dB/Hz)
- **DVOACAP-Python:** No `bandwidth` parameter in `VoacapParams`
- **Impact:** Cannot differentiate between modes with different bandwidths
- **Severity:** 🟡 **MEDIUM** - Affects noise calculations and SNR

**Formula Impact:**
```
Noise Power (dBW) = Noise Density + 10*log10(Bandwidth)
SNR = Signal Power - Noise Power
```

Without bandwidth, the noise floor is calculated incorrectly for different modes.

### 2. Required SNR Default Too High 🔴

**Issue:** Default `required_snr = 73.0 dB` is unrealistically high

- **VOACAP validation tests:** Use 73 dB (reference level)
- **Practical communications:**
  - WSPR: -28 dB
  - FT8: -21 dB
  - CW: 5-8 dB
  - SSB: 10-15 dB

- **DVOACAP default:** 73.0 dB
- **Impact:** Causes 0-1.2% reliability predictions when should be 20-100%
- **Severity:** 🔴 **CRITICAL** (already documented in REQUIRED_SNR_PARAMETER_FIX.md)

**Documented Solution:**
```python
# For practical use
engine.params.required_snr = 10.0  # SSB
engine.params.required_snr = 6.0   # CW
engine.params.required_snr = -21.0 # FT8
engine.params.required_snr = -28.0 # WSPR
```

### 3. Antenna Model Mismatch ⚠️

**Issue:** VOACAP uses HVD025.ANT at -1° takeoff angle

- **VOACAP reference:** HVD025.ANT (half-wave dipole at 25 feet)
- **Takeoff angle:** -1° (slightly downward)
- **DVOACAP-Python:** Uses generic antenna models, no direct HVD025 equivalent
- **Impact:** Antenna gain patterns may differ
- **Severity:** 🟡 **MEDIUM** - Affects signal strength predictions

### 4. Noise Floor Specification ⚠️

**Issue:** Different noise specification methods

- **VOACAP maps show:** -150 dBW absolute noise level
- **DVOACAP-Python uses:** `man_made_noise_at_3mhz = 145.0 dB above kTB`
- **DVOACAP default:** 145.0 dB (relative to thermal noise)
- **Impact:** Need to verify noise calculations match
- **Severity:** 🟡 **MEDIUM** - Affects SNR calculations

**Noise Calculation:**
```
Thermal noise kTB at 1 Hz = -204 dBW/Hz
At 3 MHz bandwidth: kTB = -204 + 10*log10(3e6) = -139.2 dBW
Man-made noise: -139.2 + 145 = 5.8 dBW (seems wrong?)
```

Need to investigate how VOACAP's -150 dBW maps to our noise model.

---

## Parameter Comparison Summary

| Parameter | VOACAP Reference | DVOACAP-Python | Status |
|-----------|------------------|----------------|--------|
| **Location** | 44.35N, 64.29W | 44.35N, 64.29W | ✅ Match |
| **SSN** | 77 | 77 | ✅ Match |
| **Month** | 11 (November) | 11 | ✅ Match |
| **Time** | 1800 UTC | 1800 UTC | ✅ Match |
| **Frequency** | 14.100 MHz | 14.100 MHz | ✅ Match |
| **Power** | 80 W | 80 W | ✅ Match |
| **Bandwidth** | 3/13/19/38 dB/Hz | **NOT AVAILABLE** | ❌ Missing |
| **Required SNR** | Mode-dependent | 73 dB (default) | ❌ Wrong default |
| **TX Antenna** | HVD025.ANT @ -1° | Generic models | ⚠️ Different |
| **RX Antenna** | HVD025.ANT | Generic models | ⚠️ Different |
| **Noise** | -150 dBW | 145 dB @ 3MHz | ⚠️ Different spec |

---

## Recommendations

### Immediate Actions

1. **🔴 IMPLEMENT BANDWIDTH PARAMETER**
   ```python
   @dataclass
   class VoacapParams:
       ...
       bandwidth_hz: float = 2700.0  # Default for SSB (2.7 kHz)
       # Or bandwidth_db_hz for dB/Hz specification
   ```

2. **🔴 ADD MODE PRESETS**
   ```python
   MODE_PRESETS = {
       'WSPR': {'bandwidth_hz': 6, 'required_snr': -28},
       'FT8': {'bandwidth_hz': 50, 'required_snr': -21},
       'CW': {'bandwidth_hz': 500, 'required_snr': 6},
       'SSB': {'bandwidth_hz': 2700, 'required_snr': 10}
   }
   ```

3. **🟡 ADD HVD025 ANTENNA MODEL**
   - Half-wave dipole at 25 feet (7.6m)
   - Implement takeoff angle control
   - Match VOACAP antenna gain patterns

4. **🟡 VERIFY NOISE CALCULATIONS**
   - Compare noise floor output to VOACAP -150 dBW
   - Add bandwidth to noise power calculation
   - Document noise model differences

### Testing Required

1. **Run predictions with mode-specific parameters:**
   ```python
   # WSPR test
   engine.params.required_snr = -28.0
   # bandwidth TBD once parameter added

   # FT8 test
   engine.params.required_snr = -21.0
   # bandwidth TBD

   # CW test
   engine.params.required_snr = 6.0
   # bandwidth TBD

   # SSB test
   engine.params.required_snr = 10.0
   # bandwidth TBD
   ```

2. **Compare outputs to VOACAP reference maps**
   - Generate coverage predictions for each mode
   - Verify SNR values match within ±5 dB
   - Verify reliability values match within ±20%
   - Check MUF predictions

### Documentation Needed

1. **User Guide:** How to set parameters for different modes
2. **Validation Report:** Quantified comparison vs VOACAP maps
3. **Known Limitations:** Document missing features vs VOACAP

---

## Detailed Analysis: Bandwidth Impact

### Current Behavior (No Bandwidth Parameter)

Without bandwidth in noise calculations:
```python
# Current: Noise is frequency-dependent but NOT bandwidth-dependent
noise_dbw = atmospheric_noise + galactic_noise + man_made_noise
snr_db = signal_power_dbw - noise_dbw
```

This gives the same noise floor for WSPR (6 Hz) and SSB (2700 Hz), which is incorrect.

### Correct Behavior (With Bandwidth)

VOACAP uses bandwidth in dB/Hz format:
```
Bandwidth (dB/Hz) = 10 * log10(Bandwidth_Hz)

WSPR: 10*log10(6) = 7.78 dB ≈ 8 dB/Hz (maps show 3 dB/Hz - CHECK!)
FT8: 10*log10(50) = 16.99 dB ≈ 17 dB/Hz (maps show 19 dB/Hz - CHECK!)
CW: 10*log10(500) = 26.99 dB ≈ 27 dB/Hz (maps show 13 dB/Hz - CHECK!)
SSB: 10*log10(2700) = 34.31 dB ≈ 34 dB/Hz (maps show 38 dB/Hz - CHECK!)
```

**Note:** The bandwidth values in VOACAP maps don't match standard signal bandwidths! Need to investigate what these values actually represent.

**Hypothesis:** These may be receiver bandwidth or processing gain values, not signal bandwidths.

### Impact on SNR

For the same signal power and noise density:
```
SNR_WSPR = SNR_base - 3 dB   (3 dB/Hz bandwidth)
SNR_CW   = SNR_base - 13 dB  (13 dB/Hz bandwidth)
SNR_FT8  = SNR_base - 19 dB  (19 dB/Hz bandwidth)
SNR_SSB  = SNR_base - 38 dB  (38 dB/Hz bandwidth)
```

This explains why weak-signal modes (WSPR, FT8) can work with much lower SNR!

---

## Next Steps

### Phase 1: Investigation
- [ ] Understand VOACAP bandwidth specification (dB/Hz vs Hz)
- [ ] Compare noise calculations: our output vs VOACAP -150 dBW
- [ ] Identify where HVD025 antenna pattern is defined
- [ ] Run test predictions with current implementation

### Phase 2: Implementation
- [ ] Add `bandwidth` parameter to `VoacapParams`
- [ ] Integrate bandwidth into noise calculations
- [ ] Add mode preset system
- [ ] Implement HVD025 antenna model (if needed)

### Phase 3: Validation
- [ ] Generate predictions matching VOACAP test cases
- [ ] Compare numerical outputs
- [ ] Generate coverage maps (if visualization added)
- [ ] Document validation results

### Phase 4: Documentation
- [ ] Update user guide with mode settings
- [ ] Add example scripts for each mode
- [ ] Document validation against VOACAP
- [ ] Update README with known differences

---

## Validation Test Cases (from PDFs)

Based on uploaded reference maps, we should test:

1. **FN74ui → Various distances, WSPR mode**
   - Bandwidth: 3 dB/Hz
   - Required SNR: -28 dB
   - Compare REL and SDBW maps

2. **FN74ui → Various distances, FT8 mode**
   - Bandwidth: 19 dB/Hz
   - Required SNR: -21 dB
   - Compare REL and SDBW maps

3. **FN74ui → Various distances, CW mode**
   - Bandwidth: 13 dB/Hz
   - Required SNR: 6 dB
   - Compare REL and SDBW maps

4. **FN74ui → Various distances, SSB mode**
   - Bandwidth: 38 dB/Hz
   - Required SNR: 10 dB
   - Compare REL and SDBW maps

For each test:
- Extract sample points from maps at various distances/azimuths
- Run DVOACAP prediction with matching parameters
- Compare SNR, Reliability, and Signal Strength
- Document discrepancies

---

## Conclusion

**Main Issues Identified:**

1. ❌ **No bandwidth parameter** - Cannot differentiate between modes
2. ❌ **Required SNR default too high** - Already documented, solution exists
3. ⚠️ **Antenna model differences** - May affect results
4. ⚠️ **Noise specification differences** - Need verification

**Priority Fixes:**

1. **HIGH:** Add bandwidth parameter and integrate into noise calculations
2. **MEDIUM:** Add mode preset system for easy configuration
3. **MEDIUM:** Verify noise calculations match VOACAP
4. **LOW:** Add HVD025 antenna model (may not be critical)

**Expected Outcome:**

With bandwidth and required_snr properly set, DVOACAP should produce predictions matching VOACAP reference maps within acceptable tolerances (±5 dB SNR, ±20% reliability).

---

**Report Generated:** 2025-11-17
**Analysis By:** Claude Code
**Reference:** VOACAP maps from examples/FN74ui 2025.11.17-*.pdf
**Status:** READY FOR IMPLEMENTATION
