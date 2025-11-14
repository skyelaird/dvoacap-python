"""
Tests for Phase 3: Ionospheric Profiles
Tests fourier_maps, ionospheric_profile, and layer_parameters modules
"""

import math
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from dvoacap.fourier_maps import FourierMaps, VarMapKind, FixedMapKind, Distribution
from dvoacap.ionospheric_profile import IonosphericProfile, LayerInfo
from dvoacap.layer_parameters import (
    ControlPoint,
    GeographicPoint,
    compute_iono_params,
    RinD
)


# ============================================================================
# FourierMaps Tests
# ============================================================================

def test_fourier_maps_initialization():
    """Test that FourierMaps initializes correctly"""
    maps = FourierMaps()
    assert maps.month == 1
    assert maps.ssn == 1.0
    assert maps.utc_fraction == 0.0
    print("✓ test_fourier_maps_initialization")


def test_fourier_maps_set_conditions():
    """Test setting conditions"""
    maps = FourierMaps()
    maps.set_conditions(month=6, ssn=100, utc_fraction=0.5)
    assert maps.month == 6
    assert maps.ssn == 100.0
    assert maps.utc_fraction == 0.5
    print("✓ test_fourier_maps_set_conditions")


def test_compute_var_map_fof2():
    """Test foF2 computation at various locations"""
    maps = FourierMaps()
    maps.set_conditions(month=6, ssn=100, utc_fraction=0.5)

    # Equator
    fof2_eq = maps.compute_var_map(VarMapKind.F2, 0.0, 0.0, 1.0)
    assert 5.0 < fof2_eq < 15.0, f"foF2 at equator should be 5-15 MHz, got {fof2_eq}"

    # Mid-latitude
    lat = 40 * RinD
    fof2_mid = maps.compute_var_map(VarMapKind.F2, lat, 0.0, math.cos(lat))
    assert 3.0 < fof2_mid < 12.0, f"foF2 at 40N should be 3-12 MHz, got {fof2_mid}"

    print("✓ test_compute_var_map_fof2")


def test_compute_var_map_foe():
    """Test foE computation"""
    maps = FourierMaps()
    maps.set_conditions(month=6, ssn=100, utc_fraction=0.5)

    # Equator at noon
    foe = maps.compute_var_map(VarMapKind.ER, 0.0, 0.0, 1.0)
    assert 2.0 < foe < 5.0, f"foE should be 2-5 MHz, got {foe}"

    print("✓ test_compute_var_map_foe")


def test_compute_fixed_map():
    """Test fixed map computation"""
    maps = FourierMaps()
    maps.set_conditions(month=6, ssn=100, utc_fraction=0.5)

    # YmF2 should be positive and reasonable
    ym_f2 = maps.compute_fixed_map(FixedMapKind.YM_F2, 0.0, 0.0)
    assert 2.0 < ym_f2 < 10.0, f"YmF2 should be 2-10, got {ym_f2}"

    print("✓ test_compute_fixed_map")


def test_compute_fof1():
    """Test F1 layer frequency computation"""
    maps = FourierMaps()
    maps.set_conditions(month=6, ssn=100, utc_fraction=0.5)

    # Test at small zenith angle (daytime)
    zen = 0.3  # ~17 degrees
    fof1 = maps.compute_fof1(zen)
    assert 3.0 < fof1 < 8.0, f"foF1 should be 3-8 MHz, got {fof1}"

    print("✓ test_compute_fof1")


def test_compute_zen_max():
    """Test maximum zenith angle for F1 formation"""
    maps = FourierMaps()
    maps.set_conditions(month=6, ssn=100, utc_fraction=0.5)

    # Test at various magnetic dips
    mag_dip = 60 * RinD
    zen_max = maps.compute_zen_max(mag_dip)
    assert 1.0 < zen_max < 2.0, f"zen_max should be 1-2 rad, got {zen_max}"

    print("✓ test_compute_zen_max")


# ============================================================================
# IonosphericProfile Tests
# ============================================================================

def test_ionospheric_profile_creation():
    """Test creating an ionospheric profile"""
    profile = IonosphericProfile()
    assert profile.e.fo == 0.0
    assert profile.f1.fo == 0.0
    assert profile.f2.fo == 0.0
    print("✓ test_ionospheric_profile_creation")


