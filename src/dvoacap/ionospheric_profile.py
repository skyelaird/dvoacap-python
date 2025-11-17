#!/usr/bin/env python3
"""
Ionospheric Profile Module for VOACAP
Ported from IonoProf.pas (DVOACAP)

Original Author: Alex Shovkoplyas, VE3NEA
Python Port: 2025

This module models the electron density profile of the ionosphere:
- E, F1, and F2 layer modeling with parabolic and linear profiles
- True height and virtual height calculations
- Ionogram generation
- Deviative loss calculations
- Penetration angle calculations
"""

import math
from dataclasses import dataclass
from typing import Any
import numpy as np


# ============================================================================
# Constants
# ============================================================================

TWO_PI = 2 * math.pi
HALF_PI = math.pi / 2
RinD = math.pi / 180  # radians in degree
DinR = 180 / math.pi  # degrees in radian
EARTH_R = 6370  # Earth radius in km

# D and E layer constants
HM_D = 70   # D layer peak height (km)
HM_E = 110  # E layer peak height (km)
YM_E = 20   # E layer semi-thickness (km)

BOT_E = HM_E - 0.85 * YM_E
TOP_E = HM_E + YM_E

FNX = 1 - 0.85 * 0.85
ALP = 2 * (HM_E - BOT_E) / (FNX * YM_E * YM_E)

# Angle constants
MAX_NON_POLE_LAT = 89.9 * RinD
JUST_BELOW_MAX_ELEV = 89.9 * RinD
MAX_ELEV_ANGLE = 89.99 * RinD

# Gaussian integration constants
TWDIV = 0.5

# Gaussian integration weights and points (20-point)
XT = np.array([
    0.0387724175, 0.1160840707, 0.1926975807, 0.2681521850,
    0.3419940908, 0.4137792043, 0.4830758017, 0.5494671251,
    0.6125538897, 0.6719566846, 0.7273182552, 0.7783056514,
    0.8246122308, 0.8659595032, 0.9020988070, 0.9328128083,
    0.9579168192, 0.9772599500, 0.9907262387, 0.9982377097
], dtype=np.float32)

WT = np.array([
    0.0775059480, 0.0770398182, 0.0761103619, 0.0747231691,
    0.0728865824, 0.0706116474, 0.0679120458, 0.0648040135,
    0.0613062425, 0.0574397691, 0.0532278470, 0.0486958076,
    0.0438709082, 0.0387821680, 0.0334601953, 0.0279370070,
    0.0222458492, 0.0164210584, 0.0104982845, 0.0045212771
], dtype=np.float32)

# Angle array for raytracing (degrees converted to radians)
ANGLES = np.array([
    0, 0.5, 1, 2, 3, 4, 5, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26,
    28, 30, 32, 34, 36, 38, 40, 42, 44, 46, 48, 50, 52, 54, 56, 60,
    65, 70, 75, 80, 85, MAX_ELEV_ANGLE / RinD
], dtype=np.float32) * RinD


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class LayerInfo:
    """Information about an ionospheric layer"""
    fo: float = 0.0   # Critical frequency (MHz)
    hm: float = 0.0   # Peak height (km)
    ym: float = 0.0   # Semi-thickness (km)


@dataclass
class Reflection:
    """Reflection point information"""
    elevation: float = 0.0       # Elevation angle (radians)
    true_height: float = 0.0     # True height (km)
    virt_height: float = 0.0     # Virtual height (km)
    vert_freq: float = 0.0       # Vertical frequency (MHz)
    dev_loss: float = 0.0        # Deviative loss (dB)


@dataclass
class ModeInfo:
    """Propagation mode information"""
    ref: Reflection = None
    hop_dist: float = 0.0  # Single hop ground distance (radians)
    hop_cnt: int = 0  # Number of hops
    layer: str = ''  # Layer name ('E', 'F1', or 'F2')
    signal: 'SignalInfo' = None  # Signal information (forward reference to avoid circular import)

    def __post_init__(self):
        """Initialize ref and signal if not provided"""
        if self.ref is None:
            self.ref = Reflection()
        # Signal will be initialized by prediction_engine when needed


