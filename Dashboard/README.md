# VE1ATM HF Propagation Dashboard 📡

> Real-time HF band propagation predictions using the DVOACAP-Python prediction engine

A modern web-based dashboard for monitoring and predicting HF amateur radio band conditions from VE1ATM's QTH in Lunenburg, Nova Scotia (FN74ui) to major DX regions worldwide.

---

## 🎯 What It Does

The dashboard provides **real-time HF propagation forecasts** with:

- **24-hour band-by-band predictions** for 40m through 10m
- **Interactive world map** showing propagation paths to 10 major regions
- **Live solar conditions** (Solar Flux, Sunspot Number, Kp index)
- **Color-coded band status** (Good/Fair/Poor/Closed)
- **DXCC tracking integration** showing worked/confirmed/needed entities
- **Real-time validation** with PSKreporter reception data (optional)

---

## 🚀 Quick Start

### Installation

**Recommended: Install from main package** (ensures DVOACAP library is available)
```bash
# From the repository root
pip install -e ".[dashboard]"
```

**Alternative: Install just Dashboard dependencies**
```bash
cd Dashboard
pip install -r requirements.txt
# Note: You'll also need the dvoacap library installed separately
```

---

### Running the Dashboard

You have two options for running the dashboard:

### Option A: Web Server with Refresh Button (Recommended)

**1. Start the server:**
```bash
cd Dashboard
python3 server.py
```

**2. Open in browser:**
Visit `http://localhost:8000`

**3. Use the refresh button:**
Click the **⚡ Refresh Predictions** button in the dashboard to generate fresh predictions on demand!

**Benefits:**
- ✅ Refresh predictions with a button click
- ✅ No need to manually run scripts
- ✅ Progress indicator shows generation status
- ✅ Dashboard auto-reloads when complete

---

### Option B: Static Files (Manual Updates)

**1. Generate Predictions:**
```bash
cd Dashboard
python3 generate_predictions.py
```

This will:
- Fetch current solar-terrestrial conditions from NOAA
- Run DVOACAP predictions for all bands and regions
- Generate `propagation_data.json` with 24-hour forecasts
- Takes ~30-60 seconds depending on your system

**2. View Dashboard:**

Open `dashboard.html` in your web browser:

```bash
# Linux/macOS
open dashboard.html

# Windows
start dashboard.html

# Or just double-click the file
```

**3. Update Regularly:**

For best results, regenerate predictions:
- **Every 2-4 hours** for current conditions
- **After solar events** (flares, CMEs, storms)
- **Before operating sessions** to plan which bands are open

---

## 📊 Dashboard Features

### Main Tabs

1. **Overview** - Current band openings and solar conditions
2. **Validation** - Compare predictions vs. actual PSKreporter data
3. **Bands** - Detailed band-by-band analysis
4. **Forecast** - 24-hour timeline view
5. **DXCC** - Track your DXCC progress and needed entities

### Band Status Indicators

- 🟢 **GOOD** - Reliability > 60%, SNR > 10 dB
- 🟡 **FAIR** - Reliability 30-60%, or SNR 3-10 dB
- 🔴 **POOR** - Reliability < 30%, SNR < 3 dB
- ⚫ **CLOSED** - No propagation predicted

### Solar Conditions

The dashboard displays current:
- **SFI** (Solar Flux Index) - Higher = better HF conditions
- **SSN** (Sunspot Number) - Indicates solar cycle phase
- **Kp** (Geomagnetic activity) - Lower = more stable propagation
- **A-index** (Absorption) - Lower = less D-layer absorption

---

## 🔧 Configuration

### Station Settings

Edit `generate_predictions.py` to customize for your station:

```python
MY_QTH = {
    'call': 'YOUR_CALL',
    'lat': 44.374,      # Your latitude
    'lon': -64.300,     # Your longitude
    'grid': 'FN74ui',   # Your grid square
    'antenna': 'DX Commander 7m Vertical',
    'location': GeoPoint.from_degrees(44.374, -64.300)
}
```

### Target Regions

Add or modify DX regions in `TARGET_REGIONS`:

```python
TARGET_REGIONS = {
    'EU': {'name': 'Europe', 'location': GeoPoint.from_degrees(50.0, 10.0)},
    'JA': {'name': 'Japan', 'location': GeoPoint.from_degrees(36.0, 138.0)},
    # Add more regions...
}
```

