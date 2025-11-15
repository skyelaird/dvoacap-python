Overview
========

DVOACAP Python is a complete Python port of the VOACAP (Voice of America Coverage Analysis Program)
ionospheric propagation model. It provides accurate HF radio propagation predictions based on
ionospheric physics and empirical models.

What is VOACAP?
---------------

VOACAP is the industry-standard software for predicting HF radio propagation. It uses:

* **Ionospheric Models**: CCIR/URSI coefficients for worldwide ionospheric conditions
* **Solar Activity**: Integration of solar flux and sunspot number data
* **Geomagnetic Field**: IGRF model for magnetic field effects
* **Ray Tracing**: Sophisticated raytracing through the ionosphere
* **Statistical Analysis**: Reliability and probability calculations

Why Python?
-----------

The original VOACAP is written in FORTRAN, making it difficult to integrate into modern applications.
DVOACAP Python provides:

* **Modern API**: Clean, Pythonic interface with type hints
* **Easy Integration**: Use in web apps, data analysis, automation
* **Extensibility**: Add custom antenna patterns, noise models, etc.
* **Cross-Platform**: Works on Windows, macOS, Linux
* **Open Source**: MIT licensed, community-driven development

Use Cases
---------

* **Amateur Radio**: Plan DX contacts and optimize antenna systems
* **Professional Communications**: Design HF communication networks
* **Research**: Study ionospheric propagation phenomena
* **Education**: Learn about HF radio propagation
* **Automated Systems**: Build propagation prediction services

Architecture
------------

The codebase is organized into 5 phases:

Phase 1: Path Geometry
~~~~~~~~~~~~~~~~~~~~~~

* Great circle path calculations
* Azimuth and distance computations
* Hop geometry (elevation angles, skip distances)

Phase 2: Solar & Geomagnetic
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Solar position calculations
* Geomagnetic field modeling (IGRF)
* Magnetic latitude and gyrofrequency

Phase 3: Ionospheric Profiles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Fourier coefficient maps (CCIR/URSI)
* Layer parameter computations (E, F1, F2)
* Electron density profiles
* True and virtual height calculations

Phase 4: Raytracing
~~~~~~~~~~~~~~~~~~~

* MUF (Maximum Usable Frequency) calculations
* Reflectrix (frequency vs elevation angle)
* Multi-hop mode finding
* Penetration angle computations

Phase 5: Signal Predictions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Radio noise modeling (ITU-R P.372)
* Antenna gain patterns
* Path loss calculations
* SNR and reliability predictions
