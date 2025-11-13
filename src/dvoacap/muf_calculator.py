#!/usr/bin/env python3
"""
MUF Calculator Module for VOACAP
Ported from MufCalc.pas (DVOACAP)

Original Author: Alex Shovkoplyas, VE3NEA
Python Port: 2025

This module computes Maximum Usable Frequency (MUF) for HF propagation:
- Circuit MUF calculations for E, F1, F2 layers
- FOT (Frequency of Optimum Traffic) and HPF calculations
- MUF probability distributions
- First estimate and iterative refinement algorithms
"""

import math
from dataclasses import dataclass
from typing import List, Optional
import numpy as np

from .ionospheric_profile import (
    IonosphericProfile,
    LayerInfo,
    Reflection,
    corr_to_martyns_theorem
)
from .path_geometry import (
    PathGeometry,
    calc_elevation_angle,
    sin_of_incidence,
    cos_of_incidence,
    EarthR,
    RinD
)
from .fourier_maps import FourierMaps


# ============================================================================
# Constants
# ============================================================================

# Iteration tolerance for MUF refinement
FQDEL = 0.1  # MHz

# Standard deviation percentage point (10% decile)
NORM_DECILE = 1.28

# E layer constants
HM_E = 110  # km
YM_E = 20   # km

# Common distances in radians
RAD_2000KM = 2000 / EarthR


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class MufInfo:
    """MUF information for a single layer"""
    ref: Reflection  # Reflection parameters at MUF
    hop_count: int = 1  # Number of hops
    fot: float = 0.0  # Frequency of Optimum Traffic (MHz)
    hpf: float = 0.0  # High Probability Frequency (MHz)
    muf: float = 0.0  # Maximum Usable Frequency (MHz)
    sig_lo: float = 0.0  # Lower standard deviation
    sig_hi: float = 0.0  # Upper standard deviation

    def __post_init__(self):
        """Ensure ref is a Reflection object"""
        if not isinstance(self.ref, Reflection):
            raise TypeError("ref must be a Reflection object")


@dataclass
class CircuitMuf:
    """Circuit MUF for all layers"""
    muf_info: dict  # Dictionary mapping layer name to MufInfo
    fot: float = 0.0  # Circuit FOT (MHz)
    muf: float = 0.0  # Circuit MUF (MHz)
    hpf: float = 0.0  # Circuit HPF (MHz)
    angle: float = 0.0  # Elevation angle (radians)
    layer: str = 'F2'  # Controlling layer ('E', 'F1', or 'F2')


# ============================================================================
# Helper Functions
# ============================================================================

def select_profile(profiles: List[IonosphericProfile]) -> Optional[IonosphericProfile]:
    """
    Select the controlling profile from multiple sample areas.

    From VOACAP: SELECT CONTROLING SAMPLE AREA

    Args:
        profiles: List of ionospheric profiles (1, 2, or 3 profiles)

    Returns:
        Selected profile or None
    """
    if not profiles:
        return None

    n = len(profiles)

    if n == 1:
        return profiles[0]

    elif n == 2:
        # Select profile with lower E layer critical frequency
        if profiles[0].e.fo <= profiles[1].e.fo:
            return profiles[0]
        else:
            return profiles[1]

    elif n >= 3:
        # Check F2 layer difference first
        if abs(profiles[0].f2.fo - profiles[2].f2.fo) > 0.01:
            if profiles[0].f2.fo <= profiles[2].f2.fo:
                return profiles[0]
            else:
                return profiles[2]
        else:
            # F2 layers similar, check E layer
            if profiles[0].e.fo <= profiles[2].e.fo:
                return profiles[0]
            else:
                return profiles[2]

    return profiles[0]


def calc_muf_prob(freq: float, mode_muf: float, median: float,
                  sigma_lo: float, sigma_hi: float) -> float:
    """
    Calculate probability that MUF exceeds the operating frequency.

    Args:
        freq: Operating frequency (MHz)
        mode_muf: MUF at a set angle for a particular layer (MHz)
        median: Where median of distribution is placed (FOT, MUF or HPF)
        sigma_lo: Lower decile standard deviation
        sigma_hi: Upper decile standard deviation

    Returns:
        Probability that MUF exceeds freq (0.0 to 1.0)
    """
    z = freq - mode_muf

    if median <= 0:
        return 1.0 if z <= 0 else 0.0

    # Select appropriate standard deviation
    sig = sigma_lo if z <= 0 else sigma_hi

    # Normalize
    z = z / max(0.001, mode_muf * sig / median)

    # Cumulative normal distribution
    return 1.0 - _cumulative_normal(z)