### Operating Bands

Modify `BANDS` to change which bands are predicted:

```python
BANDS = {
    '40m': 7.150,   # Frequency in MHz (center of band)
    '20m': 14.150,
    # Add more bands...
}
```

---

## 📁 File Structure

```
Dashboard/
├── dashboard.html              # Main web interface (primary)
├── index.html                  # Landing page with quick start guide
├── generate_predictions.py     # Prediction generator (NEW - uses DVOACAP)
│
├── Data Files
├── propagation_data.json       # Generated predictions
├── dxcc_entities.json          # DXCC entity database
├── dxcc_summary.json           # Your DXCC progress
├── enhanced_predictions.json   # With PSKreporter validation
├── pskreporter_data.json       # Real-time spots
│
├── Utility Modules
├── dvoacap_wrapper.py          # DVOACAP DLL wrapper (legacy)
├── parse_adif.py               # ADIF log parser for DXCC tracking
├── pskreporter_api.py          # PSKreporter integration
├── proppy_net_api.py           # PropPy.net VOACAP API (alternative)
│
└── archive/                    # Old/deprecated files
    ├── old_dashboards/         # Previous dashboard versions
    ├── old_generators/         # Aborted prediction attempts
    └── old_docs/               # Legacy documentation
```

---

## 🧪 Advanced Features

### PSKreporter Validation

To enable real-time validation with actual reception data:

```bash
python3 -c "from pskreporter_api import PSKReporterAPI; \
    api = PSKReporterAPI(); \
    api.fetch_spots('VE1ATM', last_hours=1)"
```

This fetches actual reception reports and compares them against predictions to show:
- ✅ **Confirmed** - Predicted AND actually received
- ⚠️ **Unexpected** - Received but not predicted
- ❓ **Unconfirmed** - Predicted but not yet verified

### DXCC Tracking

1. Export your log from QRZ as ADIF format
2. Run the ADIF parser:

```bash
python3 parse_adif.py your_logbook.adi
```

This generates `dxcc_summary.json` with:
- Entities worked
- LoTW confirmations
- Most-wanted list
- Regional statistics

### Automated Updates

Set up automatic prediction updates with cron:

```bash
# Update predictions every 2 hours
crontab -e

# Add this line:
0 */2 * * * cd /path/to/Dashboard && python3 generate_predictions.py
```

---

## 🛠️ Technical Details

### Prediction Engine

The dashboard uses the **DVOACAP-Python** prediction engine, which implements:

1. **Phase 1: Path Geometry** - Great circle calculations, geodetic conversions
2. **Phase 2: Solar & Geomagnetic** - Solar zenith angles, magnetic field (IGRF)
3. **Phase 3: Ionospheric Profiles** - CCIR/URSI models, E/F1/F2 layers
4. **Phase 4: Raytracing** - MUF calculations, skip distance, multi-hop paths
5. **Phase 5: Signal Predictions** - Path loss, SNR, reliability, service probability

This is a **complete VOACAP implementation**, far more accurate than simplified ITU-R models.

### Data Flow

```
Solar Data (NOAA) → DVOACAP Engine → JSON Output → Dashboard Display
                         ↓
                  Phases 1-5 Processing
                         ↓
                  Band Predictions
```

### Performance

- **Prediction generation**: ~30-60 seconds for 10 regions × 12 time points × 7 bands
- **Dashboard loading**: <1 second
- **Memory usage**: ~50 MB for prediction engine
- **Browser compatibility**: All modern browsers (Chrome, Firefox, Safari, Edge)

---

## 🌐 Deployment Options

### Option 1: Local Use (Current)

Open HTML files directly in browser. Run prediction script manually when needed.

**Pros**: Simple, no server required
**Cons**: Manual updates, local access only

### Option 2: Local Web Server

```bash
# Python simple server
python3 -m http.server 8000

# Access at http://localhost:8000
```

**Pros**: Clean URLs, no file:// restrictions
**Cons**: Still local only

### Option 3: Static Hosting (Recommended)

Deploy to GitHub Pages, Netlify, or Cloudflare Pages:

```bash
# Example: GitHub Pages
git add Dashboard/*
git commit -m "Update dashboard"
git push origin main

# Enable GitHub Pages in repo settings
# Visit: https://yourusername.github.io/dvoacap-python/Dashboard/
```

