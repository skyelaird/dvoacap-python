#!/usr/bin/env python3
"""
Layer Parameters Module for VOACAP
Ported from LayrParm.pas (DVOACAP)

Original Author: Alex Shovkoplyas, VE3NEA
Python Port: 2025

This module computes ionospheric layer parameters (E, F1, F2, Es) by
combining CCIR/URSI maps with local solar/geomagnetic conditions.
"""

import math
from dataclasses import dataclass, field
from .fourier_maps import FourierMaps, VarMapKind, FixedMapKind
from .ionospheric_profile import LayerInfo


# ============================================================================
# Constants
# ============================================================================

TWO_PI = 2 * math.pi
HALF_PI = math.pi / 2
RinD = math.pi / 180  # radians in degree
DinR = 180 / math.pi  # degrees in radian

PSC4 = 0.7       # Es scaling factor
BETA_E = 5.5     # E layer shape parameter
BETA_F1 = 4.0    # F1 layer shape parameter
DELZ = 2 * RinD  # Zenith angle transition zone
XF1 = 1.1        # F1 frequency ratio threshold


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class GeographicPoint:
    """Geographic location"""
    latitude: float   # radians
    longitude: float  # radians

    @classmethod
    def from_degrees(cls, lat: float, lon: float) -> "GeographicPoint":
        """Create from degrees"""
        return cls(lat * RinD, lon * RinD)


@dataclass
class ControlPoint:
    """
    Control point with location and ionospheric parameters.

    This represents all the ionospheric conditions at a specific
    location and time along a propagation path.
    """
    # Location
    location: GeographicPoint = field(default_factory=lambda: GeographicPoint(0.0, 0.0))
    east_lon: float = 0.0  # East longitude in radians
    distance_rad: float = 0.0  # Distance from transmitter in radians

    # Time and solar
    local_time: float = 0.0  # Local time as fraction of day (0-1)
    zen_angle: float = 0.0  # Solar zenith angle in radians
    zen_max: float = 0.0  # Maximum zenith for F1 layer

    # Geomagnetic
    mag_lat: float = 0.0  # Magnetic latitude in radians
    mag_dip: float = 0.0  # Magnetic dip angle in radians
    gyro_freq: float = 0.0  # Gyrofrequency in MHz

    # Ground parameters
    gnd_sig: float = 0.005  # Ground conductivity (S/m)
    gnd_eps: float = 15.0   # Ground permittivity

    # Ionospheric layers
    e: LayerInfo = None
    f1: LayerInfo = None
    f2: LayerInfo = None
    es: LayerInfo = None

    # Additional layer parameters
    es_fo_lo: float = 0.0  # Es lower decile critical frequency
    es_fo_hi: float = 0.0  # Es upper decile critical frequency
    absorp: float = 0.0    # Absorption index
    f2m3: float = 0.0      # M3000F2 propagation factor
    hpf2: float = 0.0      # F2 peak height before retardation
    rat: float = 0.0       # F2 layer shape ratio (hm/ym)

    def __post_init__(self) -> None:
        """Initialize layer info objects"""
        if self.e is None:
            self.e = LayerInfo()
        if self.f1 is None:
            self.f1 = LayerInfo()
        if self.f2 is None:
            self.f2 = LayerInfo()
        if self.es is None:
            self.es = LayerInfo()


# ============================================================================
# Layer Parameter Functions
# ============================================================================

