# Multi-Source Space Weather Data Architecture

## Overview

DVOACAP-Python now supports fetching space weather data from **multiple international sources** with automatic fallback, reducing dependence on any single data provider (particularly NOAA/USA).

## Why Multiple Sources?

- **Resilience**: If one source is down, others automatically take over
- **Geopolitical Independence**: Not relying solely on US government sources
- **Data Diversity**: Cross-validation from multiple authoritative sources
- **Future-proofing**: Protection against service discontinuation

## Supported Data Sources

### Solar Flux Index (F10.7)
1. **NOAA SWPC** (USA) - Primary
   - API: `https://services.swpc.noaa.gov/json/f107_cm_flux.json`
   - Coverage: Daily observations

2. **LISIRD** (LASP Colorado) - Backup
   - URL: `https://lasp.colorado.edu/lisird/data/penticton_radio_flux/`
   - Coverage: Historical + current Penticton data

3. **Space Weather Canada** - Tertiary
   - URL: `https://spaceweather.gc.ca/forecast-prevision/solar-solaire/solarflux/`
   - Coverage: Penticton observatory data

### Sunspot Number (SSN)
1. **SIDC/SILSO** (Belgium) - Primary (Authoritative Source)
   - API: `https://data.opendatasoft.com/api/records/1.0/search/?dataset=daily-sunspot-number@datastro`
   - Organization: Royal Observatory of Belgium
   - Coverage: Official World Data Center for sunspot index
   - License: CC BY-NC

2. **NOAA SWPC** (USA) - Backup
   - API: `https://services.swpc.noaa.gov/json/solar-cycle/observed-solar-cycle-indices.json`
   - Coverage: Solar cycle observations

### Kp Index (Geomagnetic Activity)
1. **GFZ Potsdam** (Germany) - Primary (Authoritative Source)
   - API: `https://kp.gfz.de/app/json/?start=<ISO8601>&end=<ISO8601>&index=Kp`
   - Organization: German Research Centre for Geosciences
   - Coverage: Official Kp index producer
   - License: CC BY 4.0

2. **NOAA SWPC** (USA) - Backup
   - API: `https://services.swpc.noaa.gov/json/planetary_k_index_1m.json`
   - Coverage: 1-minute planetary K-index

### A-Index (Geomagnetic Activity)
1. **GFZ Potsdam** (Germany) - Primary
   - API: `https://kp.gfz.de/app/json/?start=<ISO8601>&end=<ISO8601>&index=Ap`
   - Coverage: Daily A-index (Ap)

2. **NOAA SWPC** (USA) - Backup
   - API: `https://services.swpc.noaa.gov/json/predicted_fredericksburg_a_index.json`
   - Coverage: Predicted A-index

## Additional Sources for Future Implementation

### Magnetometer Networks
1. **IMAGE Network** (Finland/Scandinavia)
   - API: `https://space.fmi.fi/image/www/data_download.php`
   - Stations: 57 magnetometers including Tromsø, Sodankylä
   - Coverage: Real-time auroral zone data
   - Use: Local geomagnetic disturbances, Kp validation

2. **INTERMAGNET** (International)
   - API: `https://imag-data.bgs.ac.uk/GIN_V1/hapi`
   - Coverage: Global observatory network including 14 Canadian stations
   - Use: High-quality geomagnetic field measurements

3. **Tromsø Geophysical Observatory** (Norway)
   - URL: `https://flux.phys.uit.no/geomag.html`
   - Coverage: High-latitude magnetometer data

4. **Sodankylä Geophysical Observatory** (Finland)
   - URL: `https://www.sgo.fi/Data/Magnetometer/magnData.php`
   - Coverage: Auroral zone measurements

### Alternative Solar Flux Sources
1. **Nobeyama** (Japan)
   - Coverage: F30, F15, F8, F3.2 (can derive F10.7)
   - Organization: National Astronomical Observatory of Japan

2. **CLS** (France)
   - Coverage: Interpolated F10.7 values
   - Organization: Collecte Localisation Satellites

## Architecture

### Module: `src/dvoacap/space_weather_sources.py`

The multi-source fetcher uses a hierarchical fallback architecture:

```python
from dvoacap.space_weather_sources import MultiSourceSpaceWeatherFetcher

# Initialize fetcher
fetcher = MultiSourceSpaceWeatherFetcher(timeout=10, verbose=True)

# Fetch all parameters with automatic fallback
data = fetcher.fetch_all()

# Access results
print(f"SFI: {data.sfi} from {data.sources['sfi']}")
print(f"SSN: {data.ssn} from {data.sources['ssn']}")
print(f"Kp: {data.kp} from {data.sources['kp']}")
print(f"A-index: {data.a_index} from {data.sources['a_index']}")
```

### Fallback Logic

For each parameter:
1. Try primary authoritative source (e.g., SIDC for SSN, GFZ for Kp)
2. If fails, try secondary source (e.g., NOAA)
3. If all fail, use sensible defaults (mid-cycle quiet conditions)
4. Track which source provided each value

