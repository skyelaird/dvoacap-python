"""
Simple HF Propagation Prediction Example
Location: Halifax, Nova Scotia
Perfect for screenshots in club presentations!
"""
from dvoacap import FourierMaps, ControlPoint, IonoPoint, compute_iono_params
import math

def predict_halifax(month=6, ssn=100, utc_hour=12):
    """Predict HF propagation conditions at Halifax, NS."""

    # Load ionospheric maps
    maps = FourierMaps()
    maps.set_conditions(month=month, ssn=ssn, utc_fraction=utc_hour/24.0)

    # Halifax, Nova Scotia coordinates
    pnt = ControlPoint(
        location=IonoPoint.from_degrees(44.65, -63.57),
        east_lon=-63.57 * math.pi/180,
        distance_rad=0.0,
        local_time=utc_hour/24.0,
        zen_angle=0.3,
        zen_max=1.5,
        mag_lat=55.0 * math.pi/180,
        mag_dip=70.0 * math.pi/180,
        gyro_freq=1.4
    )

    # Compute propagation
    compute_iono_params(pnt, maps)

    # Display results
    print("\n" + "="*60)
    print("HF PROPAGATION PREDICTION - HALIFAX, NOVA SCOTIA")
    print("="*60)
    print(f"\nLocation: 44.65°N, 63.57°W (Halifax, NS)")
    print(f"Month: {['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'][month-1]}")
    print(f"Time: {utc_hour:02d}:00 UTC")
    print(f"Solar Activity: SSN {ssn}")

    print("\n" + "-"*60)
    print("IONOSPHERIC LAYERS:")
    print("-"*60)
    print(f"E  Layer: foE  = {pnt.e.fo:5.2f} MHz  at  {pnt.e.hm:4.0f} km altitude")
    print(f"F1 Layer: foF1 = {pnt.f1.fo:5.2f} MHz  at  {pnt.f1.hm:4.0f} km altitude")
    print(f"F2 Layer: foF2 = {pnt.f2.fo:5.2f} MHz  at  {pnt.f2.hm:4.0f} km altitude")
    print("-"*60)

    # Calculate MUF and band recommendations
    muf = pnt.f2.fo * 3.0

    print(f"\nMaximum Usable Frequency (MUF): ~{muf:.1f} MHz")
    print(f"Optimum Working Frequency (FOT): ~{muf * 0.85:.1f} MHz")

    print("\n" + "-"*60)
    print("BAND CONDITIONS:")
    print("-"*60)

    bands = [
        ("160m", 1.8, 2.0),
        ("80m", 3.5, 4.0),
        ("40m", 7.0, 7.3),
        ("30m", 10.1, 10.15),
        ("20m", 14.0, 14.35),
        ("17m", 18.068, 18.168),
        ("15m", 21.0, 21.45),
        ("12m", 24.89, 24.99),
        ("10m", 28.0, 29.7),
    ]

    for band_name, freq_low, freq_high in bands:
        freq_mid = (freq_low + freq_high) / 2

        if freq_mid < pnt.f2.fo:
            status = "✅ EXCELLENT - Good for long-distance"
        elif freq_mid < muf * 0.85:
            status = "✅ GOOD - Usable for DX"
        elif freq_mid < muf:
            status = "⚠️  MARGINAL - May work"
        else:
            status = "❌ POOR - Frequency too high"

        print(f"{band_name:5s} ({freq_mid:6.2f} MHz): {status}")

    print("="*60)
    print()

    return pnt

if __name__ == "__main__":
    print("\n" + "="*60)
    print("DVOACAP-PYTHON - HF PROPAGATION PREDICTION")
    print("="*60)
    print("\nExample predictions for Halifax, Nova Scotia")
    print("Great for ham radio club presentations!")
    print()

    # Example 1: Daytime conditions
    print("\n### EXAMPLE 1: Daytime Conditions ###")
    predict_halifax(month=6, ssn=100, utc_hour=12)

    # Example 2: Nighttime conditions
    print("\n### EXAMPLE 2: Nighttime Conditions ###")
    predict_halifax(month=6, ssn=100, utc_hour=0)

    # Example 3: High solar activity
    print("\n### EXAMPLE 3: High Solar Activity ###")
    predict_halifax(month=6, ssn=150, utc_hour=12)

    print("\nTry different parameters:")
    print("  predict_halifax(month=1, ssn=50, utc_hour=18)")
    print("  predict_halifax(month=12, ssn=200, utc_hour=6)")
    print("\nMonth: 1-12, SSN: 0-200+, UTC Hour: 0-23")
    print()