def compute_f2_retardation(pnt: ControlPoint) -> float:
    """
    Compute F2 layer retardation and adjust F1 layer if necessary.

    The retardation accounts for the group delay through lower layers
    and adjusts the F2 peak height accordingly. Also handles twilight
    transitions for F1 layer.

    Args:
        pnt: Control point with layer parameters

    Returns:
        Total retardation in km
    """
    # E layer retardation
    fc = 0.834 * pnt.f2.fo
    fec = max(1.1, fc / pnt.e.fo)
    result = fec * math.log((fec + 1) / (fec - 1))
    result = (result - 2) * pnt.e.ym

    # Force merger of F1 layer into F2 layer at twilight
    if pnt.f1.fo > 0:
        fec = max(XF1, fc / pnt.f1.fo)
        fec = fec * math.log((fec + 1) / (fec - 1))
        zn = pnt.zen_max - DELZ

        if pnt.zen_angle <= zn:
            # Daytime: normal F1 retardation
            rft = 0.5 * pnt.f1.ym * (fec - 2)
        else:
            # Twilight: merge F1 into F2
            # NEAR DAY-NIGHT, CORRECT HI(2,II) AND RETARDATION
            # FORCE F1 UP INTO F2 AND RETARDATION TO ZERO FROM ZN TO ZMAX
            sz = (pnt.zen_angle - zn) / DELZ
            hn = 165 + 0.6428 / RinD * zn
            yn = hn * pnt.f1.ym / pnt.f1.hm
            rft = 0.5 * yn * (fec - 2) * (1 - sz)

            # F2 without F1
            hm = pnt.hpf2 - result
            ym = hm / pnt.rat
            dh = (hm - ym) - (hn - yn)

            if dh > 0:
                # Bottom of F1 goes to bottom of F2
                dh = dh * (1 - sz)
                pnt.f1.hm = (hm - ym) - dh + pnt.f1.ym

                if pnt.f1.fo > fc:
                    # F1 is also close to F2 in frequency
                    # Force F1 ym to F2 ym
                    y1_max = yn + (ym - yn) * (pnt.f1.fo / pnt.f2.fo - 0.834) / 0.166
                    pnt.f1.ym = yn + (y1_max - yn) * sz
                    pnt.f1.hm = (hm - ym) - dh + pnt.f1.ym

        result += rft

    return result


def compute_iono_params(pnt: ControlPoint, maps: FourierMaps) -> None:
    """
    Compute all ionospheric layer parameters for a control point.

    This is the main function that computes E, F1, F2, and Es layer
    parameters by querying the CCIR/URSI coefficient maps and applying
    corrections based on local conditions.

    Args:
        pnt: Control point to compute parameters for
        maps: FourierMaps object with loaded coefficients

    The control point is modified in place with computed layer parameters.

    Example:
        >>> from dvoacap import GeographicPoint
        >>> pnt = ControlPoint(
        ...     location=GeographicPoint.from_degrees(40, -75),
        ...     east_lon=-75 * RinD,
        ...     local_time=0.5,
        ...     zen_angle=0.3,
        ...     mag_lat=50 * RinD,
        ...     mag_dip=60 * RinD,
        ...     gyro_freq=1.2
        ... )
        >>> maps = FourierMaps()
        >>> maps.set_conditions(month=6, ssn=100, utc_fraction=0.5)
        >>> compute_iono_params(pnt, maps)
        >>> print(f"foF2: {pnt.f2.fo:.2f} MHz")
    """
    cos_lat = math.cos(pnt.location.latitude)

    # ========================================================================
    # E layer
    # ========================================================================
    v = maps.compute_var_map(VarMapKind.ER, pnt.location.latitude,
                             pnt.east_lon, cos_lat)
    if v < 0.36:
        v = 0.36 * math.sqrt(1 + 0.0098 * maps.ssn)

    pnt.e.fo = v
    pnt.e.hm = 110
    pnt.e.ym = 110 / BETA_E

    # Absorption index (never used, overwritten in SIGDIS)
    pnt.absorp = -0.04 * math.exp(-2.937 + 0.8445 * pnt.e.fo)

    # ========================================================================
    # F1 layer
    # ========================================================================
    pnt.zen_max = maps.compute_zen_max(pnt.mag_dip)

    if pnt.zen_angle <= pnt.zen_max:
        # Daytime: F1 layer exists
        pnt.f1.fo = maps.compute_fof1(pnt.zen_angle)
        pnt.f1.hm = 165 + 0.6428 / RinD * pnt.zen_angle
        pnt.f1.ym = pnt.f1.hm / BETA_F1
    else:
        # Nighttime: no F1 layer
        pnt.f1.fo = 0

    # ========================================================================
    # F2 layer
    # ========================================================================
    gm = abs(pnt.mag_lat) - 0.25 * math.pi
    z = pnt.zen_angle * (1 if pnt.local_time > 0.5 else -1) + math.pi

    pnt.rat = max(2.0, maps.compute_fixed_map(FixedMapKind.YM_F2, gm, z))
    pnt.f2m3 = maps.compute_var_map(VarMapKind.FM3, pnt.mag_dip,
                                     pnt.east_lon, cos_lat)
    pnt.hpf2 = 1490 / pnt.f2m3 - 176

    pnt.f2.fo = maps.compute_var_map(VarMapKind.F2, pnt.mag_dip,
                                      pnt.east_lon, cos_lat)
    pnt.f2.fo = pnt.f2.fo + 0.5 * pnt.gyro_freq

    # F1 must be less than F2
    pnt.f1.fo = min(pnt.f1.fo, pnt.f2.fo - 0.2)

    # Compute F2 peak height with retardation correction
    pnt.f2.hm = pnt.hpf2 - compute_f2_retardation(pnt)
    pnt.f2.ym = pnt.f2.hm / pnt.rat

    # ========================================================================
    # Es layer (sporadic E)
    # ========================================================================
    pnt.es.fo = maps.compute_var_map(VarMapKind.ES_M, pnt.mag_dip,
                                      pnt.east_lon, cos_lat) * PSC4
    pnt.es_fo_lo = maps.compute_var_map(VarMapKind.ES_L, pnt.mag_dip,
                                         pnt.east_lon, cos_lat) * PSC4
    pnt.es_fo_hi = maps.compute_var_map(VarMapKind.ES_U, pnt.mag_dip,
                                         pnt.east_lon, cos_lat) * PSC4
    pnt.es.hm = 110


