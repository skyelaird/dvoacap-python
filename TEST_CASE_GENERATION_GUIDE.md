# Test Case Generation Guide
## DVOACAP-Python Reference Validation

This guide explains how to generate new reference test cases for validating DVOACAP-Python against the original VOACAP implementation.

---

## Overview

To expand test coverage, we need reference outputs from the original VOACAP engine for various propagation scenarios. Each test case consists of:

1. **Input parameters** (path, frequency, time, solar conditions)
2. **Reference output** from original VOACAP
3. **Test configuration** added to `tests/test_reference_validation.py`

---

## Prerequisites

### Option 1: VOACAPL (Linux/Mac)

Install VOACAPL (Linux-compatible VOACAP):

```bash
# Install dependencies
sudo apt-get install gfortran make

# Clone and build VOACAPL
git clone https://github.com/jawatson/voacapl.git
cd voacapl
./configure
make
sudo make install
```

### Option 2: VOACAP Online API

Contact voacap.com or use proppy.net API:
- Request API access for research/educational use
- Note: Automated access may be restricted

### Option 3: Windows VOACAP (Voacapwin.exe)

Run original Voacapwin.exe on Windows:
- Download from voacap.com
- Run predictions manually
- Export output files

---

## Generating Reference Data

### Step 1: Define Test Case Parameters

For each new test case, define:

```python
TestCase(
    name="test_case_name",
    description="Brief description",
    tx_lat=<latitude>,      # Transmitter latitude (degrees, -90 to 90)
    tx_lon=<longitude>,     # Transmitter longitude (degrees, -180 to 180)
    rx_lat=<latitude>,      # Receiver latitude
    rx_lon=<longitude>,     # Receiver longitude
    distance_km=<distance>, # Approximate path distance
    month=<month>,          # 1-12
    ssn=<ssn>,              # Sunspot number (0-250)
    reference_file="SampleIO/reference_<name>/voacapx.out",
    tx_power_w=500000,      # 500 kW (VOACAP default)
    enabled=True
)
```

### Step 2: Create Input File for VOACAP

Create VOACAP input file (e.g., `voacap_input.txt`):

```
Circuit: TX → RX
Path:    <tx_lat> <tx_lon> → <rx_lat> <rx_lon>
Month:   <month>
SSN:     <ssn>
Frequencies: 6.07 7.20 9.70 11.85 13.70 15.35 17.73 21.65 25.89
UTC Hours: 1-24
Power: 500 kW
Antenna: Isotropic (both TX and RX)
```

### Step 3: Run VOACAP

#### Using VOACAPL (Linux):

```bash
cd SampleIO/reference_<name>/

# Create VOACAP input card file
cat > voacap.dat <<EOF
LINEMAX    1
COEFFS     CCIR
TIME       1 1 24
MONTH      <month> <month> 1
SUNSPOT    <ssn> <ssn> 1
CIRCUIT    1
SYSTEM     500 145 3
FPROB      1.00 1.00 1.00 1.00
ANTENNA    1 0 0
ANTENNA    1 0 0
TXCCT      <tx_lat> <tx_lon>
RXCCT      <rx_lat> <rx_lon>
FREQS      9 6.07 7.20 9.70 11.85 13.70 15.35 17.73 21.65 25.89
QUIT
EOF

# Run VOACAP
voacapl voacap

# Output will be in voacapx.out
ls -la voacapx.out
```

#### Using VOACAP Online:

```bash
# Create Python script to call API
python3 scripts/generate_reference.py \
    --tx-lat <tx_lat> --tx-lon <tx_lon> \
    --rx-lat <rx_lat> --rx-lon <rx_lon> \
    --month <month> --ssn <ssn> \
    --output SampleIO/reference_<name>/voacapx.out
```

#### Using Windows Voacapwin.exe:

1. Open Voacapwin.exe
2. Set parameters:
   - Transmitter: lat/lon
   - Receiver: lat/lon
   - Month: <month>
   - SSN: <ssn>
   - Frequencies: 6.07, 7.20, 9.70, 11.85, 13.70, 15.35, 17.73, 21.65, 25.89
   - UTC Hours: 1-24
   - Power: 500 kW
   - Antenna: Isotropic
3. Run prediction
4. Export output to `voacapx.out`

### Step 4: Verify Reference File

Check that reference file is valid:

```bash
# Check file exists
ls -la SampleIO/reference_<name>/voacapx.out

# Check file has content
wc -l SampleIO/reference_<name>/voacapx.out

# Quick parse test
python3 -c "
from pathlib import Path
import sys
sys.path.insert(0, 'tests')
from test_reference_validation import VoacapReferenceParser

parser = VoacapReferenceParser()
data = parser.parse_voacapx_out(Path('SampleIO/reference_<name>/voacapx.out'))

print(f\"Metadata: {data['metadata']}\")
print(f\"Predictions: {len(data['predictions'])} hours\")
print(f\"Frequencies: {data['predictions'][0]['frequencies']}\")
"
```