def _cumulative_normal(x: float) -> float:
    """
    Cumulative normal distribution function.

    Args:
        x: Standard normal variable

    Returns:
        P(X <= x) for X ~ N(0,1)
    """
    # Constants for approximation
    C = [0.196854, 0.115194, 0.000344, 0.019527]

    y = min(5, abs(x))
    result = 1 + y * (C[0] + y * (C[1] + y * (C[2] + y * C[3])))
    result = result * result * result * result
    result = 0.5 * (1 / result)

    if x > 0:
        result = 1 - result

    return result


# ============================================================================
# MUF Calculator Class
# ============================================================================

class MufCalculator:
    """
    Calculate Maximum Usable Frequency (MUF) for HF circuit.

    This class computes MUF, FOT, and HPF for all ionospheric layers
    along a propagation path.
    """

    def __init__(self, path: PathGeometry, maps: FourierMaps, min_angle: float = 3 * RinD):
        """
        Initialize MUF calculator.

        Args:
            path: PathGeometry object with Tx/Rx locations
            maps: FourierMaps object for ionospheric parameters
            min_angle: Minimum elevation angle (radians), default 3°
        """
        self.path = path
        self.maps = maps
        self.min_angle = min_angle

        # Working variables (used across methods)
        self._profile: Optional[IonosphericProfile] = None
        self._hop_dist: float = 0.0
        self._sin_i_sqr: float = 0.0

    def compute_circuit_muf(self, profiles: List[IonosphericProfile]) -> CircuitMuf:
        """
        Compute circuit MUF for all layers.

        Args:
            profiles: List of ionospheric profiles (typically 1-3)

        Returns:
            CircuitMuf object with MUF for all layers
        """
        # Select controlling profile
        self._profile = select_profile(profiles)

        if self._profile is None:
            raise ValueError("No valid profile provided")

        # Calculate electron density profile
        self._profile.compute_el_density_profile()

        # Compute MUF for each layer
        muf_info = {}
        muf_info['E'] = self._compute_muf_e()
        muf_info['F2'] = self._compute_muf_f2()

        # F1 layer (may not exist)
        if self._profile.f1.fo > 0:
            muf_info['F1'] = self._compute_muf_f1()
        else:
            muf_info['F1'] = muf_info['E']  # Use E layer if no F1

        # Determine circuit MUF (maximum of all layers)
        # Note: Es (sporadic E) is not included here
        fot = max(muf_info['E'].fot, muf_info['F1'].fot, muf_info['F2'].fot)
        muf = max(muf_info['E'].muf, muf_info['F1'].muf, muf_info['F2'].muf)
        hpf = max(muf_info['E'].hpf, muf_info['F1'].hpf, muf_info['F2'].hpf)

        # Determine controlling layer
        if muf_info['E'].muf >= muf:
            angle = muf_info['E'].ref.elevation
            layer = 'E'
        elif muf_info['F1'].muf >= muf:
            angle = muf_info['F1'].ref.elevation
            layer = 'F1'
        else:
            angle = muf_info['F2'].ref.elevation
            layer = 'F2'

        return CircuitMuf(
            muf_info=muf_info,
            fot=fot,
            muf=muf,
            hpf=hpf,
            angle=angle,
            layer=layer
        )

    def _compute_muf_e(self) -> MufInfo:
        """Compute MUF for E layer."""
        # Tangent frequency for E layer
        vert_freq = self._profile.e.fo / math.sqrt(1 + 0.5 * YM_E / HM_E)

        ref = Reflection(vert_freq=vert_freq)
        result = self._compute_first_estimate(ref)

        # Distribution for E layer MUF
        result.sig_lo = max(0.01, 0.1 * result.muf)
        result.sig_hi = result.sig_lo

        # Deciles
        result.fot = result.muf - NORM_DECILE * result.sig_lo
        result.hpf = result.muf + NORM_DECILE * result.sig_hi

        # Deviative loss factor for E layer
        result.ref.dev_loss = 0.0

        return result

    def _compute_muf_f2(self) -> MufInfo:
        """Compute MUF for F2 layer."""
        # Tangent frequency
        xt_f2 = 1 / math.sqrt(1 + 0.5 * self._profile.f2.ym / self._profile.f2.hm)
        vert_freq = self._profile.f2.fo * xt_f2

        # Force F2 MUF to approach MUF(0) for short distances
        if self.path.dist < RAD_2000KM:
            bex = 9.5
            beta = 1 + (1/xt_f2 - 1) * math.exp(-bex * self.path.dist / RAD_2000KM)
            vert_freq = vert_freq * beta

        ref = Reflection(vert_freq=vert_freq)
        result = self._compute_first_estimate(ref)
        self._refine_estimate(result, self._profile.f2.fo)

        # F2 MUF distribution from F2 M(3000) tables
        result.sig_lo = max(0.01, self.maps.compute_f2_deviation(
            result.muf, self._profile.lat, self._profile.local_time_f2, False))
        result.sig_hi = max(0.01, self.maps.compute_f2_deviation(
            result.muf, self._profile.lat, self._profile.local_time_f2, True))

        result.fot = result.muf - NORM_DECILE * result.sig_lo
        result.hpf = result.muf + NORM_DECILE * result.sig_hi
        result.ref.dev_loss = 0.0

        return result

    def _compute_muf_f1(self) -> MufInfo:
        """Compute MUF for F1 layer."""
        # Tangent frequency
        vert_freq = self._profile.f1.fo / math.sqrt(
            1 + 0.5 * self._profile.f1.ym / self._profile.f1.hm)

        ref = Reflection(vert_freq=vert_freq)
        result = self._compute_first_estimate(ref)
        self._refine_estimate(result, self._profile.f1.fo)

        result.sig_lo = max(0.01, 0.1 * result.muf)
        result.sig_hi = result.sig_lo

        result.fot = result.muf - NORM_DECILE * result.sig_lo
        result.hpf = result.muf + NORM_DECILE * result.sig_hi
        result.ref.dev_loss = 0.0

        return result

    def _compute_first_estimate(self, ref: Reflection) -> MufInfo:
        """
        Compute first estimate of MUF using simple geometry.

        Args:
            ref: Reflection with vert_freq set

        Returns:
            MufInfo with first estimate
        """
        # Heights
        ref.true_height = self._profile.get_true_height(ref.vert_freq)
        ref.virt_height = self._profile.get_virtual_height_gauss(ref.vert_freq)

        # Number of hops
        hop_count = self.path.hop_count(self.min_angle, ref.virt_height)
        self._hop_dist = self.path.dist / hop_count

        # Elevation angle
        ref.elevation = calc_elevation_angle(self._hop_dist, ref.virt_height)

        # MUF calculation using Snell's law
        self._sin_i_sqr = sin_of_incidence(ref.elevation, ref.true_height) ** 2
        muf = ref.vert_freq / math.sqrt(1 - self._sin_i_sqr)

        return MufInfo(
            ref=ref,
            hop_count=hop_count,
            muf=muf
        )

    def _refine_estimate(self, result: MufInfo, layer_fo: float) -> None:
        """
        Refine MUF estimate using iterative correction.

        Applies Martyn's theorem correction iteratively until convergence.

        Args:
            result: MufInfo to refine (modified in place)
            layer_fo: Layer critical frequency (MHz)
        """
        orig_height = result.ref.virt_height
        corr0 = corr_to_martyns_theorem(result.ref)

        # Iteration for MUF: allows 4 tries to obtain epsilon of 0.1 MHz
        for _ in range(4):
            prev_muf = result.muf

            # Correction to Martyn's theorem
            corr = corr0 * (prev_muf / layer_fo) ** 2 * self._sin_i_sqr

            # Corrected virtual height
            result.ref.virt_height = orig_height + corr

            # New elevation angle and MUF
            result.ref.elevation = calc_elevation_angle(self._hop_dist, result.ref.virt_height)
            self._sin_i_sqr = sin_of_incidence(result.ref.elevation, result.ref.true_height) ** 2
            result.muf = result.ref.vert_freq / math.sqrt(1 - self._sin_i_sqr)

            # Check convergence
            if abs(result.muf - prev_muf) <= FQDEL:
                break


# ============================================================================
# Example/Test Code
# ============================================================================

def example_usage():
    """Demonstrate usage of the MUF Calculator module"""
    from .solar import compute_solar_parameters
    from .geomagnetic import compute_geomagnetic_parameters
    from .path_geometry import GeoPoint

    print("=" * 70)
    print("MUF Calculator Module - Example Usage")
    print("=" * 70)
    print()

    # Set up path
    tx = GeoPoint.from_degrees(40.0, -75.0)  # Philadelphia
    rx = GeoPoint.from_degrees(51.5, -0.1)   # London

    path = PathGeometry()
    path.set_tx_rx(tx, rx)

    print(f"Path: Philadelphia to London")
    print(f"Distance: {path.get_distance_km():.0f} km")
    print()

    # Set up ionospheric maps
    maps = FourierMaps()
    maps.set_conditions(month=6, ssn=100, utc_fraction=0.5)

    # Compute ionospheric profile at midpoint
    # (This is simplified - normally you'd compute profiles at multiple points)
    # For demonstration, we'll create a simple profile

    print("MUF Calculator Example - Implementation requires ionospheric profile")
    print("See examples/phase4_raytracing_example.py for complete example")


if __name__ == "__main__":
    example_usage()