# ============================================================================
# Module Test
# ============================================================================

if __name__ == "__main__":
    print("Testing LayerParameters module...")

    try:
        # Create a control point
        pnt = ControlPoint(
            location=GeographicPoint.from_degrees(40.0, -75.0),
            east_lon=-75.0 * RinD,
            distance_rad=0.0,
            local_time=0.5,  # Noon local time
            zen_angle=0.3,   # ~17 degrees
            zen_max=1.5,
            mag_lat=50.0 * RinD,
            mag_dip=60.0 * RinD,
            gyro_freq=1.2
        )
        print("✓ Created control point")

        # Load coefficient maps
        maps = FourierMaps()
        maps.set_conditions(month=6, ssn=100, utc_fraction=0.5)
        print("✓ Loaded Fourier maps (June, SSN=100)")

        # Compute ionospheric parameters
        compute_iono_params(pnt, maps)
        print("✓ Computed ionospheric parameters")

        # Display results
        print(f"\nIonospheric Layers:")
        print(f"  E layer:  foE  = {pnt.e.fo:.2f} MHz, hm = {pnt.e.hm:.0f} km, ym = {pnt.e.ym:.1f} km")
        print(f"  F1 layer: foF1 = {pnt.f1.fo:.2f} MHz, hm = {pnt.f1.hm:.0f} km, ym = {pnt.f1.ym:.1f} km")
        print(f"  F2 layer: foF2 = {pnt.f2.fo:.2f} MHz, hm = {pnt.f2.hm:.0f} km, ym = {pnt.f2.ym:.1f} km")
        print(f"  Es layer: foEs = {pnt.es.fo:.2f} MHz, hm = {pnt.es.hm:.0f} km")
        print(f"\nAdditional Parameters:")
        print(f"  M3000F2 = {pnt.f2m3:.2f}")
        print(f"  hpF2 = {pnt.hpf2:.1f} km")
        print(f"  Rat = {pnt.rat:.2f}")

        print("\nAll basic tests passed!")

    except Exception as e:
        print(f"✗ Error: {e}")
        raise
