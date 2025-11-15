#!/usr/bin/env python3
"""Generate VOACAP input files from test_config.json

This script reads the test configuration and generates .voa input files
that can be run through the original VOACAP FORTRAN engine to produce
reference output for validation.

Usage:
    python generate_voa_inputs.py

Output:
    Creates SampleIO/input_*.voa files for each pending test case
"""

import json
from pathlib import Path


def generate_voa_input(test_case):
    """Generate VOACAP .voa input file from test case config

    Args:
        test_case: Test case dict from test_config.json

    Returns:
        str: VOACAP input file content
    """

    tx = test_case['tx_location']
    rx = test_case['rx_location']

    # Format UTC hours
    hours = test_case['utc_hours']
    hours_str = ' '.join(str(h if h != 0 else 24) for h in hours)  # VOACAP uses 24 instead of 0

    # Format frequencies
    freqs = test_case['frequencies_mhz']
    freqs_str = ' '.join(f"{f:.2f}" for f in freqs)

    # VOACAP input format
    voa_content = f'''LINEMAX   20
COEFFS    CCIR
TIME      {len(hours)} {hours_str}
MONTH     {test_case['month']} {test_case['month']}
SUNSPOT   {test_case['ssn']} {test_case['ssn']}
LABEL     {test_case['name']}
CIRCUIT   1 {test_case['id']}
TRANSMIT  {tx['lat']:.2f} {tx['lon']:.2f}
RECEIVE   {rx['lat']:.2f} {rx['lon']:.2f}
SYSTEM    100  73  3.00
FREQUENCY {len(freqs)} {freqs_str}
FPROB     1.00 0.10 0.90 0.10 0.90
METHOD    30
EXECUTE
QUIT
'''

    return voa_content


def main():
    """Generate input files for all pending test cases"""

    # Load test config
    config_file = Path('test_config.json')
    if not config_file.exists():
        print(f"Error: {config_file} not found")
        return 1

    with open(config_file) as f:
        config = json.load(f)

    # Ensure SampleIO directory exists
    output_dir = Path('SampleIO')
    output_dir.mkdir(exist_ok=True)

    # Generate input file for each test case
    generated = 0
    skipped = 0

    for tc in config['test_cases']:
        test_id = tc['id']
        input_file = output_dir / f"input_{test_id}.voa"

        if tc['status'] == 'active':
            print(f"⊙ {test_id:25s} - already has reference data, skipping")
            skipped += 1
            continue

        # Generate input content
        content = generate_voa_input(tc)

        # Write to file
        with open(input_file, 'w') as f:
            f.write(content)

        print(f"✓ {test_id:25s} → {input_file}")
        generated += 1

    print(f"\n{'='*70}")
    print(f"Generated {generated} input files")
    print(f"Skipped {skipped} active test cases")
    print(f"\nNext steps:")
    print(f"  1. Run VOACAP with these input files (see GENERATING_REFERENCE_DATA.md)")
    print(f"  2. Move output files to SampleIO/ref_<testid>.out")
    print(f"  3. Update test_config.json status to 'active'")
    print(f"  4. Run: python test_voacap_reference.py --all")

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
