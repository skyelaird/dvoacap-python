#!/usr/bin/env python3
"""Debug MUFday calculation in detail."""

import sys
sys.path.insert(0, 'src')

import numpy as np
from dvoacap.prediction_engine import PredictionEngine
from dvoacap.path_geometry import GeoPoint
from dvoacap.muf_calculator import calc_muf_prob

# Setup engine
engine = PredictionEngine()
engine.params.ssn = 100
engine.params.month = 6
engine.params.tx_location = GeoPoint(lat=np.deg2rad(35.80), lon=np.deg2rad(-5.90))
rx_location = GeoPoint(lat=np.deg2rad(44.90), lon=np.deg2rad(20.50))

# Test hour 06 where we see MUFday error
utc_time = 6 / 24.0
freq = 25.90

# Run prediction
engine.predict(rx_location, utc_time, [freq])

# Get MUF info for F2 layer
from dvoacap.prediction_engine import IonosphericLayer
muf_info = engine.circuit_muf.muf_info[IonosphericLayer.F2.name]

print("="*70)
print(f"MUF DAY CALCULATION DEBUG for {freq:.2f} MHz at Hour 06")
print("="*70)

print(f"\nCircuit MUF Info (F2 layer):")
print(f"  MUF: {muf_info.muf:.2f} MHz")
print(f"  FOT: {muf_info.fot:.2f} MHz")
print(f"  HPF: {muf_info.hpf:.2f} MHz")
print(f"  Sigma Lo: {muf_info.sig_lo:.4f}")
print(f"  Sigma Hi: {muf_info.sig_hi:.4f}")
print(f"  Ref vert freq: {muf_info.ref.vert_freq:.2f} MHz")
print(f"  Ref true height: {muf_info.ref.true_height:.2f} km")
print(f"  Ref virt height: {muf_info.ref.virt_height:.2f} km")

if engine._best_mode:
    mode = engine._best_mode
    print(f"\nBest Mode Info:")
    print(f"  Hop distance: {mode.hop_dist:.6f} rad ({mode.hop_dist * 6370:.1f} km)")
    print(f"  Hop count: {mode.hop_cnt}")
    print(f"  Elevation: {np.deg2rad(mode.ref.elevation):.4f} rad ({np.rad2deg(mode.ref.elevation):.2f} deg)")

    # Recalculate mode_muf step by step
    mode_muf_elev = engine._calc_elevation_angle(mode.hop_dist, muf_info.ref.virt_height)
    print(f"\n  Mode MUF elevation: {mode_muf_elev:.6f} rad ({np.rad2deg(mode_muf_elev):.2f} deg)")

    cos_inc = engine._cos_of_incidence(mode_muf_elev, muf_info.ref.true_height)
    print(f"  Cos of incidence: {cos_inc:.6f}")
    print(f"  Secant (1/cos): {1/cos_inc:.6f}")

    mode_muf = muf_info.ref.vert_freq / cos_inc
    print(f"  Mode MUF: {muf_info.ref.vert_freq:.2f} / {cos_inc:.6f} = {mode_muf:.2f} MHz")

    # Calculate MUFday
    print(f"\nMUF Probability Calculation:")
    print(f"  Inputs:")
    print(f"    frequency = {freq:.2f} MHz")
    print(f"    mode_muf = {mode_muf:.2f} MHz")
    print(f"    median (circuit MUF) = {muf_info.muf:.2f} MHz")
    print(f"    sigma_lo = {muf_info.sig_lo:.4f}")
    print(f"    sigma_hi = {muf_info.sig_hi:.4f}")

    z = freq - mode_muf
    print(f"\n  z = freq - mode_muf = {freq:.2f} - {mode_muf:.2f} = {z:.2f}")

    sig = muf_info.sig_hi if z > 0 else muf_info.sig_lo
    print(f"  sig = {'sig_hi' if z > 0 else 'sig_lo'} = {sig:.4f}")

    normalizer = max(0.001, mode_muf * sig / muf_info.muf)
    print(f"  normalizer = mode_muf * sig / median = {mode_muf:.2f} * {sig:.4f} / {muf_info.muf:.2f} = {normalizer:.6f}")

    z_norm = z / normalizer
    print(f"  z_normalized = z / normalizer = {z:.2f} / {normalizer:.6f} = {z_norm:.6f}")

    mufday = calc_muf_prob(freq, mode_muf, muf_info.muf, muf_info.sig_lo, muf_info.sig_hi)
    print(f"\n  MUFday = {mufday:.6f} ({mufday*100:.4f}%)")

    print(f"\nActual MUFday from prediction: {mode.signal.muf_day:.6f}")

print("\n" + "="*70)
print("REFERENCE VALUE (from VOACAP):")
print("  MUFday = 0.02 (2%)")
print("="*70)
