#!/usr/bin/env python3
"""Analyze validation results to identify failure patterns"""

import json
from collections import defaultdict
from pathlib import Path

# Load validation results
with open('validation_reference_results.json', 'r') as f:
    data = json.load(f)

print("=" * 80)
print("VALIDATION FAILURE ANALYSIS")
print("=" * 80)
print()

# Overall summary
print(f"Total tests: {data['summary']['total']}")
print(f"Pass rate: {data['summary']['pass_rate']:.1f}%")
print()

# Categorize failures
snr_failures = []
rel_failures = []
both_failures = []
other_failures = []

for comp in data['comparisons']:
    if not comp['passed']:
        has_snr_error = any('SNR' in err for err in comp['errors'])
        has_rel_error = any('Reliability' in err for err in comp['errors'])

        if has_snr_error and has_rel_error:
            both_failures.append(comp)
        elif has_snr_error:
            snr_failures.append(comp)
        elif has_rel_error:
            rel_failures.append(comp)
        else:
            other_failures.append(comp)

print("FAILURE BREAKDOWN:")
print(f"  SNR only:              {len(snr_failures)} ({100*len(snr_failures)/data['summary']['failed']:.1f}%)")
print(f"  Reliability only:      {len(rel_failures)} ({100*len(rel_failures)/data['summary']['failed']:.1f}%)")
print(f"  Both SNR & Reliability: {len(both_failures)} ({100*len(both_failures)/data['summary']['failed']:.1f}%)")
print(f"  Other:                 {len(other_failures)} ({100*len(other_failures)/data['summary']['failed']:.1f}%)")
print()

# Analyze SNR errors
if snr_failures or both_failures:
    all_snr_errors = snr_failures + both_failures
    snr_diffs = []
    for comp in all_snr_errors:
        if 'SNR' in comp['metrics']:
            diff = comp['metrics']['SNR']['diff']
            snr_diffs.append({
                'diff': diff,
                'dvoacap': comp['metrics']['SNR']['dvoacap'],
                'voacap': comp['metrics']['SNR']['voacap'],
                'freq': comp['freq_mhz'],
                'hour': comp['utc_hour']
            })

    snr_diffs.sort(key=lambda x: x['diff'], reverse=True)

    print(f"SNR ERROR STATISTICS ({len(snr_diffs)} failures):")
    avg_diff = sum(x['diff'] for x in snr_diffs) / len(snr_diffs)
    max_diff = snr_diffs[0]
    print(f"  Average deviation: {avg_diff:.1f} dB")
    print(f"  Max deviation: {max_diff['diff']:.1f} dB (DVOACAP: {max_diff['dvoacap']:.1f}, VOACAP: {max_diff['voacap']:.1f})")
    print()

    # Show top 10 worst SNR errors
    print("  Top 10 worst SNR errors:")
    for i, err in enumerate(snr_diffs[:10], 1):
        print(f"    {i}. {err['freq']:6.2f} MHz @ {err['hour']:02d}00: "
              f"Δ={err['diff']:5.1f} dB (DVOACAP: {err['dvoacap']:6.1f}, VOACAP: {err['voacap']:6.1f})")
    print()

# Analyze Reliability errors
if rel_failures or both_failures:
    all_rel_errors = rel_failures + both_failures
    rel_diffs = []
    for comp in all_rel_errors:
        if 'REL' in comp['metrics']:
            diff = comp['metrics']['REL']['diff']
            rel_diffs.append({
                'diff': diff,
                'dvoacap': comp['metrics']['REL']['dvoacap'],
                'voacap': comp['metrics']['REL']['voacap'],
                'freq': comp['freq_mhz'],
                'hour': comp['utc_hour']
            })

    rel_diffs.sort(key=lambda x: x['diff'], reverse=True)

    print(f"RELIABILITY ERROR STATISTICS ({len(rel_diffs)} failures):")
    avg_diff = sum(x['diff'] for x in rel_diffs) / len(rel_diffs)
    max_diff = rel_diffs[0]
    print(f"  Average deviation: {avg_diff:.1f}%")
    print(f"  Max deviation: {max_diff['diff']:.1f}% (DVOACAP: {max_diff['dvoacap']:.1f}%, VOACAP: {max_diff['voacap']:.1f}%)")
    print()

    # Show top 10 worst REL errors
    print("  Top 10 worst Reliability errors:")
    for i, err in enumerate(rel_diffs[:10], 1):
        print(f"    {i}. {err['freq']:6.2f} MHz @ {err['hour']:02d}00: "
              f"Δ={err['diff']:5.1f}% (DVOACAP: {err['dvoacap']:5.1f}%, VOACAP: {err['voacap']:5.1f}%)")
    print()

# Analyze by frequency
freq_stats = defaultdict(lambda: {'total': 0, 'passed': 0, 'failed': 0})
for comp in data['comparisons']:
    freq = comp['freq_mhz']
    freq_stats[freq]['total'] += 1
    if comp['passed']:
        freq_stats[freq]['passed'] += 1
    else:
        freq_stats[freq]['failed'] += 1

print("PASS RATE BY FREQUENCY:")
for freq in sorted(freq_stats.keys()):
    stats = freq_stats[freq]
    pass_rate = 100 * stats['passed'] / stats['total']
    print(f"  {freq:6.2f} MHz: {pass_rate:5.1f}% ({stats['passed']}/{stats['total']})")
print()

# Analyze by UTC hour
hour_stats = defaultdict(lambda: {'total': 0, 'passed': 0, 'failed': 0})
for comp in data['comparisons']:
    hour = comp['utc_hour']
    hour_stats[hour]['total'] += 1
    if comp['passed']:
        hour_stats[hour]['passed'] += 1
    else:
        hour_stats[hour]['failed'] += 1

print("PASS RATE BY UTC HOUR:")
for hour in sorted(hour_stats.keys()):
    stats = hour_stats[hour]
    pass_rate = 100 * stats['passed'] / stats['total']
    print(f"  {hour:02d}00: {pass_rate:5.1f}% ({stats['passed']}/{stats['total']})")
print()

print("=" * 80)
