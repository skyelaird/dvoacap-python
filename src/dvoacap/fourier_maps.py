#!/usr/bin/env python3
"""
Fourier Coefficient Maps Module for VOACAP
Ported from FrMaps.pas (DVOACAP)

Original Author: Alex Shovkoplyas, VE3NEA
Python Port: 2025

This module loads and processes CCIR/URSI ionospheric coefficient data:
- Loads binary coefficient files for each month
- Interpolates coefficients by sunspot number (SSN) and UTC time
- Computes ionospheric parameters: foF2, foE, foEs, M3000F2
- Provides fixed maps (noise, land mass, YmF2) and variable maps
"""

import math
import struct
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple
import numpy as np


# ============================================================================
# Constants
# ============================================================================

TWO_PI = 2 * math.pi
HALF_PI = math.pi / 2
RinD = math.pi / 180  # radians in degree
DinR = 180 / math.pi  # degrees in radian
NORM_DECILE = 1.28  # Normal distribution 10% decile


# ============================================================================
# Enumerations
# ============================================================================

class FixedMapKind:
    """Types of fixed ionospheric maps"""
    NOISE1 = 0
    NOISE2 = 1
    NOISE3 = 2
    NOISE4 = 3
    NOISE5 = 4
    NOISE6 = 5
    LAND_MASS = 6
    YM_F2 = 7


class VarMapKind:
    """Types of variable ionospheric maps"""
    ES_U = 0  # foEs upper decile
    ES_M = 1  # foEs median
    ES_L = 2  # foEs lower decile
    F2 = 3    # foF2 critical frequency
    FM3 = 4   # M3000F2 propagation factor
    ER = 5    # foE critical frequency


# ============================================================================
# Helper Functions
# ============================================================================

def make_sincos_array(angle: float, count: int) -> List[Tuple[float, float]]:
    """
    Generate array of sine and cosine values for Fourier series.

    Args:
        angle: Base angle in radians
        count: Number of harmonics to generate

    Returns:
        List of (sin, cos) tuples for each harmonic
    """
    result = [(0.0, 1.0)]  # 0th element
    for n in range(1, count):
        result.append((math.sin(n * angle), math.cos(n * angle)))
    return result


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class Distribution:
    """Statistical distribution with median and decile values"""
    median: float
    hi: float  # Upper decile
    lo: float  # Lower decile

    @classmethod
    def with_error(cls, value_mdn: float, value_hi: float, value_lo: float,
                   error_mdn: float, error_hi: float, error_lo: float) -> "Distribution":
        """Create distribution with separate value and error components"""
        return cls(
            median=value_mdn + error_mdn,
            hi=value_hi + error_hi,
            lo=value_lo + error_lo
        )


# ============================================================================
# FourierMaps Class
# ============================================================================