### Step 5: Add to Test Suite

Edit `tests/test_reference_validation.py` and add to `TEST_CASES`:

```python
TestCase(
    name="<test_case_name>",
    description="<description>",
    tx_lat=<tx_lat>, tx_lon=<tx_lon>,
    rx_lat=<rx_lat>, rx_lon=<rx_lon>,
    distance_km=<distance>,
    month=<month>,
    ssn=<ssn>,
    reference_file="SampleIO/reference_<name>/voacapx.out",
    enabled=True  # Set to True when reference file is ready
),
```

### Step 6: Run Tests

```bash
# Run all tests
pytest tests/test_reference_validation.py -v

# Run specific test case
pytest tests/test_reference_validation.py::TestReferenceValidation::test_predictions_within_tolerance[<test_case_name>] -v

# Run with verbose output
pytest tests/test_reference_validation.py -v -s
```

---

## Recommended Test Cases

### Priority 1: Path Distance Diversity

#### Short Path (<1000 km)
```python
TestCase(
    name="philadelphia_boston_ssn100",
    description="Short path (430km), NVIS/E-layer",
    tx_lat=39.95, tx_lon=-75.17,  # Philadelphia
    rx_lat=42.36, rx_lon=-71.06,  # Boston
    distance_km=430,
    month=6,
    ssn=100,
    reference_file="SampleIO/reference_short_path/voacapx.out",
    enabled=False  # Enable after generating reference
)
```

#### Long Path (>10,000 km)
```python
TestCase(
    name="philadelphia_tokyo_ssn100",
    description="Long path (10,900km), multi-hop F2",
    tx_lat=39.95, tx_lon=-75.17,  # Philadelphia
    rx_lat=35.68, rx_lon=139.69,  # Tokyo
    distance_km=10900,
    month=6,
    ssn=100,
    reference_file="SampleIO/reference_long_path/voacapx.out",
    enabled=False
)
```

#### Very Long Path (Antipodal)
```python
TestCase(
    name="philadelphia_perth_ssn100",
    description="Very long path (18,700km), near-antipodal",
    tx_lat=39.95, tx_lon=-75.17,  # Philadelphia
    rx_lat=-31.95, rx_lon=115.86, # Perth, Australia
    distance_km=18700,
    month=6,
    ssn=100,
    reference_file="SampleIO/reference_antipodal/voacapx.out",
    enabled=False
)
```

### Priority 2: Solar Condition Variations

#### Solar Minimum
```python
TestCase(
    name="tangier_belgrade_ssn10",
    description="Medium path, solar minimum",
    tx_lat=35.80, tx_lon=-5.90,
    rx_lat=44.90, rx_lon=20.50,
    distance_km=2440,
    month=6,
    ssn=10,  # Solar minimum
    reference_file="SampleIO/reference_ssn10/voacapx.out",
    enabled=False
)
```

#### Solar Maximum
```python
TestCase(
    name="tangier_belgrade_ssn200",
    description="Medium path, solar maximum",
    tx_lat=35.80, tx_lon=-5.90,
    rx_lat=44.90, rx_lon=20.50,
    distance_km=2440,
    month=6,
    ssn=200,  # Solar maximum
    reference_file="SampleIO/reference_ssn200/voacapx.out",
    enabled=False
)
```

### Priority 3: Seasonal Variations

#### Winter
```python
TestCase(
    name="tangier_belgrade_december",
    description="Medium path, winter solstice",
    tx_lat=35.80, tx_lon=-5.90,
    rx_lat=44.90, rx_lon=20.50,
    distance_km=2440,
    month=12,  # December
    ssn=100,
    reference_file="SampleIO/reference_winter/voacapx.out",
    enabled=False
)
```

#### Equinox
```python
TestCase(
    name="tangier_belgrade_march",
    description="Medium path, equinox",
    tx_lat=35.80, tx_lon=-5.90,
    rx_lat=44.90, rx_lon=20.50,
    distance_km=2440,
    month=3,  # March
    ssn=100,
    reference_file="SampleIO/reference_equinox/voacapx.out",
    enabled=False
)
```

### Priority 4: Geographic Diversity

#### Trans-Pacific
```python
TestCase(
    name="san_francisco_sydney_ssn100",
    description="Trans-Pacific (11,900km)",
    tx_lat=37.77, tx_lon=-122.42,  # San Francisco
    rx_lat=-33.87, rx_lon=151.21,  # Sydney
    distance_km=11900,
    month=6,
    ssn=100,
    reference_file="SampleIO/reference_trans_pacific/voacapx.out",
    enabled=False
)
```

#### Trans-Atlantic
```python
TestCase(
    name="new_york_london_ssn100",
    description="Trans-Atlantic (5,570km)",
    tx_lat=40.71, tx_lon=-74.01,   # New York
    rx_lat=51.51, rx_lon=-0.13,    # London
    distance_km=5570,
    month=6,
    ssn=100,
    reference_file="SampleIO/reference_trans_atlantic/voacapx.out",
    enabled=False
)
```

