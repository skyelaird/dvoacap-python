# Propagation Maps Guide

**VOACAP-Style Coverage Maps with Maidenhead Grid Overlay**

---

## Overview

The Propagation Maps feature provides VOACAP-compatible signal strength and reliability predictions visualized on an interactive map with Maidenhead grid square alignment.

**What You Get:**
- **Reliability (REL) Maps** - Circuit reliability percentage (0-100%)
- **Signal Strength (SDBW) Maps** - Signal-to-noise ratio in dB
- **Maidenhead Grid Alignment** - Perfect for amateur radio operators
- **Interactive Display** - Click grid squares for detailed predictions
- **Mode-Specific Predictions** - WSPR, FT8, CW, SSB presets
- **Space-Efficient Design** - Fullscreen map interface

---

## Features

### Two Map Types

**1. Reliability (REL) Maps**
Shows circuit reliability percentage based on signal fading statistics and required SNR threshold.

**Color Scale:**
- 🔴 Red (90-100%): Excellent propagation
- 🟠 Orange (70-90%): Good propagation
- 🟡 Yellow (50-70%): Fair propagation
- 🟢 Green (30-50%): Marginal propagation
- 🔵 Blue (10-30%): Poor propagation
- ⚪ Gray (0-10%): Unlikely propagation

**2. Signal Strength (SDBW) Maps**
Shows signal-to-noise ratio in decibels.

**Color Scale:**
- 🔴 Red (>40 dB): S9+ signals
- 🟠 Orange (30-40 dB): S9 signals
- 🟡 Yellow (20-30 dB): S7 signals
- 🟢 Green (10-20 dB): S5 signals
- 🔵 Blue (0-10 dB): S3 signals
- ⚪ Gray (<0 dB): Weak signals

### Mode Presets

Automatic configuration for common amateur radio modes:

| Mode | Bandwidth | Required SNR | VOACAP Match |
|------|-----------|--------------|--------------|
| **WSPR** | 6 Hz | -28 dB | 3 dB/Hz ✓ |
| **FT8** | 50 Hz | -21 dB | 19 dB/Hz ✓ |
| **CW** | 500 Hz | +6 dB | 13 dB/Hz ✓ |
| **SSB** | 2700 Hz | +10 dB | 38 dB/Hz ✓ |

These match VOACAP's bandwidth specifications exactly for accurate predictions.

---

## Quick Start

### 1. Generate Map Data

```bash
cd Dashboard
python generate_propagation_maps.py
```

This creates map files in `Dashboard/propagation_maps/`:
```
map_20m_SSB_1800Z.json
map_20m_FT8_1800Z.json
map_40m_FT8_0000Z.json
map_15m_FT8_1800Z.json
```

**First Generation Time:** ~5-10 minutes per map (25,000+ grid points)

### 2. View Maps

**Option A: Via Dashboard Server**
```bash
cd Dashboard
python server.py
```
Then open: `http://localhost:8000/propagation_maps.html`

**Option B: Direct File Access**
Open `Dashboard/propagation_maps.html` directly in your browser.

### 3. Interact with Maps

**Controls:**
- **Band Selection:** 40m, 20m, 17m, 15m, 10m
- **Mode Selection:** WSPR, FT8, CW, SSB
- **Display Toggle:** Reliability ↔ Signal Strength
- **Time Selection:** Hourly UTC (0-23)
- **Refresh:** Generate new predictions

**Click any grid square** for detailed popup:
```
Grid: FN74
Distance: 4,689 km
SNR: 26.2 dB
Reliability: 82.9%
Mode: 2F2 (2 hops)
```

---

## Using Programmatically

### Generate Custom Maps

```python
from Dashboard.generate_propagation_maps import generate_propagation_map

# Your station
TX_LAT = 44.374
TX_LON = -64.300

# Generate map
map_data = generate_propagation_map(
    tx_lat=TX_LAT,
    tx_lon=TX_LON,
    frequency=14.074,      # 20m FT8
    mode='FT8',
    utc_hour=18,
    month=11,
    ssn=77,
    tx_power=80.0,
    map_range_deg=60.0,    # ±60° coverage
    resolution='medium'     # 2° x 1° grid squares
)

# Access predictions
for pred in map_data['predictions']:
    print(f"{pred['grid']}: SNR={pred['snr_db']:.1f} dB, "
          f"REL={pred['reliability']:.1f}%")
```

### Apply Mode Presets

```python
from src.dvoacap.prediction_engine import PredictionEngine
from Dashboard.mode_presets import apply_mode_preset

engine = PredictionEngine()

# Automatically configure for FT8
apply_mode_preset(engine, 'FT8')
# Now engine.params.bandwidth_hz = 50
# And engine.params.required_snr = -21

# Or manually set
engine.params.bandwidth_hz = 2700  # SSB
engine.params.required_snr = 10    # 10 dB SNR
```

---

## Map Data Format

```json
{
  "metadata": {
    "generated": "2025-11-17T23:30:00Z",
    "tx_location": {"lat": 44.374, "lon": -64.300},
    "frequency_mhz": 14.074,
    "mode": "FT8",
    "ssn": 77,
    "bandwidth_hz": 50,
    "required_snr": -21,
    "grid_count": 25652,
    "successful_predictions": 24891
  },
  "statistics": {
    "snr": {
      "min": -5.2,
      "max": 45.3,
      "mean": 28.7,
      "median": 30.1
    },
    "reliability": {
      "min": 12.3,
      "max": 98.7,
      "mean": 76.2,
      "median": 81.5
    }
  },
  "predictions": [
    {
      "grid": "FN74",
      "lat": 44.5,
      "lon": -64.0,
      "distance_km": 45.2,
      "snr_db": 42.1,
      "reliability": 95.3,
      "signal_dbw": -68.2,
      "loss_db": 142.5,
      "mode": "1F2",
      "hops": 1
    }
  ]
}
```

