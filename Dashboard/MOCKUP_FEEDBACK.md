# Dashboard Mockup Feedback & Design Updates
**Date:** 2025-11-15
**Session:** claude/voacap-coverage-maps-ui-013e3gQxJgkr2d3adu2ojJrE

## User Feedback Summary

### ✅ Approved Features
- Radio button controls (Band/Mode/Time)
- DXCC entity pins (one per entity, tooltip to identify)
- Overall layout concept

### 🔄 Requested Changes

#### 1. Heat Map Visualization
**Request:** Replace coarse region blocks with fine-grained heat map

**Current Design:** 10 large region polygons (EU, AS, SA, etc.) colored uniformly

**New Design:** Grid-based heat map
- **Grid resolution:** 10° x 10° lat/lon squares (36 x 18 = 648 cells globally)
- **Alternative:** 5° x 5° for more detail (72 x 36 = 2,592 cells)
- **Color gradient:**
  - Dark green → Light green → Yellow → Orange → Red → Dark gray
  - Represents: Excellent → Good → Fair → Poor → Very Poor → Closed

**Implementation:**
```javascript
// Generate heat map grid
const heatMapGrid = [];
for (let lat = -90; lat < 90; lat += 10) {
    for (let lon = -180; lon < 180; lon += 10) {
        const prediction = voacap.getPrediction(lat, lon, band, mode);
        heatMapGrid.push({
            bounds: [[lat, lon], [lat+10, lon+10]],
            snr: prediction.snr,
            signal: prediction.signal,
            color: getColorFromSNR(prediction.snr, mode)
        });
    }
}
```

**Rendering:**
- Use Leaflet rectangle layers for each grid cell
- Opacity: 0.6 (semi-transparent to see map underneath)
- Update on band/mode/time change

**Data source:**
- VOACAP can generate predictions for specific lat/lon points
- Pre-calculate grid for all 7 bands for current hour
- Store in `enhanced_predictions.json` or separate grid file

---

#### 2. TX Power Selector
**Request:** Add transmit power control

**Design:**
```
TX Power: ○ 5W (QRP)  ⦿ 100W  ○ 500W  ○ 1500W
```

**Impact:**
- Changes SNR calculations (higher power = better SNR)
- Formula: `SNR_new = SNR_base + 10*log10(P_new/P_base)`
- Example: 5W → 100W = +13 dB improvement

**Implementation:**
- Add to control panel (after Mode selector)
- Default: 100W (typical ham transceiver)
- Recalculate heat map colors on change
- Update Quick Summary with power level

**Phase:** Phase 2

---

#### 3. Best Frequency Within Band
**Request:** Show optimal frequency (not just band number)

**Current:** "20m is open"
**New:** "14.074 MHz (FT8) is best"

**Data Source:** VOACAP provides:
- **FOT (Frequency of Optimum Traffic):** Best frequency for the path
- **MUF (Maximum Usable Frequency):** Highest usable frequency
- **LUF (Lowest Usable Frequency):** Lowest usable frequency

**Implementation:**

1. **For each DXCC entity tooltip:**
   ```
   VP8 (Falkland Islands)
   Best: 14.074 MHz (FT8)
   Signal: S9 (+15 dB SNR)
   MUF: 18.2 MHz | FOT: 14.1 MHz
   Distance: 8,420 km | Bearing: 180°
   ```

2. **For Quick Summary:**
   ```
   BEST: 14.074 → JA: S9+20 (FT8, 100W)
   ```

3. **For heat map grid tooltips:**
   ```
   35°N, 139°E (Tokyo area)
   Best: 14.074 MHz (FT8)
   Signal: S9+20 (+22 dB SNR)
   Reliability: 95%
   ```

**Mode-Specific Frequencies:**
- FT8: Use WSJT-X calling frequencies (14.074, 21.074, etc.)
- SSB: Use band center (14.200, 21.300, etc.)
- CW: Use CW portion (14.050, 21.050, etc.)
- Show FOT if within band limits

