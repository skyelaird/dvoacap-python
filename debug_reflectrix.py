#!/usr/bin/env python3
"""Debug reflectrix calculation for over-the-MUF frequencies"""

import sys
sys.path.insert(0, 'src')

import numpy as np
from dvoacap.prediction_engine import PredictionEngine
from dvoacap.path_geometry import GeoPoint
from dvoacap.reflectrix import Reflectrix

# Monkey-patch Reflectrix.compute to see what's happening
original_compute = Reflectrix.compute

def debug_compute(self, freq_mhz, profile):
    """Debug version of Reflectrix.compute"""
    result = original_compute(self, freq_mhz, profile)

    print(f"\nREFLECTRIX COMPUTATION FOR {freq_mhz:.2f} MHz:")
    print(f"  foE:          {profile.e.fo:.2f} MHz")
    print(f"  foF1:         {profile.f1.fo:.2f} MHz")
    print(f"  foF2:         {profile.f2.fo:.2f} MHz")
    print(f"  Reflections found: {len(self.refl)}")
    print(f"  Skip distance:     {self.skip_distance * 6370:.1f} km")
    print(f"  Max distance:      {self.max_distance * 6370:.1f} km")

    if len(self.refl) == 0:
        print(f"  WARNING: No reflections found (frequency above all layer critical frequencies?)")
    else:
        print(f"  Sample reflections:")
        for i in range(min(3, len(self.refl))):
            mode = self.refl[i]
            layer_name = mode.layer.name if hasattr(mode.layer, 'name') else str(mode.layer)
            print(f"    {i+1}. {layer_name}: elev={np.rad2deg(mode.ref.elevation):.2f}°, "
                  f"dist={mode.hop_dist * 6370:.1f} km, h={mode.ref.virt_height:.1f} km")

    return result

Reflectrix.compute = debug_compute

# Run test
engine = PredictionEngine()
engine.params.ssn = 100.0
engine.params.month = 6
engine.params.tx_power = 500000.0
engine.params.tx_location = GeoPoint.from_degrees(35.80, -5.90)
engine.params.min_angle = np.deg2rad(0.1)

rx_location = GeoPoint.from_degrees(44.90, 20.50)
utc_fraction = 1.0 / 24.0

print("=" * 80)
print("REFLECTRIX DEBUGGING FOR HIGH FREQUENCIES")
print("=" * 80)
print(f"Expected foF2 ~ 6-7 MHz")
print(f"Testing frequencies: 6.07 MHz (below foF2), 17.73 MHz (above foF2)")
print()

engine.predict(rx_location=rx_location, utc_time=utc_fraction, frequencies=[6.07, 17.73])
