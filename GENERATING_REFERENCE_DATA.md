# Generating Reference VOACAP Data

This guide explains how to generate reference output from the original VOACAP FORTRAN implementation for validation testing.

## Overview

DVOACAP-Python validation requires reference output from the original VOACAP engine. Test cases are defined in `test_config.json`, and we need to run each through VOACAP to generate baseline data.

## Current Status

| Test Case | Status | Reference File | Priority |
|-----------|--------|----------------|----------|
| ref_001_medium_path | ✓ Active | SampleIO/voacapx.out | Baseline |
| short_001_us_east | Pending | SampleIO/ref_short_001.out | High |
| short_002_europe | Pending | SampleIO/ref_short_002.out | Medium |
| medium_001_transatlantic | Pending | SampleIO/ref_medium_001.out | High |
| medium_002_us_japan | Pending | SampleIO/ref_medium_002.out | Medium |
| long_001_antipodal | Pending | SampleIO/ref_long_001.out | High |
| long_002_australia | Pending | SampleIO/ref_long_002.out | Medium |
| polar_001_arctic | Pending | SampleIO/ref_polar_001.out | Low |
| equatorial_001 | Pending | SampleIO/ref_equatorial_001.out | Medium |
| solar_min_001 | Pending | SampleIO/ref_solar_min_001.out | High |
| solar_max_001 | Pending | SampleIO/ref_solar_max_001.out | High |

## Method 1: Using VOACAP Windows Executable

### Requirements
- Windows PC or Wine on Linux/Mac
- VOACAPW.exe (in `reference/voacap_original/`)
- Input file generator

### Steps for Each Test Case

#### 1. Create VOACAP Input File

For test case `short_001_us_east` (Philadelphia → Boston):

```
LINEMAX   20
COEFFS    CCIR
TIME      4 0 6 12 18     ! UTC hours to test
MONTH     3 3             ! March
SUNSPOT   100 100         ! SSN=100
LABEL     Short Path: Philadelphia to Boston
CIRCUIT   1 Philly-Boston
TRANSMIT  39.95 -75.17    ! Philadelphia
RECEIVE   42.36 -71.06    ! Boston
SYSTEM    100  73  3.00   ! 100W, SNR requirement
FREQUENCY 5 3.5 7.0 14.0 21.0 28.0
FPROB     1.00 0.10 0.90 0.10 0.90
METHOD    30
EXECUTE
QUIT
```

Save as `SampleIO/input_short_001.voa`

#### 2. Run VOACAP

**On Windows:**
```cmd
cd reference\voacap_original
voacapw.exe ..\..\SampleIO\input_short_001.voa
```

**On Linux with Wine:**
```bash
cd reference/voacap_original
wine voacapw.exe ../../SampleIO/input_short_001.voa
```

#### 3. Extract Output

VOACAP will generate `voacapx.out`. Rename and move it:
```bash
mv voacapx.out ../../SampleIO/ref_short_001.out
```

#### 4. Update test_config.json

Change the test case status from "pending_reference" to "active":
```json
{
  "id": "short_001_us_east",
  "status": "active"
}
```

## Method 2: Using VE3NEA's DVOA Online

As an alternative, you can use the web-based VOACAP service:

1. Visit http://www.voacap.com/prediction.html
2. Enter parameters from test_config.json
3. Run prediction
4. Download output file
5. Convert to voacapx.out format if needed

## Method 3: Automated Batch Generation Script

### Python Script to Generate All Input Files

Create `generate_voa_inputs.py`:

