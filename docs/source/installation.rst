Installation
============

Requirements
------------

* Python 3.8 or higher
* NumPy
* (Optional) Matplotlib for visualization

Installing from Source
----------------------

1. Clone the repository::

    git clone https://github.com/skyelaird/dvoacap-python.git
    cd dvoacap-python

2. Install in development mode::

    pip install -e .

3. Verify installation::

    python -c "import dvoacap; print(dvoacap.__version__)"

Data Files
----------

DVOACAP requires coefficient data files (DVoaData directory) which should be included
in the repository. These files contain:

* ``Coeff01.dat`` through ``Coeff12.dat``: Monthly ionospheric coefficients
* ``FOF2CCIR01.dat`` through ``FOF2CCIR12.dat``: F2 layer critical frequency data

The data files should be located at ``DVoaData/`` in the project root.

Dependencies
------------

Core dependencies::

    numpy>=1.20.0

Optional dependencies for examples and visualization::

    matplotlib>=3.3.0
    scipy>=1.6.0

Development dependencies::

    sphinx>=4.0.0
    pytest>=6.0.0
    mypy>=0.900

Troubleshooting
---------------

**Import Error**: If you get an import error, make sure you've installed the package::

    pip install -e .

**Missing Data Files**: If you see ``FileNotFoundError`` for coefficient files,
ensure the DVoaData directory is in the correct location.

**NumPy Compatibility**: Some operations require NumPy 1.20 or higher for proper
type handling.