**Phase:** Phase 1-2

---

#### 4. Future Selector: Antenna Type
**Request:** Add antenna pattern selector for later phases

**Proposed Design:**
```
Antenna: ⦿ Dipole  ○ Yagi (3-el)  ○ Vertical  ○ NVIS  ○ Custom
```

**Impact:**
- Changes takeoff angle and gain
- VOACAP supports different antenna files (.ant)
- Dipole: 0 dBi gain, omnidirectional
- Yagi: +7 dBi gain, directional
- Vertical: -3 dBi gain, low angle
- NVIS: High angle (for short skip)

**Implementation:**
- Requires running VOACAP with different antenna files
- Significant computation (may need server-side caching)
- Or: Apply gain correction to existing predictions

**Phase:** Phase 4 (Advanced)

---

## Updated Control Panel Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 📡 VE1ATM HF Propagation Monitor                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│ Band:     ⦿ 40m  ○ 30m  ○ 20m  ○ 17m  ○ 15m  ○ 12m  ○ 10m                │
│ Mode:     ⦿ FT8  ○ SSB  ○ CW                                               │
│ TX Power: ○ 5W   ⦿ 100W  ○ 500W  ○ 1500W                                   │
│ Time:     ⦿ Now  ○ +3h  ○ +6h  ○ +12h  ○ +24h  ○ +48h  ○ +72h             │
│ Layer:    ⦿ Signal  ○ Reliability  ○ SNR  │  [Future: ○ Antenna: Dipole]  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Heat Map Color Scheme

### SNR-Based Gradient (for FT8 mode example)

| SNR Range | S-Meter | Color | Status |
|-----------|---------|-------|--------|
| +20 dB and above | S9+30 | `#00ff00` (Bright Green) | EXCELLENT |
| +10 to +20 dB | S9+10 to S9+20 | `#66ff66` (Light Green) | VERY GOOD |
| 0 to +10 dB | S9 to S9+10 | `#99ff99` (Pale Green) | GOOD |
| -5 to 0 dB | S7 to S9 | `#ffff00` (Yellow) | FAIR |
| -10 to -5 dB | S5 to S7 | `#ffaa00` (Orange) | MARGINAL |
| -15 to -10 dB | S3 to S5 | `#ff5500` (Dark Orange) | POOR |
| -20 to -15 dB | S1 to S3 | `#ff0000` (Red) | VERY POOR |
| Below -20 dB | <S1 | `#666666` (Gray) | CLOSED |

**Mode Adjustments:**
- **SSB:** Shift thresholds up by +20 dB (SSB needs stronger signal)
- **CW:** Shift thresholds up by +13 dB (CW between FT8 and SSB)

---

## Heat Map Data Structure

### Option 1: Pre-calculated Grid (Recommended)
Store grid data in JSON:

```json
{
    "timestamp": "2025-11-15T00:45:00Z",
    "bands": {
        "20m": {
            "grid": [
                {
                    "lat": -90,
                    "lon": -180,
                    "snr": -25,
                    "signal_dbw": -150,
                    "reliability": 10,
                    "fot_mhz": 0,
                    "muf_mhz": 0
                },
                {
                    "lat": -90,
                    "lon": -170,
                    "snr": -25,
                    "signal_dbw": -148,
                    "reliability": 12,
                    "fot_mhz": 0,
                    "muf_mhz": 0
                },
                // ... 646 more cells
            ]
        }
    }
}
```

**File size estimate:**
- 648 cells x 7 bands x 50 bytes = ~230 KB per hour
- 72 hours = ~16 MB (acceptable for modern web)
- Or: Only store current + next 24 hours = ~5.5 MB

### Option 2: On-the-Fly Calculation
- Use VOACAP Python API to calculate grid point predictions
- Slower (1-2 seconds per band change)
- Lower storage footprint

**Recommendation:** Option 1 (pre-calculated) for better UX

---

## DXCC Pin Enhancements

