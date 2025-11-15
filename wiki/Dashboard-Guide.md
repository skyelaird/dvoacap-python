# Dashboard Guide

Complete guide to setting up, configuring, and using the DVOACAP-Python web dashboard for HF propagation predictions.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Features](#features)
- [API Endpoints](#api-endpoints)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

---

## Overview

The DVOACAP-Python dashboard is a modern web-based interface for visualizing HF radio propagation predictions. It provides:

- **Real-time propagation forecasts** for amateur radio bands (40m-10m)
- **Interactive world map** with propagation paths to major DX regions
- **Live solar conditions** (SFI, SSN, Kp, A-index)
- **Color-coded band status** indicators (Good/Fair/Poor/Closed)
- **DXCC tracking integration** showing worked/confirmed/needed entities
- **On-demand predictions** with Flask server backend
- **24-hour forecast timeline** for band planning

---

## Installation

### Option 1: Install from Main Package (Recommended)

Install DVOACAP-Python with dashboard dependencies:

```bash
# From the repository root
cd dvoacap-python
pip install -e ".[dashboard]"
```

This ensures the DVOACAP library and all dashboard dependencies are installed together.

### Option 2: Install Dashboard Dependencies Only

If you already have the DVOACAP library installed:

```bash
cd Dashboard
pip install -r requirements.txt
```

### Verify Installation

Check that all required dependencies are installed:

```bash
python3 -c "import numpy, requests, flask, flask_cors, dvoacap; print('All dependencies OK')"
```

---

## Quick Start

### Method A: Flask Server with Refresh Button (Recommended)

The Flask server provides an interactive dashboard with on-demand prediction generation.

**1. Start the server:**

```bash
cd Dashboard
python3 server.py
```

You should see:
```
 * Running on http://localhost:8000
 * Checking dependencies...
 * All required packages found!
```

**2. Open in browser:**

Visit `http://localhost:8000` in your web browser.

**3. Generate predictions:**

Click the **⚡ Refresh Predictions** button to generate fresh predictions. The dashboard will:
- Show a progress indicator
- Run DVOACAP predictions in the background
- Automatically reload when complete (~30-60 seconds)

**Benefits:**
- ✅ No manual script execution
- ✅ Real-time progress updates
- ✅ Always shows latest predictions
- ✅ Non-blocking background processing

---

### Method B: Static Files (Manual Updates)

For simpler deployment without a server, you can pre-generate predictions and view static HTML files.

**1. Generate predictions:**

```bash
cd Dashboard
python3 generate_predictions.py
```

This will:
- Fetch current solar data from NOAA
- Run DVOACAP predictions for all configured bands and regions
- Generate `propagation_data.json` (takes 30-60 seconds)

**2. View dashboard:**

Open `dashboard.html` in your browser:

```bash
# Linux/macOS
open dashboard.html

# Windows
start dashboard.html

# Or just double-click the file
```

**3. Update regularly:**

Re-run `generate_predictions.py` every 2-4 hours for current conditions.

---

## Configuration

### Station Settings

Edit `generate_predictions.py` to customize for your station:

```python
MY_QTH = {
    'call': 'YOUR_CALL',        # Your callsign
    'lat': 44.374,              # Latitude (decimal degrees)
    'lon': -64.300,             # Longitude (decimal degrees)
    'grid': 'FN74ui',           # Maidenhead grid square
    'antenna': 'Your Antenna',  # Antenna description
    'location': GeoPoint.from_degrees(44.374, -64.300)
}
```

### Target DX Regions

Customize which regions to predict by editing `TARGET_REGIONS`:

```python
TARGET_REGIONS = {
    'EU': {
        'name': 'Europe',
        'location': GeoPoint.from_degrees(50.0, 10.0),  # Center of region
        'color': '#FF6B6B'
    },
    'JA': {
        'name': 'Japan',
        'location': GeoPoint.from_degrees(36.0, 138.0),
        'color': '#4ECDC4'
    },
    # Add more regions as needed
}
```

**Common DX Regions:**

| Region | Name | Latitude | Longitude |
|--------|------|----------|-----------|
| `EU` | Europe | 50.0 | 10.0 |
| `JA` | Japan | 36.0 | 138.0 |
| `VK` | Australia | -33.87 | 151.21 |
| `ZS` | South Africa | -33.92 | 18.42 |
| `LU` | Argentina | -34.61 | -58.38 |
| `W6` | California | 37.77 | -122.42 |

### Operating Bands

Configure which amateur radio bands to predict:

```python
BANDS = {
    '160m': 1.850,   # Band name: frequency (MHz)
    '80m': 3.750,
    '40m': 7.150,
    '30m': 10.125,
    '20m': 14.150,
    '17m': 18.110,
    '15m': 21.200,
    '12m': 24.940,
    '10m': 28.300,
}
```

Use the center of each band or your preferred operating frequency.

### Prediction Parameters

Adjust prediction settings in `generate_predictions.py`:

```python
# In the PredictionEngine configuration
engine.params.ssn = 100.0                    # Sunspot number (auto-fetched)
engine.params.tx_power = 100.0               # Transmitter power (watts)
engine.params.min_angle = np.deg2rad(3.0)    # Minimum takeoff angle (degrees)
engine.params.required_snr = 10.0            # Required SNR for comms (dB)
engine.params.required_reliability = 0.9     # Reliability threshold (0-1)
```

---

## Features

### Main Dashboard Tabs

#### 1. Overview Tab
- Current band openings summary
- Solar-terrestrial conditions (SFI, SSN, Kp, A-index)
- Quick reference for which bands are open

#### 2. Validation Tab
- Compare predictions vs. actual reception reports (PSKreporter integration)
- Shows confirmed, unexpected, and unconfirmed predictions
- Helps verify prediction accuracy

#### 3. Bands Tab
- Detailed band-by-band analysis
- SNR, reliability, and service probability for each region
- Visual indicators for band conditions

#### 4. Forecast Tab
- 24-hour timeline view
- See band openings throughout the day
- Plan operating sessions

#### 5. DXCC Tab
- Track DXCC progress by band and mode
- View worked/confirmed/needed entities
- Integration with QRZ ADIF logbook exports

### Band Status Indicators

The dashboard uses color-coded indicators to show band conditions:

- 🟢 **GOOD** - Reliability > 60%, SNR > 10 dB (Excellent propagation)
- 🟡 **FAIR** - Reliability 30-60% or SNR 3-10 dB (Marginal propagation)
- 🔴 **POOR** - Reliability < 30%, SNR < 3 dB (Weak signals)
- ⚫ **CLOSED** - No propagation predicted (Band not open)

### Solar Conditions Display

**SFI (Solar Flux Index):**
- Measured at 10.7 cm wavelength
- Higher values = better HF conditions
- Typical range: 70-250

**SSN (Sunspot Number):**
- Indicates solar cycle phase
- Higher during solar maximum
- Typical range: 0-300

**Kp Index:**
- Geomagnetic activity (0-9 scale)
- Lower = more stable propagation
- Kp > 5 indicates disturbed conditions

**A-Index:**
- D-layer absorption indicator
- Lower = less absorption
- High A-index degrades low-band propagation

---

## API Endpoints

When running the Flask server, the following API endpoints are available:

### `POST /api/generate`

Trigger prediction generation in the background.

**Request:**
```bash
curl -X POST http://localhost:8000/api/generate
```

**Response:**
```json
{
  "status": "started",
  "message": "Prediction generation started"
}
```

### `GET /api/status`

Check the status of prediction generation.

**Request:**
```bash
curl http://localhost:8000/api/status
```

**Response (running):**
```json
{
  "status": "running",
  "progress": "Processing predictions..."
}
```

**Response (complete):**
```json
{
  "status": "idle",
  "last_update": "2025-11-15 14:30:00"
}
```

**Response (error):**
```json
{
  "status": "error",
  "error": "Error message here"
}
```

### `GET /api/data`

Retrieve the latest prediction data (serves `propagation_data.json`).

**Request:**
```bash
curl http://localhost:8000/api/data
```

**Response:**
```json
{
  "timestamp": "2025-11-15T14:30:00Z",
  "solar": {
    "sfi": 145.2,
    "ssn": 100,
    "kp": 2,
    "a_index": 8
  },
  "predictions": [...]
}
```

---

## Deployment

### Option 1: Local Use (Current)

Open HTML files directly or run the Flask server locally. Best for personal use.

**Pros:** Simple, no hosting required
**Cons:** Manual updates, local access only

---

### Option 2: Static Hosting (GitHub Pages, Netlify, Cloudflare Pages)

Deploy static files to free hosting services.

**GitHub Pages Example:**

```bash
# Enable GitHub Pages in repository settings
# Select source: main branch, /Dashboard folder

# Push updates
git add Dashboard/propagation_data.json Dashboard/*.html
git commit -m "Update dashboard predictions"
git push origin main

# Access at: https://yourusername.github.io/dvoacap-python/Dashboard/
```

**Pros:** Access from anywhere, free hosting
**Cons:** Manual updates (or use GitHub Actions)

---

### Option 3: Automated Updates with GitHub Actions

Set up automatic prediction updates every 2 hours.

Create `.github/workflows/update-predictions.yml`:

```yaml
name: Update Dashboard Predictions

on:
  schedule:
    - cron: '0 */2 * * *'  # Every 2 hours
  workflow_dispatch:        # Manual trigger

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: pip install -e ".[dashboard]"

      - name: Generate predictions
        run: cd Dashboard && python3 generate_predictions.py

      - name: Commit and push
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add Dashboard/propagation_data.json
          git commit -m "Auto-update predictions" || exit 0
          git push
```

**Pros:** Fully automated, always up-to-date
**Cons:** Uses GitHub Actions minutes (2000/month free)

---

### Option 4: Self-Hosted Server

Deploy the Flask server on a VPS or cloud instance.

**Using systemd (Linux):**

Create `/etc/systemd/system/dvoacap-dashboard.service`:

```ini
[Unit]
Description=DVOACAP Dashboard
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/dvoacap-python/Dashboard
ExecStart=/usr/bin/python3 server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable dvoacap-dashboard
sudo systemctl start dvoacap-dashboard
```

**Add cron job for automatic updates:**

```bash
crontab -e

# Add this line:
0 */2 * * * curl -X POST http://localhost:8000/api/generate
```

---

## Troubleshooting

### Dashboard shows "No data available"

**Cause:** Predictions haven't been generated yet.

**Solution:**
```bash
cd Dashboard
python3 generate_predictions.py
```

---

### "Generator failed" error when clicking Refresh

**Cause:** Missing dependencies or import errors.

**Solution:**

1. Check server console for detailed error messages
2. Install all dependencies:
   ```bash
   pip install -e ".[dashboard]"
   ```
3. Verify installation:
   ```bash
   python3 -c "import numpy, flask, dvoacap; print('OK')"
   ```
4. Test generator directly:
   ```bash
   cd Dashboard
   python3 generate_predictions.py
   ```

---

### Predictions take a very long time

**Cause:** Full VOACAP calculations are computationally intensive.

**Solutions:**
- Reduce number of target regions in `TARGET_REGIONS`
- Increase time step in UTC hours (predict every 3 hours instead of 2)
- Remove bands you don't use
- Use fewer frequency points per band

**Typical generation times:**
- 5 regions × 7 bands × 12 time points = ~45 seconds
- 10 regions × 7 bands × 12 time points = ~90 seconds

---

### Solar data not fetching

**Symptom:** "Could not fetch live solar data" message.

**Cause:** NOAA API temporarily unavailable.

**Impact:** Predictions will use default values (SSN=100). This is normal and predictions will still work.

**Solution:** The script automatically retries and uses reasonable defaults.

---

### ModuleNotFoundError: No module named 'dvoacap'

**Cause:** DVOACAP library not installed or not in Python path.

**Solution:**
```bash
# From repository root
pip install -e .

# Or with dashboard extras
pip install -e ".[dashboard]"
```

---

### Dashboard doesn't auto-reload after generation

**Cause:** Browser caching or server not responding.

**Solutions:**
1. Hard refresh: Ctrl+F5 (Windows/Linux) or Cmd+Shift+R (Mac)
2. Check server console for errors
3. Manually reload the page

---

## Advanced Features

### PSKreporter Validation

Integrate real-time reception reports to validate predictions.

See the **pskreporter_api.py** module for integration details.

### DXCC Tracking

Import your logbook to track DXCC progress:

```bash
# Export ADIF from QRZ
python3 parse_adif.py your_logbook.adi
```

This generates `dxcc_summary.json` with worked/confirmed entity tracking.

---

## Next Steps

- **[Quick Examples](Quick-Examples)** - Code snippets for common tasks
- **[Integration Guide](Integration-Guide)** - Build custom applications
- **[API Reference](API-Reference)** - Complete API documentation
- **[Performance Tips](Performance-Tips)** - Optimize prediction speed

---

**73 de VE1ATM!** For questions or issues, visit the [GitHub repository](https://github.com/skyelaird/dvoacap-python/issues).
