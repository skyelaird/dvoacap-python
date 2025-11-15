Examples
========

This page contains example code for common DVOACAP Python tasks.

Complete Prediction Workflow
-----------------------------

A complete example showing all phases of propagation prediction:

.. code-block:: python

    import numpy as np
    from dvoacap import GeoPoint
    from dvoacap.prediction_engine import PredictionEngine

    # Initialize engine
    engine = PredictionEngine()

    # Configure prediction parameters
    engine.params.ssn = 100              # Sunspot number
    engine.params.month = 6              # June
    engine.params.tx_power = 1500        # 1.5 kW
    engine.params.min_angle = np.deg2rad(3.0)  # 3° takeoff angle
    engine.params.required_snr = 73.0    # Required SNR for reliability
    engine.params.required_reliability = 0.9  # 90% reliability

    # Set transmitter (Philadelphia)
    engine.params.tx_location = GeoPoint.from_degrees(40.0, -75.0)

    # Set receiver (London)
    rx = GeoPoint.from_degrees(51.5, -0.1)

    # Predict for HF bands at noon UTC
    frequencies = [3.5, 7.0, 10.1, 14.0, 18.1, 21.0, 24.9, 28.0]
    engine.predict(rx, utc_time=0.5, frequencies=frequencies)

    # Print detailed results
    print(f"Path: Philadelphia to London")
    print(f"Distance: {engine.path.get_distance_km():.0f} km")
    print(f"Azimuth: {engine.path.get_azimuth_tr_degrees():.1f}°")
    print(f"Circuit MUF: {engine.circuit_muf.muf:.2f} MHz")
    print()
    print(f"{'Freq':<6} {'SNR':<6} {'Rel':<6} {'Mode':<8} {'Hops':<6}")
    print("-" * 40)

    for i, freq in enumerate(frequencies):
        pred = engine.predictions[i]
        mode = pred.get_mode_name(engine.path.dist)
        print(f"{freq:<6.1f} {pred.signal.snr_db:<6.1f} "
              f"{pred.signal.reliability:<6.3f} {mode:<8} {pred.hop_count:<6}")

24-Hour Prediction
------------------

Predict propagation throughout the day:

.. code-block:: python

    import numpy as np
    import matplotlib.pyplot as plt
    from dvoacap import GeoPoint
    from dvoacap.prediction_engine import PredictionEngine

    engine = PredictionEngine()
    engine.params.ssn = 100
    engine.params.month = 6
    engine.params.tx_location = GeoPoint.from_degrees(40.0, -75.0)
    rx = GeoPoint.from_degrees(51.5, -0.1)

    # Sample every 2 hours
    utc_hours = np.arange(0, 24, 2)
    frequencies = [7.0, 14.0, 21.0, 28.0]

    results = {freq: {'snr': [], 'rel': []} for freq in frequencies}

    for hour in utc_hours:
        utc_time = hour / 24.0
        engine.predict(rx, utc_time, frequencies)

        for i, freq in enumerate(frequencies):
            pred = engine.predictions[i]
            results[freq]['snr'].append(pred.signal.snr_db)
            results[freq]['rel'].append(pred.signal.reliability)

    # Plot results
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

    for freq in frequencies:
        ax1.plot(utc_hours, results[freq]['snr'], marker='o', label=f'{freq} MHz')
        ax2.plot(utc_hours, results[freq]['rel'], marker='o', label=f'{freq} MHz')

    ax1.set_ylabel('SNR (dB)')
    ax1.set_title('24-Hour SNR Prediction')
    ax1.legend()
    ax1.grid(True)

    ax2.set_xlabel('UTC Hour')
    ax2.set_ylabel('Reliability')
    ax2.set_title('24-Hour Reliability Prediction')
    ax2.legend()
    ax2.grid(True)

    plt.tight_layout()
    plt.show()

Coverage Map
------------

Generate a coverage map from a transmitter location:

.. code-block:: python

    import numpy as np
    import matplotlib.pyplot as plt
    from dvoacap import GeoPoint
    from dvoacap.prediction_engine import PredictionEngine

    # Set up prediction
    engine = PredictionEngine()
    engine.params.ssn = 100
    engine.params.month = 6
    engine.params.tx_location = GeoPoint.from_degrees(40.0, -75.0)

    # Create grid of receiver locations
    lats = np.arange(-60, 61, 5)
    lons = np.arange(-180, 181, 5)

    # Frequency to predict
    freq = 14.0  # MHz

    # Storage for results
    snr_map = np.zeros((len(lats), len(lons)))

    # Compute for each grid point
    for i, lat in enumerate(lats):
        for j, lon in enumerate(lons):
            rx = GeoPoint.from_degrees(lat, lon)
            try:
                engine.predict(rx, utc_time=0.5, frequencies=[freq])
                snr_map[i, j] = engine.predictions[0].signal.snr_db
            except:
                snr_map[i, j] = np.nan

    # Plot coverage map
    plt.figure(figsize=(12, 6))
    plt.contourf(lons, lats, snr_map, levels=20, cmap='RdYlGn')
    plt.colorbar(label='SNR (dB)')
    plt.title(f'Coverage Map at {freq} MHz')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.grid(True, alpha=0.3)
    plt.show()

More Examples
-------------

For more examples, see the ``examples/`` directory in the repository:

* ``examples/phase1_path_geometry_example.py`` - Path geometry calculations
* ``examples/phase2_solar_geomag_example.py`` - Solar and geomagnetic calculations
* ``examples/phase3_ionospheric_example.py`` - Ionospheric profile generation
* ``examples/phase4_raytracing_example.py`` - MUF and raytracing
* ``examples/phase5_prediction_example.py`` - Complete prediction workflow
