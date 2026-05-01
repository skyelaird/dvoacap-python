"""
DVOACAP Installation Script
Automated installation for Windows, Linux, and macOS
"""
import sys
import subprocess
import platform

def install_dvoacap():
    """Install DVOACAP package using pip."""
    print("=" * 60)
    print("DVOACAP Installation Script")
    print("=" * 60)
    print(f"\nPlatform: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Python Executable: {sys.executable}")

    # Check Python version
    if sys.version_info < (3, 11):
        print("\n✗ ERROR: Python 3.11 or higher required")
        print(f"  Current version: {sys.version.split()[0]}")
        print("\nPlease install Python 3.11+ from https://python.org")
        return False

    print("\n✓ Python version OK (3.11+)")

    # Upgrade pip first
    print("\n" + "=" * 60)
    print("Step 1: Upgrading pip...")
    print("=" * 60)
    try:
        subprocess.check_call([
            sys.executable,
            "-m",
            "pip",
            "install",
            "--upgrade",
            "pip"
        ])
        print("✓ pip upgraded successfully")
    except subprocess.CalledProcessError as e:
        print(f"⚠ Warning: Could not upgrade pip (this is usually OK)")

    # Install dvoacap
    print("\n" + "=" * 60)
    print("Step 2: Installing DVOACAP...")
    print("=" * 60)
    try:
        subprocess.check_call([
            sys.executable,
            "-m",
            "pip",
            "install",
            "dvoacap"
        ])
        print("\n✓ DVOACAP installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"\n✗ ERROR: Installation failed")
        print(f"  Error: {e}")
        return False

    # Verify installation
    print("\n" + "=" * 60)
    print("Step 3: Verifying installation...")
    print("=" * 60)
    try:
        result = subprocess.run([
            sys.executable,
            "-m",
            "pip",
            "show",
            "dvoacap"
        ], capture_output=True, text=True, check=True)

        print(result.stdout)
        print("✓ DVOACAP package verified")
    except subprocess.CalledProcessError:
        print("✗ ERROR: Package verification failed")
        return False

    # Test import
    print("\n" + "=" * 60)
    print("Step 4: Testing import...")
    print("=" * 60)
    try:
        import dvoacap
        version = getattr(dvoacap, '__version__', 'unknown')
        print(f"✓ DVOACAP imported successfully (version {version})")
    except ImportError as e:
        print(f"✗ ERROR: Cannot import dvoacap: {e}")
        return False

    print("\n" + "=" * 60)
    print("✓ INSTALLATION COMPLETE!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Run validate_dvoacap.py to verify everything works")
    print("2. See examples at: https://github.com/skyelaird/dvoacap-python")
    print("\nTo uninstall: pip uninstall dvoacap")

    return True

if __name__ == "__main__":
    print("\nDVOACAP - HF Radio Propagation Prediction Engine")
    print("https://github.com/skyelaird/dvoacap-python\n")

    success = install_dvoacap()

    if success:
        print("\n" + "=" * 60)
        input("\nPress Enter to exit...")
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("Installation failed. Please check the errors above.")
        print("\nFor help, visit:")
        print("https://github.com/skyelaird/dvoacap-python/issues")
        input("\nPress Enter to exit...")
        sys.exit(1)
