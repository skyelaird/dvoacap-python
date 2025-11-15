.. DVOACAP Python documentation master file

Welcome to DVOACAP Python's documentation!
===========================================

DVOACAP Python is a modern Python implementation of the VOACAP ionospheric propagation model,
providing HF radio propagation prediction capabilities.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   overview
   installation
   quickstart
   api
   examples

Overview
========

DVOACAP Python provides a complete implementation of the VOACAP (Voice of America Coverage Analysis Program)
ionospheric propagation model. This allows amateur radio operators, professional communicators, and researchers
to predict HF radio propagation conditions worldwide.

Key Features
------------

* **Complete VOACAP Implementation**: Full port of the VOACAP propagation model
* **Ionospheric Modeling**: E, F1, and F2 layer modeling with realistic profiles
* **Path Geometry**: Great circle path calculations with multi-hop support
* **Solar & Geomagnetic**: Accurate solar position and geomagnetic field calculations
* **MUF Calculations**: Maximum Usable Frequency with reliability statistics
* **Signal Predictions**: SNR, field strength, and reliability predictions
* **Antenna Modeling**: Flexible antenna gain patterns
* **Modern Python API**: Clean, type-hinted interface

Development Status
------------------

The project is organized into 5 phases:

* **Phase 1: Path Geometry** - ✓ Complete
* **Phase 2: Solar & Geomagnetic** - ✓ Complete
* **Phase 3: Ionospheric Profiles** - ✓ Complete
* **Phase 4: Raytracing** - ✓ Complete
* **Phase 5: Signal Predictions** - ✓ Complete (Noise & Antennas)

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