class FourierMaps:
    """
    Manages CCIR/URSI ionospheric coefficient maps.

    This class loads binary coefficient data and computes ionospheric
    parameters using Fourier series expansions. The coefficients are
    interpolated for specific month, sunspot number, and UTC time.

    Example:
        >>> maps = FourierMaps()
        >>> maps.set_conditions(month=6, ssn=100, utc_fraction=0.5)
        >>> fof2 = maps.compute_var_map(VarMapKind.F2, lat, lon, cos_lat)
    """

    def __init__(self, data_dir: str | None = None) -> None:
        """
        Initialize Fourier maps handler.

        Args:
            data_dir: Path to DVoaData directory. If None, uses default location.
        """
        if data_dir is None:
            # Default to DVoaData directory inside package
            package_dir = Path(__file__).parent
            data_dir = package_dir / "DVoaData"

            # Fallback to repository root for development/editable installs
            if not data_dir.exists():
                repo_root = package_dir.parent.parent
                data_dir = repo_root / "DVoaData"

        self.data_dir = Path(data_dir)

        # Current conditions (set to invalid values to force initial load)
        self.month: int = 0
        self.ssn: float = -1.0
        self.utc_fraction: float = -1.0

        # Coefficient arrays (loaded from files)
        self.ikim: dict[int, np.ndarray] = {}
        self.sys: np.ndarray | None = None
        self.f2d: np.ndarray | None = None
        self.perr: np.ndarray | None = None
        self.anew: np.ndarray | None = None
        self.bnew: np.ndarray | None = None
        self.achi: np.ndarray | None = None
        self.bchi: np.ndarray | None = None
        self.dud: np.ndarray | None = None
        self.fam: np.ndarray | None = None

        # Fixed coefficient arrays
        self.coef_fixed_p: np.ndarray | None = None
        self.coef_fixed_abp: np.ndarray | None = None

        # Variable coefficient arrays (before UTC interpolation)
        self.xf2cof: np.ndarray | None = None
        self.xfm3cf: np.ndarray | None = None
        self.xesmcf: np.ndarray | None = None
        self.xeslcf: np.ndarray | None = None
        self.xesucf: np.ndarray | None = None
        self.xercof: np.ndarray | None = None
        self.xpmap: np.ndarray | None = None

        # Interpolated coefficient arrays
        self.cofion: dict[int, np.ndarray] = {}
        self.coef_v: dict[int, np.ndarray] = {}

        # Initialize with default conditions
        self.set_conditions(1, 1, 0)

    def set_conditions(self, month: int, ssn: float, utc_fraction: float) -> None:
        """
        Set month, sunspot number, and UTC time for coefficient interpolation.

        Args:
            month: Month number (1-12)
            ssn: Smoothed sunspot number (0-200+)
            utc_fraction: UTC time as fraction of day (0.0-1.0)
        """
        # Reload coefficients if month changed
        if month != self.month:
            self._load_month_coefficients(month)
            self._interpolate_ssn(ssn)
            self._interpolate_utc(utc_fraction)
        # Re-interpolate if SSN changed
        elif ssn != self.ssn:
            self._interpolate_ssn(ssn)
            self._interpolate_utc(utc_fraction)
        # Re-interpolate if UTC changed
        elif utc_fraction != self.utc_fraction:
            self._interpolate_utc(utc_fraction)

    def _load_month_coefficients(self, month: int) -> None:
        """Load coefficient files for specified month"""
        self.month = month

        # Load main coefficient file (Coeff01.dat through Coeff12.dat)
        coeff_file = self.data_dir / f"Coeff{month:02d}.dat"
        if not coeff_file.exists():
            raise FileNotFoundError(f"Coefficient file not found: {coeff_file}")

        with open(coeff_file, 'rb') as f:
            # Read IKIM array (6 x 10 integers)
            ikim_data = struct.unpack('60i', f.read(60 * 4))
            for kind in range(6):
                self.ikim[kind] = np.array(ikim_data[kind*10:(kind+1)*10], dtype=np.int32)

            # Read DUD array (5 x 12 x 5 singles)
            dud_data = struct.unpack('300f', f.read(300 * 4))
            self.dud = np.array(dud_data, dtype=np.float32).reshape(5, 12, 5)

            # Read FAM array (12 x 2 x 7 singles)
            fam_data = struct.unpack('168f', f.read(168 * 4))
            self.fam = np.array(fam_data, dtype=np.float32).reshape(12, 2, 7)

            # Read SYS array (6 x 16 x 9 singles)
            sys_data = struct.unpack('864f', f.read(864 * 4))
            self.sys = np.array(sys_data, dtype=np.float32).reshape(6, 16, 9)

            # Read FAKP array (6 x 16 x 29 singles)
            fakp_data = struct.unpack('2784f', f.read(2784 * 4))
            fakp = np.array(fakp_data, dtype=np.float32).reshape(6, 16, 29)

            # Read FAKABP array (6 x 2 singles)
            fakabp_data = struct.unpack('12f', f.read(12 * 4))
            fakabp = np.array(fakabp_data, dtype=np.float32).reshape(6, 2)

            # Read XFM3CF array (2 x 49 x 9 singles)
            xfm3cf_data = struct.unpack('882f', f.read(882 * 4))
            self.xfm3cf = np.array(xfm3cf_data, dtype=np.float32).reshape(2, 49, 9)

            # Read ANEW array (3 singles)
            self.anew = np.array(struct.unpack('3f', f.read(3 * 4)), dtype=np.float32)

            # Read BNEW array (3 singles)
            self.bnew = np.array(struct.unpack('3f', f.read(3 * 4)), dtype=np.float32)

            # Read ACHI array (2 singles)
            self.achi = np.array(struct.unpack('2f', f.read(2 * 4)), dtype=np.float32)

            # Read BCHI array (2 singles)
            self.bchi = np.array(struct.unpack('2f', f.read(2 * 4)), dtype=np.float32)

            # Read FAKMAP array (16 x 29 singles)
            fakmap_data = struct.unpack('464f', f.read(464 * 4))
            fakmap = np.array(fakmap_data, dtype=np.float32).reshape(16, 29)

            # Read ABMAP array (3 x 2 singles)
            abmap_data = struct.unpack('6f', f.read(6 * 4))
            abmap = np.array(abmap_data, dtype=np.float32).reshape(3, 2)

            # Read F2D array (6 x 6 x 16 singles)
            f2d_data = struct.unpack('576f', f.read(576 * 4))
            self.f2d = np.array(f2d_data, dtype=np.float32).reshape(6, 6, 16)

            # Read PERR array (6 x 4 x 9 singles)
            perr_data = struct.unpack('216f', f.read(216 * 4))
            self.perr = np.array(perr_data, dtype=np.float32).reshape(6, 4, 9)

            # Read XESMCF array (2 x 61 x 7 singles)
            xesmcf_data = struct.unpack('854f', f.read(854 * 4))
            self.xesmcf = np.array(xesmcf_data, dtype=np.float32).reshape(2, 61, 7)

            # Read XPMAP array (2 x 16 x 29 singles)
            xpmap_data = struct.unpack('928f', f.read(928 * 4))
            self.xpmap = np.array(xpmap_data, dtype=np.float32).reshape(2, 16, 29)

            # Read XESLCF array (2 x 55 x 5 singles)
            xeslcf_data = struct.unpack('550f', f.read(550 * 4))
            self.xeslcf = np.array(xeslcf_data, dtype=np.float32).reshape(2, 55, 5)

            # Read XESUCF array (2 x 55 x 5 singles)
            xesucf_data = struct.unpack('550f', f.read(550 * 4))
            self.xesucf = np.array(xesucf_data, dtype=np.float32).reshape(2, 55, 5)

            # Read XERCOF array (2 x 22 x 9 singles)
            xercof_data = struct.unpack('396f', f.read(396 * 4))
            self.xercof = np.array(xercof_data, dtype=np.float32).reshape(2, 22, 9)

        # Organize fixed coefficients
        self.coef_fixed_p = np.zeros((8, 16, 29), dtype=np.float32)
        self.coef_fixed_p[:6] = fakp
        self.coef_fixed_p[6] = fakmap
        self.coef_fixed_p[7] = np.zeros((16, 29), dtype=np.float32)  # Will be filled with YmF2

        self.coef_fixed_abp = np.zeros((8, 2), dtype=np.float32)
        self.coef_fixed_abp[:6] = fakabp
        self.coef_fixed_abp[6] = abmap[0]
        self.coef_fixed_abp[7] = abmap[1]

        # Load F2 coefficient file (FOF2CCIR01.dat through FOF2CCIR12.dat)
        f2_file = self.data_dir / f"FOF2CCIR{month:02d}.dat"
        if not f2_file.exists():
            raise FileNotFoundError(f"F2 coefficient file not found: {f2_file}")

        with open(f2_file, 'rb') as f:
            # Read XF2COF array (2 x 76 x 13 singles)
            xf2cof_data = struct.unpack('1976f', f.read(1976 * 4))
            self.xf2cof = np.array(xf2cof_data, dtype=np.float32).reshape(2, 76, 13)

    def _interpolate_ssn(self, ssn: float) -> None:
        """Interpolate coefficients for specified sunspot number"""
        self.ssn = ssn

        # Interpolation ratios for different SSN ranges
        r100 = (ssn - 0) / (100 - 0)
        r125 = (ssn - 25) / (125 - 25)
        r150 = (ssn - 10) / (150 - 10)

        # foF2: interpolate between SSN=0 and SSN=100
        self.cofion[VarMapKind.F2] = (
            self.xf2cof[0] * (1 - r100) + self.xf2cof[1] * r100
        )

        # foEs median: interpolate between SSN=10 and SSN=150
        self.cofion[VarMapKind.ES_M] = (
            self.xesmcf[0] * (1 - r150) + self.xesmcf[1] * r150
        )

        # YmF2: interpolate between SSN=25 and SSN=125
        self.coef_fixed_p[7] = (
            self.xpmap[0] * (1 - r125) + self.xpmap[1] * r125
        )

        # foEs lower decile (note: XESUCF is lower, XESLCF is upper - bug in data)
        self.cofion[VarMapKind.ES_L] = (
            self.xesucf[0] * (1 - r150) + self.xesucf[1] * r150
        )

        # foEs upper decile
        self.cofion[VarMapKind.ES_U] = (
            self.xeslcf[0] * (1 - r150) + self.xeslcf[1] * r150
        )

        # M3000F2: interpolate between SSN=0 and SSN=100
        self.cofion[VarMapKind.FM3] = (
            self.xfm3cf[0] * (1 - r100) + self.xfm3cf[1] * r100
        )

        # foE: interpolate between SSN=10 and SSN=150
        self.cofion[VarMapKind.ER] = (
            self.xercof[0] * (1 - r150) + self.xercof[1] * r150
        )

    def _interpolate_utc(self, utc_fraction: float) -> None:
        """Interpolate coefficients for specified UTC time"""
        self.utc_fraction = utc_fraction

        # Generate sine/cosine array for Fourier series
        w = make_sincos_array((utc_fraction - 0.5) * TWO_PI, 8)

        # Interpolate each variable map type
        for kind in [VarMapKind.ES_U, VarMapKind.ES_M, VarMapKind.ES_L,
                     VarMapKind.F2, VarMapKind.FM3, VarMapKind.ER]:
            cofion = self.cofion[kind]
            n_coef = cofion.shape[0]
            n_harm = self.ikim[kind][9]

            # Start with DC component
            coef_v = cofion[:, 0].copy()

            # Add Fourier harmonics
            for j in range(1, n_harm + 1):
                sin_val, cos_val = w[j]
                coef_v += sin_val * cofion[:, 2*j-1] + cos_val * cofion[:, 2*j]

            self.coef_v[kind] = coef_v

    def compute_fixed_map(self, kind: int, lat: float, east_lon: float) -> float:
        """
        Compute fixed ionospheric map value.

        Fixed maps are noise levels, land mass, and YmF2 that don't
        vary with UTC time but depend on SSN and month.

        Args:
            kind: Map type (use FixedMapKind constants)
            lat: Latitude in radians
            east_lon: East longitude in radians

        Returns:
            Map value (units depend on map type)
        """
        # Base value (linear in latitude)
        result = (
            self.coef_fixed_abp[kind, 0] +
            self.coef_fixed_abp[kind, 1] * (lat + HALF_PI)
        )

        # Determine array dimensions
        if kind == FixedMapKind.YM_F2:
            lm, ln = 15, 10
        else:
            lm, ln = 29, 15

        # Generate sine/cosine arrays for Fourier series
        wn = make_sincos_array(0.5 * east_lon, ln + 1)
        wm = make_sincos_array(lat + HALF_PI, lm + 1)

        # Double Fourier series expansion
        for m in range(lm):
            r = 0.0
            for n in range(ln):
                r += wn[n+1][0] * self.coef_fixed_p[kind, n, m]
            result += wm[m+1][0] * (r + self.coef_fixed_p[kind, 15, m])

        return result

    def compute_var_map(self, kind: int, lat: float, east_lon: float,
                        cos_lat: float) -> float:
        """
        Compute variable ionospheric map value.

        Variable maps include foF2, foE, foEs, M3000F2 that vary with
        month, SSN, and UTC time.

        Args:
            kind: Map type (use VarMapKind constants)
            lat: Latitude in radians (or magnetic dip for some maps)
            east_lon: East longitude in radians
            cos_lat: Cosine of latitude

        Returns:
            Map value in MHz (for critical frequencies) or unitless (M3000)
        """
        coef = self.coef_v[kind]
        sx = math.sin(lat)
        cx = cos_lat

        # Build G array with spherical harmonic terms
        n_coef = len(coef)
        g = np.zeros(n_coef, dtype=np.float32)
        g[0] = 1.0

        # Compute G[i] = sx^N
        last_i = self.ikim[kind][0]
        if last_i > 0:
            g[1] = sx
            for i in range(2, min(last_i + 1, n_coef)):
                g[i] = g[i-1] * sx

        # Compute G[i] = sx^N * cx^M * sin/cos(M*lon)
        power_cx = cx
        for pwr_c in range(1, 9):
            i = last_i + 1
            last_i = self.ikim[kind][pwr_c]
            if i > last_i or last_i >= n_coef:
                break

            # First two terms: cos and sin of M*lon
            if i < n_coef:
                g[i] = power_cx * math.cos(pwr_c * east_lon)
            if i + 1 < n_coef:
                g[i+1] = power_cx * math.sin(pwr_c * east_lon)
            i += 2

            # Remaining terms: multiply by sx
            while i <= last_i and i < n_coef:
                if i >= 2:
                    g[i] = sx * g[i-2]
                if i + 1 < n_coef and i + 1 <= last_i:
                    g[i+1] = sx * g[i-1]
                i += 2

            power_cx *= cx

        # Compute result = sum(G[i] * coef[i])
        result = np.dot(g[:n_coef], coef[:n_coef])
        return float(result)

    def compute_zen_max(self, mag_dip: float) -> float:
        """
        Compute maximum solar zenith angle for F1 layer formation.

        Args:
            mag_dip: Magnetic dip angle in radians

        Returns:
            Maximum zenith angle in radians
        """
        result = (
            self.achi[0] + self.bchi[0] * self.ssn +
            (self.achi[1] + self.bchi[1] * self.ssn) * math.cos(mag_dip)
        )
        return result * RinD

    def compute_fof1(self, zen_angle: float) -> float:
        """
        Compute F1 layer critical frequency.

        Args:
            zen_angle: Solar zenith angle in radians

        Returns:
            foF1 in MHz
        """
        cos_z = math.cos(zen_angle)
        cos_z2 = cos_z * cos_z

        result = (
            (self.anew[0] + self.bnew[0] * self.ssn) +
            (self.anew[1] + self.bnew[1] * self.ssn) * cos_z +
            (self.anew[2] + self.bnew[2] * self.ssn) * cos_z2
        )
        return result

    def compute_f2_deviation(self, muf: float, lat: float,
                            local_time: float, above: bool) -> float:
        """
        Compute F2 layer deviation for reliability calculations.

        Args:
            muf: Maximum usable frequency in MHz
            lat: Latitude in radians
            local_time: Local time as fraction of day (0.0-1.0)
            above: True for above MUF, False for below

        Returns:
            Standard deviation in MHz
        """
        # Local time index (0-5 for 4-hour blocks)
        t = int(local_time * 6 + 0.55)
        if t >= 6:
            t = 0

        # Latitude index (0-7 for latitude bands, 8-15 for below MUF)
        l = int(8.5 - abs(lat) * 0.1 / RinD)
        l = max(0, min(7, l))
        if not above:
            l += 8

        # SSN index (0-2 for SSN ranges, +3 for south lat)
        if self.ssn <= 50:
            s = 0
        elif self.ssn <= 100:
            s = 1
        else:
            s = 2

        if lat <= 0:
            s += 3

        # Get deviation from lookup table
        f2d_value = self.f2d[t, s, l]
        result = abs((1 - f2d_value) * muf) * (1 / NORM_DECILE)

        # Debug F2 deviation calculation
        import sys
        if False:  # Enable for debugging
            print(f"\n=== F2 DEVIATION DEBUG ===", file=sys.stderr)
            print(f"MUF: {muf:.2f} MHz", file=sys.stderr)
            print(f"Lat: {lat * 180 / np.pi:.2f}°", file=sys.stderr)
            print(f"Local time: {local_time:.4f}", file=sys.stderr)
            print(f"Above: {above}", file=sys.stderr)
            print(f"Indices: T={t}, S={s}, L={l}", file=sys.stderr)
            print(f"F2D value: {f2d_value:.6f}", file=sys.stderr)
            print(f"Result: {result:.4f} MHz", file=sys.stderr)
            print("=" * 50, file=sys.stderr)

        return max(0.001, result)

    def compute_excessive_system_loss(self, mag_lat: float, local_time: float,
                                      over_2500km: bool) -> Distribution:
        """
        Compute excessive system loss distribution.

        Args:
            mag_lat: Magnetic latitude in radians
            local_time: Local time as fraction of day (0.0-1.0)
            over_2500km: True if path > 2500 km

        Returns:
            Distribution with median, hi, and lo values in dB
        """
        nn = 3 if over_2500km else 0
        nd = 3 if mag_lat < 0 else 0

        hour = round(local_time * 24)

        # Local time index for SYS array
        lj = int(hour / 3 - 0.33)
        if lj < 0:
            lj = 7
        if mag_lat < 0:
            lj += 8

        # Local time index for PERR array
        ld = int(hour / 6 - 0.33)
        if ld < 0:
            ld = 3

        # Magnetic latitude index
        kj = round((abs(mag_lat * DinR) - 40) / 5)
        kj = max(0, min(8, kj))

        # Extract values and errors
        value_mdn = self.sys[nn+1, lj, kj]
        value_hi = self.sys[nn+2, lj, kj] / NORM_DECILE
        value_lo = self.sys[nn, lj, kj] / NORM_DECILE

        error_mdn = self.perr[nd, ld, kj]
        error_hi = self.perr[nd+1, ld, kj]
        error_lo = self.perr[nd+2, ld, kj]

        return Distribution.with_error(
            value_mdn, value_hi, value_lo,
            error_mdn, error_hi, error_lo
        )

    def compute_fam(self, idx1: int, idx2: int, u: float) -> float:
        """
        Compute FAM noise parameter using polynomial.

        Args:
            idx1: First index (0-11)
            idx2: Second index (0-1)
            u: Parameter value

        Returns:
            FAM value
        """
        coeffs = self.fam[idx1, idx2]
        result = coeffs[0]
        for i in range(1, len(coeffs)):
            result = u * result + coeffs[i]
        return result

    def compute_dud(self, idx1: int, idx2: int, u: float) -> float:
        """
        Compute DUD noise parameter using polynomial.

        Args:
            idx1: First index (0-4)
            idx2: Second index (0-11)
            u: Parameter value

        Returns:
            DUD value
        """
        coeffs = self.dud[idx1, idx2]
        result = coeffs[0]
        for i in range(1, len(coeffs)):
            result = u * result + coeffs[i]
        return result


# ============================================================================
# Module Test
# ============================================================================

if __name__ == "__main__":
    # Simple test of coefficient loading
    print("Testing FourierMaps module...")

    try:
        maps = FourierMaps()
        print(f"✓ Initialized FourierMaps")

        maps.set_conditions(month=6, ssn=100, utc_fraction=0.5)
        print(f"✓ Set conditions: June, SSN=100, Noon UTC")

        # Test compute_var_map for foF2 at equator
        lat = 0.0  # Equator
        lon = 0.0  # Prime meridian
        fof2 = maps.compute_var_map(VarMapKind.F2, lat, lon, 1.0)
        print(f"✓ foF2 at equator: {fof2:.2f} MHz")

        # Test compute_fixed_map for YmF2
        ym_f2 = maps.compute_fixed_map(FixedMapKind.YM_F2, lat, lon)
        print(f"✓ YmF2 at equator: {ym_f2:.2f}")

        print("\nAll basic tests passed!")

    except Exception as e:
        print(f"✗ Error: {e}")
        raise
