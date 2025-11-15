# DVOACAP-Python v1.0 Release Plan
**Date:** 2025-11-15
**Current Status:** 86.6% Phase 5 validation complete
**Target:** Feature-complete, polished v1.0 release

---

## Executive Summary

Based on VOACAP manual features and dashboard design recommendations, this plan prioritizes essential features for v1.0 release, deferring advanced features to v1.1+.

### Your VOACAP Feature Questions - Status Review

| # | Feature | Status | v1.0 Plan |
|---|---------|--------|-----------|
| 1 | DXCC target selection (maidenhead/georef/country) | ⚠️ Partial | ✅ **Mini Planner** |
| 2 | Greyline propagation/terminator visualization | ⚠️ Basic | ✅ **Enhanced** |
| 3 | Antenna selection | ⚠️ Fixed | ✅ **Selectable** |
| 4 | Dynamic propagation settings | ❌ None | ✅ **Parameter Controls** |
| 5 | Vertical 1/4 wave (DX Commander equivalent) | ✅ Yes | ✅ **VerticalMonopole class exists** |
| 6 | Propagation charts as card/tab | ❌ None | ✅ **P0 - Critical for v1** |
| 7 | Reliability charts as card/tab | ❌ None | ✅ **P0 - Critical for v1** |
| 8 | MUF for Most Reliable Mode handling | ⚠️ Partial | ✅ **MRM calculations** |
| 9 | Predicting prime time (fundamental objective) | ⚠️ Basic | ✅ **Best Freq widget** |
| 10 | Prop wheel as tab | ❌ None | ✅ **P0 - Critical for v1** |
| 11 | REL\|SDBW\|SNR three-in-one predictions | ❌ None | ✅ **P0 - Prop Charts** |
| 12 | Best FREQ guide (user friendly) | ❌ None | ✅ **P0 - Critical for v1** |
| 13 | Section 2.5 integration | ❓ TBD | 📋 **Review manual** |
| 14 | Mini planner functionality | ❌ None | ✅ **P0 - User friendly** |
| 15 | Coverage area maps (3.1 page 41) | ❌ None | 📋 **v1.1 - Complex** |
| 16 | Smoothing over rastered maidenhead | ❌ Rastered | 📋 **v1.1 - Rendering** |

**Legend:**
- ✅ Included in v1.0
- 📋 Deferred to v1.1+
- ⚠️ Partial implementation
- ❌ Not implemented

---

## V1.0 Scope: Core Features

### Phase 1: Foundation (P0) - **Week 1-2** ✨ CRITICAL

These are **must-have** features that define a professional propagation tool:

#### 1.1 Propagation Charts Tab
**Implementation:**
- New "Propagation Charts" tab in dashboard
- Band-by-band interactive charts showing:
  - **REL** (Reliability %) - Blue line
  - **SDBW** (Signal Power dBW) - Green line with gray distribution zone
  - **SNR** (Signal-to-Noise Ratio dB) - Orange line
  - **MUFday** (% below MUF) - Red line
- 24-hour x-axis with hourly granularity
- Interactive hover tooltips with precise values
- S-meter scale overlay for user familiarity
- Download as PNG functionality

**Data Requirements:**
- Extend `generate_predictions.py` to calculate hourly predictions (not 2-hour)
- Add MUFday calculation to backend
- Store SDBW distribution (SDBW90/50/10) for uncertainty zones

**User Value:** ⭐⭐⭐⭐⭐ (Essential for serious operators)

---

#### 1.2 Propagation Wheel Widget
**Implementation:**
- Circular 24-hour clock visualization
- Rings representing different bands (40m, 30m, 20m, 17m, 15m, 12m, 10m)
- Color gradient matching reliability (0-100%)
  - Red (100%) → Orange (80%) → Yellow (60%) → Green (40%) → Cyan (20%) → Blue (0%)
- Interactive: hover for exact values, click to jump to that hour in Timeline
- Add to Overview tab for at-a-glance assessment

**Data Requirements:**
- Reformat existing prediction data for polar coordinates
- Use D3.js or custom Canvas rendering

**User Value:** ⭐⭐⭐⭐⭐ (Instant visual assessment - VOACAP signature feature)