---

## Directory Structure

Organize reference files:

```
SampleIO/
├── voacapx.out                          # Existing baseline
├── input.json                           # Existing baseline
├── reference_short_path/
│   ├── voacapx.out
│   ├── input.json
│   └── README.md
├── reference_long_path/
│   ├── voacapx.out
│   ├── input.json
│   └── README.md
├── reference_ssn10/
│   ├── voacapx.out
│   └── ...
├── reference_ssn200/
│   └── ...
└── reference_winter/
    └── ...
```

Each directory should include:
- `voacapx.out` - Reference output
- `input.json` - Input parameters (for documentation)
- `README.md` - Description of test case

---

## Automation Script (Optional)

Create `scripts/generate_reference.py`:

```python
#!/usr/bin/env python3
"""
Generate reference VOACAP output for test cases

Usage:
    python3 scripts/generate_reference.py \
        --tx-lat 39.95 --tx-lon -75.17 \
        --rx-lat 42.36 --rx-lon -71.06 \
        --month 6 --ssn 100 \
        --output SampleIO/reference_short_path/voacapx.out
"""

import argparse
import subprocess
from pathlib import Path


def generate_voacap_input(tx_lat, tx_lon, rx_lat, rx_lon, month, ssn):
    """Generate VOACAP input card file"""
    return f"""LINEMAX    1
COEFFS     CCIR
TIME       1 1 24
MONTH      {month} {month} 1
SUNSPOT    {ssn} {ssn} 1
CIRCUIT    1
SYSTEM     500 145 3
FPROB      1.00 1.00 1.00 1.00
ANTENNA    1 0 0
ANTENNA    1 0 0
TXCCT      {tx_lat} {tx_lon}
RXCCT      {rx_lat} {rx_lon}
FREQS      9 6.07 7.20 9.70 11.85 13.70 15.35 17.73 21.65 25.89
QUIT
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tx-lat', type=float, required=True)
    parser.add_argument('--tx-lon', type=float, required=True)
    parser.add_argument('--rx-lat', type=float, required=True)
    parser.add_argument('--rx-lon', type=float, required=True)
    parser.add_argument('--month', type=int, required=True)
    parser.add_argument('--ssn', type=int, required=True)
    parser.add_argument('--output', type=str, required=True)

    args = parser.parse_args()

    # Create output directory
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Generate input
    input_content = generate_voacap_input(
        args.tx_lat, args.tx_lon,
        args.rx_lat, args.rx_lon,
        args.month, args.ssn
    )

    # Write input file
    input_file = output_path.parent / 'voacap.dat'
    with open(input_file, 'w') as f:
        f.write(input_content)

    print(f"Input file created: {input_file}")

    # Run VOACAPL (if available)
    try:
        result = subprocess.run(
            ['voacapl', str(input_file.stem)],
            cwd=output_path.parent,
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print(f"Reference output generated: {output_path}")
        else:
            print(f"Error running VOACAPL: {result.stderr}")
            print("Please run VOACAP manually with the input file.")

    except FileNotFoundError:
        print("VOACAPL not found. Please run VOACAP manually.")


if __name__ == '__main__':
    main()
```

---

## Validation Checklist

Before adding a new test case:

- [ ] Reference file generated and validated
- [ ] Reference file contains correct path parameters
- [ ] Reference file contains 24 UTC hours
- [ ] Reference file contains expected frequencies
- [ ] Test case added to `TEST_CASES` in `test_reference_validation.py`
- [ ] Test case `enabled=True`
- [ ] Tests run successfully: `pytest tests/test_reference_validation.py::TestReferenceValidation -k "<test_name>"`
- [ ] Pass rate documented
- [ ] README.md created in reference directory

---

## Troubleshooting

### Issue: VOACAP output format different

**Solution:** Check parser in `VoacapReferenceParser.parse_voacapx_out()`. May need to adjust regex patterns for different VOACAP versions.

### Issue: Missing frequencies in output

**Solution:** Verify input file specifies all frequencies. Check that frequencies aren't over the MUF (VOACAP omits unusable frequencies).

### Issue: No predictions for certain hours

**Solution:** Some paths/frequencies may have no valid propagation modes. This is expected and tests should skip these cases.

### Issue: Large deviations from DVOACAP

**Solution:** This indicates bugs in DVOACAP implementation. Document the deviations and investigate root cause.

---

## Next Steps

After generating reference data:

1. Run tests: `pytest tests/test_reference_validation.py -v`
2. Analyze results: Check pass rates, identify patterns
3. Document findings: Update `VALIDATION_ANALYSIS_<date>.md`
4. Fix bugs: Address systematic deviations
5. Re-test: Verify fixes don't break existing tests

---

**Last Updated:** 2025-11-14
**Maintainer:** DVOACAP-Python Development Team
