"""
DVOACAP Validation Script
Validates installation and tests core functionality
Run this AFTER running install_dvoacap.py
"""
import sys

def validate_installation():
    """Validate DVOACAP installation and basic functionality."""
    print("=" * 60)
    print("DVOACAP Validation Script")
    print("=" * 60)
    print("\nThis script will test your DVOACAP installation")
    print("and run a basic HF propagation prediction.\n")

    # Test 1: Import dvoacap
    print("=" * 60)
    print("[1/4] Testing package import...")
    print("=" * 60)
    try:
        import dvoacap
        version = getattr(dvoacap, '__version__', 'unknown')
        print(f"✓ Successfully imported dvoacap (version {version})")
    except ImportError as e:
        print(f"✗ FAILED: Cannot import dvoacap")
        print(f"  Error: {e}")
        print("\nPlease run install_dvoacap.py first")
        return False

    # Test 2: Import core components
    print("\n" + "=" * 60)
    print("[2/4] Testing core components...")
    print("=" * 60)
    try:
        from dvoacap import FourierMaps, ControlPoint, IonoPoint, compute_iono_params
        print("✓ Core components available:")
        print("  - FourierMaps (ionospheric data)")
        print("  - ControlPoint (location/time)")
        print("  - IonoPoint (geographic coordinates)")
        print("  - compute_iono_params (calculation engine)")
    except ImportError as e:
        print(f"✗ FAILED: Cannot import core components")
        print(f"  Error: {e}")
        return False

    # Test 3: Load ionospheric maps
    print("\n" + "=" * 60)
    print("[3/4] Loading ionospheric maps...")
    print("=" * 60)
    print("Loading CCIR/URSI coefficients...")
    try:
        maps = FourierMaps()
        print("✓ Ionospheric maps loaded successfully")

        # Set conditions
        print("\nSetting conditions:")
        print("  - Month: June")
        print("  - Sunspot Number (SSN): 100 (moderate solar activity)")
        print("  - UTC Time: 12:00 (noon)")
        maps.set_conditions(month=6, ssn=100, utc_fraction=0.5)
        print("✓ Conditions set successfully")
    except Exception as e:
        print(f"✗ FAILED: Cannot load ionospheric maps")
        print(f"  Error: {e}")
        return False

    # Test 4: Run basic computation
    print("\n" + "=" * 60)
    print("[4/4] Running HF propagation prediction...")
    print("=" * 60)
    print("Computing ionospheric conditions at Halifax, Nova Scotia")
    print("Location: 44.65°N, 63.57°W\n")

    try:
        import math

        # Create control point at Halifax, NS
        pnt = ControlPoint(
            location=IonoPoint.from_degrees(44.65, -63.57),
            east_lon=-63.57 * math.pi/180,
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

        print("✓ Prediction calculation successful!\n")

        # Display results
        print("=" * 60)
        print("IONOSPHERIC PREDICTION RESULTS")
        print("=" * 60)
        print("\nLocation: Halifax, Nova Scotia (44.65°N, 63.57°W)")
        print("Date: June")
        print("Time: 12:00 UTC (Noon)")
        print("Solar Activity: SSN 100 (moderate)")
        print("\n" + "-" * 60)
        print("IONOSPHERIC LAYERS:")
        print("-" * 60)
        print(f"E  Layer: foE  = {pnt.e.fo:5.2f} MHz  at  {pnt.e.hm:4.0f} km altitude")
        print(f"F1 Layer: foF1 = {pnt.f1.fo:5.2f} MHz  at  {pnt.f1.hm:4.0f} km altitude")
        print(f"F2 Layer: foF2 = {pnt.f2.fo:5.2f} MHz  at  {pnt.f2.hm:4.0f} km altitude")
        print("-" * 60)

        print("\nWhat these numbers mean:")
        print(f"  • E Layer (110 km):  Supports frequencies up to {pnt.e.fo:.1f} MHz")
        print(f"  • F1 Layer (200 km): Supports frequencies up to {pnt.f1.fo:.1f} MHz")
        print(f"  • F2 Layer (300 km): Supports frequencies up to {pnt.f2.fo:.1f} MHz")
        print(f"\n  Maximum Usable Frequency (MUF): ~{pnt.f2.fo * 3.0:.1f} MHz")
        print(f"  (for this location and time)")

    except Exception as e:
        print(f"✗ FAILED: Prediction calculation error")
        print(f"  Error: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Success!
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nDVOACAP is installed correctly and ready to use.")
    print("\nFor more examples and documentation, visit:")
    print("https://github.com/skyelaird/dvoacap-python")
    print("https://skyelaird.github.io/dvoacap-python/")

    return True

def main():
    """Main entry point."""
    print("\n" + "=" * 60)
    print("DVOACAP-Python - HF Propagation Prediction Engine")
    print("=" * 60)
    print("https://github.com/skyelaird/dvoacap-python\n")

    success = validate_installation()

    print("\n" + "=" * 60)
    if success:
        print("Status: ✓ VALIDATION SUCCESSFUL")
    else:
        print("Status: ✗ VALIDATION FAILED")
        print("\nTroubleshooting:")
        print("1. Make sure you ran install_dvoacap.py first")
        print("2. Check that Python 3.11+ is installed")
        print("3. Try: pip install --upgrade dvoacap")
        print("\nFor help, create an issue at:")
        print("https://github.com/skyelaird/dvoacap-python/issues")

    print("=" * 60)
    input("\nPress Enter to exit...")
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
