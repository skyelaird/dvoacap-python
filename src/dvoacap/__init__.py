"""
DVOACAP - Python Port of Digital Voice of America Coverage Analysis Program

A modern Python implementation of the VOACAP ionospheric propagation model,
providing HF radio propagation prediction capabilities.

Original DVOACAP by Alex Shovkoplyas, VE3NEA
Python Port: 2025
"""

# Modern Python 3.11+ uses built-in types for annotations

__version__ = "1.0.1"
__author__ = "Joel Morin and Contributors"
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

# Phase 5: Signal Predictions
try:
    from .noise_model import (
        NoiseModel,
        TripleValue,
        Distribution,
    )
    from .antenna_gain import (
        AntennaModel,
        IsotropicAntenna,
        HalfWaveDipole,
        VerticalMonopole,
        AntennaFarm,
    )
    __all_phase5__ = [
        "NoiseModel",
        "TripleValue",
        "Distribution",
        "AntennaModel",
        "IsotropicAntenna",
        "HalfWaveDipole",
        "VerticalMonopole",
        "AntennaFarm",
    ]
except ImportError:
    __all_phase5__ = []

# Combine all exports
__all__ = __all_phase1__ + __all_phase2__ + __all_phase3__ + __all_phase4__ + __all_phase5__

# Module information
_phase_status = {
    "Phase 1": "Complete - Path Geometry",
    "Phase 2": "Complete - Solar & Geomagnetic",
    "Phase 3": "Complete - Ionospheric Profiles",
    "Phase 4": "Complete - Raytracing",
    "Phase 5": "Complete - Signal Predictions",
}


def get_phase_status() -> dict[str, str]:
    """Return the current development phase status"""
    return _phase_status.copy()


def get_version_info() -> dict[str, str | int]:
    """Return version and build information"""
    total_modules = (len(__all_phase1__) + len(__all_phase2__) + len(__all_phase3__) +
                    len(__all_phase4__) + len(__all_phase5__))
    return {
        "version": __version__,
        "author": __author__,
        "license": __license__,
        "python_requires": ">=3.11",
        "modules_complete": total_modules,
        "progress": "100%",
    }
