#!/usr/bin/env python3
"""
Phase 4: Raytracing Example
Demonstrates MUF calculation and ray path tracing through the ionosphere
"""

import sys
import math
sys.path.insert(0, '../src')

from dvoacap import (
    # Path geometry
    PathGeometry,
    PathPoint,
    # Solar/Geomagnetic
    SolarCalculator,
    GeomagneticCalculator,
    GeoPoint,
    # Ionospheric
    FourierMaps,
    LayerInfo,
    IonosphericProfile,
    ControlPoint,
    compute_iono_params,
    # Raytracing (Phase 4)
    MufCalculator,
    Reflectrix,
)


def main():
    print("=" * 80)
    print("Phase 4: Raytracing Example - MUF and Ray Path Calculations")
    print("=" * 80)
    print()

    # ========================================================================
    # Step 1: Set up path geometry
    # ========================================================================
    print("Step 1: Setting up propagation path")
    print("-" * 80)

    # Philadelphia, PA to London, UK
    tx = PathPoint.from_degrees(40.0, -75.0)
    rx = PathPoint.from_degrees(51.5, -0.1)

    path = PathGeometry()
    path.set_tx_rx(tx, rx)

    print(f"Transmitter: Philadelphia (40.0°N, 75.0°W)")
    print(f"Receiver:    London (51.5°N, 0.1°W)")
    print(f"Distance:    {path.get_distance_km():.1f} km")
    print(f"Azimuth:     {path.get_azimuth_tr_degrees():.1f}°")
    print()

    # ========================================================================
    # Step 2: Set up ionospheric conditions
    # ========================================================================
    print("Step 2: Loading ionospheric maps")
    print("-" * 80)

    # June, SSN=100, noon UTC
    month = 6
    ssn = 100
    utc_hour = 12.0

    maps = FourierMaps()
    maps.set_conditions(month=month, ssn=ssn, utc_fraction=utc_hour/24.0)

    print(f"Month:       June")
    print(f"SSN:         {ssn}")
    print(f"UTC Time:    {utc_hour:.1f}:00")
    print()

    # ========================================================================
    # Step 3: Compute ionospheric profile at path midpoint
    # ========================================================================
    print("Step 3: Computing ionospheric profile at midpoint")
    print("-" * 80)

    # Get midpoint
    midpoint = path.get_point_at_dist(path.dist / 2)
    mid_lat_deg, mid_lon_deg = midpoint.to_degrees()

    print(f"Midpoint:    {mid_lat_deg:.2f}°N, {abs(mid_lon_deg):.2f}°W")

    # Create control point
    solar_calc = SolarCalculator()
    mag_calc = GeomagneticCalculator()

    # Convert to solar/geomagnetic point
    geo_point = GeoPoint(lat=midpoint.lat, lon=midpoint.lon)

    # Compute solar parameters
    solar_params = solar_calc.compute_parameters(
        point=geo_point,
        month=month,
        utc_hour=utc_hour
    )

    # Compute geomagnetic parameters
    mag_params = mag_calc.compute_parameters(geo_point)

    # Create control point for ionospheric calculation
    control_point = ControlPoint(
        location=geo_point,
        east_lon=geo_point.lon,
        distance_rad=path.dist / 2,
        local_time=solar_params.local_time,
        zen_angle=solar_params.zenith_angle,
        zen_max=solar_params.max_zenith,
        mag_lat=mag_params.mag_lat,
        mag_dip=mag_params.dip_angle,
        gyro_freq=mag_params.gyro_freq
    )

    # Compute ionospheric parameters
    compute_iono_params(control_point, maps)

    print(f"E layer:     foE  = {control_point.e.fo:.2f} MHz at {control_point.e.hm:.0f} km")
    print(f"F1 layer:    foF1 = {control_point.f1.fo:.2f} MHz at {control_point.f1.hm:.0f} km")
    print(f"F2 layer:    foF2 = {control_point.f2.fo:.2f} MHz at {control_point.f2.hm:.0f} km")
    print()

    # ========================================================================
    # Step 4: Create ionospheric profile
    # ========================================================================
    print("Step 4: Creating detailed ionospheric profile")
    print("-" * 80)

    profile = IonosphericProfile()
    profile.e = control_point.e
    profile.f1 = control_point.f1
    profile.f2 = control_point.f2
    profile.lat = control_point.location.lat
    profile.local_time_f2 = control_point.local_time

    # Compute electron density profile
    profile.compute_el_density_profile()
    print(f"✓ Computed electron density profile ({len(profile.dens_true_height)} points)")

    # Compute ionogram
    profile.compute_ionogram()
    print(f"✓ Computed ionogram ({len(profile.igram_vert_freq)} frequencies)")

    # Compute oblique frequencies for raytracing
    profile.compute_oblique_frequencies()
    print(f"✓ Computed oblique frequency table (40 angles × 31 heights)")
    print()

    # ========================================================================
    # Step 5: Calculate MUF (Maximum Usable Frequency)
    # ========================================================================
    print("Step 5: Calculating Maximum Usable Frequency (MUF)")
    print("-" * 80)

    min_angle = 3.0 * math.pi / 180  # 3 degrees minimum elevation

    muf_calc = MufCalculator(path, maps, min_angle)
    circuit_muf = muf_calc.compute_circuit_muf([profile])

    print(f"Circuit MUF: {circuit_muf.muf:.2f} MHz (via {circuit_muf.layer} layer)")
    print(f"Circuit FOT: {circuit_muf.fot:.2f} MHz (Frequency of Optimum Traffic)")
    print(f"Circuit HPF: {circuit_muf.hpf:.2f} MHz (High Probability Frequency)")
    print(f"Elevation:   {circuit_muf.angle * 180/math.pi:.1f}°")
    print()

    print("Layer-specific MUF values:")
    for layer, info in circuit_muf.muf_info.items():
        print(f"  {layer:3s} layer: MUF={info.muf:6.2f} MHz, "
              f"FOT={info.fot:6.2f} MHz, "
              f"Hops={info.hop_count}, "
              f"Elev={info.ref.elevation*180/math.pi:5.1f}°")
    print()

    # ========================================================================
    # Step 6: Compute Reflectrix (Ray Paths)
    # ========================================================================
    print("Step 6: Computing reflectrix (ray paths)")
    print("-" * 80)

    # Test at a frequency near the MUF
    test_freq = circuit_muf.muf * 0.85  # 85% of MUF (good operating frequency)

    reflectrix = Reflectrix(min_angle, test_freq, profile)

    print(f"Frequency:   {test_freq:.2f} MHz")
    print(f"Skip dist:   {reflectrix.skip_distance * 6370:.1f} km (minimum usable distance)")
    print(f"Max dist:    {reflectrix.max_distance * 6370:.1f} km (maximum single-hop distance)")
    print(f"Reflections: {len(reflectrix.refl)} ray paths found")
    print()

    # Show first few reflection points
    print("First 5 reflection points:")
    print(f"{'Elev (°)':<10} {'Layer':<8} {'Height (km)':<12} {'Hop Dist (km)':<15}")
    print("-" * 45)
    for i, mode in enumerate(reflectrix.refl[:5]):
        elev_deg = mode.ref.elevation * 180 / math.pi
        hop_dist_km = mode.hop_dist * 6370
        print(f"{elev_deg:<10.1f} {mode.layer:<8} {mode.ref.virt_height:<12.0f} {hop_dist_km:<15.1f}")
    print()

    # ========================================================================
    # Step 7: Find modes for specific path distance
    # ========================================================================
    print("Step 7: Finding propagation modes for the circuit")
    print("-" * 80)

    # For our path distance, find possible modes
    single_hop_dist = path.dist  # Try single hop first
    hop_count = 1

    reflectrix.find_modes(single_hop_dist, hop_count)

    if len(reflectrix.modes) > 0:
        print(f"Found {len(reflectrix.modes)} propagation modes for single hop:")
        print()
        print(f"{'Mode':<6} {'Layer':<8} {'Elev (°)':<10} {'Virt H (km)':<12} {'True H (km)':<12}")
        print("-" * 58)

        for i, mode in enumerate(reflectrix.modes):
            elev_deg = mode.ref.elevation * 180 / math.pi
            print(f"{i+1:<6} {mode.layer:<8} {elev_deg:<10.1f} "
                  f"{mode.ref.virt_height:<12.0f} {mode.ref.true_height:<12.0f}")
    else:
        # Path too long for single hop, try 2 hops
        single_hop_dist = path.dist / 2
        hop_count = 2
        reflectrix.find_modes(single_hop_dist, hop_count)

        print(f"Single hop not possible. Found {len(reflectrix.modes)} modes for 2-hop:")
        print()
        print(f"{'Mode':<6} {'Layer':<8} {'Elev (°)':<10} {'Virt H (km)':<12} {'Hops':<6}")
        print("-" * 52)

        for i, mode in enumerate(reflectrix.modes):
            elev_deg = mode.ref.elevation * 180 / math.pi
            print(f"{i+1:<6} {mode.layer:<8} {elev_deg:<10.1f} "
                  f"{mode.ref.virt_height:<12.0f} {mode.hop_cnt:<6}")
    print()

    # ========================================================================
    # Summary
    # ========================================================================
    print("=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"Path:        {path.get_distance_km():.0f} km from Philadelphia to London")
    print(f"Conditions:  June, SSN={ssn}, {utc_hour:.0f}:00 UTC")
    print(f"MUF:         {circuit_muf.muf:.2f} MHz via {circuit_muf.layer} layer")
    print(f"Recommended: {test_freq:.2f} MHz (85% of MUF)")
    print(f"Modes:       {len(reflectrix.modes)} propagation paths available")
    print()
    print("Phase 4 (Raytracing) complete! ✓")
    print("=" * 80)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