### Tooltip Content (Enhanced)
```
┌─────────────────────────────────┐
│ VP8 (Falkland Islands)          │
│ ─────────────────────────────── │
│ Status: NEEDED (Open Now!)      │
│                                  │
│ Best Freq: 14.074 MHz (FT8)     │
│ Signal: S9 (+15 dB SNR)         │
│ Reliability: 85%                │
│                                  │
│ MUF: 18.2 MHz | FOT: 14.1 MHz   │
│ Distance: 8,420 km              │
│ Bearing: 180° (South)           │
│                                  │
│ Click for more details          │
└─────────────────────────────────┘
```

### Popup Content (On Click)
```
┌──────────────────────────────────────┐
│ 🏴 VP8 - Falkland Islands           │
│ ────────────────────────────────── │
│ Status: ⚠️ NEEDED (Not Worked)      │
│ Worked: 0 QSOs | Confirmed: 0      │
│                                      │
│ PROPAGATION RIGHT NOW (0045 UTC)    │
│ ─────────────────────────────────  │
│ 20m: 14.074 MHz - S9 (OPEN)        │
│ 17m: 18.100 MHz - S5 (MARGINAL)    │
│ 15m: CLOSED                         │
│                                      │
│ Best Band: 20m FT8 at 14.074 MHz   │
│ SNR: +15 dB (Excellent!)            │
│ Reliability: 85%                    │
│                                      │
│ NEXT 6 HOURS                        │
│ ─────────────────────────────────  │
│ 0200 UTC: 20m improves to S9+10    │
│ 0400 UTC: 40m opens (S7)           │
│                                      │
│ PATH INFO                           │
│ ─────────────────────────────────  │
│ Distance: 8,420 km                  │
│ Bearing: 180° (South)               │
│ Sunrise: 0845 UTC                   │
│ Sunset: 2315 UTC                    │
│                                      │
│ [QRZ.com] [DXWatch] [Close]        │
└──────────────────────────────────────┘
```

---

## Updated Quick Summary Bar

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 🎯 RIGHT NOW (0045 UTC, 100W, Dipole)                                       │
│ ─────────────────────────────────────────────────────────────────────────── │
│ BEST: 14.074 MHz → JA: S9+20 (FT8, 95% reliable)                           │
│ DXCC: VP8 open on 14.074 MHz (S9) | EA8 on 14.074 MHz (S7)                │
│ NEXT: 40m→EU opens 0200 UTC on 7.074 MHz                                   │
│                                                     [Hover regions for info]│
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Priority Updates

### Phase 1: Critical Fixes (Week 1) - UPDATED
1. ✅ Fix 72-hour forecast bug
2. ✅ Add mode selection UI (FT8/SSB/CW)
3. ✅ Implement mode-specific SNR thresholds
4. ✅ Add tooltips on map hover
5. **NEW:** Add TX power selector (5W/100W/500W/1500W)
6. **NEW:** Show best frequency in tooltips (FOT from VOACAP)

**Total:** ~18 hours (was 13 hours)

### Phase 2: Heat Map Visualization (Week 2-3) - UPDATED
1. ✅ Restructure layout to 80/20
2. ✅ Add band selection radio buttons
3. **CHANGED:** Implement heat map grid (10° x 10° cells) instead of region polygons
4. **NEW:** Pre-calculate grid data for all bands
5. ✅ Improve Quick Summary
6. **NEW:** Add frequency display (14.074 MHz format)

**Total:** ~28 hours (was 22 hours)

### Phase 3: DXCC Map Integration (Week 4)
1. ✅ Create DXCC GeoJSON layer
2. ✅ Add DXCC filtering controls
3. ✅ DXCC entity popups
4. **NEW:** Enhanced tooltips with FOT/MUF
5. **NEW:** Multi-band propagation in popup

**Total:** ~18 hours (was 15 hours)

### Phase 4: Advanced Features (Week 5-6)
1. Maidenhead grid overlay (optional toggle)
2. Time window selector
3. **NEW:** Antenna type selector (Dipole/Yagi/Vertical/NVIS)
4. **NEW:** Animation mode (show propagation changes over time)