def test_compute_el_density_profile():
    """Test electron density profile computation"""
    profile = IonosphericProfile()
    profile.e = LayerInfo(fo=3.0, hm=110, ym=20)
    profile.f1 = LayerInfo(fo=5.0, hm=200, ym=50)
    profile.f2 = LayerInfo(fo=8.0, hm=300, ym=100)

    profile.compute_el_density_profile()

    assert profile.dens_true_height is not None
    assert profile.el_density is not None
    assert len(profile.dens_true_height) == 51
    assert len(profile.el_density) == 51

    # Check that heights increase monotonically
    for i in range(1, 50):
        assert profile.dens_true_height[i] < profile.dens_true_height[i+1]

    print("✓ test_compute_el_density_profile")


def test_get_true_height():
    """Test true height calculation"""
    profile = IonosphericProfile()
    profile.e = LayerInfo(fo=3.0, hm=110, ym=20)
    profile.f1 = LayerInfo(fo=5.0, hm=200, ym=50)
    profile.f2 = LayerInfo(fo=8.0, hm=300, ym=100)
    profile.compute_el_density_profile()

    # Test at F1 layer frequency
    h = profile.get_true_height(5.0)
    assert 150 < h < 250, f"True height at foF1 should be near F1 peak, got {h}"

    print("✓ test_get_true_height")


def test_get_virtual_height():
    """Test virtual height calculation"""
    profile = IonosphericProfile()
    profile.e = LayerInfo(fo=3.0, hm=110, ym=20)
    profile.f1 = LayerInfo(fo=5.0, hm=200, ym=50)
    profile.f2 = LayerInfo(fo=8.0, hm=300, ym=100)
    profile.compute_el_density_profile()

    # Virtual height should be greater than true height
    freq = 5.0
    h_true = profile.get_true_height(freq)
    h_virt = profile.get_virtual_height_gauss(freq)

    assert h_virt > h_true, "Virtual height should exceed true height"
    assert h_virt < h_true * 3, "Virtual height shouldn't be excessively large"

    print("✓ test_get_virtual_height")


def test_compute_ionogram():
    """Test ionogram computation"""
    profile = IonosphericProfile()
    profile.e = LayerInfo(fo=3.0, hm=110, ym=20)
    profile.f1 = LayerInfo(fo=5.0, hm=200, ym=50)
    profile.f2 = LayerInfo(fo=8.0, hm=300, ym=100)
    profile.compute_el_density_profile()
    profile.compute_ionogram()

    assert profile.igram_vert_freq is not None
    assert profile.igram_true_height is not None
    assert profile.igram_virt_height is not None
    assert len(profile.igram_vert_freq) == 31

    # Check that frequencies increase
    for i in range(1, 30):
        assert profile.igram_vert_freq[i] <= profile.igram_vert_freq[i+1]

    # Check that virtual >= true height
    for i in range(1, 31):
        assert profile.igram_virt_height[i] >= profile.igram_true_height[i]

    print("✓ test_compute_ionogram")


def test_compute_penetration_angles():
    """Test penetration angle computation"""
    profile = IonosphericProfile()
    profile.e = LayerInfo(fo=3.0, hm=110, ym=20)
    profile.f1 = LayerInfo(fo=5.0, hm=200, ym=50)
    profile.f2 = LayerInfo(fo=8.0, hm=300, ym=100)
    profile.compute_el_density_profile()
    profile.compute_ionogram()

    # Test at frequency above all layers
    freq = 10.0
    angles = profile.compute_penetration_angles(freq)
    e_angle = angles['E']
    f1_angle = angles['F1']
    f2_angle = angles['F2']

    # All angles should be valid
    assert 0 <= e_angle <= math.pi/2
    assert 0 <= f1_angle <= math.pi/2
    assert 0 <= f2_angle <= math.pi/2

    # Angles should increase: E < F1 < F2
    assert e_angle <= f1_angle
    assert f1_angle <= f2_angle

    print("✓ test_compute_penetration_angles")


# ============================================================================
# LayerParameters Tests
# ============================================================================