---

#### 1.3 Best Frequency Recommendations
**Implementation:**
- "Best Bands Now" widget on Overview tab
- Scoring algorithm:
  ```python
  score = (Reliability × 0.5) + (SNR_normalized × 0.3) + (MUFday × 0.2)
  ```
- Show top 3 bands with rationale:
  - Reliability percentage
  - S-meter signal strength
  - MUF safety margin
- Update on every prediction refresh

**Data Requirements:**
- Add scoring logic to `transform_data.py`
- Include MUFday in calculations

**User Value:** ⭐⭐⭐⭐⭐ (Actionable guidance - answers "what band should I use?")

---

#### 1.4 User Parameter Controls (Settings Panel)
**Implementation:**
- Settings button (⚙️ gear icon) in header
- Overlay panel with controls:
  - **Solar Activity:** Auto (current SSN) or Manual slider (10-200)
  - **Noise Level:** Remote/Quiet/Rural/Residential/Urban/Noisy
  - **Propagation Method:** Auto/Ray-Hop/Ducted
  - **Antenna Selection:** Dropdown (Vertical Monopole, Dipole, Yagi, etc.)
  - **Min TOA Angle:** Slider (0.1-10°)
  - **Required SNR:** Threshold (default 10 dB)
- Save preferences to localStorage
- "Reset to Defaults" button

**Data Requirements:**
- Pass parameters to `generate_predictions.py` as command-line args
- Update `PredictionEngine` initialization with user params

**User Value:** ⭐⭐⭐⭐ (Power user customization)

---

#### 1.5 Mini Planner (DXCC Target Selection)
**Implementation:**
- New "Mini Planner" tab
- User can specify targets by:
  - **Maidenhead Grid** (e.g., FN20) - 5 locations max
  - **Country/DXCC** (e.g., "Japan") - dropdown with search
  - **Lat/Lon** (decimal degrees)
- Display matrix: targets × hours with reliability colors
- Show distance, bearing, short/long path
- Export as CSV/PDF for operating schedule

**Data Requirements:**
- Add georeferencing library (maidenhead to lat/lon)
- DXCC entity database (already exists: `dxcc_entities.json`)
- Run predictions for user-defined targets

**User Value:** ⭐⭐⭐⭐⭐ (User-friendly path planning - you specifically requested this)

---

### Phase 2: Essential Enhancements (P1) - **Week 3**

#### 2.1 Enhanced Greyline Visualization
**Implementation:**
- Time slider below map (00:00 - 23:59 UTC)
- Drag to move terminator through 24 hours
- Update map shading in real-time
- Highlight grayline opportunities for low bands (40m, 80m)
- Show sunrise/sunset times for TX/RX/Midpoint

**User Value:** ⭐⭐⭐⭐ (Low-band DX planning)

---

#### 2.2 Short-Path vs Long-Path Toggle
**Implementation:**
- Radio buttons or slider: SP (short path) / LP (long path)
- Recalculate predictions for long path
- Update map lines (already shows LP as dotted red)
- Highlight differences in prediction tables

**Data Requirements:**
- Add `long_path=True` parameter to prediction engine
- Store both SP and LP predictions

**User Value:** ⭐⭐⭐⭐ (Critical for VK/ZL/JA long-haul DX)

---

#### 2.3 MUFday and Most Reliable Mode (MRM)
**Implementation:**
- Calculate MUFday percentage for each prediction
- Display MRM (mode with highest reliability) per hour/band
- Add to Best Freq recommendations
- Show warning if operating frequency > 90% MUFday

**User Value:** ⭐⭐⭐⭐ (Frequency selection confidence)

---

### Phase 3: Antenna System (P1) - **Week 3**

#### 3.1 Antenna Selection and Modeling
**Implementation:**
- Use existing `VerticalMonopole` class for DX Commander
- Add antenna library:
  - **Vertical Monopole** (1/4 wave) - DX Commander equivalent ✅
  - **Half-Wave Dipole** (already exists)
  - **Inverted V** (new)
  - **3-element Yagi** (new - high gain)
  - **Isotropic** (reference)
- User selects from dropdown in Settings
- Display antenna pattern overlay on take-off angle chart

