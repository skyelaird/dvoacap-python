#!/usr/bin/env python3
"""
Debug script to trace through a single prediction and identify the bug
"""

import sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.dvoacap.path_geometry import GeoPoint
from src.dvoacap.prediction_engine import PredictionEngine

def debug_prediction():
    """Run a single prediction with detailed logging"""

    # Test case from validation (Tangier → Belgrade, 6.1 MHz, UTC hour 1)
    engine = PredictionEngine()
    engine.params.ssn = 100.0
    engine.params.month = 6
    engine.params.tx_power = 500000  # 500 kW
    engine.params.tx_location = GeoPoint.from_degrees(35.80, -5.90)  # Tangier
    engine.params.min_angle = np.deg2rad(0.1)

    rx_location = GeoPoint.from_degrees(44.90, 20.50)  # Belgrade
    utc_fraction = 1.0 / 24.0  # Hour 1
    freq_mhz = 6.1

    print("=" * 80)
    print("DEBUG PREDICTION - Single Test Case")
    print("=" * 80)
    tx_lat, tx_lon = engine.params.tx_location.to_degrees()
    rx_lat, rx_lon = rx_location.to_degrees()
    print(f"Path: Tangier ({tx_lat:.2f}°N, {abs(tx_lon):.2f}°W)")
    print(f"   → Belgrade ({rx_lat:.2f}°N, {rx_lon:.2f}°E)")
    print(f"Frequency: {freq_mhz} MHz")
    print(f"UTC Hour: 1 ({utc_fraction:.4f})")
    print(f"SSN: {engine.params.ssn}")
    print(f"Month: {engine.params.month}")
    print()

    # Add debug hook to check modes
    original_evaluate = engine._evaluate_short_model

    def debug_evaluate(reflectrix, freq_idx):
        print("DEBUG: _evaluate_short_model called")
        print(f"  Path distance: {engine.path.dist:.6f} radians ({engine.path.dist * 6370:.1f} km)")
        print(f"  reflectrix.max_distance: {reflectrix.max_distance:.6f} radians ({reflectrix.max_distance * 6370:.1f} km)")
        print(f"  reflectrix.skip_distance: {reflectrix.skip_distance:.6f} radians ({reflectrix.skip_distance * 6370:.1f} km)")

        # Check hop count range
        from src.dvoacap.prediction_engine import IonosphericLayer
        min_hops = min(
            engine.circuit_muf.muf_info[IonosphericLayer.E.name].hop_count,
            engine.circuit_muf.muf_info[IonosphericLayer.F2.name].hop_count
        )
        print(f"  min_hops: {min_hops}")

        if reflectrix.max_distance <= 0:
            hops_begin = min_hops
            hops_end = min_hops
        else:
            hops_begin = int(engine.path.dist / reflectrix.max_distance) + 1
            hops_begin = max(min_hops, hops_begin)
            max_hops = int(engine.path.dist / reflectrix.skip_distance)
            max_hops = max(hops_begin, max_hops)
            hops_end = min(max_hops, hops_begin + 2)
            if hops_begin > min_hops:
                hops_begin = max(min_hops, hops_end - 2)

        print(f"  Hop range: {hops_begin} to {hops_end}")

        # Check each hop count
        for hop_count in range(hops_begin, hops_end + 1):
            hop_dist = engine.path.dist / hop_count
            print(f"  Trying hop_count={hop_count}, hop_dist={hop_dist:.6f} radians ({hop_dist * 6370:.1f} km)")
            modes = reflectrix.find_modes(hop_dist, hop_count)
            if modes:
                print(f"    Found {len(modes)} modes")
            else:
                print(f"    No modes found")

        result = original_evaluate(reflectrix, freq_idx)

        print(f"  Number of modes found: {len(engine._modes)}")
        for i, mode in enumerate(engine._modes):
            print(f"  Mode {i}: {mode.layer}, hops={mode.hop_cnt}, "
                  f"elev={np.rad2deg(mode.ref.elevation):.2f}°, "
                  f"virt_h={mode.ref.virt_height:.1f} km")
            print(f"    Signal: power={mode.signal.power_dbw:.2f} dBW, "
                  f"loss={mode.signal.total_loss_db:.2f} dB, "
                  f"snr={mode.signal.snr_db:.2f} dB")

        print(f"  Best mode: {result.hop_count} hops on {result.mode_tx if result.mode_tx else 'None'}")
        print()
        return result

    engine._evaluate_short_model = debug_evaluate

    # Run prediction
    try:
        engine.predict(rx_location=rx_location, utc_time=utc_fraction, frequencies=[freq_mhz])

        if len(engine.predictions) > 0:
            pred = engine.predictions[0]

            print("PREDICTION RESULTS:")
            print("-" * 80)
            print(f"Mode: {pred.get_mode_name(engine.path.dist)}")
            print(f"SNR: {pred.signal.snr_db:.2f} dB")
            print(f"Reliability: {pred.signal.reliability * 100:.1f}%")
            print(f"Total Loss: {pred.signal.total_loss_db:.2f} dB")
            print(f"MUF Day: {pred.signal.muf_day:.4f}")
            print(f"Signal Power: {pred.signal.power_dbw:.2f} dBW")
            print(f"Virtual Height: {pred.virt_height:.1f} km")
            print(f"TX Elevation: {np.rad2deg(pred.tx_elevation):.2f}°")
            print()

            # Detailed signal breakdown
            print("SIGNAL BREAKDOWN:")
            print("-" * 80)
            print(f"TX Power: {engine.tx_antennas.current_antenna.tx_power_dbw:.2f} dBW")
            print(f"TX Gain: {pred.signal.tx_gain_db:.2f} dB")
            print(f"RX Gain: {pred.signal.rx_gain_db:.2f} dB")
            print(f"Total Loss: {pred.signal.total_loss_db:.2f} dB")
            print(f"Received Power: {pred.signal.power_dbw:.2f} dBW")
            print()

            # Noise breakdown
            print("NOISE BREAKDOWN:")
            print("-" * 80)
            if hasattr(engine, 'noise_model') and engine.noise_model:
                print(f"Combined Noise: {engine.noise_model.combined_noise.value.median:.2f} dBW")
                print(f"Noise Upper: {engine.noise_model.combined_noise.value.upper:.2f} dB")
                print(f"Noise Lower: {engine.noise_model.combined_noise.value.lower:.2f} dB")
                print()

            # SNR calculation breakdown
            print("SNR CALCULATION:")
            print("-" * 80)
            print(f"Signal Power (dBW): {pred.signal.power_dbw:.2f}")
            if hasattr(engine, 'noise_model') and engine.noise_model:
                noise_dbw = engine.noise_model.combined_noise.value.median
                print(f"Noise Power (dBW): {noise_dbw:.2f}")
                print(f"SNR = Signal - Noise = {pred.signal.power_dbw:.2f} - {noise_dbw:.2f} = {pred.signal.snr_db:.2f} dB")
            print()

            # Reliability calculation breakdown
            print("RELIABILITY CALCULATION:")
            print("-" * 80)
            print(f"Signal Power10: {pred.signal.power10:.2f} dB")
            print(f"Signal Power90: {pred.signal.power90:.2f} dB")
            print(f"SNR10: {pred.signal.snr10:.2f}")
            print(f"SNR90: {pred.signal.snr90:.2f}")
            print(f"Required SNR: {engine.params.required_snr:.2f} dB")
            print(f"Calculated Reliability: {pred.signal.reliability * 100:.1f}%")
            print()

            # Expected values from reference VOACAP
            print("EXPECTED FROM REFERENCE:")
            print("-" * 80)
            print(f"SNR: 17.0 dB (DVOACAP shows: {pred.signal.snr_db:.2f} dB)")
            print(f"Deviation: {abs(pred.signal.snr_db - 17.0):.2f} dB")
            print()

        else:
            print("ERROR: No predictions generated!")

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    debug_prediction()
