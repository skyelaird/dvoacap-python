#!/usr/bin/env python3
"""Debug SNR calculation for failing cases"""

import sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.dvoacap.path_geometry import GeoPoint
from src.dvoacap.prediction_engine import PredictionEngine

# Test case from reference: 6.10 MHz @ 1200 UTC (worst failure)
# Path: Tangier (35.80°N, 5.90°W) → Belgrade (44.90°N, 20.50°E)

engine = PredictionEngine()
engine.params.ssn = 100.0
engine.params.month = 6  # June
engine.params.tx_power = 500000  # 500 kW
engine.params.tx_location = GeoPoint.from_degrees(35.80, -5.90)
engine.params.min_angle = np.deg2rad(0.1)

rx_location = GeoPoint.from_degrees(44.90, 20.50)
utc_hour = 12
utc_fraction = utc_hour / 24.0
freq_mhz = 6.10

print("=" * 80)
print("DEBUGGING SNR CALCULATION - 6.10 MHz @ 1200 UTC")
print("=" * 80)
print()
print(f"TX: {35.80}°N, {-5.90}°E")
print(f"RX: {44.90}°N, {20.50}°E")
print(f"Frequency: {freq_mhz} MHz")
print(f"UTC: {utc_hour:02d}00")
print(f"SSN: {engine.params.ssn}")
print(f"TX Power: {engine.params.tx_power} W ({engine._to_db(engine.params.tx_power):.1f} dBW)")
print()

# Run prediction
engine.predict(rx_location=rx_location, utc_time=utc_fraction, frequencies=[freq_mhz])

if len(engine.predictions) > 0:
    pred = engine.predictions[0]

    print("PREDICTION RESULTS:")
    print(f"  Mode: {pred.get_mode_name(engine.path.dist)}")
    print(f"  Hops: {pred.hop_count}")
    print(f"  TX Elevation: {np.rad2deg(pred.tx_elevation):.1f}°")
    print(f"  Virtual Height: {pred.virt_height:.1f} km")
    print()

    print("SIGNAL CALCULATION:")
    print(f"  TX Power: {engine.tx_antennas.current_antenna.tx_power_dbw:.1f} dBW")
    print(f"  Total Loss: {pred.signal.total_loss_db:.1f} dB")
    print(f"  RX Power: {pred.signal.power_dbw:.1f} dBW")
    print()

    print("NOISE CALCULATION:")
    print(f"  Atmospheric: {engine.noise_model.atmospheric_noise.value.median:.1f} dBW")
    print(f"  Galactic: {engine.noise_model.galactic_noise.value.median:.1f} dBW")
    print(f"  Man-made: {engine.noise_model.man_made_noise.value.median:.1f} dBW")
    print(f"  Combined: {engine.noise_model.combined:.1f} dBW")
    print()

    print("SNR CALCULATION:")
    print(f"  SNR = RX Power - Noise")
    print(f"  SNR = {pred.signal.power_dbw:.1f} - {engine.noise_model.combined:.1f}")
    print(f"  SNR = {pred.signal.snr_db:.1f} dB")
    print()

    print("VOACAP REFERENCE:")
    print(f"  Expected SNR: 72.0 dB")
    print(f"  Deviation: {abs(pred.signal.snr_db - 72.0):.1f} dB")
    print()

    # Detailed mode information
    if engine._modes:
        print("MODE DETAILS:")
        for i, mode in enumerate(engine._modes[:3]):  # Show first 3 modes
            layer_name = mode.layer.name if hasattr(mode.layer, 'name') else str(mode.layer)
            print(f"  Mode {i+1}: {layer_name}")
            print(f"    Hops: {mode.hop_cnt}")
            print(f"    Elevation: {np.rad2deg(mode.ref.elevation):.2f}°")
            print(f"    Virt Height: {mode.ref.virt_height:.1f} km")
            print(f"    Vert Freq: {mode.ref.vert_freq:.2f} MHz")
            print(f"    Free Space Loss: {mode.free_space_loss:.1f} dB")
            print(f"    Absorption Loss: {mode.absorption_loss:.1f} dB/hop (x{mode.hop_cnt} hops = {mode.absorption_loss * mode.hop_cnt:.1f} dB)")
            print(f"    Ground Loss: {mode.ground_loss:.1f} dB/hop (x{mode.hop_cnt-1} hops = {mode.ground_loss * (mode.hop_cnt-1):.1f} dB)")
            print(f"    Deviation Term: {mode.deviation_term:.1f} dB/hop (x{mode.hop_cnt} hops = {mode.deviation_term * mode.hop_cnt:.1f} dB)")
            print(f"    Obscuration: {mode.obscuration:.1f} dB")
            print(f"    TX Gain: {mode.signal.tx_gain_db:.1f} dBi")
            print(f"    RX Gain: {mode.signal.rx_gain_db:.1f} dBi")
            print(f"    Auroral adj: {engine._adj_auroral:.1f} dB")
            print(f"    Total Loss: {mode.signal.total_loss_db:.1f} dB")
            print(f"    MUF Day: {mode.signal.muf_day:.6f}")
            print(f"    Reliability: {mode.signal.reliability * 100:.1f}%")
            print()
else:
    print("ERROR: No predictions generated!")

print("=" * 80)

# Now test a working frequency: 11.85 MHz (100% pass rate)
print()
print("=" * 80)
print("COMPARISON: 11.85 MHz @ 1200 UTC (Working frequency)")
print("=" * 80)
print()

engine2 = PredictionEngine()
engine2.params.ssn = 100.0
engine2.params.month = 6
engine2.params.tx_power = 500000
engine2.params.tx_location = GeoPoint.from_degrees(35.80, -5.90)
engine2.params.min_angle = np.deg2rad(0.1)

freq_mhz = 11.85
engine2.predict(rx_location=rx_location, utc_time=utc_fraction, frequencies=[freq_mhz])

if len(engine2.predictions) > 0:
    pred2 = engine2.predictions[0]

    print(f"Frequency: {freq_mhz} MHz")
    print(f"Mode: {pred2.get_mode_name(engine2.path.dist)}")
    print(f"Hops: {pred2.hop_count}")
    print(f"TX Power: {engine2.tx_antennas.current_antenna.tx_power_dbw:.1f} dBW")
    print(f"Total Loss: {pred2.signal.total_loss_db:.1f} dB")
    print(f"RX Power: {pred2.signal.power_dbw:.1f} dBW")
    print(f"Noise: {engine2.noise_model.combined:.1f} dBW")
    print(f"SNR: {pred2.signal.snr_db:.1f} dB")
    print(f"Reliability: {pred2.signal.reliability * 100:.1f}%")
    print()