---

## Performance

### Map Generation

| Resolution | Grid Points | Generation Time | File Size |
|------------|-------------|-----------------|-----------|
| Coarse (field) | ~1,000 | 1-2 min | 50-100 KB |
| Medium (square) | ~25,000 | 5-10 min | 200-500 KB |
| Fine (subsquare) | ~250,000 | 50-100 min | 2-5 MB |

**Recommendation:** Use medium resolution for most applications.

### Map Display

- **Loading Time:** <1 second
- **Rendering:** Instant with Leaflet
- **Memory Usage:** ~10 MB per map
- **Browser Support:** All modern browsers

---

## Advanced Configuration

### Custom Grid Resolution

```python
# Coarse: 10° x 5° field-level squares
map_data = generate_propagation_map(..., resolution='coarse')

# Medium: 2° x 1° square-level (default)
map_data = generate_propagation_map(..., resolution='medium')

# Fine: 5' x 2.5' subsquare-level
map_data = generate_propagation_map(..., resolution='fine')
```

### Custom Map Range

```python
# Local coverage (±30°)
map_data = generate_propagation_map(..., map_range_deg=30.0)

# Continental coverage (±60°)
map_data = generate_propagation_map(..., map_range_deg=60.0)

# Global coverage (±90°)
map_data = generate_propagation_map(..., map_range_deg=90.0)
```

### Batch Generation

Generate maps for multiple scenarios:

```python
bands = [(7.074, '40m'), (14.074, '20m'), (21.074, '15m')]
modes = ['WSPR', 'FT8', 'CW', 'SSB']
hours = [0, 6, 12, 18]

for (freq, band), mode, hour in itertools.product(bands, modes, hours):
    map_data = generate_propagation_map(
        tx_lat=TX_LAT, tx_lon=TX_LON,
        frequency=freq, mode=mode, utc_hour=hour,
        month=MONTH, ssn=SSN
    )
    # Save or process map_data
```

---

## Comparison to VOACAP

| Feature | VOACAP | DVOACAP-Python | Status |
|---------|--------|----------------|--------|
| **REL Maps** | ✅ Static PNG | ✅ Interactive | **Enhanced** |
| **SDBW Maps** | ✅ Static PNG | ✅ Interactive | **Enhanced** |
| **Maidenhead Grid** | ❌ Not aligned | ✅ Perfect alignment | **New** |
| **Mode Presets** | ❌ Manual entry | ✅ Auto-config | **New** |
| **Bandwidth Parameter** | ✅ Yes | ✅ Yes | **Fixed** |
| **Click for Details** | ❌ No | ✅ Yes | **New** |
| **Export Format** | PDF/PNG | JSON + HTML | **Enhanced** |

---

## Integration with Dashboard

### Add to Main Dashboard

**Option 1: Navigation Link**
```html
<a href="propagation_maps.html" class="nav-link">
    📊 Propagation Maps
</a>
```

**Option 2: Embedded Tab**
```html
<div class="tab-content" id="maps-tab">
    <iframe src="propagation_maps.html"
            style="width:100%;height:100%;border:none;">
    </iframe>
</div>
```

**Option 3: Flask Route**
```python
@app.route('/maps')
def maps_page():
    return send_from_directory('Dashboard', 'propagation_maps.html')
```

---

## Troubleshooting

### Map Data Not Found

**Error:** `Map data not found: map_20m_SSB_1800Z.json`

**Solution:** Generate maps first:
```bash
cd Dashboard
python generate_propagation_maps.py
```

### Slow Map Generation

**Problem:** Takes >10 minutes to generate

**Solutions:**
1. Use coarse resolution for wide areas
2. Reduce map_range_deg (e.g., 30° instead of 60°)
3. Run overnight for large batches
4. Cache generated maps (reuse for same conditions)

### High Memory Usage

**Problem:** Browser uses >500 MB RAM

**Solutions:**
1. Close unused tabs
2. Reduce map_range_deg
3. Use coarse/medium resolution
4. Restart browser periodically

---

## Future Enhancements

Planned features:

1. **Real-time Generation** - API endpoint for on-demand maps
2. **Animation** - 24-hour time-lapse playback
3. **Path Overlay** - Show specific DX paths on map
4. **Contour Lines** - Add MUF/FOT/LUF contours
5. **3D Visualization** - Height-coded reliability surface
6. **Export** - Save maps as PNG/PDF
7. **Compare Mode** - Side-by-side WSPR vs SSB

---

## References

- **VOACAP Online:** [voacap.com](https://www.voacap.com/)
- **Maidenhead System:** [Wikipedia](https://en.wikipedia.org/wiki/Maidenhead_Locator_System)
- **DVOACAP Validation:** See `VOACAP_VALIDATION_FINDINGS.md`
- **Implementation Details:** See `Dashboard/PROPAGATION_MAPS_README.md`

---

## Credits

- **VOACAP:** Original propagation model by NTIA/ITS
- **DVOACAP:** Pascal implementation by Alex Shovkoplyas (VE3NEA)
- **DVOACAP-Python:** Python port with map enhancements
- **Leaflet:** Interactive mapping library

---

**Last Updated:** 2025-11-18
**Status:** Production Ready
**Tested With:** 20m/40m/15m on SSB/FT8/CW/WSPR modes