# ============================================================================
# Helper Functions
# ============================================================================

def interpolate_linear(arr: np.ndarray, start_h: int, end_h: int) -> None:
    """Populate array with linearly interpolated data"""
    if end_h <= start_h or end_h >= len(arr):
        return

    dif = (arr[end_h] - arr[start_h]) / (end_h - start_h)
    for h in range(start_h + 1, end_h):
        arr[h] = arr[h-1] + dif


def corr_to_martyns_theorem(ref: Reflection) -> float:
    """
    Apply Martyn's theorem correction.

    Args:
        ref: Reflection point information

    Returns:
        Correction factor
    """
    dh = (ref.virt_height - ref.true_height) / EARTH_R
    return dh * (ref.true_height + 2 * (EARTH_R + ref.true_height) * dh)


def get_index_of(value: float, array: np.ndarray) -> int:
    """
    Find index of value in array.

    Args:
        value: Value to find
        array: Array to search

    Returns:
        Index of nearest value
    """
    if value <= array[1]:
        return 1

    for f in range(1, len(array) - 1):
        if array[f] == value:
            return f
        elif np.sign(value - array[f]) != np.sign(value - array[f+1]):
            return f

    return len(array) - 1


def interpolate_table(x: float, arr_x: np.ndarray, arr_y: np.ndarray) -> float:
    """
    Interpolate value from lookup table.

    Args:
        x: Input value
        arr_x: X values (argument)
        arr_y: Y values (function)

    Returns:
        Interpolated Y value
    """
    assert len(arr_y) == len(arr_x), "Arrays must be same length"

    # Before table start
    if x <= arr_x[1]:
        return arr_y[1]

    idx = get_index_of(x, arr_x)

    # After table end or exact match
    if idx == len(arr_x) - 1 or x == arr_x[idx]:
        return arr_y[idx]

    # Linear interpolation
    r = (x - arr_x[idx]) / (arr_x[idx+1] - arr_x[idx])
    return arr_y[idx] * (1 - r) + arr_y[idx+1] * r


# ============================================================================
# IonosphericProfile Class
# ============================================================================

