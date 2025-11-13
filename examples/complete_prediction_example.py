#!/usr/bin/env python3
"""
Complete End-to-End Propagation Prediction Example

This example demonstrates the complete VOACAP prediction engine, integrating
all five phases to provide comprehensive HF radio propagation predictions.

Phases integrated:
1. Path Geometry - Great circle calculations
2. Solar & Geomagnetic - Solar zenith angles, magnetic field
3. Ionospheric Profiles - E/F/F2 layer modeling with CCIR coefficients
4. Raytracing - MUF calculations, ray path finding
5. Signal Predictions - Complete signal strength, SNR, and reliability

This represents the culmination of the DVOACAP Python port!
"""

import numpy as np
from dvoacap.path_geometry import GeoPoint
from dvoacap.prediction_engine import PredictionEngine, VoacapParams

def main():
    print("=" * 80)
    print("DVOACAP Complete Propagation Prediction")
    print("=" * 80)
    print()

    # =========================================================================
    # 1. Configure the prediction
    # =========================================================================
    print("1. Configuring Prediction Parameters")
    print("-" * 80)

    # Create prediction engine
    engine = PredictionEngine()

    # Configure parameters
    engine.params.ssn = 100.0  # Sunspot number (solar cycle activity)
    engine.params.month = 6  # June (summer propagation)
    engine.params.tx_power = 100.0  # 100 watts transmitter power
    engine.params.tx_location = GeoPoint.from_degrees(39.95, -75.17)  # Philadelphia, PA
    engine.params.min_angle = np.deg2rad(3.0)  # Minimum takeoff angle
    engine.params.man_made_noise_at_3mhz = 145.0  # Residential noise level
    engine.params.required_snr = 10.0  # Required SNR for reliable comms (dB)
    engine.params.required_reliability = 0.9  # 90% reliability target

    print(f"TX Location: Philadelphia, PA (39.95°N, 75.17°W)")
    print(f"TX Power: {engine.params.tx_power} watts")
    print(f"Month: June")
    print(f"Sunspot Number: {engine.params.ssn}")
    print(f"Required SNR: {engine.params.required_snr} dB")
    print(f"Required Reliability: {engine.params.required_reliability * 100}%")
    print()

    # =========================================================================
    # 2. Run predictions for multiple paths
    # =========================================================================
    paths = [
        ("London, UK", GeoPoint.from_degrees(51.51, -0.13)),
        ("Tokyo, Japan", GeoPoint.from_degrees(35.68, 139.69)),
        ("Sydney, Australia", GeoPoint.from_degrees(-33.87, 151.21)),
        ("Buenos Aires, Argentina", GeoPoint.from_degrees(-34.61, -58.38)),
    ]

    # Test frequencies (MHz)
    frequencies = [7.0, 14.0, 21.0, 28.0]

    for path_name, rx_location in paths:
        print("=" * 80)
        print(f"Path: Philadelphia → {path_name}")
        print("=" * 80)

        try:
            # Run prediction
            engine.predict(
                rx_location=rx_location,
                utc_time=0.5,  # 12:00 UTC
                frequencies=frequencies
            )

            # Display path information
            distance_km = engine.path.dist * 6370
            print(f"\nDistance: {distance_km:.0f} km")
            print(f"Azimuth: {np.rad2deg(engine.path.azim_tr):.1f}°")
            print()

            # Display MUF information
            print("Maximum Usable Frequencies (MUF):")
            print(f"  MUF: {engine.muf_calculator.muf:.2f} MHz")
            print(f"  FOT (50%): {engine.muf_calculator.muf_info[2].fot:.2f} MHz")
            print(f"  HPF (90%): {engine.muf_calculator.muf_info[2].hpf:.2f} MHz")
            print()

            # Display predictions for each frequency
            print(f"{'Freq':>6} {'Mode':>6} {'Hops':>5} {'Elev':>6} {'Loss':>7} "
                  f"{'SNR':>6} {'Rel':>6} {'Service':>8}")
            print(f"{'(MHz)':>6} {'':>6} {'':>5} {'(deg)':>6} {'(dB)':>7} "
                  f"{'(dB)':>6} {'(%)':>6} {'Prob(%)':>8}")
            print("-" * 80)

            for freq, pred in zip(frequencies, engine.predictions):
                mode_name = pred.get_mode_name(engine.path.dist)
                elev_deg = np.rad2deg(pred.tx_elevation)
                loss_db = pred.signal.total_loss_db
                snr_db = pred.signal.snr_db
                reliability = pred.signal.reliability * 100
                service_prob = pred.service_prob * 100

                print(f"{freq:>6.1f} {mode_name:>6} {pred.hop_count:>5} {elev_deg:>6.1f} "
                      f"{loss_db:>7.1f} {snr_db:>6.1f} {reliability:>6.1f} {service_prob:>8.1f}")

            print()

            # Recommend best frequency
            best_idx = max(range(len(engine.predictions)),
                          key=lambda i: engine.predictions[i].signal.reliability)
            best_freq = frequencies[best_idx]
            best_pred = engine.predictions[best_idx]

            print("Recommendation:")
            print(f"  Best frequency: {best_freq} MHz")
            print(f"  Mode: {best_pred.get_mode_name(engine.path.dist)}")
            print(f"  SNR: {best_pred.signal.snr_db:.1f} dB")
            print(f"  Reliability: {best_pred.signal.reliability * 100:.1f}%")
            print(f"  Multipath probability: {best_pred.multipath_prob * 100:.1f}%")
            print()

        except Exception as e:
            import traceback
            print(f"\n⚠ Error running prediction: {e}")
            traceback.print_exc()
            print(f"   This may indicate the path is not feasible at this time")
            print()
            continue

    # =========================================================================
    # Summary
    # =========================================================================
    print("=" * 80)
    print("Prediction Complete!")
    print("=" * 80)
    print()
    print("This example demonstrated:")
    print("  ✓ Phase 1: Path geometry calculations")
    print("  ✓ Phase 2: Solar and geomagnetic parameters")
    print("  ✓ Phase 3: Ionospheric profile modeling")
    print("  ✓ Phase 4: Ray tracing and MUF calculations")
    print("  ✓ Phase 5: Signal strength and reliability predictions")
    print()
    print("The DVOACAP Python port is now functionally complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
