#!/usr/bin/env python3
"""
Phase 5 Example: Signal Predictions

This example demonstrates Phase 5 capabilities:
- Noise modeling (atmospheric, galactic, man-made)
- Antenna gain calculations
- Integration with previous phases for signal prediction basics

Phase 5 adds the final pieces for complete HF propagation prediction including
signal strength, reliability, and system performance metrics.

Note: The full prediction engine is under development. This example shows
the core Phase 5 components that are complete.
"""

import numpy as np
from datetime import datetime

# Phase 1: Path Geometry
from dvoacap.path_geometry import PathGeometry, GeoPoint

# Phase 2: Solar & Geomagnetic
from dvoacap.solar import compute_zenith_angle, compute_local_time

# Phase 3: Ionospheric Profiles
from dvoacap.fourier_maps import FourierMaps
from dvoacap.ionospheric_profile import IonosphericProfile
from dvoacap.layer_parameters import ControlPoint, GeographicPoint, compute_iono_params

# Phase 4: Raytracing
from dvoacap.muf_calculator import CircuitMuf

# Phase 5: Signal Predictions
from dvoacap.noise_model import NoiseModel
from dvoacap.antenna_gain import (
    AntennaFarm,
    IsotropicAntenna,
    HalfWaveDipole,
    VerticalMonopole
)


