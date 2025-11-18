# Propagation Maps - VOACAP-Style Visualization

## Overview

This feature generates VOACAP-style propagation maps with Maidenhead grid overlay, showing signal strength (SDBW) and reliability (REL) predictions across geographic regions.

## Key Features

1. **Dual Map Modes**
   - **Reliability (REL)**: Circuit reliability percentage (0-100%)
   - **Signal Strength (SDBW)**: Signal-to-noise ratio in dB

2. **Mode Support**
   - WSPR (6 Hz, -28 dB SNR)
   - FT8 (50 Hz, -21 dB SNR)
   - CW (500 Hz, +6 dB SNR)
   - SSB (2700 Hz, +10 dB SNR)

3. **Maidenhead Grid Alignment**
   - Grid squares aligned to Maidenhead locator system
   - Resolution options: coarse (field), medium (square), fine (subsquare)
   - Color-coded by signal strength or reliability

4. **Space-Efficient Design**
   - Compact header and controls
   - Full-screen map view
   - Floating legend
   - All controls accessible without scrolling

## Files

### Backend (Map Generation)

- **`mode_presets.py`**: Mode-specific parameters matching VOACAP
- **`generate_propagation_maps.py`**: Map data generator
  - Generates grid of Maidenhead squares
  - Runs predictions for each square
  - Outputs JSON files with map data

### Frontend (Visualization)

- **`propagation_maps.html`**: Interactive map viewer
  - Leaflet-based mapping
  - Band/mode/time selection
  - Real-time map display with color coding
  - Popup details for each grid square

## Usage

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
...
```

### 2. View Maps in Browser

Open `http://localhost:8000/propagation_maps.html` (when server.py is running)

Or open `propagation_maps.html` directly in browser.

### 3. Interact with Maps

- **Band Selection**: 40m, 20m, 17m, 15m, 10m
- **Mode Selection**: WSPR, FT8, CW, SSB
- **Display Mode**: Reliability (REL) or Signal Strength (SDBW)
- **Time**: Select UTC hour (0-23)
- **Click grid squares**: See detailed popup with:
  - Grid square locator
  - Distance from TX
  - SNR and reliability
  - Propagation mode and hops

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
    "required_snr": -21
  },
  "statistics": {
    "snr": {"min": -5.2, "max": 45.3, "mean": 28.7},
    "reliability": {"min": 12.3, "max": 98.7, "mean": 76.2}
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
    },
    ...
  ]
}
```

## Implementation Details

### Bandwidth Parameter

**NEW**: Added `bandwidth_hz` parameter to `VoacapParams`:

```python
engine.params.bandwidth_hz = 2700.0  # SSB default
```

This affects noise floor calculations:
```
Noise Power (dBW) = Noise Density + 10*log10(Bandwidth_Hz)
SNR = Signal Power - Noise Power
```

### Mode Presets

Presets automatically configure bandwidth and required SNR:

```python
from Dashboard.mode_presets import apply_mode_preset

engine = PredictionEngine()
apply_mode_preset(engine, 'FT8')
# Now configured with bandwidth_hz=50, required_snr=-21
```

### Color Scales

**Reliability (REL)**:
- Red (90-100%): Excellent
- Orange (70-90%): Good
- Yellow (50-70%): Fair
- Green (30-50%): Marginal
- Blue (10-30%): Poor
- Gray (0-10%): Unlikely

**Signal Strength (SDBW)**:
- Red (>40 dB): S9+
- Orange (30-40 dB): S9
- Yellow (20-30 dB): S7
- Green (10-20 dB): S5
- Blue (0-10 dB): S3
- Gray (<0 dB): Weak

## Integration with Dashboard

To add to main dashboard, include an iframe or navigation link:

```html
<a href="propagation_maps.html">View Propagation Maps</a>
```

Or embed in tab:

```html
<div class="tab-content" id="maps-tab">
    <iframe src="propagation_maps.html" style="width:100%;height:100%;border:none;"></iframe>
</div>
```

## Performance Considerations

### Map Generation

- **Medium resolution** (2° x 1° squares): ~3000 grid points for ±60° range
- **Prediction time**: ~0.1s per grid point
- **Total generation**: ~5 minutes per map
- **Recommended**: Pre-generate maps for common bands/times

### Map Display

- **File size**: ~200-500 KB per map (JSON)
- **Loading time**: <1 second
- **Rendering**: Instant with Leaflet
- **Memory**: ~10 MB per map in browser

## Comparison to VOACAP

| Feature | VOACAP | DVOACAP-Python | Status |
|---------|--------|----------------|--------|
| **REL Maps** | ✅ | ✅ | **Implemented** |
| **SDBW Maps** | ✅ | ✅ | **Implemented** |
| **Maidenhead Grid** | ❌ | ✅ | **Enhanced** |
| **Mode Presets** | Manual | ✅ Automatic | **Enhanced** |
| **Bandwidth Param** | ✅ | ✅ | **Now Supported** |
| **Interactive Display** | Static PNG | ✅ Interactive | **Enhanced** |
| **Grid Details** | ❌ | ✅ Click for details | **Enhanced** |

## Known Issues

1. **Initial Generation Time**: First map generation takes ~5 minutes
   - **Solution**: Pre-generate common scenarios, cache results

2. **Missing Map Data**: If map file not found, shows error
   - **Solution**: Run `generate_propagation_maps.py` first

3. **Large Area Coverage**: ±60° range creates large datasets
   - **Solution**: Use coarse resolution for wide areas, fine for local

## Future Enhancements

1. **Real-time Generation**: Generate maps on-demand via API
2. **Animation**: Play 24-hour time-lapse of propagation changes
3. **Path Overlay**: Show specific DX paths on map
4. **Contour Lines**: Add MUF/FOT/LUF contours
5. **3D Visualization**: Height-coded reliability surface
6. **Export**: Save maps as PNG/PDF for reports

## References

- VOACAP Online: https://www.voacap.com/
- Maidenhead Locator System: https://en.wikipedia.org/wiki/Maidenhead_Locator_System
- DVOACAP Validation: See `VOACAP_VALIDATION_FINDINGS.md`

## Credits

- **VOACAP**: Original propagation model by NTIA/ITS
- **DVOACAP**: Pascal implementation by Alex Shovkoplyas (VE3NEA)
- **DVOACAP-Python**: Python port with map enhancements
- **VE1ATM**: Test station and requirements

---

**Last Updated**: 2025-11-17
**Status**: Ready for Testing
