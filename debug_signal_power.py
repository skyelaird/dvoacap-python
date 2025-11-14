#!/usr/bin/env python3
"""
Debug Signal Power Calculation for Specific Test Cases

This script enables detailed logging to investigate the 30-60 dB errors
in daytime E-layer modes and reliability deviations.
"""

import sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.dvoacap.path_geometry import GeoPoint
from src.dvoacap.prediction_engine import PredictionEngine


def debug_prediction(tx_lat, tx_lon, rx_lat, rx_lon, freq_mhz, utc_hour,
                     month=6, ssn=100, tx_power_w=500000, label=""):
    """
    Run a single prediction with detailed loss component logging.
    """
    print("=" * 80)
    print(f"DEBUG: {label}")
    print("=" * 80)
    print(f"Path: {tx_lat:.2f}°N, {tx_lon:.2f}°W -> {rx_lat:.2f}°N, {rx_lon:.2f}°E")
    print(f"Freq: {freq_mhz:.2f} MHz, UTC: {utc_hour:02d}00, Month: {month}, SSN: {ssn}")
    print(f"Power: {tx_power_w} W")
    print()

    # Setup engine
    engine = PredictionEngine()
    engine.params.ssn = float(ssn)
    engine.params.month = month
    engine.params.tx_power = tx_power_w
    engine.params.tx_location = GeoPoint.from_degrees(tx_lat, tx_lon)
    engine.params.min_angle = np.deg2rad(0.1)

    rx_location = GeoPoint.from_degrees(rx_lat, rx_lon)
    utc_fraction = utc_hour / 24.0

    # Enable debug logging by monkey-patching
    original_compute_signal = engine._compute_signal

    def debug_compute_signal(mode, frequency):
        """Wrapper to add detailed logging."""
        result = original_compute_signal(mode, frequency)

        # Print detailed loss breakdown
        print(f"\n--- MODE: {mode.layer}, {mode.hop_cnt} hop(s) ---")
        print(f"Reflection height: {mode.ref.true_height:.1f} km")
        print(f"Virtual height: {mode.ref.virt_height:.1f} km")
        print(f"Vertical frequency: {mode.ref.vert_freq:.3f} MHz")
        print(f"Elevation angle: {np.rad2deg(mode.ref.elevation):.2f}°")
        print()

        # Absorption calculation details
        ac = 677.2 * engine._absorption_index
        bc = (frequency + engine._current_profile.gyro_freq) ** 1.98

        # Determine nsqr and h_eff (from lines 671-691)
        if mode.ref.vert_freq <= engine._current_profile.e.fo:
            # D-E mode
            if mode.ref.true_height >= engine.HTLOSS:
                nsqr = 10.2
                nsqr_type = "D-E mode, height >= HTLOSS"
            else:
                nsqr = engine.XNUZ * np.exp(
                    -2 * (1 + 3 * (mode.ref.true_height - 70) / 18) / engine.HNU
                )
                nsqr_type = f"D-E mode, height < HTLOSS (h={mode.ref.true_height:.1f} km)"
            h_eff = 100.0
            xv = max(mode.ref.vert_freq / engine._current_profile.e.fo, engine._adj_de_loss)
            xv = max(1.0, xv)
            adx = engine._adj_ccir252_a + engine._adj_ccir252_b * np.log(xv)
        else:
            # F layer modes
            nsqr = 10.2
            nsqr_type = "F-layer mode"
            h_eff = 100.0
            adx = 0.0

        cos_inc = engine._cos_of_incidence(mode.ref.elevation, h_eff)

        print(f"ABSORPTION CALCULATION:")
        print(f"  ac (absorption coeff): {ac:.2f}")
        print(f"  bc: {bc:.2f}")
        print(f"  nsqr: {nsqr:.4f} ({nsqr_type})")
        print(f"  h_eff: {h_eff:.1f} km")
        print(f"  cos_incidence: {cos_inc:.6f}")
        print(f"  Absorption loss: {mode.absorption_loss:.2f} dB/hop")
        print()

        # Deviation term details
        print(f"DEVIATION TERM CALCULATION:")
        print(f"  dev_loss (from reflectrix): {mode.ref.dev_loss:.4f}")
        print(f"  bc + nsqr: {bc + nsqr:.2f}")
        print(f"  (vert_freq + gyro_freq)^1.98: {(mode.ref.vert_freq + engine._current_profile.gyro_freq)**1.98:.2f}")
        print(f"  numerator: {(mode.ref.vert_freq + engine._current_profile.gyro_freq)**1.98 + nsqr:.2f}")
        print(f"  cos_incidence (at virt_height): {engine._cos_of_incidence(mode.ref.elevation, mode.ref.virt_height):.6f}")
        print(f"  ADX term: {adx:.4f}")
        print(f"  Deviation term: {mode.deviation_term:.2f} dB/hop")
        print()

        # Loss breakdown
        print(f"LOSS BREAKDOWN:")
        print(f"  Free space loss: {mode.free_space_loss:.2f} dB")
        print(f"  Absorption: {mode.absorption_loss:.2f} dB × {mode.hop_cnt} hops = {mode.hop_cnt * mode.absorption_loss:.2f} dB")
        print(f"  Deviation: {mode.deviation_term:.2f} dB × {mode.hop_cnt} hops = {mode.hop_cnt * mode.deviation_term:.2f} dB")
        print(f"  Ground loss: {mode.ground_loss:.2f} dB × {mode.hop_cnt-1} = {mode.ground_loss * (mode.hop_cnt-1):.2f} dB")
        print(f"  Auroral adj: {engine._adj_auroral:.2f} dB")
        print(f"  TX gain: {mode.signal.tx_gain_db:.2f} dB")
        print(f"  RX gain: {mode.signal.rx_gain_db:.2f} dB")
        print(f"  TOTAL LOSS: {mode.signal.total_loss_db:.2f} dB")
        print()

        # Check for additional losses (lines 760-769)
        layer_name = mode.layer
        muf_info = engine.circuit_muf.muf_info[layer_name]

        # MUF_DAY penalty
        muf_day_penalty = 0.0
        if mode.signal.muf_day < 1e-4:
            muf_day_penalty = -max(-24.0, 8.0 * np.log10(max(1e-10, mode.signal.muf_day)) + 32.0)
            print(f"MUF_DAY PENALTY:")
            print(f"  MUF day: {mode.signal.muf_day:.6f} (< 1e-4, triggers penalty)")
            print(f"  Penalty: {muf_day_penalty:.2f} dB")
            print()

        # Additional xls loss
        from src.dvoacap.muf_calculator import calc_muf_prob
        sec = 1.0 / engine._cos_of_incidence(mode.ref.elevation, mode.ref.true_height)
        xmuf = muf_info.ref.vert_freq * sec
        xls_prob = calc_muf_prob(frequency, xmuf, muf_info.muf, muf_info.sig_lo, muf_info.sig_hi)
        xls = -engine._to_db(max(1e-6, xls_prob)) * sec
        xls_total = mode.hop_cnt * xls

        print(f"ADDITIONAL XLS LOSS:")
        print(f"  Secant (at true height): {sec:.4f}")
        print(f"  Mode MUF (vert_freq × sec): {xmuf:.2f} MHz")
        print(f"  Circuit MUF: {muf_info.muf:.2f} MHz")
        print(f"  Operating freq: {frequency:.2f} MHz")
        print(f"  MUF probability: {xls_prob:.6f}")
        print(f"  xls: {xls:.2f} dB")
        print(f"  xls × hops: {xls_total:.2f} dB")
        print()

        # Signal and SNR
        print(f"SIGNAL RESULTS:")
        print(f"  Signal power: {mode.signal.power_dbw:.2f} dBW")
        print(f"  Noise power: {engine.noise_model.combined:.2f} dBW")
        print(f"  SNR: {mode.signal.snr_db:.2f} dB")
        print(f"  Reliability: {mode.signal.reliability * 100:.1f}%")
        print(f"  MUF day: {mode.signal.muf_day:.4f}")
        print()

        # Show total of all losses
        loss_sum = (mode.free_space_loss +
                   mode.hop_cnt * (mode.absorption_loss + mode.deviation_term) +
                   mode.ground_loss * (mode.hop_cnt - 1) +
                   engine._adj_auroral +
                   muf_day_penalty + xls_total)
        print(f"LOSS VERIFICATION:")
        print(f"  Sum of components shown: {loss_sum:.2f} dB")
        print(f"  Actual total_loss_db: {mode.signal.total_loss_db:.2f} dB")
        print(f"  Difference: {mode.signal.total_loss_db - loss_sum:.2f} dB")
        print()

        return result

    engine._compute_signal = debug_compute_signal

    # Run prediction
    try:
        engine.predict(rx_location=rx_location, utc_time=utc_fraction, frequencies=[freq_mhz])

        if len(engine.predictions) > 0:
            pred = engine.predictions[0]
            print("\n" + "=" * 80)
            print("FINAL PREDICTION:")
            print("=" * 80)
            print(f"Mode: {pred.get_mode_name(engine.path.dist)}")
            print(f"SNR: {pred.signal.snr_db:.1f} dB")
            print(f"Reliability: {pred.signal.reliability * 100:.1f}%")
            print(f"Signal power: {pred.signal.power_dbw:.1f} dBW")
            print("=" * 80)
            print()

            return pred
        else:
            print("No valid modes found")
            return None

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == '__main__':
    # Reference path: Tangier -> Belgrade
    tx_lat, tx_lon = 35.80, -5.90
    rx_lat, rx_lon = 44.90, 20.50

    print("\n" + "#" * 80)
    print("# SIGNAL POWER INVESTIGATION - Daytime E-layer Mode Errors")
    print("#" * 80)
    print()

    # Test Case 1: UTC 06, 25.90 MHz (47 dB error)
    # VOACAP: 42.0 dB, DVOACAP: -5.2 dB
    print("\nTest Case 1: Daytime high frequency with large error")
    debug_prediction(tx_lat, tx_lon, rx_lat, rx_lon, 25.90, 6,
                    label="UTC 06, 25.90 MHz (47 dB error in baseline)")

    # Test Case 2: UTC 11, 7.20 MHz (daytime E-layer)
    # Should be 2E mode according to ABSORPTION_BUG_ANALYSIS.md
    print("\n" + "=" * 80)
    print("\nTest Case 2: Daytime E-layer mode")
    debug_prediction(tx_lat, tx_lon, rx_lat, rx_lon, 7.20, 11,
                    label="UTC 11, 7.20 MHz (daytime E-layer)")

    # Test Case 3: UTC 01, 7.20 MHz (nighttime F-layer, should be good)
    print("\n" + "=" * 80)
    print("\nTest Case 3: Nighttime F-layer mode (reference for comparison)")
    debug_prediction(tx_lat, tx_lon, rx_lat, rx_lon, 7.20, 1,
                    label="UTC 01, 7.20 MHz (nighttime F-layer, should pass)")

    # Test Case 4: UTC 09, 15.40 MHz (56.6 dB error - largest)
    print("\n" + "=" * 80)
    print("\nTest Case 4: Largest error case")
    debug_prediction(tx_lat, tx_lon, rx_lat, rx_lon, 15.40, 9,
                    label="UTC 09, 15.40 MHz (56.6 dB error - largest in baseline)")