### Integration

The Dashboard's `generate_predictions.py` now uses the multi-source fetcher:

```python
def fetch_solar_conditions() -> Dict:
    fetcher = MultiSourceSpaceWeatherFetcher(timeout=10, verbose=True)
    return fetcher.fetch_all_legacy_format()
```

## Usage

### Command Line Testing

```bash
# Test the multi-source fetcher
python3 src/dvoacap/space_weather_sources.py
```

Output shows which source provided each parameter:
```
======================================================================
Multi-Source Space Weather Data Fetcher
======================================================================
[OK] Solar Flux (F10.7): 149.0 from NOAA SWPC (USA)
[OK] Sunspot Number: 114.6 from SIDC/SILSO (Belgium)
[OK] Kp Index: 3.0 from GFZ Potsdam (Germany)
[OK] A-Index: 15.0 from GFZ Potsdam (Germany)
======================================================================
```

### In Your Code

```python
from dvoacap.space_weather_sources import MultiSourceSpaceWeatherFetcher

# Create fetcher
fetcher = MultiSourceSpaceWeatherFetcher(timeout=10, verbose=False)

# Get data
data = fetcher.fetch_all()

# Use data
solar_flux = data.sfi
sunspot_number = data.ssn
kp_index = data.kp
a_index = data.a_index

# Check sources
print(f"SSN from: {data.sources['ssn']}")  # e.g., "SIDC/SILSO (Belgium)"

# Check for errors
if data.fetch_errors:
    for error in data.fetch_errors:
        print(f"Warning: {error}")
```

## Benefits

### Reliability
- **Single point of failure eliminated**: If NOAA goes down, European sources take over
- **Automatic failover**: No manual intervention required
- **Graceful degradation**: Uses defaults only when all sources fail

### Data Quality
- **Authoritative sources**: SIDC for SSN, GFZ for Kp (official producers)
- **Cross-validation**: Can compare values from multiple sources
- **Source transparency**: Know exactly where each value came from

### Geopolitical Resilience
- **International diversity**: Data from Belgium, Germany, Canada, Finland, Japan
- **Reduced US dependence**: Multiple European and Asian alternatives
- **Future-proof**: Easy to add new sources as needed

## Future Enhancements

### Planned Features
1. **Data cross-validation**: Compare values from multiple sources, flag discrepancies
2. **Source health monitoring**: Track success/failure rates by source
3. **Automatic source rotation**: Distribute load across sources
4. **Magnetometer integration**: Use IMAGE/INTERMAGNET for real-time Kp validation
5. **Historical data**: Fetch data for specific dates (backfilling)

### Additional Sources to Integrate
1. **Australian Space Weather Services** (BoM)
2. **UK Met Office Space Weather**
3. **ESA Space Weather Service Network**
4. **Chinese National Space Science Center**

## Configuration

### Timeout Settings

```python
# Default timeout: 10 seconds
fetcher = MultiSourceSpaceWeatherFetcher(timeout=10)

# Longer timeout for slow connections
fetcher = MultiSourceSpaceWeatherFetcher(timeout=30)
```

### Verbose Mode

```python
# Enable detailed logging
fetcher = MultiSourceSpaceWeatherFetcher(verbose=True)

# Quiet mode
fetcher = MultiSourceSpaceWeatherFetcher(verbose=False)
```

## Data Licenses

| Source | License | Attribution Required |
|--------|---------|---------------------|
| SIDC/SILSO | CC BY-NC | Yes - Royal Observatory of Belgium |
| GFZ Potsdam | CC BY 4.0 | Yes - GFZ Helmholtz Centre |
| NOAA SWPC | Public Domain | Recommended |
| IMAGE Network | Free for scientific use | Yes - contact required for publications |
| INTERMAGNET | Open access | Yes - cite INTERMAGNET |

## Troubleshooting

### All Sources Failing
If all sources fail (network issues, etc.), the fetcher returns sensible defaults:
- SFI: 150.0 (mid-cycle)
- SSN: 100.0 (mid-cycle)
- Kp: 2.0 (quiet)
- A-index: 10.0 (quiet)

### SSL Errors (GFZ Potsdam)
Some systems may have SSL issues with GFZ. The fetcher automatically falls back to NOAA.

### API Rate Limits
Currently no rate limiting implemented. Most sources have generous limits for research use.

## References

1. SIDC/SILSO: https://www.sidc.be/SILSO/home
2. GFZ Potsdam Kp Index: https://kp.gfz-potsdam.de/
3. IMAGE Network: https://space.fmi.fi/image/
4. INTERMAGNET: https://intermagnet.org/
5. NOAA SWPC: https://www.swpc.noaa.gov/

## Contact

For questions about data sources or to suggest additional sources:
- Open an issue on GitHub
- Check source documentation for data provider contacts

---

**Last Updated**: November 2025
**Status**: Production Ready ✓
