#!/usr/bin/env python3
"""Debug loss components for 1-hop mode"""

import sys
sys.path.insert(0, 'src')

import numpy as np
from dvoacap.prediction_engine import PredictionEngine
from dvoacap.path_geometry import GeoPoint

# Monkey-patch to capture loss calculation details
original_compute_signal = PredictionEngine._compute_signal

def debug_compute_signal(self, mode, freq):
    """Debug version of _compute_signal"""
    original_compute_signal(self, mode, freq)

    if mode.hop_cnt == 1:  # Only log 1-hop mode
        print(f"\n1-HOP MODE LOSS BREAKDOWN (Frequency: {freq:.2f} MHz):")
        print(f"  Free space loss:     {mode.free_space_loss:.2f} dB")
        print(f"  Absorption loss:     {mode.absorption_loss:.2f} dB (per hop)")
        print(f"  Deviation term:      {mode.deviation_term:.2f} dB (per hop)")
        print(f"  Ground loss:         {mode.ground_loss:.2f} dB (per hop, x{mode.hop_cnt-1} reflections)")
        print(f"  Obscuration:         {mode.obscuration:.2f} dB (per hop, x{min(2, mode.hop_cnt)})")
        print(f"  Auroral adjustment:  {self._adj_auroral:.2f} dB")
        print(f"  TX antenna gain:     {mode.signal.tx_gain_db:.2f} dB")
        print(f"  RX antenna gain:     {mode.signal.rx_gain_db:.2f} dB")
        print()

        # Calculate total from components
        hop_count = mode.hop_cnt
        hop_count2 = min(2, hop_count)
        total_from_components = (
            mode.free_space_loss +
            hop_count * (mode.absorption_loss + mode.deviation_term) +
            mode.ground_loss * (hop_count - 1) +
            hop_count2 * mode.obscuration +
            self._adj_auroral -
            mode.signal.rx_gain_db -
            mode.signal.tx_gain_db
        )

        print(f"  Total from components: {total_from_components:.2f} dB")
        print(f"  Total loss (final):    {mode.signal.total_loss_db:.2f} dB")
        print(f"  MUF day:               {mode.signal.muf_day:.4f}")
        print(f"  TX power:              {self.tx_antennas.current_antenna.tx_power_dbw:.2f} dBW")
        print(f"  Signal power:          {mode.signal.power_dbw:.2f} dBW")
        print()

        print(f"REFERENCE (from voacapx.out):")
        print(f"  Total loss:          131 dB")
        print(f"  Signal power:        -73 dBW")
        print(f"  TX power:            57 dBW (500 kW)")
        print()
        print(f"EXCESS LOSS: {mode.signal.total_loss_db - 131:.2f} dB")

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
print("LOSS COMPONENT DEBUGGING FOR 1-HOP MODE")
print("=" * 80)

engine.predict(rx_location=rx_location, utc_time=utc_fraction, frequencies=[6.07])
