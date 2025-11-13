#!/usr/bin/env python3
"""
Test script to verify proppy library capabilities
"""

import sys

print("Testing proppy library...")
print("-" * 60)

try:
    import proppy
    print("✓ proppy imported successfully")
    print(f"  Version: {proppy.__version__ if hasattr(proppy, '__version__') else 'unknown'}")
    
    # Check what's available in proppy
    print(f"\nAvailable attributes:")
    attrs = [a for a in dir(proppy) if not a.startswith('_')]
    for attr in attrs:
        print(f"  - {attr}")
        obj = getattr(proppy, attr)
        if callable(obj):
            print(f"    Type: function/class")
            if hasattr(obj, '__doc__') and obj.__doc__:
                doc_lines = obj.__doc__.strip().split('\n')
                print(f"    Doc: {doc_lines[0][:70]}")
    
    # Try to instantiate or use the library
    print("\nAttempting to use proppy...")
    
    # Common patterns for propagation libraries
    if hasattr(proppy, 'predict'):
        print("  Found: proppy.predict()")
    if hasattr(proppy, 'Prediction'):
        print("  Found: proppy.Prediction class")
    if hasattr(proppy, 'voacap'):
        print("  Found: proppy.voacap")
    if hasattr(proppy, 'VOACAP'):
        print("  Found: proppy.VOACAP class")
        
except ImportError as e:
    print(f"✗ Failed to import proppy: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Error testing proppy: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("Test complete. Check output above for capabilities.")
