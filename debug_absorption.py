#!/usr/bin/env python3
"""Debug absorption loss calculation"""

import sys
sys.path.insert(0, 'src')

import numpy as np
from dvoacap.prediction_engine import PredictionEngine
from dvoacap.path_geometry import GeoPoint

# Monkey-patch to capture absorption calculation details
original_compute_signal = PredictionEngine._compute_signal

def debug_compute_signal(self, mode, freq):
    """Debug version of _compute_signal"""
    if mode.hop_cnt == 1:  # Only log 1-hop mode
        # Get the calculation variables
        ac = 677.2 * self._absorption_index
        bc = (freq + self._current_profile.gyro_freq) ** 1.98

        if mode.ref.vert_freq <= self._current_profile.e.fo:
            # D-E mode
            if mode.ref.true_height >= 88.0:
                nsqr = 10.2
            else:
                nsqr = 63.07 * np.exp(
                    -2 * (1 + 3 * (mode.ref.true_height - 70) / 18) / 4.39
                )
            h_eff = min(100.0, mode.ref.true_height)
            mode_type = "D-E"
        else:
            # F layer modes
            nsqr = 10.2
            h_eff = 100.0
            mode_type = "F-layer"

        cos_inc = self._cos_of_incidence(mode.ref.elevation, h_eff)
        absorption = ac / (bc + nsqr) / cos_inc

        print(f"\nABSORPTION LOSS CALCULATION (1-HOP {mode_type}):")
        print(f"  Frequency:          {freq:.2f} MHz")
        print(f"  Vert freq (foF2):   {mode.ref.vert_freq:.2f} MHz")
        print(f"  E-layer fo:         {self._current_profile.e.fo:.2f} MHz")
        print(f"  True height:        {mode.ref.true_height:.1f} km")
        print(f"  Elevation:          {np.rad2deg(mode.ref.elevation):.2f}°")
        print(f"  Gyro frequency:     {self._current_profile.gyro_freq:.2f} MHz")
        print(f"  Absorption index:   {self._absorption_index:.4f}")
        print()
        print(f"  ac = 677.2 × {self._absorption_index:.4f} = {ac:.2f}")
        print(f"  bc = ({freq:.2f} + {self._current_profile.gyro_freq:.2f})^1.98 = {bc:.2f}")
        print(f"  nsqr = {nsqr:.2f}")
        print(f"  h_eff = {h_eff:.1f} km")
        print(f"  cos(incidence) = {cos_inc:.4f}")
        print()
        print(f"  absorption_loss = ac / (bc + nsqr) / cos_inc")
        print(f"                  = {ac:.2f} / ({bc:.2f} + {nsqr:.2f}) / {cos_inc:.4f}")
        print(f"                  = {ac:.2f} / {bc + nsqr:.2f} / {cos_inc:.4f}")
        print(f"                  = {absorption:.2f} dB")
        print()
        print(f"  REFERENCE absorption should be ~5-10 dB for this path")
        print(f"  EXCESS: {absorption - 8:.2f} dB")

    # Call original
    original_compute_signal(self, mode, freq)

PredictionEngine._compute_signal = debug_compute_signal

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
print("ABSORPTION LOSS DEBUGGING")
print("=" * 80)

engine.predict(rx_location=rx_location, utc_time=utc_fraction, frequencies=[6.07])