def main():
    print("=" * 70)
    print("DVOACAP Phase 5 Example: Signal Predictions")
    print("=" * 70)
    print()

    # =========================================================================
    # Setup: Define TX and RX locations
    # =========================================================================
    print("1. Setting up propagation path")
    print("-" * 70)

    # Philadelphia, PA to London, UK (same as Phase 4 example)
    tx_location = GeoPoint.from_degrees(39.95, -75.17)  # Philadelphia
    rx_location = GeoPoint.from_degrees(51.51, -0.13)   # London

    # Create path
    path = PathGeometry()
    path.set_tx_rx(tx_location, rx_location)

    print(f"TX: Philadelphia, PA (39.95°N, 75.17°W)")
    print(f"RX: London, UK (51.51°N, 0.13°W)")
    print(f"Great circle distance: {path.dist * 6370:.0f} km")
    print(f"Azimuth (TX to RX): {np.rad2deg(path.azim_tr):.1f}°")
    print()

    # =========================================================================
    # Phase 5.1: Noise Modeling
    # =========================================================================
    print("2. Noise Modeling")
    print("-" * 70)

    # Create Fourier maps and noise model
    fourier_maps = FourierMaps()
    fourier_maps.set_conditions(month=1, ssn=100, utc_fraction=0.5)  # January, SSN=100, 12:00 UTC

    noise_model = NoiseModel(fourier_maps)

    # Configure man-made noise level
    # 145 dB is default (residential area), can be adjusted:
    # - Rural: ~120 dB
    # - Residential: ~145 dB
    # - Urban: ~160-170 dB
    noise_model.man_made_noise_at_3mhz = 145.0

    # Compute noise at receiver location
    local_time = compute_local_time(0.5, rx_location.lon)
    noise_model.compute_noise_at_1mhz(rx_location, local_time)

    # Test frequencies
    frequencies = [7.0, 14.0, 21.0, 28.0]  # MHz

    # Compute ionospheric parameters for foF2 (needed for galactic noise)
    ctrl_pt = ControlPoint(
        location=GeographicPoint(rx_location.lat, rx_location.lon),
        east_lon=rx_location.lon if rx_location.lon >= 0 else 2*np.pi + rx_location.lon,
        distance_rad=0.0,
        local_time=local_time,
        zen_angle=compute_zenith_angle(rx_location, 0.5, 1),
        zen_max=np.deg2rad(102),
        mag_lat=0.0,
        mag_dip=0.0,
        gyro_freq=1.0
    )
    compute_iono_params(ctrl_pt, fourier_maps)
    fof2 = ctrl_pt.f2.fo

    print(f"Location: London (local time: {local_time*24:.1f}:00)")
    print(f"Man-made noise at 3 MHz: {noise_model.man_made_noise_at_3mhz:.0f} dB")
    print(f"foF2: {fof2:.2f} MHz")
    print()
    print("Noise levels at different frequencies:")
    print(f"{'Freq':>6} {'Atmos':>8} {'Galactic':>10} {'ManMade':>10} {'Combined':>10} {'SNR Impact':>12}")
    print(f"{'(MHz)':>6} {'(dBW)':>8} {'(dBW)':>10} {'(dBW)':>10} {'(dBW)':>10} {'(dB)':>12}")
    print("-" * 70)

    for freq in frequencies:
        noise_model.compute_distribution(freq, fof2)

        # Show noise components
        atmos = noise_model.atmospheric_noise.value.median
        galactic = noise_model.galactic_noise.value.median
        manmade = noise_model.man_made_noise.value.median
        combined = noise_model.combined_noise.value.median

        # For a 1 kW transmitter (60 dBW), estimate SNR impact
        typical_signal = 60.0 - 150.0  # 60 dBW TX - typical 150 dB path loss
        snr_impact = typical_signal - combined

        print(f"{freq:>6.1f} {atmos:>8.1f} {galactic:>10.1f} {manmade:>10.1f} "
              f"{combined:>10.1f} {snr_impact:>12.1f}")

    print()
    print("Note: Galactic noise only penetrates ionosphere when f > foF2")
    print("      At HF frequencies (< foF2), atmospheric and man-made noise dominate")
    print()

    # =========================================================================
    # Phase 5.2: Antenna Gain
    # =========================================================================
    print("3. Antenna Modeling")
    print("-" * 70)

    # Create antenna farm with multiple antennas
    tx_farm = AntennaFarm()

    # Add different antennas for different frequency ranges
    # HF antennas (3-30 MHz)
    dipole_7mhz = HalfWaveDipole(low_frequency=5.0, high_frequency=10.0, tx_power_dbw=10.0)
    dipole_14mhz = HalfWaveDipole(low_frequency=10.0, high_frequency=18.0, tx_power_dbw=10.0)
    vertical = VerticalMonopole(low_frequency=18.0, high_frequency=30.0, tx_power_dbw=10.0)

    tx_farm.add_antenna(dipole_7mhz)
    tx_farm.add_antenna(dipole_14mhz)
    tx_farm.add_antenna(vertical)

    print("Antenna Farm Configuration:")
    print(f"  - Half-wave dipole: 5-10 MHz (40m band)")
    print(f"  - Half-wave dipole: 10-18 MHz (20m band)")
    print(f"  - Vertical monopole: 18-30 MHz (15m/10m bands)")
    print()

    # Test elevation angles (typical for HF propagation)
    elevations_deg = np.array([5, 10, 15, 20, 30, 45])
    elevations_rad = np.deg2rad(elevations_deg)

    print("Antenna gain patterns vs elevation angle:")
    print()

    for freq in [7.0, 14.0, 21.0]:
        tx_farm.select_antenna(freq)
        antenna = tx_farm.current_antenna

        print(f"Frequency: {freq} MHz - {type(antenna).__name__}")
        print(f"{'Elevation (deg)':>18}: " + "  ".join(f"{e:>5.0f}" for e in elevations_deg))
        print(f"{'Gain (dBi)':>18}: " + "  ".join(f"{antenna.get_gain_db(elev):>5.1f}" for elev in elevations_rad))
        print()

    print("Note: Lower elevation angles are typically better for long-distance (DX)")
    print("      HF propagation, while higher angles serve shorter distances.")
    print()

    # =========================================================================
    # Phase 5.3: Signal Budget Example
    # =========================================================================
    print("4. Simple Signal Budget Example")
    print("-" * 70)

    # For a specific frequency
    freq = 14.0  # MHz
    elevation = np.deg2rad(15)  # degrees

    # Select antenna
    tx_farm.select_antenna(freq)
    tx_antenna = tx_farm.current_antenna

    # Receiver antenna (isotropic for simplicity)
    rx_antenna = IsotropicAntenna(tx_power_dbw=0.0)

    # Get antenna gains
    tx_gain = tx_antenna.get_gain_db(elevation)
    rx_gain = rx_antenna.get_gain_db(elevation)

    # Compute noise
    noise_model.compute_distribution(freq, fof2)
    noise_power = noise_model.combined

    # Typical path loss for this distance at 14 MHz
    # (simplified - full calculation requires raytracing)
    typical_path_loss = 150.0  # dB (rough estimate)

    # Signal budget
    tx_power = tx_antenna.tx_power_dbw
    rx_power = tx_power + tx_gain + rx_gain - typical_path_loss

    snr = rx_power - noise_power

    print(f"Frequency: {freq} MHz")
    print(f"Elevation angle: {np.rad2deg(elevation):.0f}°")
    print()
    print("Signal Budget:")
    print(f"  TX Power:        {tx_power:>7.1f} dBW")
    print(f"  TX Antenna Gain: {tx_gain:>7.1f} dBi")
    print(f"  RX Antenna Gain: {rx_gain:>7.1f} dBi")
    print(f"  Path Loss:       {-typical_path_loss:>7.1f} dB")
    print(f"  ─" * 20)
    print(f"  RX Power:        {rx_power:>7.1f} dBW")
    print(f"  Noise Power:     {noise_power:>7.1f} dBW")
    print(f"  ─" * 20)
    print(f"  SNR:             {snr:>7.1f} dB")
    print()

    if snr > 15:
        print(f"✓ Excellent SNR - high quality communications expected")
    elif snr > 10:
        print(f"✓ Good SNR - reliable communications expected")
    elif snr > 0:
        print(f"⚠ Marginal SNR - communications may be unreliable")
    else:
        print(f"✗ Poor SNR - communications not expected")
    print()

    # =========================================================================
    # Summary
    # =========================================================================
    print("=" * 70)
    print("Phase 5 Implementation Status")
    print("=" * 70)
    print()
    print("✓ Completed:")
    print("  - Noise modeling (atmospheric, galactic, man-made)")
    print("  - Antenna gain calculations")
    print("  - Basic signal budget calculations")
    print()
    print("In Progress:")
    print("  - Full prediction engine integration")
    print("  - Complete end-to-end signal predictions")
    print("  - Reliability and service probability calculations")
    print()
    print("Phase 5 provides the foundation for:")
    print("  - Signal-to-noise ratio (SNR) prediction")
    print("  - Circuit reliability assessment")
    print("  - System performance optimization")
    print("  - Frequency selection recommendations")
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
