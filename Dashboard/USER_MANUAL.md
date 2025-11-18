# VE1ATM HF Propagation Dashboard - User Manual

**Version:** 1.0
**Last Updated:** 2025-11-18

## Table of Contents

1. [Introduction](#introduction)
2. [Quick Start](#quick-start)
3. [Installation & Setup](#installation--setup)
4. [Dashboard Features](#dashboard-features)
5. [Configuration](#configuration)
6. [Troubleshooting](#troubleshooting)
7. [API Reference](#api-reference)
8. [Advanced Usage](#advanced-usage)

---

## Introduction

The VE1ATM HF Propagation Dashboard is a comprehensive real-time propagation forecasting system for amateur radio operators. It provides:

- **24-hour propagation predictions** to major DX regions worldwide
- **Real-time solar conditions** from international data sources
- **Interactive maps** with greyline visualization
- **Band-by-band analysis** across all HF amateur bands
- **Antenna configuration** for accurate predictions
- **DXCC tracking** and logbook integration

The dashboard uses the **DVOACAP-Python prediction engine**, a complete Python implementation of the Voice of America Coverage Analysis Program (VOACAP) ionospheric propagation prediction software.

---

## Quick Start

### Running the Dashboard

1. **Navigate to the Dashboard directory:**
   ```bash
   cd dvoacap-python/Dashboard
   ```

2. **Generate initial prediction data:**
   ```bash
   python3 generate_predictions.py
   ```
   This will fetch current solar conditions and generate 24-hour predictions for all bands and regions.

3. **Start the web server:**
   ```bash
   python3 server.py
   ```

4. **Open your browser:**
   Navigate to `http://localhost:8000`

The dashboard will load with live propagation data!

---

## Installation & Setup

### System Requirements

- **Python:** 3.8 or higher
- **Operating System:** Linux, macOS, or Windows
- **RAM:** 2GB minimum
- **Internet Connection:** Required for solar data fetching

### Installing Dependencies

The dashboard requires several Python packages. Install them using:

```bash
pip3 install -r requirements.txt
```

Or install manually:
```bash
pip3 install flask>=2.3.0 flask-cors>=4.0.0 requests>=2.31.0 numpy>=1.24.0
```

### Installing DVOACAP-Python

The dashboard requires the dvoacap-python package to be installed:

```bash
cd dvoacap-python
pip3 install -e .
```

This installs the package in development mode, allowing you to use the prediction engine.

---

## Dashboard Features

### 1. Solar Conditions Bar

Displays real-time space weather data:
- **SFI (Solar Flux Index):** F10.7 cm radio flux
- **SSN (Sunspot Number):** International sunspot count
- **Kp Index:** Geomagnetic activity (0-9 scale)
- **A-Index:** Daily geomagnetic activity

**Data Sources:**
- Solar Flux: NOAA SWPC, LISIRD, Space Weather Canada
- Sunspot Number: SIDC/SILSO (Belgium), NOAA SWPC
- Kp & A Index: GFZ Potsdam (Germany), NOAA SWPC

### 2. Interactive Map

Features:
- **World map** with your QTH and DX targets
- **Greyline visualization** - drag the slider to see day/night terminator at any UTC hour
- **Great circle paths** to all target regions
- **Color-coded regions** based on propagation quality

### 3. Band Grid

Visual overview of all 9 HF bands:
- **160m through 10m** in a compact grid
- **Color-coded status:**
  - Green: GOOD propagation (SNR ≥10 dB, Reliability ≥60%)
  - Yellow: FAIR propagation (SNR ≥3 dB or Reliability ≥30%)
  - Orange: POOR propagation (some signal but marginal)
  - Red: CLOSED (no usable path)

### 4. Quick Summary

Top regions for each band based on:
- Signal-to-Noise Ratio (SNR)
- Path reliability
- Current band conditions

### 5. Propagation Charts

Detailed 24-hour forecast charts for each band:
- **Reliability timeline** - Shows path reliability percentage over 24 hours
- **SNR timeline** - Signal strength predictions with 10th/90th percentile ranges
- **MUF usage** - How close the frequency is to the Maximum Usable Frequency
- **Signal strength** - Median power with upper/lower decile variations

### 6. Timeline View

24-hour propagation forecast showing:
- Hour-by-hour band openings
- Which regions are open on which bands
- Marginal paths (shown in yellow)

### 7. DXCC Tracking

Track your awards progress:
- **DXCC Worked:** Total entities contacted
- **DXCC Confirmed (LoTW):** Entities confirmed via Logbook of the World
- **DXCC Missing:** Entities you still need to work
- **Import ADIF logbook** to update your tracking

---

## Configuration

### Station Configuration

1. **Click the gear icon** in the upper right
2. **Enter your station details:**
   - Callsign
   - Grid square (Maidenhead locator)
   - Latitude/Longitude (auto-filled from grid)
   - Transmit power (watts)

3. **Click Save Configuration**

Your settings are saved in `station_config.json` and persist between sessions.

### Antenna Configuration

Configure your antenna farm for accurate predictions:

1. **Click the antenna icon** in the toolbar
2. **Add antennas:**
   - Name (e.g., "40m Dipole")
   - Type: Vertical, Dipole, Yagi, or Log Periodic
   - Assign to specific bands

3. **Save Antenna Configuration**

The prediction engine uses your actual antenna characteristics to calculate:
- Elevation angles
- Antenna gain patterns
- Optimal takeoff angles

Antenna configurations are saved in `antenna_config.json`.

### Supported Antenna Types

- **Vertical Monopole:** Ground-mounted or elevated vertical
- **Dipole:** Horizontal or inverted-V dipole
- **Yagi:** 3-element or larger beam
- **Log Periodic:** Wideband directional antenna

---

## Troubleshooting

### Dashboard Shows No Data

**Problem:** Dashboard loads but displays no propagation data.

**Solution:**
1. Check if prediction data exists:
   ```bash
   ls -lh *.json
   ```
   You should see `enhanced_predictions.json` and `propagation_data.json`

2. If files are missing, generate predictions:
   ```bash
   python3 generate_predictions.py
   ```

3. If generation fails, check dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```

### Solar Data Not Updating

**Problem:** Solar conditions show old or default values.

**Solution:**
1. Check internet connection
2. Re-run prediction generator:
   ```bash
   python3 generate_predictions.py
   ```

The generator fetches fresh solar data from multiple international sources with automatic fallback.

### Server Won't Start

**Problem:** `python3 server.py` fails with errors.

**Solution:**
1. Check if port 8000 is already in use:
   ```bash
   lsof -i :8000
   ```

2. Use a different port:
   ```bash
   python3 server.py --port 8080
   ```

3. Check Flask is installed:
   ```bash
   pip3 install flask flask-cors
   ```

### Predictions Look Wrong

**Problem:** Predictions don't match observed conditions.

**Possible causes:**
1. **Outdated solar data** - Regenerate predictions to fetch latest conditions
2. **Wrong antenna configuration** - Verify antenna types match your actual setup
3. **Incorrect station location** - Check grid square and coordinates
4. **Power setting** - Verify transmit power is set correctly

### Browser Cache Issues

**Problem:** Dashboard doesn't show updates after regenerating predictions.

**Solution:**
- Hard refresh your browser: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
- Or start server with cache disabled:
  ```bash
  python3 server.py --no-cache
  ```

---

## API Reference

The dashboard server provides several REST API endpoints:

### GET /api/data

Fetch current prediction data.

**Response:**
```json
{
  "current_conditions": { ... },
  "timeline_24h": { ... },
  "propagation_charts": { ... }
}
```

### POST /api/generate

Trigger background prediction generation.

**Response:**
```json
{
  "status": "started",
  "message": "Prediction generation started"
}
```

### GET /api/status

Check prediction generation status.

**Response:**
```json
{
  "running": false,
  "progress": 100,
  "message": "Predictions updated successfully!",
  "last_updated": "2025-11-17T20:25:49.809840+00:00"
}
```

### GET /api/health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-17T20:30:00.000000+00:00",
  "service": "dvoacap-dashboard"
}
```

### GET/POST /api/station-config

Get or set station configuration.

### GET/POST /api/antenna-config

Get or set antenna configuration.

### GET /api/debug/cache

Debug HTTP caching configuration.

---

## Advanced Usage

### Running in Production

For production deployments:

```bash
python3 server.py --host 0.0.0.0 --port 80
```

**Note:** Binding to port 80 requires root/administrator privileges. Consider using nginx or Apache as a reverse proxy.

### Automated Updates

Set up a cron job to regenerate predictions automatically:

```bash
# Edit crontab
crontab -e

# Add this line to regenerate predictions every 6 hours
0 */6 * * * cd /path/to/dvoacap-python/Dashboard && /usr/bin/python3 generate_predictions.py
```

### Custom Target Regions

Edit `generate_predictions.py` to customize target regions:

```python
TARGET_REGIONS = {
    'EU': {'name': 'Europe', 'location': GeoPoint.from_degrees(50.0, 10.0)},
    'JA': {'name': 'Japan', 'location': GeoPoint.from_degrees(36.0, 138.0)},
    # Add your custom regions here
}
```

### Debug Mode

Run server in debug mode for development:

```bash
python3 server.py --debug
```

This enables:
- Auto-reload on code changes
- Detailed error messages
- HTTP caching disabled

### Disable HTTP Caching

For development or testing:

```bash
python3 server.py --no-cache
```

---

## Data Files Reference

| File | Purpose | Location |
|------|---------|----------|
| `enhanced_predictions.json` | Dashboard-compatible prediction data | `Dashboard/` |
| `propagation_data.json` | Raw prediction engine output | `Dashboard/` |
| `station_config.json` | Your station settings | `Dashboard/` |
| `antenna_config.json` | Your antenna farm configuration | `Dashboard/` |
| `dxcc_summary.json` | DXCC tracking data (optional) | `Dashboard/` |

---

## Getting Help

### Documentation

- **Dashboard Guide:** `wiki/Dashboard-Guide.md`
- **Design Recommendations:** `DASHBOARD_DESIGN_RECOMMENDATIONS.md`
- **DVOACAP Docs:** `docs/`

### Community

- **GitHub Issues:** Report bugs or request features
- **Pull Requests:** Contributions welcome!

### Development

- **Python version:** 3.8+
- **DVOACAP-Python:** Full prediction engine source in `src/dvoacap/`
- **Test suite:** Run `pytest` from project root

---

## License

This project is part of the DVOACAP-Python suite. See LICENSE file for details.

---

## Acknowledgments

- **DVOACAP prediction model** - Based on VOACAP by Voice of America
- **Solar data sources:**
  - NOAA Space Weather Prediction Center (USA)
  - SIDC/SILSO (Belgium)
  - GFZ Potsdam (Germany)
  - LISIRD (USA)
  - Space Weather Canada

---

**For the latest updates and documentation, visit:** https://github.com/skyelaird/dvoacap-python
