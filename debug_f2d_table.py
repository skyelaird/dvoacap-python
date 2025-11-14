#!/usr/bin/env python3
"""Debug F2D table values."""

import sys
sys.path.insert(0, 'src')

import numpy as np
from dvoacap.fourier_maps import FourierMaps, RinD

# Setup fourier maps
maps = FourierMaps()
maps.set_conditions(month=6, ssn=100, utc_fraction=6/24.0)

# Test parameters from hour 06
muf = 19.06
lat = np.deg2rad(44.33)  # Approximate midpoint latitude
local_time = 0.25  # Approximate local time for midpoint at UTC 06

print("="*70)
print("F2D TABLE VALUE DEBUG")
print("="*70)

# Calculate indices (same as in compute_f2_deviation)
t = int(local_time * 6 + 0.55)
if t >= 6:
    t = 0

l = int(8.5 - abs(lat) * 0.1 / RinD)
l = max(0, min(7, l))

ssn = 100
if ssn <= 50:
    s = 0
elif ssn <= 100:
    s = 1
else:
    s = 2

if lat <= 0:
    s += 3

print(f"\nParameters:")
print(f"  MUF: {muf:.2f} MHz")
print(f"  Latitude: {np.rad2deg(lat):.2f}°")
print(f"  Local time: {local_time:.4f} ({local_time*24:.1f} hours)")
print(f"  SSN: {ssn}")

print(f"\nTable indices:")
print(f"  T (time): {t}")
print(f"  S (SSN/hemisphere): {s}")
print(f"  L (latitude, below MUF): {l}")
print(f"  L (latitude, above MUF): {l+8}")

# Get F2D values for both above and below
f2d_below = maps.f2d[t, s, l]
f2d_above = maps.f2d[t, s, l + 8]

print(f"\nF2D table values:")
print(f"  F2D[{t},{s},{l}] (below MUF): {f2d_below:.6f}")
print(f"  F2D[{t},{s},{l+8}] (above MUF): {f2d_above:.6f}")

# Calculate deviations
from dvoacap.muf_calculator import NORM_DECILE
dev_below = abs((1 - f2d_below) * muf) * (1 / NORM_DECILE)
dev_above = abs((1 - f2d_above) * muf) * (1 / NORM_DECILE)

print(f"\nCalculated deviations:")
print(f"  Below MUF: abs((1 - {f2d_below:.6f}) * {muf:.2f}) / {NORM_DECILE:.6f} = {dev_below:.4f} MHz")
print(f"  Above MUF: abs((1 - {f2d_above:.6f}) * {muf:.2f}) / {NORM_DECILE:.6f} = {dev_above:.4f} MHz")

# Compare with actual function output
sig_lo = maps.compute_f2_deviation(muf, lat, local_time, False)
sig_hi = maps.compute_f2_deviation(muf, lat, local_time, True)

print(f"\nFunction outputs:")
print(f"  Sigma_lo (below MUF): {sig_lo:.4f} MHz")
print(f"  Sigma_hi (above MUF): {sig_hi:.4f} MHz")

print("\n" + "="*70)
