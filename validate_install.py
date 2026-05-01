"""
DVOACAP Installation Validation Script
Run this after installing: pip install dvoacap
"""
import sys

def validate_installation():
    """Validate DVOACAP installation and basic functionality."""
    print("=" * 60)
    print("DVOACAP Installation Validation")
    print("=" * 60)

    # Test 1: Import dvoacap
    print("\n[1/4] Testing import...")
    try:
        import dvoacap
        print("✓ Successfully imported dvoacap")
    except ImportError as e:
        print(f"✗ Failed to import dvoacap: {e}")
        return False

    # Test 2: Import core components
    print("\n[2/4] Testing core components...")
    try:
        from dvoacap import FourierMaps, ControlPoint, IonoPoint, compute_iono_params
        print("✓ Core components available")
    except ImportError as e:
        print(f"✗ Failed to import core components: {e}")
        return False

    # Test 3: Load ionospheric maps
    print("\n[3/4] Loading ionospheric maps...")
    try:
        maps = FourierMaps()
        maps.set_conditions(month=6, ssn=100, utc_fraction=0.5)
        print("✓ Ionospheric maps loaded successfully")
    except Exception as e:
        print(f"✗ Failed to load maps: {e}")
        return False

    # Test 4: Run basic computation
    print("\n[4/4] Running basic propagation calculation...")
    try:
        import math

        # Create control point at Philadelphia
        pnt = ControlPoint(
            location=IonoPoint.from_degrees(40.0, -75.0),
            east_lon=-75.0 * math.pi/180,
            distance_rad=0.0,
            local_time=0.5,
            zen_angle=0.3,
            zen_max=1.5,
            mag_lat=50.0 * math.pi/180,
            mag_dip=60.0 * math.pi/180,
            gyro_freq=1.2
        )

        # Compute ionospheric parameters
        compute_iono_params(pnt, maps)

        print("✓ Propagation calculation successful")
        print("\n" + "=" * 60)
        print("RESULTS - Ionospheric Conditions at Philadelphia")
        print("=" * 60)
        print(f"E layer:  foE  = {pnt.e.fo:.2f} MHz at {pnt.e.hm:.0f} km")
        print(f"F1 layer: foF1 = {pnt.f1.fo:.2f} MHz at {pnt.f1.hm:.0f} km")
        print(f"F2 layer: foF2 = {pnt.f2.fo:.2f} MHz at {pnt.f2.hm:.0f} km")

    except Exception as e:
        print(f"✗ Failed to run calculation: {e}")
        import traceback
        traceback.print_exc()
        return False

    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED - DVOACAP is ready to use!")
    print("=" * 60)
    return True

if __name__ == "__main__":
    success = validate_installation()
    sys.exit(0 if success else 1)
