"""
DVOACAP - Python Port of Digital Voice of America Coverage Analysis Program

A modern Python implementation of the VOACAP ionospheric propagation model,
providing HF radio propagation prediction capabilities.

Original DVOACAP by Alex Shovkoplyas, VE3NEA
Python Port: 2025
"""

__version__ = "0.4.0"
__author__ = "Python Port Contributors"
__license__ = "MIT"

# Phase 1: Path Geometry
try:
    from .path_geometry import (
        PathGeometry,
        GeographicPoint as PathPoint,
    )
    __all_phase1__ = [
        "PathGeometry",
        "PathPoint",
    ]
except ImportError:
    __all_phase1__ = []

# Phase 2: Solar & Geomagnetic
try:
    from .solar import (
        SolarCalculator,
        GeographicPoint as SolarPoint,
        compute_zenith_angle,
        compute_local_time,
        is_daytime,
    )
    from .geomagnetic import (
        GeomagneticCalculator,
        GeomagneticField,
        GeomagneticParameters,
        GeographicPoint as GeoPoint,
    )
    __all_phase2__ = [
        "SolarCalculator",
        "SolarPoint",
        "compute_zenith_angle",
        "compute_local_time",
        "is_daytime",
        "GeomagneticCalculator",
        "GeomagneticField",
        "GeomagneticParameters",
        "GeoPoint",
    ]
except ImportError:
    __all_phase2__ = []

# Phase 3: Ionospheric Profiles
try:
    from .fourier_maps import (
        FourierMaps,
        VarMapKind,
        FixedMapKind,
        Distribution,
    )
    from .ionospheric_profile import (
        IonosphericProfile,
        LayerInfo,
        Reflection,
        ModeInfo,
    )
    from .layer_parameters import (
        ControlPoint,
        GeographicPoint as IonoPoint,
        compute_iono_params,
        compute_f2_retardation,
    )
    __all_phase3__ = [
        "FourierMaps",
        "VarMapKind",
        "FixedMapKind",
        "Distribution",
        "IonosphericProfile",
        "LayerInfo",
        "Reflection",
        "ModeInfo",
        "ControlPoint",
        "IonoPoint",
        "compute_iono_params",
        "compute_f2_retardation",
    ]
except ImportError:
    __all_phase3__ = []

# Phase 4: Raytracing
try:
    from .muf_calculator import (
        MufCalculator,
        MufInfo,
        CircuitMuf,
        select_profile,
        calc_muf_prob,
    )
    from .reflectrix import (
        Reflectrix,
    )
    __all_phase4__ = [
        "MufCalculator",
        "MufInfo",
        "CircuitMuf",
        "select_profile",
        "calc_muf_prob",
        "Reflectrix",
    ]
except ImportError:
    __all_phase4__ = []

# Combine all exports
__all__ = __all_phase1__ + __all_phase2__ + __all_phase3__ + __all_phase4__

# Module information
_phase_status = {
    "Phase 1": "Complete - Path Geometry",
    "Phase 2": "Complete - Solar & Geomagnetic",
    "Phase 3": "Complete - Ionospheric Profiles",
    "Phase 4": "Complete - Raytracing",
    "Phase 5": "Planned - Signal Predictions",
}


def get_phase_status():
    """Return the current development phase status"""
    return _phase_status.copy()


def get_version_info():
    """Return version and build information"""
    return {
        "version": __version__,
        "author": __author__,
        "license": __license__,
        "python_requires": ">=3.8",
        "modules_complete": len(__all_phase1__) + len(__all_phase2__) + len(__all_phase3__) + len(__all_phase4__),
        "progress": "80%",
    }