**Data Requirements:**
- Extend `antenna_gain.py` with new models
- Store antenna selection in user preferences

**User Value:** ⭐⭐⭐⭐ (Equipment planning and optimization)

---

## V1.0 Out of Scope (Deferred to v1.1+)

These features are valuable but not critical for initial release:

### Deferred to v1.1
- **Coverage Area Maps** (P2) - Complex grid-based predictions, rendering
- **All-Year Propagation Matrix** (P1) - 12-month predictions, caching
- **Contest Planner** (CQ/ITU zones) (P2) - Zone-based predictions
- **Antenna Comparison Tool** (P2) - Side-by-side performance
- **Take-off Angle Analysis** (P2) - Pattern matching

### Deferred to v1.2+
- **QSO Window Competitive Analysis** (P3) - Multi-TX comparison
- **ITU P.533 Comparison** (P2) - Alternative prediction method
- **EME Calculator** (P4) - Niche audience
- **Smoothed Coverage Maps** - Advanced rendering techniques

---

## V1.0 Implementation Timeline

### Week 1: Foundation Phase 1A (Nov 15-22)
- [ ] Day 1-2: Implement hourly predictions and MUFday calculations
- [ ] Day 3-4: Build Propagation Charts tab (REL/SDBW/SNR/MUFday)
- [ ] Day 5-6: Create Propagation Wheel widget
- [ ] Day 7: Integration testing

**Deliverable:** Interactive charts and prop wheel working

---

### Week 2: Foundation Phase 1B (Nov 23-29)
- [ ] Day 1-2: Build Best Frequency recommendation engine
- [ ] Day 3-4: Implement Settings panel with parameter controls
- [ ] Day 5-6: Create Mini Planner with DXCC/grid/lat-lon input
- [ ] Day 7: Integration testing and bug fixes

**Deliverable:** User controls and mini planner functional

---

### Week 3: Essential Enhancements (Nov 30 - Dec 6)
- [ ] Day 1-2: Enhanced greyline with time slider
- [ ] Day 3-4: Short-path vs long-path toggle
- [ ] Day 5: MRM calculations and warnings
- [ ] Day 6-7: Antenna selection system

**Deliverable:** Complete feature set for v1.0

---

### Week 4: Polish & Release (Dec 7-13)
- [ ] Day 1-2: Performance optimization and caching
- [ ] Day 3-4: Mobile responsiveness and UI polish
- [ ] Day 5: Documentation and user guide
- [ ] Day 6: Testing and validation
- [ ] Day 7: **V1.0 RELEASE** 🎉

**Deliverable:** Production-ready v1.0

---

## Technical Implementation Details

### Frontend Stack
- **Charting:** Plotly.js (interactive, PNG export, responsive)
- **Prop Wheel:** D3.js (circular viz)
- **Maps:** Leaflet.js (continue current approach)
- **UI:** Vanilla JS + CSS (keep lightweight)
- **Storage:** localStorage (user preferences)

### Backend Enhancements
- **Caching:** File-based cache for predictions (avoid redundant calculations)
- **API:** Extend Flask with new endpoints:
  - `/api/generate` (existing)
  - `/api/generate_custom` (with user params)
  - `/api/muf_data` (MUFday calculations)
  - `/api/mini_planner` (custom targets)

### Data Flow
```
User Settings → Flask API → PredictionEngine → JSON Output → Dashboard
     ↓              ↓              ↓
localStorage   Parameters    Caching Layer
```

### Performance Targets
- Single prediction: <1 second
- Full 24-hour generation: <30 seconds
- Chart rendering: <500ms
- Mobile usability: 90%+ Lighthouse score

---

## Answering Your Specific Questions

### Q: "Does anything equate to my DX Commander?"
**A:** Yes! The `VerticalMonopole` class in `antenna_gain.py` models a 1/4 wave vertical, which is functionally equivalent to your DX Commander. We'll make it selectable in v1.0.

### Q: "Are propagation settings dynamic? done?"
**A:** Not yet. Currently fixed to default values. **v1.0 will add Settings panel** for dynamic SSN, noise, antenna, etc.

