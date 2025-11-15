# Coverage Heat Map UI Mockups

This directory contains three interactive mockup variants for the VOACAP coverage map visualization.

## Quick Start

Open each mockup in your web browser to compare them:
- `mockup_v1_regions.html` - Region block visualization
- `mockup_v2_heatmap.html` - Smooth heat map visualization
- `mockup_v3_hybrid.html` - Hybrid: heat map + light region boundaries

## Common Features (All Versions)

All three mockups implement the following features:

### 1. **TX Power Options**
- 5W, 25W, 50W, 100W, 500W, 1000W, 1500W
- Default: 100W

### 2. **Frequency Display Format**
- Format B: Implied MHz (e.g., "14.074" instead of "14.074 MHz")
- Cleaner display, less visual clutter

### 3. **Mode-Specific Calling Frequencies**
When you select a mode (FT8, FT4, SSB, CW), the frequency automatically updates to the standard calling frequency for that mode on the selected band.

**Examples:**
- 20m FT8: 14.074
- 20m SSB: 14.200
- 40m FT8: 7.074
- 30m CW: 10.120 (30m is CW/Digital only, SSB disabled)

### 4. **Interactive Controls**
- **Band Selection:** 40m, 30m, 20m, 17m, 15m, 12m, 10m
- **Mode Selection:** FT8, FT4, SSB, CW
- **TX Power:** 5W to 1500W
- **Time Offset:** Now, +3h, +6h, +12h, +24h (for propagation forecasting)

### 5. **DXCC Entity Tracking**
- Red pins: Needed DXCC entities with current propagation
- Gray pins: Needed DXCC entities without current propagation
- Click pins for detailed popup information

### 6. **Quick Summary Bar**
Real-time summary showing:
- Current UTC time
- Best current opportunity (band/region/frequency/signal)
- DXCC opportunity (needed entities currently workable)
- Next major band opening

---

## Version Comparisons

### V1: Region Blocks (`mockup_v1_regions.html`)

**Visualization Style:**
- Discrete colored regions (EU, AS, JA, SA, AF, OC)
- Solid fill colors indicating propagation quality
- Clear region boundaries

**Advantages:**
✅ Easy to understand at a glance
✅ Clear regional distinctions
✅ Works well for quick "what regions are open?" assessment
✅ Lower computational requirements
✅ Clean visual separation between regions

**Disadvantages:**
❌ Less granular detail within regions
❌ Doesn't show gradual propagation changes
❌ Can't see "hotspots" within regions

**Best For:**
- Users who want quick regional overview
- Lower-end devices
- Simple decision-making ("Can I work EU right now?")

---

### V2: Smooth Heat Map (`mockup_v2_heatmap.html`)

**Visualization Style:**
- Continuous heat map gradient
- Smooth color transitions showing signal strength
- No discrete region boundaries
- Uses Leaflet.heat plugin

**Advantages:**
✅ Shows detailed propagation gradients
✅ Identifies "hotspots" with best propagation
✅ Beautiful, modern visualization
✅ More accurate representation of real-world propagation
✅ Shows transition zones clearly

**Disadvantages:**
❌ Can be harder to read at first glance
❌ Higher computational requirements
❌ May be "too much information" for quick checks
❌ Regional names not immediately obvious

**Best For:**
- Users who want maximum detail
- Identifying optimal beam headings
- Understanding propagation nuances
- Modern devices with good GPU

---

### V3: Hybrid (`mockup_v3_hybrid.html`)

**Visualization Style:**
- Smooth heat map (like V2)
- PLUS light dashed region boundaries
- Best of both worlds approach

**Advantages:**
✅ Detailed heat map visualization
✅ Regional context from boundaries
✅ Easy to see both gradients AND regions
✅ Tooltips on regions provide summary info
✅ Balances detail with usability

**Disadvantages:**
❌ Slightly more visual complexity
❌ Boundaries might clutter for some users
❌ Higher computational requirements (same as V2)

**Best For:**
- Users who want both detail AND context
- Best overall compromise
- Users transitioning from region-based to heat map
- Most versatile for different use cases

---

## Technical Implementation Notes

### Heat Map Grid Resolution

The current mockups use simulated data points. For production implementation:

**Option A: Smooth Iso-Areas (Preferred)**
- Generate VOACAP predictions on a fine grid (e.g., 2° x 2° lat/lon)
- Use Leaflet.heat to render smooth gradients
- Computationally intensive but provides best visualization

**Option B: 4-Character Maidenhead Grid (Fallback)**
- If computation is prohibitive, use 4-char maidenhead (roughly 1° x 2°)
- Faster computation
- Still provides good granularity
- Example: FN74, FN84, FN85, etc.

**Decision Logic:**
```
IF (grid_size <= reasonable_compute_time):
    use smooth iso-areas (Option A)
ELSE:
    use 4-char maidenhead (Option B)
```

### Data Format

All mockups expect propagation data in this structure:
```javascript
{
    band: '20m',
    mode: 'FT8',
    power: 100,
    time_offset: 0,
    grid_data: [
        { lat: 45.2, lon: -64.3, reliability: 85, snr: 15, signal: 'S9+10' },
        // ... more grid points
    ]
}
```

### Color Scale

All versions use the same color gradient:
- **Closed** (0-30%): Gray `rgba(138, 155, 181, 0.3)`
- **Poor** (30-45%): Red `rgba(248, 113, 113, 0.6)`
- **Fair** (45-70%): Yellow `rgba(251, 191, 36, 0.6)`
- **Good** (70-100%): Green `rgba(74, 222, 128, 0.6)`

---

## Recommendations

Based on the design requirements, here are my recommendations:

### For Initial Release: **V3 Hybrid**
**Reasoning:**
- Provides detailed heat map for power users
- Includes regional context for newcomers
- Most versatile for different user needs
- Can be simplified to V1 or V2 by toggling layer visibility

### For Performance-Constrained Scenarios: **V1 Region Blocks**
**Reasoning:**
- Lower computational overhead
- Works well on older devices
- Faster data processing
- Good enough for most use cases

### For Advanced Users: **V2 Smooth Heat Map**
**Reasoning:**
- Maximum detail and accuracy
- Best for optimizing antenna headings
- Professional appearance
- Preferred by experienced operators

---

## Next Steps

1. **User Testing:** Show all three mockups to representative users
2. **Performance Testing:** Benchmark computational requirements for each
3. **Data Integration:** Connect to actual VOACAP prediction engine
4. **Implement Fallback:** Add automatic switching between smooth/maidenhead based on compute time
5. **Add Layer Toggle:** Allow users to switch between V1/V2/V3 in settings

---

## Files

- `mockup_v1_regions.html` - Region block visualization mockup
- `mockup_v2_heatmap.html` - Smooth heat map mockup
- `mockup_v3_hybrid.html` - Hybrid visualization mockup
- `MOCKUPS_README.md` - This documentation

## Questions?

These are interactive prototypes. Open them in a web browser and experiment with the controls to get a feel for each approach.