```python
#!/usr/bin/env python3
"""Generate VOACAP input files from test_config.json"""

import json
from pathlib import Path

def generate_voa_input(test_case):
    """Generate VOACAP .voa input file from test case config"""

    tx = test_case['tx_location']
    rx = test_case['rx_location']

    # Format UTC hours
    hours_str = ' '.join(str(h) for h in test_case['utc_hours'])

    # Format frequencies
    freqs_str = ' '.join(f"{f:.2f}" for f in test_case['frequencies_mhz'])

    voa_content = f'''LINEMAX   20
COEFFS    CCIR
TIME      {len(test_case['utc_hours'])} {hours_str}
MONTH     {test_case['month']} {test_case['month']}
SUNSPOT   {test_case['ssn']} {test_case['ssn']}
LABEL     {test_case['name']}
CIRCUIT   1 {test_case['id']}
TRANSMIT  {tx['lat']:.2f} {tx['lon']:.2f}
RECEIVE   {rx['lat']:.2f} {rx['lon']:.2f}
SYSTEM    100  73  3.00
FREQUENCY {len(test_case['frequencies_mhz'])} {freqs_str}
FPROB     1.00 0.10 0.90 0.10 0.90
METHOD    30
EXECUTE
QUIT
'''

    return voa_content

def main():
    # Load test config
    with open('test_config.json') as f:
        config = json.load(f)

    # Generate input file for each pending test case
    for tc in config['test_cases']:
        if tc['status'] == 'pending_reference':
            input_file = Path('SampleIO') / f"input_{tc['id']}.voa"
            content = generate_voa_input(tc)

            with open(input_file, 'w') as f:
                f.write(content)

            print(f"Generated: {input_file}")

if __name__ == '__main__':
    main()
```

### Batch Processing Script

Create `run_all_voacap.sh`:

```bash
#!/bin/bash
# Run VOACAP for all pending test cases

cd reference/voacap_original

for input in ../../SampleIO/input_*.voa; do
    basename=$(basename "$input" .voa)
    testid=${basename#input_}

    echo "Running VOACAP for $testid..."

    # Run VOACAP (adjust for Wine if needed)
    ./voacapw.exe "$input"

    # Move output to correct location
    if [ -f voacapx.out ]; then
        mv voacapx.out "../../SampleIO/ref_${testid}.out"
        echo "  ✓ Generated ref_${testid}.out"
    else
        echo "  ✗ Failed to generate output"
    fi
done

cd ../..
echo "Done!"
```

## Validation After Generating References

After generating a new reference file, validate it:

```bash
# Test specific case
python test_voacap_reference.py --test-id short_001_us_east

# Run all active tests
python test_voacap_reference.py --all
```

## Priority Order for Generation

Based on NEXT_STEPS.md goals, generate in this order:

### Week 3 Priority (Need ASAP)
1. **short_001_us_east** - Short path validation
2. **long_001_antipodal** - Long path validation
3. **medium_001_transatlantic** - Additional medium path
4. **solar_min_001** - Low solar activity
5. **solar_max_001** - High solar activity

### Week 4 Priority
6. medium_002_us_japan
7. long_002_australia
8. equatorial_001
9. short_002_europe
10. polar_001_arctic

## Expected Results

Once all reference files are generated:
- **11 test cases** covering diverse propagation scenarios
- **~400-500 total comparisons** (frequencies × hours × test cases)
- **Target: >80% pass rate** across all tests
- **Excellent: >90% pass rate**

## Troubleshooting

### VOACAP Won't Run
- Ensure all coefficient files (CCIR*.BIN) are in same directory
- Check that voacap.dat configuration file exists
- Try running with Wine if on Linux/Mac

### Output Format Different
- Original VOACAP output format may vary by version
- May need to update VoacapReferenceParser in test_voacap_reference.py
- Check that voacapx.out contains all required metrics (SNR, REL, MODE, etc.)

### Wrong Results
- Verify input parameters match test_config.json exactly
- Check VOACAP version (should be VOACAPW v15 or later)
- Ensure CCIR coefficient files are correct version

## Alternative: Using Existing VOACAP Services

If you don't have access to run VOACAP locally:

1. **VOACAP Online Services:**
   - http://www.voacap.com/
   - https://www.hfcc.org/

2. **Ham Radio Tools:**
   - VOACAP GUI tools (Windows)
   - PropNET (has VOACAP backend)

3. **Contact Authors:**
   - Request help from VOACAP community
   - Amateur radio propagation groups

## Documentation References

- Original VOACAP manual: `docs/Original_VOACAP_Manual.pdf`
- Input file format: VOACAP documentation Chapter 3
- Output file format: VOACAP documentation Chapter 5

---

**Note:** Once reference files are generated, update test_config.json to mark tests as "active" so they run automatically in CI/CD.