class IonosphericProfile:
    """
    Models the electron density profile of the ionosphere.

    This class creates a detailed model of electron density vs height
    for E, F1, and F2 layers, then uses this to compute true and virtual
    heights, ionograms, and propagation parameters.

    Example:
        >>> profile = IonosphericProfile()
        >>> profile.e = LayerInfo(fo=3.0, hm=110, ym=20)
        >>> profile.f2 = LayerInfo(fo=8.0, hm=300, ym=100)
        >>> profile.compute_el_density_profile()
        >>> true_h = profile.get_true_height(5.0)  # MHz
    """

    def __init__(self) -> None:
        # Layer information
        self.e = LayerInfo()
        self.f1 = LayerInfo()
        self.f2 = LayerInfo()

        # Location and time
        self.lat: float = 0.0
        self.mag_lat: float = 0.0
        self.local_time_e: float = 0.0
        self.local_time_f2: float = 0.0

        # Electron density profile arrays
        self.dens_true_height: np.ndarray | None = None  # Height values (km)
        self.el_density: np.ndarray | None = None        # Density values (MHz^2)

        # Ionogram arrays
        self.igram_vert_freq: np.ndarray | None = None    # Vertical frequency (MHz)
        self.igram_true_height: np.ndarray | None = None  # True height (km)
        self.igram_virt_height: np.ndarray | None = None  # Virtual height (km)
        self.dev_loss: np.ndarray | None = None           # Deviative loss (dB)

        # Oblique frequency array (angle_idx, height_idx)
        self.oblique_freq: np.ndarray | None = None

        # Parameters computed elsewhere
        self.absorption_index: float = 0.0
        self.gyro_freq: float = 0.0

        # Internal variables for layer analysis
        self._fc_e: float = 0.0
        self._fc_v_bot: float = 0.0
        self._fc_v_top: float = 0.0
        self._fc_f1: float = 0.0
        self._fc_f2: float = 0.0
        self._bot_v: float = 0.0
        self._top_v: float = 0.0
        self._bot_f1: float = 0.0
        self._top_f1: float = 0.0
        self._bot_f2: float = 0.0
        self._slope_v: float = 0.0
        self._slope_f1: float = 0.0
        self._linear_f1: bool = False

        # Cache for height/frequency lookups
        self._mhz: float = 0.0
        self._true_h: float = 0.0

    def compute_el_density_profile(self) -> None:
        """
        Compute the electron density profile.

        This analyzes the layer parameters and creates arrays of
        electron density vs true height for the entire ionosphere
        from D layer through F2 layer.
        """
        # Skip if already computed
        if self.dens_true_height is not None:
            return

        # Allocate arrays (51 points)
        self.dens_true_height = np.zeros(51, dtype=np.float32)
        self.el_density = np.zeros(51, dtype=np.float32)

        self._analyze_layers()
        self._populate_true_height_array()
        self._populate_electron_density_array()

    def _analyze_layers(self) -> None:
        """Analyze layer parameters and determine profile characteristics"""
        X_LOW = 0.8516
        X_UP = 0.98 * self.e.fo / self.f2.fo

        # E layer parameters
        self._bot_v = HM_E + YM_E * math.sqrt(1 - X_LOW * X_LOW)
        self._bot_f2 = self.f2.hm - self.f2.ym
        self._fc_e = self.e.fo * self.e.fo
        self._fc_f2 = self.f2.fo * self.f2.fo

        # Valley between E and F2 layers
        self._top_v = self._bot_f2 + self.f2.ym * (1 - math.sqrt(1 - X_UP * X_UP))
        self._fc_v_top = X_UP * X_UP * self._fc_f2
        self._fc_v_bot = X_LOW * X_LOW * self._fc_e

        if self._top_v > self._bot_v:
            self._slope_v = (self._fc_v_top - self._fc_v_bot) / (self._top_v - self._bot_v)
        else:
            self._slope_v = 0.0

        # F1 layer does not exist
        if self.f1.fo <= 0:
            return

        self._fc_f1 = self.f1.fo * self.f1.fo
        self._bot_f1 = self.f1.hm - self.f1.ym
        self._top_f1 = self.f1.hm + self.f1.ym

        # Height of F2 at F1 critical frequency
        htw = self._bot_f2 + self.f2.ym * (1 - math.sqrt(1 - self._fc_f1 / self._fc_f2))

        # Force F1 above E layer
        if htw > (self.f1.hm + 0.001):
            self._linear_f1 = False
            self.f1.ym = min(self.f1.ym, self.f1.hm - HM_E + 1)
            return

        # Force F1 at critical frequency
        ys = max(1.0, htw - self._bot_f1)
        self._slope_f1 = self._fc_f1 / ys
        self.f1.hm = htw
        self.f1.ym = ys

        # Avoid spurious layer
        if self._bot_f2 < self._bot_f1:
            self._linear_f1 = False
            self.f1.ym = self.f1.hm - max(self._bot_f2, HM_E - 1)
            return

        # Set flag for linear F1 layer
        self._linear_f1 = True

        # F1 line not to obscure E layer
        yb = 1 - (self.e.fo / self.f1.fo) ** 2
        yb = max(0.17, yb)
        yb = (self.f1.hm - HM_E) / yb

        # F1 passes through E nose
        if ys >= yb:
            ys = yb
            self.f1.ym = ys
            self._slope_f1 = self._fc_f1 / ys
            self._bot_f1 = HM_E

        self._top_f1 = htw

    def _populate_true_height_array(self) -> None:
        """Populate the true height array with appropriate spacing"""
        # D-E region
        dif = max(0.0, 0.25 * (BOT_E - HM_D))
        self.dens_true_height[1] = HM_D
        self.dens_true_height[2] = self.dens_true_height[1] + dif
        self.dens_true_height[4] = BOT_E - min(1.0, dif)
        self.dens_true_height[3] = 0.5 * (self.dens_true_height[2] + self.dens_true_height[4])
        self.dens_true_height[5] = BOT_E

        # E below nose
        self.dens_true_height[11] = HM_E
        interpolate_linear(self.dens_true_height, 5, 11)

        # E above nose
        self.dens_true_height[17] = HM_E + YM_E
        interpolate_linear(self.dens_true_height, 11, 17)
        self.dens_true_height[11] = 0.5 * (self.dens_true_height[10] + self.dens_true_height[12])

        # F1/F2
        self.dens_true_height[50] = self.f2.hm

        if (self.f1.fo == 0) or ((self.f2.hm - self.f2.ym) <= (self.f1.hm - self.f1.ym + 0.00001)):
            # F2 layer, no F1 layer
            self.dens_true_height[18] = self.f2.hm - self.f2.ym
            interpolate_linear(self.dens_true_height, 18, 50)
        else:
            # F1 layer and F2 layer
            self.dens_true_height[18] = max(self.dens_true_height[17] + 1, self.f1.hm - self.f1.ym)
            self.dens_true_height[28] = self.f1.hm
            interpolate_linear(self.dens_true_height, 18, 28)
            interpolate_linear(self.dens_true_height, 28, 50)

    def _populate_electron_density_array(self) -> None:
        """Populate electron density array for each height"""
        # Slope of E is same as slope of valley at BOT_E
        fsq = FNX * math.exp(-ALP * (BOT_E - HM_D))

        # Force F1 above E layer
        if self.f1.fo > 0:
            self._bot_f1 = max(HM_E, self.f1.hm - self.f1.ym)
        else:
            self._bot_f1 = 0

        for h in range(1, 51):
            height = self.dens_true_height[h]

            fn_d = 0.0
            fn_e = 0.0
            fn_val = 0.0
            fn_f1 = 0.0
            fn_f2 = 0.0

            # Linear valley
            if self._bot_v < height < self._top_v:
                fn_val = self._fc_v_top + self._slope_v * (height - self._top_v)

            # Exponential D-E
            if height < BOT_E:
                fn_d = self._fc_e * fsq * math.exp(ALP * (height - HM_D))
            # Parabolic E
            elif height <= TOP_E:
                fn_e = self._fc_e * (1 - ((height - HM_E) / YM_E) ** 2)

            # F1 layer
            if (self.f1.fo > 0) and (self._bot_f1 <= height <= self._top_f1):
                if self._linear_f1:
                    # Linear F1
                    fn_f1 = self._slope_f1 * (height - (self.f1.hm - self.f1.ym))
                else:
                    # Parabolic F1
                    fn_f1 = self._fc_f1 * (1 - ((height - self.f1.hm) / self.f1.ym) ** 2)

            # Parabolic F2
            if height >= self._bot_f2:
                fn_f2 = self._fc_f2 * (1 - ((height - self.f2.hm) / self.f2.ym) ** 2)

            # Use the maximum
            self.el_density[h] = max(fn_d, fn_e, fn_val, fn_f1, fn_f2)

    def _density_to_height(self, dens: float) -> float:
        """Convert electron density to true height by interpolation"""
        if dens <= self.el_density[1]:
            return self.dens_true_height[1]

        for h in range(2, 51):
            if dens <= self.el_density[h]:
                r = (dens - self.el_density[h-1]) / (self.el_density[h] - self.el_density[h-1])
                return self.dens_true_height[h-1] * (1-r) + self.dens_true_height[h] * r

        return self.dens_true_height[50]

    def _height_to_density(self, height: float) -> float:
        """Convert true height to electron density by interpolation"""
        if height <= self.dens_true_height[1]:
            return self.el_density[1]

        if height >= self.dens_true_height[50]:
            return self.el_density[50]

        for h in range(2, 51):
            if height <= self.dens_true_height[h]:
                r = (height - self.dens_true_height[h-1]) / (
                    self.dens_true_height[h] - self.dens_true_height[h-1]
                )
                return self.el_density[h-1] * (1-r) + self.el_density[h] * r

        return self.el_density[50]

    def get_true_height(self, mhz: float) -> float:
        """
        Get true height for given frequency.

        Args:
            mhz: Frequency in MHz

        Returns:
            True height in km
        """
        self._mhz = mhz
        self._true_h = self._density_to_height(mhz * mhz)
        return self._true_h

    def get_virtual_height_gauss(self, mhz: float) -> float:
        """
        Get virtual height using Gaussian integration.

        Virtual height is computed by integrating the group path
        from the ground to the reflection height.

        Args:
            mhz: Frequency in MHz

        Returns:
            Virtual height in km
        """
        if mhz != self._mhz:
            self.get_true_height(mhz)

        ht = self._true_h - self.dens_true_height[1]
        dens = mhz * mhz
        result = 0.0

        # Gaussian integration
        for i in range(20):
            ymup = self.dens_true_height[1] + ht * (1 - TWDIV * (1 - XT[i]))
            ymup = min(0.9999, self._height_to_density(ymup) / dens)
            ymup = 1 / math.sqrt(1 - ymup)

            zmup = self.dens_true_height[1] + ht * (1 - TWDIV * (1 + XT[i]))
            zmup = min(0.9999, self._height_to_density(zmup) / dens)
            zmup = 1 / math.sqrt(1 - zmup)

            result += WT[i] * (ymup + zmup)

        return self.dens_true_height[1] + ht * TWDIV * result

    def compute_ionogram(self) -> None:
        """
        Compute ionogram (true and virtual height vs frequency).

        Generates arrays of frequencies and corresponding true/virtual
        heights that describe the ionospheric profile.
        """
        if self.igram_true_height is not None:
            return

        if self.dens_true_height is None:
            self.compute_el_density_profile()

        # Allocate arrays (31 points)
        self.igram_true_height = np.zeros(31, dtype=np.float32)
        self.igram_virt_height = np.zeros(31, dtype=np.float32)
        self.igram_vert_freq = np.zeros(31, dtype=np.float32)

        # D-E region tail
        self.igram_vert_freq[1] = 0.01
        self.igram_vert_freq[4] = self.e.fo * math.sqrt(FNX)
        interpolate_linear(self.igram_vert_freq, 1, 4)

        # E region nose
        self.igram_vert_freq[9] = 0.957 * self.e.fo
        self.igram_vert_freq[10] = 0.99 * self.e.fo
        interpolate_linear(self.igram_vert_freq, 4, 9)

        # E-F cusp
        self.igram_vert_freq[11] = 1.05 * self.e.fo

        # F region nose
        self.igram_vert_freq[30] = 0.99 * self.f2.fo
        self.igram_vert_freq[29] = 0.98 * self.f2.fo
        self.igram_vert_freq[28] = 0.96 * self.f2.fo
        self.igram_vert_freq[27] = 0.92 * self.f2.fo

        if self.f1.fo > 0:
            # F1 layer and F2 layer
            self.igram_vert_freq[20] = 0.99 * self.f1.fo
            interpolate_linear(self.igram_vert_freq, 11, 20)
            # F1-F2 cusp
            self.igram_vert_freq[21] = 1.01 * self.f1.fo
            interpolate_linear(self.igram_vert_freq, 21, 27)
        else:
            # F2 layer, no F1 layer
            interpolate_linear(self.igram_vert_freq, 11, 27)

        # Compute height for each frequency
        for i in range(1, 31):
            self.igram_true_height[i] = self.get_true_height(self.igram_vert_freq[i])
            self.igram_virt_height[i] = self.get_virtual_height_gauss(self.igram_vert_freq[i])

    def compute_penetration_angles(self, mhz: float) -> dict[str, float]:
        """
        Compute penetration angles for each layer.

        Args:
            mhz: Frequency in MHz

        Returns:
            Dictionary mapping layer name to penetration angle in radians
        """
        if self.igram_vert_freq is None:
            self.compute_ionogram()

        def compute_elev(height: float, frat: float) -> float:
            """Helper to compute elevation angle"""
            result = (EARTH_R + height) * math.sqrt(1 - frat) / EARTH_R
            if result > 0.999999:
                return 0.0
            return math.acos(result)

        # E layer (use cusp)
        frat = (self.igram_vert_freq[10] / mhz) ** 2
        if frat < 0.9999:
            e_angle = compute_elev(self.igram_true_height[10], frat)
        else:
            # Cannot penetrate E layer
            return {'E': JUST_BELOW_MAX_ELEV, 'F1': HALF_PI, 'F2': HALF_PI}

        # F1 layer
        if self.f1.fo > 0:
            frat = (self.igram_vert_freq[20] / mhz) ** 2
            if frat < 0.9999:
                f1_angle = compute_elev(self.igram_true_height[20], frat)
            else:
                # Cannot penetrate F1 layer
                return {'E': e_angle, 'F1': JUST_BELOW_MAX_ELEV, 'F2': HALF_PI}
        else:
            f1_angle = e_angle

        # F2 layer
        if mhz <= (self.igram_vert_freq[30] + 0.0001):
            return {'E': e_angle, 'F1': f1_angle, 'F2': MAX_NON_POLE_LAT}

        # Find maximum (R+H)*mu for F2
        xm28 = (EARTH_R + self.igram_true_height[28]) * math.sqrt(
            1 - (self.igram_vert_freq[28] / mhz) ** 2
        )
        xm29 = (EARTH_R + self.igram_true_height[29]) * math.sqrt(
            1 - (self.igram_vert_freq[29] / mhz) ** 2
        )
        xm30 = (EARTH_R + self.igram_true_height[30]) * math.sqrt(
            1 - (self.igram_vert_freq[30] / mhz) ** 2
        )

        if xm30 >= xm29:
            xm = xm28 if xm28 > xm30 else xm30
        else:
            xm = xm29 if xm29 >= xm28 else xm28

        xm = xm / EARTH_R
        if xm > 0.999999:
            f2_angle = 0.0
        else:
            f2_angle = math.acos(xm)

        return {'E': e_angle, 'F1': f1_angle, 'F2': f2_angle}

    def compute_oblique_frequencies(self) -> None:
        """
        Compute oblique reflection frequencies for all angles and heights.

        This creates a 2D array oblique_freq[angle_idx, height_idx] that stores
        the maximum frequency (in kHz) that can be reflected at each angle and height.
        """
        if self.igram_vert_freq is None:
            self.compute_ionogram()

        # Allocate oblique frequency table (40 angles x 31 heights)
        self.oblique_freq = np.zeros((40, 31), dtype=np.int32)

        # For each ionogram point, compute oblique frequencies at all angles
        for h in range(1, 31):
            vert_freq = self.igram_vert_freq[h]  # MHz
            true_h = self.igram_true_height[h]  # km

            # For each angle
            for ang_idx in range(40):
                angle = ANGLES[ang_idx]

                # Oblique frequency using Snell's law
                # f_oblique = f_vertical / cos(incidence_angle)
                # where cos(incidence) = sqrt(1 - sin²(incidence))
                # and sin(incidence) = R*cos(elev) / (R+h)

                sin_i_sqr = (EARTH_R * math.cos(angle) / (EARTH_R + true_h)) ** 2

                if sin_i_sqr >= 1.0:
                    oblique_freq = 0  # Ray escapes
                else:
                    cos_i = math.sqrt(1 - sin_i_sqr)
                    oblique_freq = int(vert_freq * 1000 / cos_i)  # Convert MHz to kHz

                self.oblique_freq[ang_idx, h] = oblique_freq

    def compute_derivative_loss(self, muf_info: dict[str, Any]) -> None:
        """
        Compute derivative loss for the ionospheric profile.

        This is a stub implementation. The full calculation is complex and
        involves layer parameters and MUF information. Currently sets dev_loss
        to a simple array of zeros.

        Args:
            muf_info: Dictionary of MUF information for each layer
        """
        # TODO: Implement full derivative loss calculation
        # For now, initialize dev_loss array with zeros
        if self.igram_vert_freq is not None:
            self.dev_loss = np.zeros_like(self.igram_vert_freq)
        else:
            self.dev_loss = np.zeros(31, dtype=np.float32)

    def populate_mode_info(self, mode: ModeInfo, idx: int, r: float = 0.0) -> None:
        """
        Populate mode information from ionogram data.

        Args:
            mode: ModeInfo object to populate (modified in place)
            idx: Index in ionogram arrays
            r: Interpolation ratio (0.0 = use idx, 1.0 = use idx+1)
        """
        if self.igram_vert_freq is None:
            self.compute_ionogram()

        if r == 0.0:
            # Exact index
            mode.ref.true_height = self.igram_true_height[idx]
            mode.ref.virt_height = self.igram_virt_height[idx]
            mode.ref.vert_freq = self.igram_vert_freq[idx]
        else:
            # Interpolate between idx and idx+1
            mode.ref.true_height = (self.igram_true_height[idx] * (1 - r) +
                                   self.igram_true_height[idx + 1] * r)
            mode.ref.virt_height = (self.igram_virt_height[idx] * (1 - r) +
                                   self.igram_virt_height[idx + 1] * r)
            mode.ref.vert_freq = (self.igram_vert_freq[idx] * (1 - r) +
                                 self.igram_vert_freq[idx + 1] * r)

        # Deviative loss (simplified - full calculation is more complex)
        # This is a placeholder - the actual calculation involves layer parameters
        mode.ref.dev_loss = 0.0


