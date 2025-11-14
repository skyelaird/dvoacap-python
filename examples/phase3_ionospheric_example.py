#!/usr/bin/env python3
"""
Phase 3 Example: Ionospheric Profiles

This example demonstrates the use of Phase 3 modules to compute ionospheric
layer parameters and electron density profiles for HF propagation prediction.

Features demonstrated:
- Loading CCIR/URSI coefficient maps
- Computing ionospheric layer parameters (E, F1, F2, Es)
- Creating electron density profiles
- Computing ionograms
- Calculating true and virtual heights
"""

import math
from datetime import datetime
from dvoacap.fourier_maps import FourierMaps, VarMapKind, FixedMapKind
from dvoacap.ionospheric_profile import IonosphericProfile, LayerInfo
from dvoacap.layer_parameters import (
    ControlPoint,
    GeographicPoint,
    compute_iono_params,
    RinD,
    DinR
)


def main():
    print("=" * 70)
    print("DVOACAP Phase 3: Ionospheric Profiles Example")
    print("=" * 70)

    # =======================================================================
    # 1. Load CCIR/URSI Coefficient Maps
    # =======================================================================
    print("\n1. Loading CCIR/URSI coefficient maps...")

    maps = FourierMaps()

    # Set propagation conditions
    # - June (summer in northern hemisphere)
    # - SSN = 100 (moderate solar activity)
    # - Noon UTC
    maps.set_conditions(month=6, ssn=100, utc_fraction=0.5)
    print(f"   Conditions: June, SSN=100, Noon UTC")

    # =======================================================================
    # 2. Query Ionospheric Parameters at Specific Locations
    # =======================================================================
    print("\n2. Querying ionospheric parameters at various locations...")

    locations = [
        (0.0, 0.0, "Equator"),
        (40.0, -75.0, "Philadelphia, PA"),
        (51.5, -0.1, "London, UK"),
        (-33.9, 18.4, "Cape Town, South Africa")
    ]

    for lat_deg, lon_deg, name in locations:
        lat = lat_deg * RinD
        lon = lon_deg * RinD
        cos_lat = math.cos(lat)

        fof2 = maps.compute_var_map(VarMapKind.F2, lat, lon, cos_lat)
        foe = maps.compute_var_map(VarMapKind.ER, lat, lon, cos_lat)
        m3000 = maps.compute_var_map(VarMapKind.FM3, lat, lon, cos_lat)

        print(f"\n   {name} ({lat_deg:.1f}°, {lon_deg:.1f}°):")
        print(f"     foF2   = {fof2:.2f} MHz")
        print(f"     foE    = {foe:.2f} MHz")
        print(f"     M3000  = {m3000:.2f}")

    # =======================================================================
    # 3. Compute Complete Ionospheric Profile for a Path Point
    # =======================================================================
    print("\n3. Computing complete ionospheric profile for Philadelphia...")

    # Create a control point representing propagation conditions
    # at Philadelphia at noon local time
    pnt = ControlPoint(
        location=GeographicPoint.from_degrees(40.0, -75.0),
        east_lon=-75.0 * RinD,
        distance_rad=0.0,
        local_time=0.5,  # Noon local time
        zen_angle=0.3,   # ~17° solar zenith angle
        zen_max=1.5,     # ~86° maximum zenith for F1
        mag_lat=50.0 * RinD,  # Magnetic latitude
        mag_dip=60.0 * RinD,  # Magnetic dip angle
        gyro_freq=1.2         # Gyrofrequency in MHz
    )

    # Compute all ionospheric layer parameters
    compute_iono_params(pnt, maps)

    print("\n   Ionospheric Layers:")
    print(f"     E layer:  foE  = {pnt.e.fo:.2f} MHz, hm = {pnt.e.hm:.0f} km, ym = {pnt.e.ym:.1f} km")
    print(f"     F1 layer: foF1 = {pnt.f1.fo:.2f} MHz, hm = {pnt.f1.hm:.0f} km, ym = {pnt.f1.ym:.1f} km")
    print(f"     F2 layer: foF2 = {pnt.f2.fo:.2f} MHz, hm = {pnt.f2.hm:.0f} km, ym = {pnt.f2.ym:.1f} km")
    print(f"     Es layer: foEs = {pnt.es.fo:.2f} MHz, hm = {pnt.es.hm:.0f} km")

    print(f"\n   Additional Parameters:")
    print(f"     M3000F2 = {pnt.f2m3:.2f}")
    print(f"     hpF2    = {pnt.hpf2:.1f} km")
    print(f"     Rat     = {pnt.rat:.2f}")

    # =======================================================================
    # 4. Create Electron Density Profile
    # =======================================================================
    print("\n4. Creating electron density profile...")

    profile = IonosphericProfile()
    profile.e = pnt.e
    profile.f1 = pnt.f1
    profile.f2 = pnt.f2

    # Compute electron density vs height
    profile.compute_el_density_profile()
    print(f"   ✓ Computed {len(profile.dens_true_height)} height points")
    print(f"   Height range: {profile.dens_true_height[1]:.0f} - {profile.dens_true_height[50]:.0f} km")

    # =======================================================================
    # 5. Calculate Heights for Specific Frequencies
    # =======================================================================
    print("\n5. Calculating heights for specific frequencies...")

    test_freqs = [3.5, 7.0, 10.0, 14.0, 21.0]
    print(f"\n   {'Freq (MHz)':<12} {'True Height':<15} {'Virtual Height':<15} {'Difference'}")
    print(f"   {'-'*12} {'-'*15} {'-'*15} {'-'*10}")

    for freq in test_freqs:
        if freq < pnt.f2.fo:
            h_true = profile.get_true_height(freq)
            h_virt = profile.get_virtual_height_gauss(freq)
            diff = h_virt - h_true
            print(f"   {freq:<12.1f} {h_true:<15.1f} {h_virt:<15.1f} {diff:>10.1f} km")
        else:
            print(f"   {freq:<12.1f} (above foF2={pnt.f2.fo:.2f} MHz - no reflection)")

    # =======================================================================
    # 6. Generate Ionogram
    # =======================================================================
    print("\n6. Generating ionogram...")

    profile.compute_ionogram()
    print(f"   ✓ Generated ionogram with {len(profile.igram_vert_freq)} frequency points")
    print(f"   Frequency range: {profile.igram_vert_freq[1]:.2f} - {profile.igram_vert_freq[30]:.2f} MHz")

    # Show key ionogram points
    print("\n   Key Ionogram Points:")
    indices = {
        10: "E layer nose",
        20: "F1 layer nose",
        30: "F2 layer nose"
    }
    for idx, label in indices.items():
        if idx < len(profile.igram_vert_freq):
            freq = profile.igram_vert_freq[idx]
            h_true = profile.igram_true_height[idx]
            h_virt = profile.igram_virt_height[idx]
            print(f"     {label:15} f={freq:.2f} MHz, h'={h_true:.0f} km, h={h_virt:.0f} km")

    # =======================================================================
    # 7. Compute Penetration Angles
    # =======================================================================
    print("\n7. Computing penetration angles for oblique propagation...")

    test_freq = 15.0  # MHz
    if test_freq <= pnt.f2.fo:
        angles = profile.compute_penetration_angles(test_freq)
        e_angle = angles['E']
        f1_angle = angles['F1']
        f2_angle = angles['F2']

        print(f"\n   At {test_freq:.1f} MHz:")
        print(f"     E layer:  Maximum elevation = {e_angle * DinR:.1f}°")
        print(f"     F1 layer: Maximum elevation = {f1_angle * DinR:.1f}°")
        print(f"     F2 layer: Maximum elevation = {f2_angle * DinR:.1f}°")
    else:
        print(f"\n   {test_freq:.1f} MHz is above foF2, cannot penetrate ionosphere")

    # =======================================================================
    # 8. Seasonal and Solar Cycle Variations
    # =======================================================================
    print("\n8. Demonstrating seasonal and solar cycle variations...")

    print("\n   Monthly variation at Philadelphia (SSN=100):")
    print(f"   {'Month':<12} {'foF2 (MHz)':<12} {'foE (MHz)':<12} {'M3000'}")
    print(f"   {'-'*12} {'-'*12} {'-'*12} {'-'*6}")

    for month_num, month_name in [(1, "January"), (6, "June"), (12, "December")]:
        maps_temp = FourierMaps()
        maps_temp.set_conditions(month=month_num, ssn=100, utc_fraction=0.5)

        pnt_temp = ControlPoint(
            location=GeographicPoint.from_degrees(40.0, -75.0),
            east_lon=-75.0 * RinD,
            distance_rad=0.0,
            local_time=0.5,
            zen_angle=0.3,
            zen_max=1.5,
            mag_lat=50.0 * RinD,
            mag_dip=60.0 * RinD,
            gyro_freq=1.2
        )

        compute_iono_params(pnt_temp, maps_temp)
        print(f"   {month_name:<12} {pnt_temp.f2.fo:<12.2f} {pnt_temp.e.fo:<12.2f} {pnt_temp.f2m3:<6.2f}")

    print("\n   Solar cycle variation at Philadelphia in June:")
    print(f"   {'SSN':<12} {'foF2 (MHz)':<12} {'foE (MHz)':<12} {'M3000'}")
    print(f"   {'-'*12} {'-'*12} {'-'*12} {'-'*6}")

    for ssn in [0, 50, 100, 150, 200]:
        maps_temp = FourierMaps()
        maps_temp.set_conditions(month=6, ssn=ssn, utc_fraction=0.5)

        pnt_temp = ControlPoint(
            location=GeographicPoint.from_degrees(40.0, -75.0),
            east_lon=-75.0 * RinD,
            distance_rad=0.0,
            local_time=0.5,
            zen_angle=0.3,
            zen_max=1.5,
            mag_lat=50.0 * RinD,
            mag_dip=60.0 * RinD,
            gyro_freq=1.2
        )

        compute_iono_params(pnt_temp, maps_temp)
        print(f"   {ssn:<12} {pnt_temp.f2.fo:<12.2f} {pnt_temp.e.fo:<12.2f} {pnt_temp.f2m3:<6.2f}")

    # =======================================================================
    # Summary
    # =======================================================================
    print("\n" + "=" * 70)
    print("Example Complete!")
    print("\nPhase 3 provides:")
    print("  • CCIR/URSI ionospheric coefficient maps")
    print("  • E, F1, F2, and Es layer parameter calculations")
    print("  • Electron density profile modeling")
    print("  • True and virtual height calculations")
    print("  • Ionogram generation")
    print("  • Penetration angle calculations for oblique propagation")
    print("\nThese capabilities form the foundation for HF propagation prediction!")
    print("=" * 70)


if __name__ == "__main__":
    main()
