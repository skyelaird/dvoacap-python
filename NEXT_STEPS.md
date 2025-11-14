# DVOACAP-Python: Next Steps Plan

**Date:** 2025-11-14
**Project Status:** 80-85% Complete (Phase 5 integration in progress)
**Current Branch:** claude/plan-next-steps-01XqbqeLrfZUcUpX6gZkhQAU

---

## Executive Summary

DVOACAP-Python has solid foundations with Phases 1-4 complete and validated. Phase 5 (Signal Predictions) has integration issues that need debugging. The path forward focuses on fixing reliability calculations, systematic validation, and leveraging the original VOACAP manual for dashboard insights.

---

## Current State

### Completed ✅
- **Phase 1:** Path Geometry (validated: <0.01% error)
- **Phase 2:** Solar & Geomagnetic (validated: <0.1° error)
- **Phase 3:** Ionospheric Profiles (CCIR/URSI maps, layer parameters)
- **Phase 4:** Raytracing (MUF, FOT, reflectrix, skip distance)
- **Dashboard:** Real-time predictions with Flask server
- **Recent Fixes:**
  - MODE field alignment bug (PR #37)
  - D-layer absorption coefficient (677.2 correction)
  - Negative ADX term bug in E-layer deviation

### In Progress ⚠️
- **Phase 5:** Signal Predictions showing 0% reliability
  - Reliability calculation issues (`_calc_reliability()`)
  - Signal distribution combinations may have inverted deciles
  - Mode selection logic needs verification

### Key Resources Added
- `docs/Original_VOACAP_Manual.pdf` - Reference for algorithms and dashboard design ideas
- `FORTRAN_ANALYSIS_AND_RECOMMENDATIONS.md` - Detailed debugging roadmap
- `ABSORPTION_BUG_ANALYSIS.md` - Recent bug fixes and remaining issues
- `VALIDATION_STRATEGY.md` - Testing approach and tolerances

---

## Priority 1: Fix Phase 5 Integration (Weeks 1-2)

### Critical Bug: Reliability Calculation

**Problem:** Predictions showing 0% reliability (not matching FORTRAN RELBIL.FOR)

**Location:** `src/dvoacap/prediction_engine.py:810+`

**Suspected Issues:**
1. Signal/noise distribution deciles may be inverted
   ```python
   # Python code (line 810+):
   signal.snr10 = np.sqrt(noise.upper**2 + signal.power10**2)
   signal.snr90 = np.sqrt(noise.lower**2 + signal.power90**2)

   # FORTRAN RELBIL.FOR line 93:
   # D10R = SQRT(DU2 + DSLF*DSLF)  ! High noise + low signal
   # D90R = SQRT(DL2 + DSUF*DSUF)  ! Low noise + high signal
   #
   # VERIFY: Are upper/lower swapped?
   ```

2. Signal calculation chain may have unit conversion errors
3. Z-score calculation for normal distribution

**Action Items:**
- [ ] Add detailed logging to `_calc_reliability()` showing intermediate values
- [ ] Compare Python intermediate values against FORTRAN reference output
- [ ] Verify signal/noise distribution combination matches RELBIL.FOR:93-100
- [ ] Check for dB vs linear, radians vs degrees, MHz vs Hz conversions
- [ ] Test with simple known case and verify reliability > 0%

**Reference Files:**
- FORTRAN: `RELBIL.FOR` (reliability calculations)
- FORTRAN: `REGMOD.FOR` (signal calculations)
- Python: `src/dvoacap/prediction_engine.py:633-850`

**Success Criteria:**
- Predictions show >0% reliability for valid paths
- At least one test case validates within tolerance
- No crashes or exceptions

### Signal Calculation Validation

**Location:** `src/dvoacap/prediction_engine.py:633+`

**Components to Verify:**
1. **Absorption loss** (line 656+)
   ```python
   mode.absorption_loss = ac / (bc + nsqr) / cos_incidence
   # Verify ac=677.2, bc, nsqr coefficients vs REGMOD.FOR
   ```

2. **Deviation term** (line 687+)
   - Complex calculation with high risk of transcription errors
   - Print intermediate values, compare to FORTRAN

3. **Ground reflection loss** (line 1084+)
   - Fresnel coefficients
   - Dielectric constants, conductivity
   - Validate against known test cases

**Action Items:**
- [ ] Add logging for all loss components
- [ ] Compare absorption_loss calculation vs FORTRAN REGMOD.FOR
- [ ] Verify deviation_term formula matches FORTRAN
- [ ] Check ground_reflection_loss against reference
- [ ] Validate cos_incidence angle calculations

**Success Criteria:**
- Loss calculations match FORTRAN within reasonable tolerance
- Signal strength predictions in valid range (-50 to +50 dB)

### Mode Selection Logic

**Location:** `src/dvoacap/reflectrix.py`, `prediction_engine.py:578+`

**Issues:**
- Over-the-MUF mode handling
- Hop count selection
- Elevation angle calculations

**Action Items:**
- [ ] Compare Reflectrix output against FORTRAN ALLMODES.FOR
- [ ] Verify hop count logic in `_evaluate_short_model()`
- [ ] Check elevation angle calculations
- [ ] Ensure over-the-MUF modes properly excluded

**Reference Files:**
- FORTRAN: `ALLMODES.FOR` (mode finding)
- Python: `src/dvoacap/reflectrix.py:550+`

---

## Priority 2: Systematic Validation (Weeks 3-4)

### Expand Reference Test Suite

**Current State:**
- Single test path (Tangier → Belgrade) in `SampleIO/voacapx.out`
- Limited frequency and time coverage

**Action Items:**
- [ ] Generate 10+ diverse reference test cases from original VOACAP
  - Short paths (<1000 km): Philadelphia → Boston
  - Medium paths (2000-5000 km): Philadelphia → London
  - Long paths (>10000 km): Philadelphia → Tokyo
  - Frequencies: 3.5, 7, 14, 21, 28 MHz
  - Times: 00, 06, 12, 18 UTC
  - Solar conditions: SSN=10, 50, 100, 150, 200

- [ ] Save reference outputs to `SampleIO/reference_*.out`

- [ ] Expand `test_voacap_reference.py`:
  ```python
  @pytest.mark.parametrize("path,freq,hour,ssn", test_cases)
  def test_prediction_accuracy(path, freq, hour, ssn):
      prediction = run_python_prediction(...)
      reference = load_reference_data(...)
      assert_within_tolerance(prediction, reference)
  ```

**Tolerance Specifications:**
- SNR: ±10 dB (typical VOACAP variation)
- Reliability: ±15% (statistical nature of model)
- MUF: ±2 MHz (ionospheric variability)

**Target:** >80% of test cases pass within tolerance

### Implement CI/CD

**Action Items:**
- [ ] Create `.github/workflows/validation.yml`:
  ```yaml
  on: [push, pull_request]
  jobs:
    validate:
      runs-on: ubuntu-latest
      steps:
        - name: Run reference validation
          run: python test_voacap_reference.py --all
        - name: Check pass rate
          run: |
            PASS_RATE=$(jq '.summary.pass_rate' validation_results.json)
            if (( $(echo "$PASS_RATE < 80" | bc -l) )); then exit 1; fi
  ```

- [ ] Add validation status badge to README.md
- [ ] Configure automated validation reports
- [ ] Set up alerts for regression detection

**Success Criteria:**
- >80% pass rate on comprehensive reference suite
- CI/CD runs automatically on every commit
- Validation status visible in README

---

## Priority 3: VOACAP Manual Review & Dashboard Design (Weeks 5-6)

### Original VOACAP Manual Analysis

**File:** `docs/Original_VOACAP_Manual.pdf`

**Action Items:**
- [ ] Extract key UX patterns and workflows from manual
  - How does VOACAP present prediction results?
  - What visualizations are most useful?
  - What parameters do users typically adjust?

- [ ] Identify features in original VOACAP not yet in dashboard:
  - Area coverage predictions
  - Point-to-point detailed analysis
  - Frequency optimization recommendations
  - Path geometry visualization
  - Signal distribution charts

- [ ] Document user workflows:
  - Frequency planning for specific path
  - Time-of-day propagation analysis
  - Solar cycle impact assessment
  - Multi-hop vs single-hop comparison

- [ ] Create design recommendations document:
  - `docs/DASHBOARD_DESIGN_RECOMMENDATIONS.md`
  - Include screenshots/diagrams from manual
  - Prioritize enhancements by user value

**Deliverables:**
- Design document with specific enhancement recommendations
- Prioritized feature list for dashboard improvements
- UI/UX mockups (optional, can be sketches)

### Dashboard Enhancement Implementation

**Immediate Improvements:**
- [ ] Better error handling and user feedback
- [ ] Loading states and progress indicators
- [ ] Historical trend graphs (SNR, MUF over time)
- [ ] Mobile responsiveness improvements
- [ ] Export predictions as PDF/CSV
- [ ] Frequency recommendation widget

**Medium-Term Improvements:**
- [ ] Path geometry visualization (great circle on map)
- [ ] Signal distribution charts (decile bands)
- [ ] Multi-path comparison view
- [ ] Solar cycle forecasting integration

**Reference:** See `Dashboard/ISSUE_MULTI_USER_WEB_APP.md` for future multi-user service ideas

---

## Priority 4: Real-World Validation (Weeks 7-8)

### WSPR Integration

**Goal:** Validate predictions against actual propagation data

**Action Items:**
- [ ] Create `validate_wspr.py`:
  ```python
  import requests

  # Fetch recent WSPR spots
  spots = fetch_wspr_data(
      callsign="<test_callsign>",
      hours=24
  )

  # For each spot, run prediction
  for spot in spots:
      prediction = engine.predict(
          rx_location=spot.rx_grid,
          freq=spot.frequency,
          utc_time=spot.time
      )

      # Compare predicted vs actual SNR
      error = abs(prediction.snr_db - spot.snr_db)
      errors.append(error)

  # Statistical analysis
  print(f"Median SNR error: {np.median(errors):.1f} dB")
  print(f"Mean SNR error: {np.mean(errors):.1f} dB")
  print(f"Std dev: {np.std(errors):.1f} dB")
  ```

- [ ] Integrate with WSPR database API
- [ ] Create statistical analysis framework
- [ ] Generate validation report with error distributions
- [ ] Identify systematic biases (frequency, distance, time-of-day)

**Target Metrics:**
- Median SNR error: <10-15 dB (initial target)
- Correlation coefficient: >0.5 between predicted and actual
- MUF predictions correlate with highest observed frequency

**Deliverables:**
- `WSPR_VALIDATION_REPORT.md` with statistical analysis
- Identified model limitations and assumptions
- Recommendations for improvement

### PSKReporter Integration (Optional)

- [ ] Similar approach to WSPR but with broader mode coverage
- [ ] Cross-validate predictions across multiple data sources

---

## Priority 5: Documentation & Polish (Ongoing)

### Code Documentation

**Action Items:**
- [ ] Add type hints throughout codebase:
  ```python
  from typing import List, Tuple, Optional
  from dataclasses import dataclass

  def compute_muf(
      profile: IonosphericProfile,
      distance_km: float,
      min_angle_deg: float = 3.0
  ) -> Tuple[float, List[ModeInfo]]:
      """Compute Maximum Usable Frequency for circuit.

      Args:
          profile: Ionospheric profile at midpoint
          distance_km: Path distance in kilometers
          min_angle_deg: Minimum elevation angle in degrees

      Returns:
          Tuple of (MUF in MHz, list of propagation modes)
      """
      ...
  ```

- [ ] Set up Sphinx documentation:
  ```bash
  pip install sphinx sphinx-rtd-theme
  sphinx-apidoc -o docs/api src/dvoacap
  sphinx-build docs docs/_build
  ```

- [ ] Create API reference documentation
- [ ] Add docstrings to all public functions/classes

### Example Notebooks

**Action Items:**
- [ ] Create `notebooks/` directory with Jupyter notebooks:
  - `01_basic_prediction.ipynb` - Simple prediction example
  - `02_parameter_sensitivity.ipynb` - How SSN, power, antenna affect results
  - `03_frequency_planning.ipynb` - Optimal frequency selection
  - `04_validation_methods.ipynb` - How validation works

### User Guides

**Action Items:**
- [ ] Update `docs/USAGE.md` with complete API examples
- [ ] Create `docs/TROUBLESHOOTING.md` with common issues
- [ ] Write `docs/COMPARISON_GUIDE.md`:
  - DVOACAP vs VOACAP vs ITU P.533
  - When to use each prediction method
  - Interpreting reliability vs service probability

### Contributing Guide

**Action Items:**
- [ ] Update `CONTRIBUTING.md` with:
  - Development environment setup
  - Testing requirements
  - Code style guidelines (PEP 8)
  - Pull request process
  - How to add new test cases

---

## Priority 6: Performance Optimization (Future)

### Profiling

**Action Items:**
- [ ] Profile `prediction_engine.py` to identify bottlenecks:
  ```python
  import cProfile

  profiler = cProfile.Profile()
  profiler.enable()
  engine.predict(...)
  profiler.disable()
  profiler.print_stats(sort='cumtime')
  ```

- [ ] Identify slow functions (likely candidates):
  - Fourier map interpolation
  - Ionospheric profile computation
  - Ray path calculations
  - Signal strength computations

### Optimization Strategies

**Action Items:**
- [ ] Implement caching for Fourier map calculations
- [ ] Use NumPy views instead of copies where possible
- [ ] Consider Numba JIT compilation for hot paths
- [ ] Lazy-load coefficient files
- [ ] Vectorize operations using NumPy

**Performance Targets:**
- Single prediction: <1 second (currently ~500ms)
- Area coverage scan (100 points): <30 seconds
- Memory usage: <500 MB

---

## Priority 7: Community & Distribution (Future)

### PyPI Package

**Action Items:**
- [ ] Prepare for PyPI distribution:
  - Ensure `pyproject.toml` is complete
  - Add long_description from README
  - Configure build system
  - Test with `python -m build`

- [ ] Create versioning strategy (semantic versioning)
- [ ] Write CHANGELOG.md
- [ ] Add release notes template

### Integration Examples

**Action Items:**
- [ ] Create integration guides for:
  - Ham Radio Deluxe
  - WSJT-X
  - Logger programs (N1MM, DXLab)
  - Web applications (Flask/Django)

### Community Building

**Action Items:**
- [ ] Set up GitHub Discussions for Q&A
- [ ] Create issue templates (bug report, feature request)
- [ ] Set up PR template with validation checklist
- [ ] Add Wiki for advanced topics
- [ ] Engage with amateur radio community forums

---

## Success Metrics

### Technical Quality
- [x] Phases 1-4: Validated and complete
- [ ] Phase 5: >80% reference validation pass rate
- [ ] End-to-end: Median WSPR SNR error <15 dB
- [ ] Code coverage: >80%
- [ ] No crashes for valid inputs
- [ ] Performance: <1 sec/prediction

### Documentation
- [ ] API documentation complete (Sphinx)
- [ ] User guides written
- [ ] Example notebooks working
- [ ] Contributing guide clear

### Community
- [ ] GitHub stars: +100
- [ ] PyPI downloads: >1000/month (after release)
- [ ] Community contributors: >5
- [ ] Integration projects: >3

---

## Timeline

### Weeks 1-2: Critical Bug Fixes
- Fix Phase 5 reliability calculation
- Validate signal strength computations
- Get basic predictions working correctly
- **Milestone:** Predictions show >0% reliability, one path validates

### Weeks 3-4: Systematic Validation
- Generate comprehensive reference test suite
- Expand test coverage to 10+ diverse paths
- Set up CI/CD automation
- **Milestone:** >80% pass rate on reference validation

### Weeks 5-6: Manual Review & Dashboard
- Analyze original VOACAP manual
- Document dashboard design recommendations
- Implement priority dashboard enhancements
- **Milestone:** Design document complete, 2-3 features implemented

### Weeks 7-8: Real-World Validation
- Implement WSPR validation framework
- Generate statistical validation report
- Document model limitations
- **Milestone:** WSPR validation report published

### Ongoing: Documentation & Polish
- Add type hints
- Create example notebooks
- Write user guides
- Performance optimization
- **Milestone:** Documentation complete, ready for v1.0 release

---

## Risk Assessment

### High Risk
**Phase 5 Integration Bugs**
- Risk: Deep bugs hard to diagnose
- Mitigation: Line-by-line FORTRAN comparison, detailed logging
- Fallback: Use simplified model temporarily, document limitations

**Validation Data Availability**
- Risk: Limited reference VOACAP output
- Mitigation: Run original VOACAP to generate test cases
- Fallback: Use VE3NEA's DVOACAP (Pascal) as secondary reference

### Medium Risk
**Performance Bottlenecks**
- Risk: Python slower than FORTRAN/Pascal
- Mitigation: NumPy vectorization, Numba JIT, Cython
- Fallback: "Fast enough" is good enough (current ~500ms acceptable)

**Community Adoption**
- Risk: Ham radio community prefers existing tools
- Mitigation: Superior UX, better docs, modern integrations
- Fallback: Position as research/educational tool

---

## Key Files Reference

### Core Implementation
- `src/dvoacap/prediction_engine.py` - Main prediction engine (Phase 5)
- `src/dvoacap/muf_calculator.py` - MUF calculations (Phase 4)
- `src/dvoacap/reflectrix.py` - Ray tracing (Phase 4)
- `src/dvoacap/ionospheric_profile.py` - Ionosphere modeling (Phase 3)
- `src/dvoacap/noise_model.py` - Noise calculations (Phase 5)

### Testing & Validation
- `tests/test_voacap_reference.py` - Reference validation
- `validate_predictions.py` - Functional validation
- `SampleIO/voacapx.out` - Reference VOACAP output

### Documentation
- `docs/Original_VOACAP_Manual.pdf` - Reference manual (NEW!)
- `FORTRAN_ANALYSIS_AND_RECOMMENDATIONS.md` - Debugging guide
- `ABSORPTION_BUG_ANALYSIS.md` - Recent bug fixes
- `VALIDATION_STRATEGY.md` - Testing approach

### FORTRAN Reference
- `RELBIL.FOR` - Reliability calculations
- `REGMOD.FOR` - Signal calculations
- `ALLMODES.FOR` - Mode selection
- `SIGDIS.FOR` - Signal distribution adjustments

---

## Notes

1. **Flexibility:** This plan is comprehensive but flexible. Priorities can shift based on findings during debugging.

2. **Incremental Progress:** Each phase builds on previous work. Don't skip ahead until critical bugs are fixed.

3. **Documentation as You Go:** Document decisions, findings, and limitations throughout the process.

4. **Community Input:** Engage with amateur radio community for feedback on dashboard and features.

5. **Version Control:** Create feature branches for major changes, use PRs for code review.

6. **Testing First:** Write tests before fixing bugs to prevent regressions.

---

## Getting Started

**Immediate Action (Week 1, Day 1):**

```bash
# 1. Ensure environment is set up
pip install numpy scipy matplotlib pytest

# 2. Run current validation to establish baseline
python validate_predictions.py --regions UK --bands 20m --debug

# 3. Examine Phase 5 reliability calculation
# Add logging to prediction_engine.py:810-850
# Compare intermediate values to FORTRAN RELBIL.FOR

# 4. Review FORTRAN reference
# Read RELBIL.FOR lines 93-100 carefully
# Verify Python signal/noise distribution matches

# 5. Test fixes
python test_voacap_reference.py
python validate_predictions.py
```

**Questions or Issues?**
- Review `FORTRAN_ANALYSIS_AND_RECOMMENDATIONS.md` for detailed debugging guidance
- Check `ABSORPTION_BUG_ANALYSIS.md` for recent fixes
- Consult `docs/Original_VOACAP_Manual.pdf` for algorithm details

---

**Last Updated:** 2025-11-14
**Status:** Ready to proceed with Week 1 debugging

**Next Review:** After Week 2 (after fixing Phase 5 bugs)