def test_control_point_creation():
    """Test control point creation"""
    pnt = ControlPoint(
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

    assert pnt.location.latitude == 40.0 * RinD
    assert pnt.e is not None
    assert pnt.f1 is not None
    assert pnt.f2 is not None

    print("✓ test_control_point_creation")


def test_compute_iono_params():
    """Test complete ionospheric parameter computation"""
    pnt = ControlPoint(
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

    maps = FourierMaps()
    maps.set_conditions(month=6, ssn=100, utc_fraction=0.5)

    compute_iono_params(pnt, maps)

    # Check E layer
    assert 1.0 < pnt.e.fo < 5.0, f"foE should be 1-5 MHz, got {pnt.e.fo}"
    assert pnt.e.hm == 110

    # Check F1 layer (should exist for daytime)
    assert pnt.f1.fo > 0, "F1 layer should exist in daytime"
    assert 3.0 < pnt.f1.fo < 8.0, f"foF1 should be 3-8 MHz, got {pnt.f1.fo}"

    # Check F2 layer
    assert 3.0 < pnt.f2.fo < 12.0, f"foF2 should be 3-12 MHz, got {pnt.f2.fo}"
    assert 200 < pnt.f2.hm < 400, f"hmF2 should be 200-400 km, got {pnt.f2.hm}"

    # Check Es layer
    assert pnt.es.fo > 0, "foEs should be positive"

    # Check layer ordering: foE < foF1 < foF2
    assert pnt.e.fo < pnt.f1.fo
    assert pnt.f1.fo < pnt.f2.fo

    print("✓ test_compute_iono_params")


def test_compute_iono_params_nighttime():
    """Test ionospheric parameters at night (no F1 layer)"""
    pnt = ControlPoint(
        location=GeographicPoint.from_degrees(40.0, -75.0),
        east_lon=-75.0 * RinD,
        distance_rad=0.0,
        local_time=0.0,  # Midnight
        zen_angle=2.5,   # Large zenith angle (night)
        zen_max=1.5,     # Smaller than zen_angle
        mag_lat=50.0 * RinD,
        mag_dip=60.0 * RinD,
        gyro_freq=1.2
    )

    maps = FourierMaps()
    maps.set_conditions(month=6, ssn=100, utc_fraction=0.0)

    compute_iono_params(pnt, maps)

    # F1 layer should not exist at night
    assert pnt.f1.fo == 0, "F1 layer should not exist at night"

    # F2 layer should still exist
    assert pnt.f2.fo > 0, "F2 layer should exist at night"

    print("✓ test_compute_iono_params_nighttime")


# ============================================================================
# Integration Tests
# ============================================================================

def test_integration_full_profile():
    """Test creating a complete ionospheric profile from layer parameters"""
    # Create control point and compute parameters
    pnt = ControlPoint(
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

    maps = FourierMaps()
    maps.set_conditions(month=6, ssn=100, utc_fraction=0.5)
    compute_iono_params(pnt, maps)

    # Create profile from computed parameters
    profile = IonosphericProfile()
    profile.e = pnt.e
    profile.f1 = pnt.f1
    profile.f2 = pnt.f2

    # Compute electron density profile
    profile.compute_el_density_profile()

    # Compute ionogram
    profile.compute_ionogram()

    # Verify ionogram frequencies match layer parameters
    assert max(profile.igram_vert_freq) <= pnt.f2.fo

    # Test height lookup
    h_true = profile.get_true_height(pnt.f1.fo)
    h_virt = profile.get_virtual_height_gauss(pnt.f1.fo)

    assert h_virt > h_true
    assert 100 < h_true < 400

    print("✓ test_integration_full_profile")


def test_integration_seasonal_variation():
    """Test that ionospheric parameters vary with season"""
    fof2_values = []

    # Test different months
    for month in [1, 6, 12]:  # January, June, December
        pnt = ControlPoint(
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
        maps = FourierMaps()
        maps.set_conditions(month=month, ssn=100, utc_fraction=0.5)
        compute_iono_params(pnt, maps)
        fof2_values.append(pnt.f2.fo)

    # Values should be different across seasons
    assert len(set(fof2_values)) > 1, "foF2 should vary with season"

    print("✓ test_integration_seasonal_variation")


# ============================================================================
# Run All Tests
# ============================================================================

def run_all_tests():
    """Run all test functions"""
    print("=" * 70)
    print("PHASE 3: IONOSPHERIC PROFILES - COMPREHENSIVE TEST SUITE")
    print("=" * 70)

    print("\n--- FourierMaps Tests ---")
    test_fourier_maps_initialization()
    test_fourier_maps_set_conditions()
    test_compute_var_map_fof2()
    test_compute_var_map_foe()
    test_compute_fixed_map()
    test_compute_fof1()
    test_compute_zen_max()

    print("\n--- IonosphericProfile Tests ---")
    test_ionospheric_profile_creation()
    test_compute_el_density_profile()
    test_get_true_height()
    test_get_virtual_height()
    test_compute_ionogram()
    test_compute_penetration_angles()

    print("\n--- LayerParameters Tests ---")
    test_control_point_creation()
    test_compute_iono_params()
    test_compute_iono_params_nighttime()

    print("\n--- Integration Tests ---")
    test_integration_full_profile()
    test_integration_seasonal_variation()

    print("\n" + "=" * 70)
    print("ALL TESTS PASSED! ✓")
    print("=" * 70)


if __name__ == "__main__":
    run_all_tests()
