# Coverage Heat Map UI Mockups

This directory contains four interactive mockup variants for the VOACAP coverage map visualization.

## ⭐ RECOMMENDED: V4 - Maidenhead Grid-Based Visualization

**`mockup_v4_maidenhead_grid.html`** - This is the correct approach for VOACAP propagation visualization.

Unlike the other mockups that overlay propagation on geographic regions, V4 implements a **pure grid-based approach** where:
- Each Maidenhead 4-character grid square (e.g., FN20, IO91) is calculated independently
- Propagation is calculated from TX location to each grid center
- Each grid is colored based on likelihood of communications
- Completely independent of geographic/political boundaries
- Global coverage using standardized amateur radio grid system

## Other Mockups (For Comparison)

Open each mockup in your web browser to compare approaches:
- `mockup_v1_regions.html` - Region block visualization (deprecated approach)
- `mockup_v2_heatmap.html` - Smooth heat map visualization (deprecated approach)
- `mockup_v3_hybrid.html` - Hybrid: heat map + light region boundaries (deprecated approach)
- `mockup_v4_maidenhead_grid.html` - **RECOMMENDED** Maidenhead grid-based visualization

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

### V4: Maidenhead Grid ⭐ RECOMMENDED (`mockup_v4_maidenhead_grid.html`)

**Visualization Style:**
- Pure grid-based visualization using Maidenhead locator system
- Each 4-character grid square (e.g., FN20, IO91) displayed as colored rectangle
- Grid size: ~1° latitude × 2° longitude (~111km × 222km at equator)
- Propagation calculated independently for each grid center
- No geographic or political boundaries

**Advantages:**
✅ **Scientifically accurate** - Shows actual propagation calculations, not geographic approximations
✅ **Amateur radio standard** - Uses familiar Maidenhead grid system
✅ **Globally consistent** - Equal treatment of all geographic areas
✅ **Detailed and granular** - ~3,240 grid squares covering the globe
✅ **Independent calculations** - Each grid's propagation computed separately
✅ **Easy to understand** - Click any grid to see detailed propagation data
✅ **No geographic bias** - Pure RF propagation, not influenced by political boundaries
✅ **Optimal for antenna planning** - See exactly which grids are workable

**Disadvantages:**
❌ Visual grid lines may look "busy" at first (but this is the reality of RF propagation)
❌ Requires calculation for each grid (but this is the correct approach)

**Best For:**
- **Production implementation** - This is the correct approach for VOACAP
- Users who want accurate propagation predictions
- Planning DX contacts by grid square
- Understanding real RF propagation patterns
- Amateur radio operators familiar with Maidenhead grids

**Why This Is The Correct Approach:**

The previous mockups (V1-V3) incorrectly tied propagation visualization to geographic regions (EU, AS, JA, etc.). This doesn't match how radio propagation actually works.

**Radio waves don't know about continents or political boundaries.** They follow physics:
- Ionospheric conditions vary by location (grid-based, not region-based)
- Propagation is calculated point-to-point (TX → each grid center)
- Different grids within the same continent can have vastly different propagation
- The Maidenhead locator system is the standard for amateur radio location reporting

**V4 correctly implements this by:**
1. Dividing the globe into Maidenhead 4-character grid squares
2. Calculating propagation from TX location to each grid's center point
3. Coloring each grid based on its calculated likelihood of communications
4. Showing results independent of geographic features

**Example:** From Halifax (FN44), you might have:
- **Good** propagation to IO91 (London) - 70% likelihood
- **Fair** propagation to JO01 (Netherlands) - 55% likelihood
- **Poor** propagation to IN88 (Sicily) - 35% likelihood
- **Closed** to IO80 (Portugal) - 15% likelihood

All four grids are in "Europe," but each has different propagation characteristics based on distance, path, and ionospheric conditions.

---

## Technical Implementation Notes

### Grid Resolution and Implementation

**RECOMMENDED: 4-Character Maidenhead Grid (V4)**
- Use Maidenhead 4-char grid system (roughly 1° lat × 2° lon)
- Scientifically accurate and follows amateur radio standards
- ~3,240 grid squares globally
- Each grid calculated independently
- Standard grid: FN20, FN21, IO91, JO01, etc.

**Alternative: Smooth Iso-Areas (V2/V3)**
- Generate VOACAP predictions on fine grid, interpolate
- Use Leaflet.heat to render smooth gradients
- Computationally intensive
- Less accurate - obscures actual grid-based calculations
- **Not recommended** - ties visualization to geography instead of RF physics

