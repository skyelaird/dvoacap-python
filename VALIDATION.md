# DVOACAP Validation Guide

This guide explains how to validate and debug DVOACAP-Python predictions against VOACAP online.

## Quick Start

### Run Full Validation

Compare local predictions against VOACAP online (proppy.net) for all test cases:

```bash
python3 validate_predictions.py
```

This will:
- Test 4 representative paths (UK, Japan, Australia, Brazil)
- Test 4 HF bands (40m, 20m, 15m, 10m)
- Compare reliability, SNR, and MUF values
- Generate a detailed report showing matches and mismatches
- Save results to `validation_results.json`

### Debug Single Prediction

For detailed debugging of a specific path/band:

```bash
python3 validate_predictions.py --debug UK 20m
```

This shows:
- All intermediate calculation values
- Path geometry details
- Ionospheric parameters
- Signal strength components
- Side-by-side comparison with VOACAP online
- Raw VOACAP response for inspection

## Validation Options

### Select Specific Regions

```bash
python3 validate_predictions.py --regions UK JA VK
```

Available regions:
- `UK` - United Kingdom (4,500 km trans-Atlantic)
- `JA` - Japan (10,500 km over Pacific)
- `VK` - Australia (16,500 km very long path)
- `SA` - South America (6,500 km different hemisphere)

### Select Specific Bands

```bash
python3 validate_predictions.py --bands 20m 15m 10m
```

Available bands:
- `40m` - 7.150 MHz
- `20m` - 14.150 MHz
- `15m` - 21.200 MHz
- `10m` - 28.500 MHz

### Test Multiple UTC Hours

```bash
python3 validate_predictions.py --hours 0 6 12 18
```

Tests predictions at different times of day to catch time-dependent issues.

### Quiet Mode

```bash
python3 validate_predictions.py --quiet
```

Shows only mismatches, hiding successful comparisons.

## Understanding Results

### Match Criteria

Predictions are considered matching if within these tolerances:
- **Reliability**: ±15%
- **SNR**: ±5 dB
- **MUF**: ±2 MHz

### Output Format

```
Region: United Kingdom (UK)
  Path: 4500 km - Trans-Atlantic, typical EU path

  UTC Hour: 1200
    20m (14.150 MHz): ✓ MATCH
        Local:  Rel= 75.0% SNR= 15.2dB Mode=2F2
        VOACAP: Rel= 78.0% SNR= 16.1dB

    15m (21.200 MHz): ✗ MISMATCH
        Local:  Rel= 45.0% SNR=  8.3dB MUF= 24.5MHz Mode=2F2
        VOACAP: Rel= 62.0% SNR= 12.1dB MUF= 26.2MHz
        → Reliability: local=45.0% vs VOACAP=62.0% (diff=17.0%)
        → SNR: local=8.3dB vs VOACAP=12.1dB (diff=3.8dB)
```

### Validation Summary

After all tests complete:

```
VALIDATION SUMMARY
Total tests:  16
Passed:       12 (75.0%)
Failed:       4 (25.0%)

FAILURE ANALYSIS:
  Reliability mismatches: 3
  SNR mismatches:         2
  MUF mismatches:         1

  By band:
    40m: 0/4 failures (0%)
    20m: 1/4 failures (25%)
    15m: 2/4 failures (50%)
    10m: 1/4 failures (25%)

  By region:
    UK: 1/4 failures (25%)
    JA: 2/4 failures (50%)
    VK: 1/4 failures (25%)
    SA: 0/4 failures (0%)
```

## Common Discrepancies

### 1. Ionospheric Model Differences

**Symptom**: Reliability differs by 10-20%, especially on higher bands

**Possible Causes**:
- CCIR vs URSI coefficient selection
- F2 layer critical frequency calculation
- Smoothing factor differences

**How to Debug**:
```bash
python3 validate_predictions.py --debug UK 15m
```
Look at the ionospheric profile parameters and compare with VOACAP online output.

### 2. Noise Model Variations

**Symptom**: SNR differs by 3-8 dB, but signal strength matches

**Possible Causes**:
- Man-made noise model differences
- Galactic noise calculation
- Atmospheric noise variations

**How to Debug**:
Check the noise_dbw values in detailed debug output.

### 3. Path Geometry

**Symptom**: Mode selection differs (e.g., 2F2 vs 3F2)

**Possible Causes**:
- Elevation angle calculation
- Hop distance determination
- Short vs long path selection

**How to Debug**:
Look at "TX elevation" and "Hops" in debug output.

