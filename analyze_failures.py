#!/usr/bin/env python3
"""Analyze validation failures to identify patterns."""

import subprocess
import re

# Run validation test and capture output
result = subprocess.run(['python3', 'test_voacap_reference.py'],
                       capture_output=True, text=True)
output = result.stdout + result.stderr

# Parse failures
failures = []
current_hour = None
for line in output.split('\n'):
    if 'UTC Hour' in line:
        current_hour = line.split()[2].rstrip(':')
    elif '✗ FAIL' in line:
        freq_match = re.search(r'(\d+\.\d+)\s+MHz', line)
        if freq_match:
            freq = freq_match.group(1)
            failures.append((current_hour, freq))

# Group by frequency
by_freq = {}
for hour, freq in failures:
    if freq not in by_freq:
        by_freq[freq] = []
    by_freq[freq].append(hour)

# Group by hour pattern
by_hour_pattern = {
    'early_night': [],  # 20-24
    'late_night': [],   # 01-04
    'morning': [],      # 05-11
    'afternoon': []     # 12-19
}

print("="*70)
print("FAILURE ANALYSIS")
print("="*70)

print("\n1. FAILURES BY FREQUENCY:")
for freq in sorted(by_freq.keys(), key=float):
    hours = by_freq[freq]
    print(f"   {freq} MHz: {len(hours)} failures at hours {', '.join(sorted(hours))}")

print("\n2. PATTERN ANALYSIS:")

# Low-freq nighttime pattern
low_freq_night = set(by_freq.get('6.10', [])) | set(by_freq.get('7.20', []))
if low_freq_night:
    print(f"   Low-frequency nighttime (6.10, 7.20 MHz): {len(low_freq_night)} hours")
    print(f"   Hours: {', '.join(sorted(low_freq_night))}")

# High-freq all-day pattern
high_freq_all = set(by_freq.get('25.90', []))
if high_freq_all:
    print(f"   High-frequency (25.90 MHz): {len(high_freq_all)} hours")
    print(f"   Hours: {', '.join(sorted(high_freq_all))}")

# Mid-freq spot failures
mid_freqs = [f for f in by_freq.keys() if float(f) > 9.0 and float(f) < 22.0]
if mid_freqs:
    print(f"   Mid-frequency spot failures: {mid_freqs}")
    for freq in mid_freqs:
        print(f"     {freq} MHz: hours {', '.join(sorted(by_freq[freq]))}")

print("\n3. RECOMMENDATIONS:")
if '6.10' in by_freq or '7.20' in by_freq:
    print("   - Low-frequency reliability is systematically under-predicted")
    print("     (DVOACAP predicts ~20-25% lower reliability than VOACAP)")
    print("     → Investigate reliability calculation for low frequencies")
    print("     → Check signal variability (snr10/snr90) calculations")

if '25.90' in by_freq:
    print("   - High-frequency SNR shows large deviations")
    print("     (DVOACAP often predicts 12-47 dB lower SNR than VOACAP)")
    print("     → Investigate loss calculations at high frequencies")
    print("     → Check absorption, MUF probability, or additional loss terms")

print("="*70)