# ============================================================================
# Module Test
# ============================================================================

if __name__ == "__main__":
    print("Testing IonosphericProfile module...")

    try:
        # Create profile with typical layer parameters
        profile = IonosphericProfile()
        profile.e = LayerInfo(fo=3.0, hm=110, ym=20)
        profile.f1 = LayerInfo(fo=5.0, hm=200, ym=50)
        profile.f2 = LayerInfo(fo=8.0, hm=300, ym=100)
        print("✓ Created ionospheric profile")

        # Compute electron density profile
        profile.compute_el_density_profile()
        print(f"✓ Computed electron density profile")
        print(f"  Profile points: {len(profile.dens_true_height)}")

        # Test height lookup
        freq = 5.0  # MHz
        true_h = profile.get_true_height(freq)
        virt_h = profile.get_virtual_height_gauss(freq)
        print(f"✓ At {freq} MHz:")
        print(f"  True height: {true_h:.1f} km")
        print(f"  Virtual height: {virt_h:.1f} km")

        # Compute ionogram
        profile.compute_ionogram()
        print(f"✓ Computed ionogram with {len(profile.igram_vert_freq)} points")

        # Test penetration angles
        test_freq = 10.0  # MHz
        angles = profile.compute_penetration_angles(test_freq)
        print(f"✓ Penetration angles at {test_freq} MHz:")
        print(f"  E layer: {angles[0] * DinR:.1f}°")
        print(f"  F1 layer: {angles[1] * DinR:.1f}°")
        print(f"  F2 layer: {angles[2] * DinR:.1f}°")

        print("\nAll basic tests passed!")

    except Exception as e:
        print(f"✗ Error: {e}")
        raise