### 4. Absorption/Loss Calculations

**Symptom**: Signal levels differ by >10 dB

**Possible Causes**:
- D-layer absorption model
- Ground reflection loss
- Free space loss calculation

**How to Debug**:
Examine "Total loss" breakdown in detailed output.

## Validation Results File

Results are saved to `validation_results.json`:

```json
{
  "timestamp": "2025-11-14T15:30:00Z",
  "summary": {
    "total": 16,
    "passed": 12,
    "failed": 4,
    "pass_rate": 75.0
  },
  "tolerance": {
    "reliability": 15.0,
    "snr": 5.0,
    "muf": 2.0
  },
  "results": [
    {
      "region": "UK",
      "band": "20m",
      "freq_mhz": 14.150,
      "utc_hour": 12,
      "local": { "reliability": 75.0, "snr": 15.2, ... },
      "voacap": { "reliability": 78.0, "snr_db": 16.1, ... },
      "comparison": {
        "match": true,
        "differences": [],
        "metrics": { ... }
      }
    }
  ]
}
```

## Troubleshooting

### proppy.net Connection Errors

If you see "Proppy.net API timeout":
- Check internet connectivity
- Proppy.net may be down or rate-limiting
- Wait 30 seconds and try again
- Use `--hours` to test fewer time slots

### Rate Limiting

The script includes 2-second delays between requests to be respectful to proppy.net. Testing many combinations will take time:
- 4 regions × 4 bands × 1 hour = 16 tests = ~32 seconds
- 4 regions × 4 bands × 4 hours = 64 tests = ~2 minutes

### Memory Issues

For very large validation runs:
```bash
python3 validate_predictions.py --regions UK --bands 20m --hours 0 6 12 18
```

Test incrementally rather than all at once.

## Interpreting Failures

### High Failure Rate (>50%)

Possible systematic issues:
1. Check month and SSN parameters match between local and VOACAP
2. Verify TX power and location are identical
3. Check coefficient file integrity (run `pytest tests/`)

### Failures on Specific Bands

- **40m/30m**: D-layer absorption model may differ
- **15m/10m**: F2 layer MUF calculations may differ
- **All bands to one region**: Path-specific ionospheric model issue

### Failures at Specific Times

- **Dawn/dusk**: Terminator effects, gray-line propagation
- **Local noon**: Maximum absorption
- **Local midnight**: Lowest ionospheric height

## Next Steps

1. **Identify patterns** in the validation results
2. **Debug specific cases** that show the largest discrepancies
3. **Check coefficient files** if systematic errors exist
4. **Compare intermediate calculations** to VOACAP documentation
5. **File issues** with detailed debug output for investigation

## Reference Documentation

- [VOACAP Quick Guide](http://www.voacap.com/voacap-quick-guide.pdf)
- [VOACAP Online Manual](http://www.voacap.com/voaarea.html)
- [Proppy.net API](https://www.proppy.net/)
- [DVOACAP GitHub](https://github.com/drmpeg/dvoacap)

## Advanced Debugging

### Compare Coefficient Files

```bash
python3 -c "from src.dvoacap.voacap_parser import VoacapParser; p = VoacapParser(1); print(p.ikim.shape)"
```

Should output: `(16, 25, 8, 11)`

### Verify Path Geometry

```python
from src.dvoacap.path_geometry import GeoPoint
import numpy as np

tx = GeoPoint.from_degrees(44.374, -64.300)
rx = GeoPoint.from_degrees(51.5, -0.1)

from src.dvoacap.path_geometry import PathGeometry
path = PathGeometry.from_locations(tx, rx, long_path=False)

print(f"Distance: {path.dist * 6370:.1f} km")
print(f"Azimuth: {np.rad2deg(path.azim_tr):.1f}°")
```

### Check Ionospheric Profile

```python
from src.dvoacap.prediction_engine import PredictionEngine
import numpy as np

engine = PredictionEngine()
engine.params.month = 11
engine.params.ssn = 100

# Run prediction and examine engine.profile_tr, engine.profile_rx
```

## Automated Testing

Add to your test suite:

```python
def test_voacap_validation():
    """Ensure predictions match VOACAP online within tolerance"""
    from validate_predictions import validate_predictions

    results, passed, failed = validate_predictions(
        test_regions=['UK'],
        test_bands_list=['20m'],
        utc_hours=[12],
        verbose=False
    )

    # Require 80% pass rate
    assert passed / (passed + failed) >= 0.8
```