**Pros**: Access from anywhere, free hosting
**Cons**: Need to push updates manually (or use GitHub Actions)

### Option 4: Automated Cloud Updates

Set up GitHub Actions to regenerate predictions hourly:

```yaml
# .github/workflows/update-predictions.yml
name: Update Predictions
on:
  schedule:
    - cron: '0 */2 * * *'  # Every 2 hours
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -e .
      - run: cd Dashboard && python3 generate_predictions.py
      - run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add Dashboard/propagation_data.json
          git commit -m "Auto-update predictions" || exit 0
          git push
```

**Pros**: Fully automated, always up-to-date
**Cons**: Uses GitHub Actions minutes (free tier: 2000 min/month)

---

## 🐛 Troubleshooting

### "Generator failed" Error in Dashboard

**Error**: When clicking "Refresh Predictions", you see "Complete! Error: Generator failed:"

**Cause**: This usually indicates missing dependencies or import errors.

**Solution**:

1. Check the detailed error message shown in the dashboard alert
2. Install all required dependencies:

```bash
# From repository root
pip install -e .[dashboard]

# Or install packages individually
pip install numpy requests flask flask-cors
```

3. Verify dependencies are installed:

```bash
python3 -c "import numpy, requests, flask, flask_cors; print('All dependencies OK')"
```

4. Test the generator directly to see full error output:

```bash
cd Dashboard
python3 generate_predictions.py
```

**Note**: The server now performs a dependency check on startup and will show exactly which packages are missing.

### Predictions Not Generating

**Error**: `ModuleNotFoundError: No module named 'dvoacap'`

**Solution**: Make sure you're running from the dvoacap-python directory:

```bash
cd /path/to/dvoacap-python
python3 Dashboard/generate_predictions.py
```

Or install the package:

```bash
pip install -e .
```

### Dashboard Not Loading

**Error**: Dashboard shows "No data available"

**Solution**: Generate predictions first:

```bash
python3 generate_predictions.py
```

### Solar Data Not Fetching

**Error**: "Could not fetch live solar data"

**Solution**: The script will use default values. This is normal if NOAA API is temporarily unavailable. Predictions will still work.

### Slow Prediction Generation

**Issue**: Takes several minutes to generate

**Solution**: This is normal for full VOACAP calculations. To speed up:
- Reduce number of regions in `TARGET_REGIONS`
- Increase time step in `utc_hours` (e.g., every 3 hours instead of 2)
- Use fewer frequencies in `BANDS`

---

## 📚 Additional Resources

### DVOACAP-Python Documentation

- [Main README](../README.md) - Project overview and installation
- [Integration Guide](../docs/INTEGRATION.md) - API usage examples
- [Phase Documentation](../docs/) - Detailed technical docs

### Propagation Resources

- [VOACAP Online](https://www.voacap.com/) - Official VOACAP site
- [PropPy.net](https://www.proppy.net/) - Web-based predictions
- [NOAA Space Weather](https://www.swpc.noaa.gov/) - Solar conditions
- [PSKreporter](https://pskreporter.info/) - Real-time propagation data

### Amateur Radio

- [ARRL Propagation](http://www.arrl.org/propagation) - Propagation basics
- [DXCC Program](http://www.arrl.org/dxcc) - DXCC awards info
- [QRZ.com](https://www.qrz.com/) - Callsign database and logbook

---

## 🤝 Contributing

Found a bug? Have a feature request?

1. Check existing issues on GitHub
2. Open a new issue with detailed description
3. Or submit a pull request!

---

## 📄 License

This dashboard is part of the DVOACAP-Python project.

- **DVOACAP-Python**: MIT License
- **Original DVOACAP**: Copyright Alex Shovkoplyas (VE3NEA)
- **Dashboard**: MIT License

---

## 👤 Author

**VE1ATM** - Skye Laird
**Location**: FN74ui (Lunenburg, Nova Scotia)
**Station**: DX Commander 7m Vertical

---

## 🎉 Acknowledgments

- **Alex Shovkoplyas (VE3NEA)** - Original DVOACAP implementation
- **NOAA Space Weather** - Solar-terrestrial data
- **PSKreporter** - Real-time propagation validation
- **Leaflet.js** - Interactive mapping library
- **Amateur radio community** - Testing and feedback

---

**73 de VE1ATM** 📻
