#!/usr/bin/env python3
"""
Quick test to verify MODE array alignment fix
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from test_voacap_reference import VoacapReferenceParser

def test_mode_alignment():
    """Test that MODE array has same length as frequency array"""

    sample_dir = Path(__file__).parent / 'SampleIO'
    voacapx_file = sample_dir / 'voacapx.out'

    if not voacapx_file.exists():
        print(f"ERROR: Reference file not found: {voacapx_file}")
        return False

    parser = VoacapReferenceParser()
    reference = parser.parse_voacapx_out(voacapx_file)

    print("Testing MODE array alignment...")
    print("=" * 80)

    all_good = True

    for pred_block in reference['predictions']:
        utc_hour = int(pred_block['utc_hour'])
        num_freqs = len(pred_block['frequencies'])
        num_modes = len(pred_block['metrics'].get('MODE', []))
        num_snrs = len(pred_block['metrics'].get('SNR', []))

        if num_modes != num_freqs:
            print(f"❌ UTC Hour {utc_hour}: MISALIGNED!")
            print(f"   Frequencies: {num_freqs} elements")
            print(f"   MODE:        {num_modes} elements")
            print(f"   SNR:         {num_snrs} elements")
            print(f"   Frequencies: {pred_block['frequencies']}")
            print(f"   MODE:        {pred_block['metrics'].get('MODE', [])}")
            print()
            all_good = False
        else:
            # Check for hour 7 specifically (has "2 E" modes)
            if utc_hour == 7:
                print(f"✓ UTC Hour {utc_hour}: ALIGNED!")
                print(f"   Frequencies: {num_freqs} elements: {pred_block['frequencies']}")
                print(f"   MODE:        {num_modes} elements: {pred_block['metrics'].get('MODE', [])}")
                print(f"   SNR:         {num_snrs} elements: {pred_block['metrics'].get('SNR', [])[:num_freqs]}")
                print()

                # Verify "2 E" is kept as single element
                modes = pred_block['metrics'].get('MODE', [])
                if '2 E' in modes or '2E' in modes:
                    print("   ✓ MODE '2 E' preserved as single element!")
                    print()

    if all_good:
        print("=" * 80)
        print("✓ ALL TESTS PASSED: MODE arrays are correctly aligned!")
        print("=" * 80)
        return True
    else:
        print("=" * 80)
        print("❌ ALIGNMENT ISSUES DETECTED")
        print("=" * 80)
        return False

if __name__ == '__main__':
    success = test_mode_alignment()
    sys.exit(0 if success else 1)