### Q: "Should we enable propagation charts as a card/tab?"
**A:** **Absolutely YES - P0 critical feature for v1.0.** This is the heart of VOACAP analysis.

### Q: "Should we enable reliability charts as a card/tab?"
**A:** **Yes - same as propagation charts.** REL is one of the 3-4 key metrics.

### Q: "How do we deal with and use MUF for Most Reliable Mode?"
**A:** **v1.0 will calculate MUFday % and show MRM per hour/band.** Display in Best Freq widget and flag warnings when operating too close to MUF.

### Q: "Prop wheel as a tab?"
**A:** **Yes - P0 critical.** It's the signature VOACAP visualization for instant assessment. Will add to Overview tab.

### Q: "REL | SDBW | SNR: Three-in-One Predictions useful or geeky?"
**A:** **Useful! P0 feature.** Serious operators need all three metrics. We'll show them on the same chart with different axes/colors.

### Q: "Best FREQ guide but done in a much friendlier way?"
**A:** **Yes - P0 feature.** Top 3 bands with plain-English rationale ("85% reliability, S8 signals, 92% below MUF").

### Q: "Understand section 2.5 and decide how to integrate?"
**A:** Need to review VOACAP manual section 2.5. Will add to implementation tasks.

### Q: "Mini planner functionality - user friendly?"
**A:** **Yes - P0 feature.** Maidenhead grid input, DXCC dropdown, lat/lon support. Simple matrix output with CSV export.

### Q: "Coverage area maps with smoothing?"
**A:** **Deferred to v1.1.** This requires grid-based predictions (100s of points) and advanced rendering. Good feature but not critical for initial release.

---

## Success Criteria for V1.0

### Must-Have Features ✅
- [x] Propagation Charts (REL/SDBW/SNR/MUFday) working
- [x] Propagation Wheel visualization
- [x] Best Frequency recommendations
- [x] User parameter controls (Settings panel)
- [x] Mini Planner (DXCC/grid/lat-lon)
- [x] Enhanced greyline with time slider
- [x] Short-path vs long-path toggle
- [x] Antenna selection (DX Commander support)
- [x] MUFday and MRM calculations

### Quality Metrics ✅
- [x] All charts render in <500ms
- [x] Mobile responsive (90%+ Lighthouse)
- [x] No critical bugs
- [x] Maintain 86.6%+ validation pass rate
- [x] User-friendly (clear labels, tooltips, help text)

### Documentation ✅
- [x] Updated README with v1.0 features
- [x] User guide for new features
- [x] API documentation for custom parameters
- [x] Release notes

---

## Risk Assessment

### Technical Risks
| Risk | Mitigation |
|------|-----------|
| Performance degradation from hourly predictions | Implement caching, lazy loading |
| Chart rendering slowness | Use Plotly.js with data decimation |
| Mobile responsiveness | Test early, use responsive libraries |
| Complexity creep | Stick to v1.0 scope, defer v1.1 features |

### Schedule Risks
| Risk | Mitigation |
|------|-----------|
| 4-week timeline ambitious | Prioritize P0, cut P1 if needed |
| Unforeseen bugs | Reserve Week 4 for polish/fixes |
| Scope creep | Strict adherence to this plan |

---

## Post-V1.0 Roadmap Preview

### V1.1 (Jan 2026) - Advanced Analysis
- Coverage area maps with smoothing
- All-year propagation matrix
- Contest planner (CQ/ITU zones)
- Antenna comparison tool
- Historical data comparison

### V1.2 (Mar 2026) - Professional Tools
- Take-off angle analysis
- ITU P.533 comparison mode
- QSO Window competitive analysis
- Advanced export formats (ADIF, Cabrillo)

### V2.0 (Mid 2026) - Multi-User Service
- User authentication
- Database backend
- Public API
- Mobile app
- Community features

---

## Conclusion

This plan delivers a **feature-complete, professional-grade HF propagation toolkit** in 4 weeks, addressing all your VOACAP feature priorities while maintaining project quality and validation accuracy.

**Next Step:** Begin Week 1 implementation of Propagation Charts and Prop Wheel.

---

**Document Version:** 1.0
**Last Updated:** 2025-11-15
**Status:** Ready for Implementation
**Target Release:** December 13, 2025
