#!/usr/bin/env python3
"""Debug E-layer absorption for daytime vs nighttime"""

import sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.dvoacap.path_geometry import GeoPoint
from src.dvoacap.prediction_engine import PredictionEngine

# Test case from SampleIO/voacapx.out
TX_LAT, TX_LON = 35.80, -5.90
RX_LAT, RX_LON = 44.90, 20.50
SSN = 100.0
MONTH = 6
TX_POWER = 500000

# Test 7.20 MHz at night (UTC 1) vs day (UTC 11)
FREQ = 7.20
UTC_HOURS = [1.0, 11.0]

print("=" * 80)
print("E-LAYER ABSORPTION DEBUG - 7.20 MHz")
print("=" * 80)

for utc in UTC_HOURS:
    print(f"\n{'=' * 80}")
    print(f"UTC HOUR: {utc:.1f}")
    print(f"{'=' * 80}\n")

    engine = PredictionEngine()
    engine.params.ssn = SSN
    engine.params.month = MONTH
    engine.params.tx_power = TX_POWER
    engine.params.tx_location = GeoPoint.from_degrees(TX_LAT, TX_LON)
    engine.params.min_angle = np.deg2rad(0.1)

    rx_location = GeoPoint.from_degrees(RX_LAT, RX_LON)
    utc_fraction = utc / 24.0

    # Run prediction
    engine.predict(rx_location=rx_location, utc_time=utc_fraction, frequencies=[FREQ])

    if engine.predictions:
        pred = engine.predictions[0]
        mode = pred.get_mode_name(engine.path.dist)

        print(f"Mode: {mode}")
        print(f"Hops: {pred.hop_count}")
        print()

        # Show ionospheric profiles
        print("Ionospheric Profiles:")
        for i, prof in enumerate(engine._profiles):
            print(f"  Profile {i+1}:")
            print(f"    foE: {prof.e.fo:.2f} MHz")
            print(f"    foF1: {prof.f1.fo:.2f} MHz")
            print(f"    foF2: {prof.f2.fo:.2f} MHz")
            print(f"    Absorption index: {prof.absorption_index:.4f}")
            print(f"    Local time (E): {prof.local_time_e:.3f}")
            print()

        print(f"Average absorption index: {engine._absorption_index:.4f}")
        print()

        # Access internal mode info
        if engine._modes:
            mode_info = engine._modes[0]

            print("Loss Components:")
            print(f"  Free space loss: {mode_info.free_space_loss:.1f} dB")
            print(f"  Absorption loss (per hop): {mode_info.absorption_loss:.1f} dB")
            print(f"  Deviation term (per hop): {mode_info.deviation_term:.1f} dB")
            print(f"  Ground loss (per hop): {mode_info.ground_loss:.1f} dB")
            print(f"  Auroral adjustment: {engine._adj_auroral:.1f} dB")
            print()

            # Show absorption calculation details
            ac = 67.72 * engine._absorption_index
            bc = (FREQ + engine._current_profile.gyro_freq) ** 1.98

            print("Absorption Calculation Details:")
            print(f"  ac = 67.72 × {engine._absorption_index:.4f} = {ac:.2f}")
            print(f"  bc = (freq + gyro)^1.98 = ({FREQ} + {engine._current_profile.gyro_freq:.2f})^1.98 = {bc:.2f}")
            print(f"  Mode layer: {mode_info.layer}")
            print(f"  Hop count: {mode_info.hop_cnt}")
            print(f"  Reflection vert freq: {mode_info.ref.vert_freq:.2f} MHz")
            print(f"  Reflection true height: {mode_info.ref.true_height:.1f} km")
            print(f"  E-layer foE: {engine._current_profile.e.fo:.2f} MHz")
            print()

            # Check if this is D-E mode
            is_de_mode = mode_info.ref.vert_freq <= engine._current_profile.e.fo
            print(f"  Is D-E mode? {is_de_mode} (vert_freq {mode_info.ref.vert_freq:.2f} <= foE {engine._current_profile.e.fo:.2f})")
            print()

            # Show expected behavior
            print(f"  Expected behavior for {mode}:")
            if mode == "2E":
                print(f"    2-hop E-layer mode during daytime")
                print(f"    Should have HIGH absorption (100-150 dB per hop)")
            elif mode == "1F2":
                print(f"    1-hop F2-layer mode")
                print(f"    Should have LOW absorption (< 5 dB per hop)")
            print()

        print()
        print(f"Total Loss: {pred.signal.total_loss_db:.1f} dB")
        print(f"SNR: {pred.signal.snr_db:.1f} dB")
        print(f"Reliability: {pred.signal.reliability*100:.1f}%")

print("\n" + "=" * 80)
