#!/usr/bin/env python3
"""
Quick test to verify Phase 5 API fixes are working.
"""

import sys
import numpy as np
sys.path.insert(0, 'src')

from dvoacap.prediction_engine import PredictionEngine
from dvoacap.path_geometry import GeoPoint

def test_prediction_engine_instantiation():
    """Test that PredictionEngine can be instantiated."""
    print("Testing PredictionEngine instantiation...")
    engine = PredictionEngine()
    assert engine is not None
    assert hasattr(engine, 'muf_calculator')
    assert hasattr(engine, 'circuit_muf')
    print("✓ PredictionEngine instantiated successfully")
    print(f"  - muf_calculator type: {type(engine.muf_calculator).__name__}")
    print(f"  - circuit_muf initialized: {engine.circuit_muf}")
    return engine

def test_basic_prediction():
    """Test that a basic prediction can be run."""
    print("\nTesting basic prediction...")

    engine = PredictionEngine()

    # Set up a simple scenario
    engine.params.tx_location = GeoPoint(lat=np.deg2rad(40.0), lon=np.deg2rad(-75.0))
    rx_location = GeoPoint(lat=np.deg2rad(51.5), lon=np.deg2rad(-0.1))

    try:
        engine.predict(
            rx_location=rx_location,
            utc_time=0.5,
            frequencies=[7.0, 14.0, 21.0]
        )
        print("✓ Basic prediction completed without errors")
        print(f"  - Number of predictions: {len(engine.predictions)}")
        print(f"  - Circuit MUF: {engine.circuit_muf.muf:.2f} MHz")

        # Check that profiles have correct attributes
        if engine._profiles:
            profile = engine._profiles[0]
            print(f"  - Profile has .e attribute: {hasattr(profile, 'e')}")
            print(f"  - Profile has .f1 attribute: {hasattr(profile, 'f1')}")
            print(f"  - Profile has .f2 attribute: {hasattr(profile, 'f2')}")
            print(f"  - Profile has .gyro_freq attribute: {hasattr(profile, 'gyro_freq')}")

            # Verify old attributes don't exist
            has_old_attrs = (hasattr(profile, 'e_layer') or
                           hasattr(profile, 'f1_layer') or
                           hasattr(profile, 'f2_layer') or
                           hasattr(profile, 'gyro_frequency'))
            if has_old_attrs:
                print("  ✗ WARNING: Profile still has old attribute names!")
            else:
                print("  ✓ Profile uses correct attribute names")

        return True
    except Exception as e:
        print(f"✗ Prediction failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Phase 5 API Fixes Verification Test")
    print("=" * 60)

    try:
        # Test 1: Instantiation
        engine = test_prediction_engine_instantiation()

        # Test 2: Basic prediction
        success = test_basic_prediction()

        print("\n" + "=" * 60)
        if success:
            print("✓ All API fixes verified successfully!")
            print("=" * 60)
            return 0
        else:
            print("✗ Some tests failed")
            print("=" * 60)
            return 1

    except Exception as e:
        print(f"\n✗ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
