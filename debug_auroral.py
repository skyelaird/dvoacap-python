#!/usr/bin/env python3
"""Debug auroral/excessive loss calculation"""

import sys
sys.path.insert(0, 'src')

import numpy as np
from dvoacap.prediction_engine import PredictionEngine
from dvoacap.path_geometry import GeoPoint

# Monkey-patch to capture auroral adjustment calculation
original_adjust = PredictionEngine._adjust_signal_distribution_tables

def debug_adjust(self):
    """Debug version of _adjust_signal_distribution_tables"""
    original_adjust(self)

    print(f"\nAURORAL/EXCESSIVE LOSS CALCULATION:")
    print(f"  Path distance:         {self.path.dist * 6370:.1f} km")
    print(f"  Long path threshold:   2500 km")
    print(f"  Is long path:          {self.path.dist > self.RAD_2500_KM}")
    print(f"  Number of profiles:    {len(self._profiles)}")
    print()

    for i, prof in enumerate(self._profiles):
        print(f"  Profile {i+1}:")
        print(f"    Mag latitude:      {np.rad2deg(prof.mag_latitude):.2f}°")
        print(f"    Local time (E):    {prof.local_time_e*24:.2f} hours")
        print(f"    Excessive loss:    median={prof.excessive_system_loss.median:.2f} dB, "
              f"lo={prof.excessive_system_loss.lo:.2f} dB, hi={prof.excessive_system_loss.hi:.2f} dB")

    print()
    print(f"  Average excessive loss:  median={self._avg_loss.median:.2f} dB, "
          f"lower={self._avg_loss.lower:.2f} dB, upper={self._avg_loss.upper:.2f} dB")
    print(f"  Absorption index:        {self._absorption_index:.4f}")
    print(f"  Auroral adjustment:      {self._adj_auroral:.2f} dB")
    print()
    print(f"  NOTE: Reference VOACAP likely has lower auroral adjustment")
    print(f"        to achieve total loss of 131 dB (vs our {136.4:.1f} dB)")

PredictionEngine._adjust_signal_distribution_tables = debug_adjust

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
print("AURORAL/EXCESSIVE LOSS DEBUGGING")
print("=" * 80)

engine.predict(rx_location=rx_location, utc_time=utc_fraction, frequencies=[6.07])
