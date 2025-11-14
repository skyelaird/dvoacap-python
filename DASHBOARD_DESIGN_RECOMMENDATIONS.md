# Dashboard Design Recommendations
## DVOACAP-Python Web Interface Enhancement Plan

**Date:** 2025-11-14
**Status:** Week 5-6 Deliverable - VOACAP Manual Review & Dashboard Design
**Based on:** VOACAP Online User's Manual Analysis

---

## Executive Summary

This document provides comprehensive design recommendations for enhancing the DVOACAP-Python dashboard based on an in-depth analysis of the VOACAP Online User's Manual and current implementation. The recommendations are prioritized by user value and implementation complexity, with the goal of creating a world-class HF propagation prediction tool that rivals or exceeds VOACAP Online capabilities.

**Key Findings:**
- Current dashboard covers basic functionality well (current conditions, band status, timeline, DXCC tracking)
- VOACAP Online offers 15+ sophisticated analysis tools not yet implemented
- Backend prediction engine is already powerful - opportunities lie in visualization enhancements
- User workflows center around 4 primary use cases: frequency planning, contest prep, DXing, and real-time decision making

---

## Table of Contents

1. [Current Dashboard Analysis](#current-dashboard-analysis)
2. [VOACAP Online Feature Analysis](#voacap-online-feature-analysis)
3. [Identified Gaps](#identified-gaps)
4. [User Workflows & UX Patterns](#user-workflows--ux-patterns)
5. [Priority Enhancement Recommendations](#priority-enhancement-recommendations)
6. [Implementation Roadmap](#implementation-roadmap)
7. [Design Mockups & Wireframes](#design-mockups--wireframes)

---

## 1. Current Dashboard Analysis

### 1.1 Strengths

**✓ Strong Foundation**
- Clean, modern dark theme interface (excellent for night operations)
- Real-time API integration with on-demand refresh capability
- Solar conditions bar providing key indices (SFI, SSN, Kp, A-index)
- Interactive world map with Leaflet.js showing propagation paths
- Gray line visualization with automatic updates
- Responsive design working on desktop and mobile

**✓ Well-Implemented Features**
- Tab-based navigation (Overview, Band Details, Timeline, DXCC Tracking)
- Color-coded band quality indicators (green/yellow/red/gray)
- 72-hour forecast with hourly granularity
- DXCC integration with progress tracking
- S-meter signal strength estimates
- Band-specific region details with distance/bearing
- Real-time "needed DXCC" alerts for workable entities

**✓ Technical Excellence**
- Progressive web app capability (offline-capable structure)
- JSON-based data architecture for easy backend integration
- Server-side generation with Flask API
- Artifact retention and historical tracking potential

### 1.2 Current Limitations

**Missing Advanced Analysis Tools**
- No propagation charts showing REL/SDBW/SNR/MUFday over 24 hours
- No propagation wheel (24-hour clock visualization)
- No frequency optimization recommendations
- No antenna comparison capabilities
- No take-off angle analysis
- No coverage area maps

**Limited Temporal Analysis**
- Fixed to current/near-term predictions
- No all-year view (12-month propagation matrix)
- No historical trend analysis
- Limited to 72-hour forecast (good, but could be extended)

**Constrained Parameter Control**
- No user control over SSN, noise level, propagation method
- No ability to toggle short-path vs long-path
- No sporadic-E considerations
- Fixed antenna configurations (no comparison mode)
- No minimum take-off angle adjustment

**Missing Professional Features**
- No ITU P.533 prediction comparison (ITURHFProp)
- No QSO Window competitive analysis
- No contest/DXpedition planning tools
- No EME (Earth-Moon-Earth) calculations
- No sun phase visualizations
- No grayline time slider for interactive exploration

---

## 2. VOACAP Online Feature Analysis

### 2.1 Core Interface Components

**Interactive Map**
- Drag-and-drop TX/RX markers
- Real-time distance, bearing, midpoint display
- Short-path (green line) and long-path (red dotted line) visualization
- Maidenhead grid overlay option
- Sunrise/sunset/midnight indicators (colored circles)
- QSO Window markers (5 competitive locations)

**Time Controls**
- Pop-up calendar for date selection
- Time slider for gray line terminator manipulation
- Automatic current date/time reset capability
- Sun phase indicators (clickable to jump to specific times)

**Parameter Controls**
- Left sidebar: QSO markers, Home locations, SP/LP toggle, Es toggle, Grid toggle
- Right sidebar: Mode, Power, Antennas, Settings
- Settings overlay with 5 sections:
  1. General Propagation Settings
  2. Coverage Area Map Settings
  3. Propagation Planner Settings
  4. TX Antenna Analysis Settings
  5. Take-off Angle Analysis Settings

### 2.2 Analysis Tools (16+ Functions)

**Point-to-Point Menu:**
1. **Prop Charts** - 15 interactive charts (3.5-28 MHz) showing REL, SDBW, MUFday with:
   - Color-coded reliability lines
   - Signal power distribution (gray zone showing SDBW90/SDBW10)
   - MUFday percentage overlay
   - S-meter scale on right axis
   - Interactive toolbox (zoom, pan, save PNG, hover data)

2. **Prop Wheel** - 24-hour clock visualization:
   - Color-coded reliability by hour/band
   - Intuitive at-a-glance propagation assessment
   - Live updates as parameters change

3. **VOA Band-by-Band** - Complete band analysis:
   - All 15 bands in one view
   - Both SP and LP propagation tables
   - Comprehensive VOACAP predictions

4. **ITU Band-by-Band** - ITURHFProp predictions:
   - Median SNR50, BCR, Operational MUF
   - Comparison capability vs VOACAP
   - Standards-compliant predictions

5. **REL | SDBW | SNR** - Three-in-one visualization:
   - Full 2-30 MHz spectrum analysis
   - Median MUF and FOT curves
   - Signal strength heatmaps

6. **Best FREQ** - Optimal frequency guide:
   - Top 3 frequencies per hour
   - Signal power at 50%/90% of days
   - SNR distribution (SNR10/50/90)
   - MUFday probability
   - Automatic uncertainty flagging (ΔSIG > 40-50 dB)

7. **Full Analysis** - Detailed statistics:
   - MUFday, REL, SNR, SDBW tables
   - All organized by hour and band
   - dSNR and dSDBW spreads
   - Raw VOACAP output access

8. **All Year** - 12-month propagation matrix:
   - Color-coded reliability by month/hour
   - Integrated SSN predictions
   - R/S/M parameters on hover
   - Day/night visualization for TX/RX/MP

9. **QSO Window** - Competitive analysis:
   - 6-station comparison (your station + 5 competitors)
   - SDBW, REL, SNR graphs for all stations
   - Strategic advantage identification
   - Dynamic marker placement

10. **Antenna** - Comparative performance:
    - Best reliability by hour across all bands
    - Best frequency/SNR analysis
    - Per-antenna signal power and SNR breakdown
    - CSV export for advanced analysis

11. **TOA Analysis** - Take-off angle matching:
    - Predicted optimal angles for MRM
    - Antenna pattern overlay
    - Gain at optimal angles
    - Monthly or yearly analysis
    - PRN export for HFTA integration

12. **Planner** - Contest/DXpedition planning:
    - CQ/ITU zone or DXCC country selection
    - Zone-based or band-specific charts
    - Color-coded reliability + signal indicators (++, +, ●)
    - Sunrise/sunset bars for TX/RX/MP
    - Interactive data on hover

13. **Mini Planner** - Quick 5-location snapshot:
    - Same visualization as Planner
    - User-defined marker locations
    - Rapid comparison capability

14. **Grayline (P2P)** - Point-to-point grayline:
    - 7 sun phase times (DAWN, RISE, POST, PRE, SET, DUSK, MNITE)
    - TX/RX/MP locations
    - Current + next month data
    - Low-band planning focus

15. **Grayline for DXCC** - Comprehensive grayline:
    - Daily sunrise/sunset for all DXCC
    - Full-year calendars
    - Deep analysis (countries on terminator or in darkness)
    - Distance/bearing for SP/LP
    - Prime DX target identification

16. **EME** - Earth-Moon-Earth windows:
    - 7-day common window calculation
    - Moon elevation, azimuth, distance
    - 5-minute interval precision
    - Path loss calculations

17. **Sun of the Day** - Sun phase visualization:
    - Graphical timeline with color coding
    - TX/RX/MP sun phases
    - 7 phases: DAWN, RISE, POST, PRE, SET, DUSK, NADIR
    - Low-band propagation planning

**Coverage Maps Menu:**
- Signal Strength (SDBW) maps
- Circuit Reliability (REL) maps
- Customizable parameters (band, UTC, time range)
- PDF download capability

**Help Menu:**
- Space Weather dashboard (Kyoto Dst, Proton Flux, Tromso A-index)
- Long-term forecasts (27-day SFI/A/K predictions)
- Short-term forecasts (3-day K index)
- Interactive graphs with filtering

### 2.3 Visualization Techniques

**Color Coding Patterns**
- REL (Reliability): Blue lines in charts, color gradient in tables (white → red for 0% → 100%)
- SDBW (Signal Power): Green lines with gray distribution zones
- MUFday: Orange lines showing frequency vs MUF probability
- Quality bands: GOOD (green/60%+), FAIR (yellow/30-60%), POOR (red/<30%), CLOSED (gray)

**Interactive Elements**
- Hover tooltips showing precise values
- Clickable legend items to toggle visibility
- Zoom/pan controls on all charts
- Save as PNG functionality
- CSV/PDF export options

**Data Representation**
- Statistical distributions (SDBW90/50/10, SNR90/50/10)
- Uncertainty indicators (spread flagging with *)
- S-meter conversions for user familiarity
- Time representations (UTC with local time awareness)

---

## 3. Identified Gaps

### 3.1 High-Priority Missing Features

| Feature | User Value | Implementation Complexity | Priority |
|---------|------------|--------------------------|----------|
| Propagation Charts (REL/SDBW/SNR/MUFday) | Very High | Medium | **P0** |
| Frequency Optimization (Best FREQ) | Very High | Low-Medium | **P0** |
| Propagation Wheel (24-hr clock) | High | Low | **P0** |
| Parameter Controls (SSN, Noise, Method) | High | Low | **P1** |
| Short/Long Path Toggle | High | Low | **P1** |
| All-Year Propagation Matrix | High | Medium | **P1** |
| Coverage Area Maps | High | High | **P2** |
| Antenna Comparison Tool | Medium-High | Medium | **P2** |
| Take-off Angle Analysis | Medium-High | Medium-High | **P2** |
| ITU P.533 Comparison | Medium | Medium | **P2** |
| Contest Planner (CQ/ITU zones) | Medium | Medium | **P3** |
| QSO Window Competitive Analysis | Medium | Medium | **P3** |
| Grayline Time Slider | Medium | Low-Medium | **P3** |
| EME Calculator | Low-Medium | Medium | **P4** |

### 3.2 UX Enhancements

| Enhancement | User Value | Implementation Complexity | Priority |
|-------------|------------|--------------------------|----------|
| Parameter persistence (Set Home) | High | Low | **P0** |
| Downloadable reports (PDF/CSV) | High | Low-Medium | **P1** |
| Historical data comparison | Medium-High | High | **P2** |
| Mobile-optimized charts | Medium | Medium | **P2** |
| Keyboard shortcuts | Medium | Low | **P3** |
| User preferences storage | Medium | Low | **P3** |
| Multi-language support | Low | High | **P4** |

---

## 4. User Workflows & UX Patterns

### 4.1 Primary User Workflows

**Workflow 1: Real-Time Band Selection (Current Operations)**

**User Goal:** Determine which band/region to operate right now

**Current Dashboard Support:** ✓ Good
- Quick Summary shows best bands with region counts
- Band Details tab provides current conditions
- Color-coded quality indicators

**VOACAP Online Approach:**
- Propagation Wheel for instant 24-hour assessment
- Prop Charts for detailed hourly analysis
- Signal power with S-meter readings

**Recommended Enhancements:**
1. Add propagation wheel as dashboard widget
2. Display "Best Band Right Now" prominent indicator
3. Show top 3 frequency recommendations with rationale
4. Include signal strength forecasts (next 2-6 hours)

---

**Workflow 2: Frequency Planning (Contest/DXpedition Prep)**

**User Goal:** Plan operating strategy for upcoming event (days to weeks ahead)

**Current Dashboard Support:** ✗ Limited
- 72-hour forecast provides near-term view
- No multi-month analysis
- No zone-based planning

**VOACAP Online Approach:**
- Planner tool with CQ/ITU zone selection
- All-Year matrix for seasonal planning
- Best FREQ recommendations per hour
- QSO Window for competitive analysis

**Recommended Enhancements:**
1. Add "Contest Planner" tab with zone-based predictions
2. Implement month selector for future predictions
3. Create downloadable operating schedule (PDF/CSV)
4. Add "Best Hours by Band" summary table

---

**Workflow 3: Path-Specific Analysis (Chasing Rare DX)**

**User Goal:** Understand propagation to a specific location/entity

**Current Dashboard Support:** ✓ Moderate
- Can see region-level predictions
- DXCC integration shows needed entities
- Distance/bearing information available

**VOACAP Online Approach:**
- Point-to-point detailed analysis (Full Analysis)
- Grayline analysis for low-band opportunities
- Long-path vs short-path comparison
- Take-off angle matching with antennas

**Recommended Enhancements:**
1. Add "Path Analysis" tool for user-defined endpoints
2. Implement SP/LP toggle and comparison
3. Show grayline opportunities for specific paths
4. Display optimal take-off angles for user's antennas

---

**Workflow 4: Equipment Optimization (Antenna Selection)**

**User Goal:** Compare antenna performance, justify upgrades

**Current Dashboard Support:** ✗ None
- Fixed antenna assumptions
- No comparison capability
- No take-off angle analysis

**VOACAP Online Approach:**
- Antenna comparison tool
- TOA analysis with pattern overlay
- Multiple antenna sets for TX/RX
- Gain at optimal angles

**Recommended Enhancements:**
1. Add "Antenna Comparison" tool
2. Allow user to define antenna inventory
3. Show performance differences in dB and % reliability
4. Visualize antenna patterns vs required angles

---

### 4.2 Common UX Patterns from VOACAP Online

**Pattern 1: Progressive Disclosure**
- Simple overview first (Prop Wheel, Quick Summary)
- Detailed analysis available on demand (Prop Charts, Full Analysis)
- Expert tools hidden behind menus (TOA Analysis, Antenna)

**Pattern 2: Multiple Parameter Views**
- Always show 3-4 key metrics together (REL + SDBW + SNR + MUFday)
- Color coding consistent across all views
- Interactive tooltips reveal additional data

**Pattern 3: Temporal Navigation**
- Hour-by-hour granularity
- Month selector for seasonal analysis
- All-year matrix for annual planning
- Grayline slider for day/night exploration

**Pattern 4: Comparative Analysis**
- Side-by-side SP/LP comparison
- VOACAP vs ITU predictions
- Multi-antenna performance
- Competitive station analysis (QSO Window)

**Pattern 5: Downloadable Artifacts**
- PNG charts for sharing
- PDF reports for printing
- CSV data for custom analysis
- PRN files for external tools (HFTA)

---

## 5. Priority Enhancement Recommendations

### Phase 1: Foundation Enhancements (P0 - Quick Wins)

**1.1 Propagation Charts (Band-by-Band Analysis)**

**User Value:** Very High - Core feature for serious operators

**Implementation:**
- Add new "Propagation Charts" tab
- Use Plotly.js or Chart.js for interactive charts
- Display REL, SDBW, MUFday for each band (7 bands × 3 parameters)
- 24-hour x-axis, color-coded lines
- Hover tooltips showing precise values
- Toggle between SP/LP via button

**Data Requirements:**
- Extend generate_predictions.py to calculate hourly (not 2-hour) predictions
- Add MUFday calculation to backend
- Store SDBW distribution (SDBW90/50/10) for gray zones

**Mockup:**
```
┌─────────────────────────────────────────────────┐
│ Propagation Charts - 40m (7.150 MHz)           │
├─────────────────────────────────────────────────┤
│ 100% ┤                                          │
│      ┤         ┌──────┐                         │
│  75% ┤    ┌───┘      └────┐       REL          │
│      ┤    │                 └──┐    MUFday     │
│  50% ┤ ───┘                    └──             │
│      ┤                                          │
│   0% └─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬──      │
│        0 2 4 6 8 10 12 14 16 18 20 22   UTC    │
│                                                  │
│ With gray zone showing SDBW distribution        │
└─────────────────────────────────────────────────┘
```

---

**1.2 Propagation Wheel (24-Hour Clock)**

**User Value:** Very High - Instant visual assessment

**Implementation:**
- Add circular chart widget to Overview tab
- Use D3.js or custom Canvas rendering
- 24 hours around clock, 7-8 bands as rings
- Color gradient matching reliability (0-100%)
- Hover to show exact values
- Click to jump to that hour in Timeline

**Data Requirements:**
- Same as current data, reformatted for polar coordinates

**Mockup:**
```
        00
   23    ↑    01
      ╱─────╲
  22 │       │ 02
     │ 40m   │
  21 │ 20m   │ 03
     │ 15m   │
  20 │ 10m   │ 04
      ╲─────╱
   19    ↓    05
        12

Color: Red=100%, Orange=80%, Yellow=60%,
       Green=40%, Cyan=20%, Blue=0%
```

---

**1.3 Best Frequency Recommendations**

**User Value:** Very High - Actionable guidance

**Implementation:**
- Add "Best Bands Now" section to Overview
- Calculate score = (Reliability × 0.5) + (SNR_normalized × 0.3) + (MUFday × 0.2)
- Show top 3 bands with rationale
- Update every prediction refresh

**Data Requirements:**
- Add scoring logic to transform_data.py
- Include MUFday in scoring

**Mockup:**
```
┌────────────────────────────────────────┐
│ 🌟 Best Bands Right Now (18:00 UTC)   │
├────────────────────────────────────────┤
│ 1. 20m (14.150 MHz)                   │
│    ✓ 85% Reliability                   │
│    ✓ S8 signals to EU/UK               │
│    ✓ 92% below MUF                     │
│                                         │
│ 2. 15m (21.200 MHz)                   │
│    ✓ 72% Reliability                   │
│    ✓ S7 signals to EU                  │
│    ✓ 78% below MUF                     │
│                                         │
│ 3. 40m (7.150 MHz)                    │
│    ✓ 68% Reliability                   │
│    ✓ S6 signals to EU/UK (grayline)    │
│    ✓ 88% below MUF                     │
└────────────────────────────────────────┘
```

---

**1.4 User Parameter Controls**

**User Value:** High - Power user customization

**Implementation:**
- Add "Settings" button to header (gear icon)
- Overlay panel with parameter controls:
  - SSN slider (10-200, default to auto)
  - Noise selection (Remote/Quiet/Rural/Residential/Urban/Noisy)
  - Propagation method (Auto/Ray-Hop/Ducted)
  - Min TOA angle (0.1-10°)
  - Required SNR threshold
- Save preferences to localStorage
- "Reset to Defaults" button

**Data Requirements:**
- Pass parameters to generate_predictions.py as args
- Update prediction engine initialization

**Mockup:**
```
┌─────────────────────────────────────────┐
│ ⚙️  Prediction Settings               │
├─────────────────────────────────────────┤
│ Solar Activity                          │
│ ◯ Auto (current SSN)                    │
│ ◉ Manual: [▓▓▓▓▓░░░] 150               │
│                                          │
│ Noise Level at Receiver                 │
│ ◯ Remote  ◉ Quiet  ◯ Residential        │
│                                          │
│ Propagation Model                       │
│ ◉ Auto (Method 30)                      │
│ ◯ Ray-Hop  ◯ Ducted                     │
│                                          │
│ Min Take-off Angle: 3.0°                │
│ Required SNR: 10 dB                     │
│                                          │
│ [Reset Defaults]  [Save & Refresh]      │
└─────────────────────────────────────────┘
```

---

### Phase 2: Advanced Analysis (P1 - High Value)

**2.1 Short-Path vs Long-Path Toggle**

**User Value:** High - Critical for long-distance DX

**Implementation:**
- Add SP/LP toggle to map controls (radio buttons or slider)
- Recalculate predictions for long path
- Update map lines (already shows LP as dotted red)
- Highlight differences in tables

**Data Requirements:**
- Add long_path=True parameter to prediction engine
- Store both SP and LP predictions

---

**2.2 All-Year Propagation Matrix**

**User Value:** High - Strategic seasonal planning

**Implementation:**
- New "All Year" tab with 12×24 heatmap
- Rows = months, columns = hours, cells = color-coded reliability
- Separate matrix per band or region
- Integrated SSN forecasts from NOAA

**Data Requirements:**
- Generate predictions for each month (12 runs)
- Use SIDC SSN predictions for future months
- Cache results to avoid regeneration

---

**2.3 Enhanced Timeline with Uncertainty**

**User Value:** Medium-High - Better decision-making

**Implementation:**
- Show SDBW distribution as error bars or shaded regions
- Indicate high-uncertainty periods (ΔSDBW > 40 dB) with warning icon
- Display MUFday % alongside reliability

**Data Requirements:**
- Calculate SDBW90/50/10 in prediction engine
- Add uncertainty flagging logic

---

### Phase 3: Professional Tools (P2 - Power Users)

**3.1 Coverage Area Maps**

**User Value:** High - Visualize signal reach

**Implementation:**
- New "Coverage Maps" tab
- Generate REL or SDBW heatmap overlays on world map
- User selects: band, hour, metric (REL/SDBW)
- Contour lines or color-coded regions
- Export as PNG

**Data Requirements:**
- Grid-based predictions (e.g., 10° × 10° lat/lon grid)
- Substantial backend computation (consider caching)

---

**3.2 Antenna Comparison Tool**

**User Value:** High - Equipment decisions

**Implementation:**
- New "Antenna Comparison" under Band Details
- User defines antenna inventory with types/heights
- Side-by-side performance comparison
- Highlight reliability and signal strength differences

**Data Requirements:**
- Extend prediction engine to support multiple TX antenna configs
- Add antenna pattern library

---

**3.3 Contest Planner**

**User Value:** Medium-High - Competitive edge

**Implementation:**
- New "Planner" tab
- Select CQ/ITU zones or DXCC regions
- Display matrix: zones × hours with reliability colors
- Add signal power indicators (++, +, ●)
- Sunrise/sunset bars for TX/RX/midpoint

**Data Requirements:**
- Predictions to multiple representative locations per zone
- Zone → lat/lon mapping

---

### Phase 4: Specialist Features (P3-P4 - Nice to Have)

**4.1 QSO Window (Competitive Analysis)**

**User Value:** Medium - DXpedition chasers

**Implementation:**
- 5 user-placed markers representing competing stations
- Comparative SDBW/REL/SNR charts
- Identify optimal calling windows

**Data Requirements:**
- Multi-TX predictions to same RX

---

**4.2 Grayline Time Slider**

**User Value:** Medium - Interactive exploration

**Implementation:**
- Slider control below map
- Drag to move grayline terminator through 24 hours
- Update map shading in real-time

**Data Requirements:**
- Calculate terminator position from date/time
- SVG overlay on map

---

**4.3 ITU P.533 Comparison**

**User Value:** Medium - Standards compliance

**Implementation:**
- Add "ITU vs VOA" comparison mode
- Side-by-side charts or difference plots
- Highlight agreement/disagreement regions

**Data Requirements:**
- Integrate ITURHFProp or implement ITU P.533 method

---

**4.4 EME Calculator**

**User Value:** Low-Medium - Niche audience

**Implementation:**
- Simple calculator widget
- Input: TX/RX locations, date range
- Output: common moon windows, elevation, azimuth

**Data Requirements:**
- Moon ephemeris library (e.g., PyEphem)

---

## 6. Implementation Roadmap

### Timeline

**Week 1-2: Foundation (P0)**
- [ ] Implement propagation charts (all bands, REL/SDBW/MUFday)
- [ ] Add propagation wheel widget
- [ ] Create Best Frequency recommendation engine
- [ ] Build user parameter controls (Settings panel)
- [ ] Add localStorage persistence

**Week 3-4: Advanced Analysis (P1)**
- [ ] Implement SP/LP toggle with recalculation
- [ ] Generate all-year propagation matrix
- [ ] Enhance timeline with uncertainty indicators
- [ ] Add MUFday calculations throughout
- [ ] Create download/export functionality (PNG, CSV)

**Week 5-6: Professional Tools (P2)**
- [ ] Build coverage area maps generator
- [ ] Create antenna comparison tool
- [ ] Implement contest planner with zone selection
- [ ] Add take-off angle analysis
- [ ] Enhance mobile responsiveness for new charts

**Week 7+: Specialist Features (P3-P4)**
- [ ] QSO Window competitive analysis
- [ ] Grayline time slider
- [ ] ITU P.533 integration
- [ ] EME calculator
- [ ] Historical data comparison
- [ ] Multi-language support

### Technical Stack Recommendations

**Frontend Enhancements:**
- **Charting:** Plotly.js (interactive, responsive, PNG export built-in)
  - Alternative: Chart.js (lighter weight) or D3.js (maximum customization)
- **Circular Viz:** D3.js for propagation wheel
- **Maps:** Continue with Leaflet.js, add heatmap plugin for coverage maps
- **UI Framework:** Keep vanilla JS or consider Alpine.js for reactivity
- **Storage:** localStorage for user preferences, IndexedDB for cached predictions

**Backend Enhancements:**
- **Caching:** Redis or file-based caching for expensive calculations
- **Queue:** Celery for async prediction generation (all-year, coverage maps)
- **Database:** SQLite for historical data (optional)
- **API:** Extend Flask with additional endpoints for new analysis types

### Resource Requirements

**Development Time Estimates:**
- P0 Foundation: ~40-60 hours (2 weeks @ 20-30 hrs/week)
- P1 Advanced: ~40-60 hours (2 weeks)
- P2 Professional: ~60-80 hours (3-4 weeks)
- P3-P4 Specialist: ~40-60 hours (2-3 weeks)

**Total:** 180-260 hours (9-13 weeks)

**Compute Resources:**
- Coverage maps: Potentially intensive (100s of grid points × hours × bands)
- All-year matrix: 12× current prediction time
- Consider AWS Lambda or background processing for heavy tasks

---

## 7. Design Mockups & Wireframes

### 7.1 Enhanced Overview Tab

```
┌────────────────────────────────────────────────────────────────┐
│  📡 VE1ATM HF Propagation Monitor         [⚙️ Settings] [⚡ Refresh] │
├────────────────────────────────────────────────────────────────┤
│  SFI: 150   SSN: 100   Kp: 2   A: 10   Conditions: GOOD       │
├────────────────────────────────────────────────────────────────┤
│ [📊 Overview] [📻 Band Details] [⏰ Timeline] [🎯 DXCC]       │
├──────────────────────────┬─────────────────────────────────────┤
│                          │ 🌟 Best Bands Now (18:00 UTC)      │
│   🌍 Current Openings    │ 1. 20m - 85% REL, S8, 92% <MUF     │
│   [Interactive Map]      │ 2. 15m - 72% REL, S7, 78% <MUF     │
│   [Gray Line]            │ 3. 40m - 68% REL, S6, 88% <MUF     │
│                          ├─────────────────────────────────────┤
│   Legend:                │ 📊 Propagation Wheel                │
│   🟢 Good (>60%)         │        00                           │
│   🟡 Fair (30-60%)       │   23  ⬆️  01     [40m] [20m]       │
│   🔴 Poor (<30%)         │     ⭕️     [15m] [10m]             │
│                          │  22 │  🟢🟡│ 02    [Click band]     │
│                          │     │🟡🟢🔴│                         │
│   🌅 Grayline: [Slider]  │  21 │🔴🔴🟢│ 03    Updates live     │
│   ◀️━━━━━━●━━━━━━━━▶    │      ⭕️                            │
│   00:00      18:00 UTC   │   20    ⬇️   04                     │
│                          │        12                           │
├──────────────────────────┴─────────────────────────────────────┤
│ 🔔 NEEDED DXCC WORKABLE NOW: EU (20m, 15m), JA (20m)          │
└────────────────────────────────────────────────────────────────┘
```

### 7.2 New Propagation Charts Tab

```
┌────────────────────────────────────────────────────────────────┐
│ 📊 Propagation Charts                                          │
├────────────────────────────────────────────────────────────────┤
│ Band: [40m ▼] Region: [Europe ▼] Path: (•) SP  ( ) LP        │
├────────────────────────────────────────────────────────────────┤
│ REL (Reliability %)                                            │
│ 100┤                 ┌──────────┐                              │
│    ┤            ┌────┘          └────┐                         │
│  50┤     ┌──────┘                    └────────                 │
│    ┤─────┘                                                     │
│   0└┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴                                  │
│     0  2  4  6  8 10 12 14 16 18 20 22  UTC                   │
│                                                                │
│ SDBW (Signal Power dBW) ↔️ S-Meter                            │
│ S9┤                                                            │
│   ┤        ┌─────────────────┐    ░░ = SDBW90/SDBW10          │
│ S5┤    ┌───░░░░░░░░░░░░░░░░░░░───┐                            │
│   ┤────░░░░░░░░░░░░░░░░░░░░░░░░░░░───                         │
│ NF└┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴                                   │
│     0  2  4  6  8 10 12 14 16 18 20 22  UTC                   │
│                                                                │
│ MUFday (% below MUF)                                           │
│100┤                     ┌────────────────┐                     │
│   ┤            ┌────────┘                └─────                │
│ 50┤     ┌──────┘                                               │
│   ┤─────┘                                                      │
│  0└┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴┴                                   │
│     0  2  4  6  8 10 12 14 16 18 20 22  UTC                   │
│                                                                │
│ [🖼️ Save PNG] [📥 Export CSV] [🔍 Zoom] Hover for details    │
└────────────────────────────────────────────────────────────────┘
```

### 7.3 New Contest Planner Tab

```
┌────────────────────────────────────────────────────────────────┐
│ 🏆 Contest Planner                                             │
├────────────────────────────────────────────────────────────────┤
│ Target: [CQ Zones ▼]  Band: [20m ▼]  Month: [Nov 2024 ▼]     │
├────────────────────────────────────────────────────────────────┤
│ Zone│ 00 01 02 03 04 05 06 07 08 09 10 11 12 13 ... 23        │
│ ────┼─────────────────────────────────────────────────────────│
│ 03  │                                                          │
│ 04  │ ░░ ░░ ▓▓ ▓▓ ░░                                          │
│ 05  │             ░░ ▓▓ ██ ██ ▓▓ ░░                           │
│ 08  │         ░░ ░░ ▓▓ ██ ██ ██ ▓▓ ▓▓ ░░ ░░                  │
│ 14  │ ▓▓ ▓▓ ▓▓ ░░ ░░                 ░░ ░░ ▓▓ ▓▓ ██ ██       │
│ 15  │ ██ ██ ▓▓ ▓▓ ░░                     ░░ ░░ ▓▓ ██ ██ ██   │
│ 20  │ ░░ ░░ ░░ ░░ ░░ ▓▓ ▓▓ ██ ██ ▓▓ ░░ ░░                    │
│     │                                                          │
│ Legend: ░░ = 30-60%  ▓▓ = 60-80%  ██ = 80-100%               │
│ Signal: ++ = S9+  + = S6+  ● = S1+                           │
│                                                                │
│ Sunrise/Sunset (Zone 14):                                     │
│ TX  ███████░░░░░░░░░░░░░░░░░░░░░░░░░░░░███████                │
│ MP  ██████████░░░░░░░░░░░░░░░░░░███████████                   │
│ RX  ████████████████░░░░░░░░███████████████                   │
│                                                                │
│ [📥 Download Schedule]                                         │
└────────────────────────────────────────────────────────────────┘
```

### 7.4 Settings Panel Mockup

```
┌─────────────────────────────────────────┐
│ ⚙️  Prediction Settings               │
├─────────────────────────────────────────┤
│ ▼ Solar & Geomagnetic Activity          │
│   ◉ Automatic (current conditions)      │
│   ◯ Manual:                              │
│     SSN: [▓▓▓▓▓░░░░░] 150               │
│     SFI: [▓▓▓▓▓▓░░░░] 175               │
│     Kp:  [▓░░░░░░░░░] 2                 │
│                                          │
│ ▼ Propagation Model                     │
│   ◉ Auto (Method 30 - recommended)      │
│   ◯ Ray-Hop (paths <10,000 km)          │
│   ◯ Ducted (paths >10,000 km)           │
│                                          │
│ ▼ Receiver Noise Environment            │
│   Remote  Quiet  Residential  Noisy     │
│     ◯       ◉        ◯          ◯       │
│   (-164dB) (-153dB) (-143dB)  (-133dB)  │
│                                          │
│ ▼ Antenna Parameters                    │
│   Min Take-off Angle: [██░░] 3.0°       │
│   Required SNR:       [████] 10 dB      │
│                                          │
│ ▼ Analysis Options                      │
│   ☑ Include long-path predictions       │
│   ☑ Consider sporadic-E propagation     │
│   ☑ Show MUFday percentages             │
│   ☑ Display signal uncertainty zones    │
│                                          │
│ [Reset to Defaults]  [Cancel]  [Apply]  │
└─────────────────────────────────────────┘
```

---

## 8. Success Metrics

### User Engagement Metrics
- **Time on site:** Target 50% increase (baseline ~3 min → 4.5 min)
- **Feature adoption:** 60%+ of users utilize Prop Charts within 1 month
- **Return rate:** 20% increase in weekly active users

### Technical Performance Metrics
- **Page load time:** <2 seconds for dashboard
- **Chart rendering:** <500ms for all interactive charts
- **Prediction refresh:** <10 seconds for full 24-hour regeneration
- **Mobile usability:** 90%+ Lighthouse score

### Quality Metrics
- **User satisfaction:** >4.0/5.0 rating for new features (survey)
- **Bug rate:** <1 critical bug per 100 user sessions
- **Prediction accuracy:** Maintain current validation pass rate (83.8%)

---

## 9. Conclusion & Next Steps

This comprehensive design document provides a roadmap for transforming the DVOACAP-Python dashboard from a solid basic tool into a world-class HF propagation prediction platform. The recommendations are informed by extensive analysis of the VOACAP Online User's Manual and prioritized by user value and implementation complexity.

**Immediate Next Steps:**
1. ✅ Review this document with stakeholders
2. ⬜ Prioritize Phase 1 (P0) features for immediate implementation
3. ⬜ Set up development branch: `feature/dashboard-enhancements`
4. ⬜ Create detailed implementation tickets for each P0 feature
5. ⬜ Begin Week 1-2 development sprint (Propagation Charts + Prop Wheel)

**Success Criteria:**
- Complete P0 features within 2 weeks
- Achieve 90%+ user satisfaction on beta testing
- Maintain or improve prediction accuracy (>80% validation pass rate)
- Zero performance regressions on mobile devices

**Risk Mitigation:**
- **Performance:** Implement progressive loading, lazy rendering for charts
- **Complexity:** Start with core features, iterate based on user feedback
- **Maintenance:** Document all new components, write tests for critical paths
- **Compatibility:** Test on major browsers (Chrome, Firefox, Safari, Edge)

---

**Document Version:** 1.0
**Last Updated:** 2025-11-14
**Author:** Claude (Anthropic) for DVOACAP-Python Project
**Review Status:** Ready for Stakeholder Review

**Appendices:**
- Appendix A: VOACAP Online Feature Comparison Matrix
- Appendix B: User Interview Findings (if available)
- Appendix C: Technical Architecture Diagrams
- Appendix D: API Specifications for New Endpoints

---

END OF DOCUMENT