**Production Implementation:**
```javascript
// Calculate propagation for each Maidenhead grid
grids = generateGlobalMaidenheadGrids(4); // 4-character grids
grids.forEach(grid => {
    center = grid.getCenter();
    propagation = voacap.calculate(txLocation, center, band, mode, power, time);
    grid.color = getColorForReliability(propagation.reliability);
    grid.display();
});
```

### Data Format

**V4 Maidenhead Grid Format (RECOMMENDED):**
```javascript
{
    band: '20m',
    mode: 'FT8',
    power: 100,
    time_offset: 0,
    tx_location: { grid: 'FN44', lat: 44.6488, lon: -63.5752 },
    grid_data: [
        {
            grid: 'IO91',
            center: { lat: 51.5, lon: -0.5 },
            reliability: 85, // 0-100%
            snr: 15,         // dB
            signal: 'S9+10', // S-meter
            distance: 4850,  // km
            bearing: 45      // degrees
        },
        { grid: 'JO01', center: { lat: 50.5, lon: 5.5 }, reliability: 72, ... },
        // ... ~3,240 more grids
    ]
}
```

**Legacy Format (V1-V3):**
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

### ⭐ PRODUCTION IMPLEMENTATION: V4 Maidenhead Grid

**This is the correct approach for VOACAP propagation visualization.**

**Reasoning:**
- ✅ **Scientifically accurate** - Calculates propagation per grid, not per region
- ✅ **Amateur radio standard** - Uses industry-standard Maidenhead locator system
- ✅ **Independent calculations** - Each of ~3,240 grids calculated separately
- ✅ **No geographic bias** - Pure RF propagation physics
- ✅ **Global coverage** - Consistent grid-based approach worldwide
- ✅ **Optimal granularity** - 1° × 2° grids provide excellent detail without overwhelming computation
- ✅ **Familiar to users** - Hams already use Maidenhead grids for QSOs

**Implementation Priority:**
1. **Primary:** V4 Maidenhead Grid-Based (mockup_v4_maidenhead_grid.html)
2. **Legacy/Comparison Only:** V1-V3 (for user reference, but not recommended)

### Why NOT V1-V3?

**V1 (Region Blocks):**
- ❌ Ties propagation to arbitrary geographic regions
- ❌ Assumes all of "Europe" has same propagation (incorrect)
- ❌ Doesn't match how VOACAP calculations work

**V2 (Smooth Heat Map):**
- ❌ Interpolates/smooths data, obscuring actual grid calculations
- ❌ Visually appealing but scientifically less accurate
- ❌ Doesn't show the discrete nature of grid-based propagation

**V3 (Hybrid):**
- ❌ Combines the problems of V1 and V2
- ❌ Geographic boundaries mislead users about propagation paths

**The fundamental issue:** V1-V3 overlay propagation on geography. V4 correctly shows propagation independent of geography.

---

## Next Steps

1. **Production Implementation:** Build V4 with actual VOACAP integration
   - Calculate propagation for each Maidenhead 4-character grid
   - Store results in grid-based format
   - Render colored rectangles for each grid

2. **Maidenhead Grid Library:** Create reusable functions
   - `latLonToMaidenhead(lat, lon, precision)` - Convert coordinates to grid
   - `maidenheadToBounds(grid)` - Get grid boundary coordinates
   - `generateGlobalGrids(precision)` - Generate all global grids

3. **VOACAP Integration:** Connect calculation engine
   - Input: TX location, RX grid center, band, mode, power, time
   - Output: reliability, SNR, signal strength, path details
   - Batch calculation for all ~3,240 grids

4. **Performance Optimization:**
   - Cache calculations by parameter combination
   - Only recalculate changed parameters
   - Progressive rendering for large grid sets

5. **User Features:**
   - Click grid to see detailed propagation path
   - Export grid data to CSV for analysis
   - Compare different times side-by-side
   - Highlight "needed" DXCC grids

---

## Files

- `mockup_v4_maidenhead_grid.html` - ⭐ **RECOMMENDED** Maidenhead grid-based visualization
- `mockup_v1_regions.html` - Legacy: Region block visualization (deprecated)
- `mockup_v2_heatmap.html` - Legacy: Smooth heat map (deprecated)
- `mockup_v3_hybrid.html` - Legacy: Hybrid visualization (deprecated)
- `MOCKUPS_README.md` - This documentation

## Questions?

**Start with V4:** Open `mockup_v4_maidenhead_grid.html` in your web browser to see the correct Maidenhead grid-based approach. This is what the production implementation should look like.

The other mockups (V1-V3) are provided for comparison only, to understand why the grid-based approach is superior to geographic region visualization.