**Total:** ~24 hours (was 18 hours)

---

## Technical Implementation Notes

### Heat Map Grid Generation

**Python script: `generate_heatmap_grid.py`**

```python
import voacap
import json

def generate_heat_map(band, hour_utc, tx_power_watts=100, grid_size=10):
    """
    Generate heat map grid for a given band and time.

    Args:
        band: '20m', '40m', etc.
        hour_utc: 0-23
        tx_power_watts: 5, 100, 500, or 1500
        grid_size: degrees (10 or 5)

    Returns:
        List of grid cells with SNR/signal/reliability
    """
    grid = []
    home_lat, home_lon = 44.651070, -63.582687  # VE1ATM

    for lat in range(-90, 90, grid_size):
        for lon in range(-180, 180, grid_size):
            # Run VOACAP prediction from home to this grid cell
            result = voacap.predict(
                tx_lat=home_lat,
                tx_lon=home_lon,
                rx_lat=lat + grid_size/2,  # Center of cell
                rx_lon=lon + grid_size/2,
                freq_mhz=band_to_freq(band),
                hour=hour_utc,
                power_watts=tx_power_watts
            )

            grid.append({
                'lat': lat,
                'lon': lon,
                'snr': result.snr,
                'signal_dbw': result.signal,
                'reliability': result.reliability,
                'fot_mhz': result.fot,
                'muf_mhz': result.muf
            })

    return grid
```

### JavaScript Heat Map Rendering

```javascript
function renderHeatMap(gridData, mode, txPower) {
    // Clear existing heat map
    heatMapLayer.clearLayers();

    gridData.forEach(cell => {
        const color = getColorFromSNR(cell.snr, mode);
        const rectangle = L.rectangle(
            [[cell.lat, cell.lon], [cell.lat + 10, cell.lon + 10]],
            {
                color: color,
                fillColor: color,
                fillOpacity: 0.6,
                weight: 0
            }
        );

        // Tooltip on hover
        rectangle.bindTooltip(`
            <strong>${cell.lat}°N, ${cell.lon}°E</strong><br>
            Best: ${cell.fot_mhz.toFixed(3)} MHz (${mode})<br>
            Signal: ${snrToSMeter(cell.snr)}<br>
            SNR: ${cell.snr > 0 ? '+' : ''}${cell.snr.toFixed(1)} dB<br>
            Reliability: ${cell.reliability}%
        `, { sticky: true });

        heatMapLayer.addLayer(rectangle);
    });
}
```

---

## Questions for Next Iteration

1. **Heat map grid size:** 10° x 10° (648 cells) or 5° x 5° (2,592 cells)?
   - 10° is faster, 5° is more detailed

2. **TX Power default:** 100W typical, but should we offer 25W and 50W options too?

3. **Frequency display format:**
   - A) "14.074 MHz" (precise)
   - B) "14.074" (implied MHz)
   - C) "14074 kHz" (alternative unit)

4. **Heat map vs region overlay:** Should we keep region boundaries visible (light lines) over the heat map?

5. **Animation:** Would you want a "play" button to animate propagation changes over 24 hours?

---

## Summary of Changes from Original Mockup

| Feature | Original Design | Updated Design |
|---------|----------------|----------------|
| Visualization | 10 region polygons | 648-cell heat map grid |
| TX Power | Fixed 100W | Selectable (5W/100W/500W/1500W) |
| Frequency display | Band only ("20m") | Specific freq ("14.074 MHz") |
| DXCC tooltips | Basic info | FOT, MUF, multi-band, forecast |
| Quick Summary | Band-level | Frequency-level |
| Antenna | Fixed dipole | Future: selectable type |

---

**Next Steps:**
1. User approval of heat map approach
2. Confirm grid size (10° vs 5°)
3. Begin Phase 1 implementation

**Status:** Awaiting user feedback
