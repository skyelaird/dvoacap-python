Quick Start Guide
=================

This guide will get you started with DVOACAP Python in just a few minutes.

Basic Prediction
----------------

Here's a simple example that predicts propagation from Philadelphia to London:

.. code-block:: python

    import numpy as np
    from dvoacap import GeoPoint
    from dvoacap.prediction_engine import PredictionEngine

    # Create prediction engine
    engine = PredictionEngine()

    # Set transmitter location (Philadelphia)
    engine.params.tx_location = GeoPoint(
        lat=40.0 * np.pi / 180,
        lon=-75.0 * np.pi / 180
    )

    # Set receiver location (London)
    rx_location = GeoPoint(
        lat=51.5 * np.pi / 180,
        lon=-0.1 * np.pi / 180
    )

    # Set parameters
    engine.params.ssn = 100  # Sunspot number
    engine.params.month = 6  # June
    engine.params.tx_power = 1500  # Watts

    # Predict for multiple frequencies
    frequencies = [7.0, 14.0, 21.0, 28.0]  # MHz
    utc_time = 0.5  # Noon UTC

    engine.predict(rx_location, utc_time, frequencies)

    # Display results
    for i, freq in enumerate(frequencies):
        pred = engine.predictions[i]
        print(f"{freq} MHz: SNR = {pred.signal.snr_db:.1f} dB, "
              f"Reliability = {pred.signal.reliability:.3f}")

Path Geometry
-------------

Calculate great circle path parameters:

.. code-block:: python

    from dvoacap import PathGeometry, GeoPoint

    path = PathGeometry()

    # Halifax to London
    tx = GeoPoint.from_degrees(44.65, -63.57)
    rx = GeoPoint.from_degrees(51.51, -0.13)

    path.set_tx_rx(tx, rx)

    print(f"Distance: {path.get_distance_km():.0f} km")
    print(f"Azimuth (Tx->Rx): {path.get_azimuth_tr_degrees():.1f}°")
    print(f"Azimuth (Rx->Tx): {path.get_azimuth_rt_degrees():.1f}°")

Solar Position
--------------

Calculate solar zenith angle and local time:

.. code-block:: python

    from dvoacap import SolarCalculator, GeographicPoint
    from datetime import datetime

    calc = SolarCalculator()

    location = GeographicPoint.from_degrees(40.0, -75.0)
    time = datetime(2024, 6, 15, 12, 0)  # Noon UTC

    zenith = calc.calculate_zenith_angle(location, time)
    is_day = calc.is_daytime_at(location, time)

    print(f"Zenith angle: {zenith * 180/3.14159:.1f}°")
    print(f"Daytime: {is_day}")

MUF Calculation
---------------

Calculate Maximum Usable Frequency:

.. code-block:: python

    from dvoacap import PathGeometry, FourierMaps, GeoPoint
    from dvoacap.muf_calculator import MufCalculator
    from dvoacap.ionospheric_profile import IonosphericProfile

    # Set up path
    path = PathGeometry()
    tx = GeoPoint.from_degrees(40.0, -75.0)
    rx = GeoPoint.from_degrees(51.5, -0.1)
    path.set_tx_rx(tx, rx)

    # Set up ionospheric maps
    maps = FourierMaps()
    maps.set_conditions(month=6, ssn=100, utc_fraction=0.5)

    # Create MUF calculator
    muf_calc = MufCalculator(path, maps)

    # Note: Full MUF calculation requires ionospheric profiles
    # See examples/ directory for complete workflow

Next Steps
----------

* Explore the :doc:`examples` page for more detailed examples
* Read the :doc:`api` documentation for complete API reference
* Check the ``examples/`` directory in the repository for runnable code
* See the VOACAP manual (in ``docs/``) for propagation theory
