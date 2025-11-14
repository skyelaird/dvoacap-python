#!/usr/bin/env python3
"""
Simple test: What if sigma values should be divided by 10?
The F2D table might be giving values that need to be scaled.
"""

import sys
sys.path.insert(0, 'src')

import numpy as np

# Test the cumulative normal function
def _cumulative_normal(x: float) -> float:
    """Cumulative normal distribution."""
    C = [0.196854, 0.115194, 0.000344, 0.019527]
    y = min(5.0, abs(x))
    result = 1.0 + y * (C[0] + y * (C[1] + y * (C[2] + y * C[3])))
    result = result ** 4
    result = 0.5 / result
    if x > 0:
        result = 1.0 - result
    return result

# Our current values
freq = 25.90
mode_muf = 18.45
median = 19.06
sig_lo = 1.9360
sig_hi = 2.0850

z = freq - mode_muf  # 7.45

print("="*70)
print("TESTING DIFFERENT SIGMA SCALING")
print("="*70)

for scale_factor in [1.0, 0.1, 0.01, 2.0]:
    scaled_sig_hi = sig_hi * scale_factor

    normalizer = max(0.001, mode_muf * scaled_sig_hi / median)
    z_norm = z / normalizer
    prob = 1.0 - _cumulative_normal(z_norm)

    print(f"\nScale factor: {scale_factor}")
    print(f"  Sigma_hi: {scaled_sig_hi:.6f}")
    print(f"  Normalizer: {normalizer:.6f}")
    print(f"  Z_normalized: {z_norm:.6f}")
    print(f"  Probability: {prob:.6f} ({prob*100:.4f}%)")

    if 0.015 < prob < 0.025:
        print(f"  *** CLOSE TO VOACAP VALUE (0.02) ***")

print("\n" + "="*70)
