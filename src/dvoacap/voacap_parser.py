"""
VOACAP Binary File Parser

This module provides functionality to parse VOACAP binary coefficient data files.
These files contain Fourier coefficients for ionospheric models used in HF radio
propagation predictions.

Binary file formats:
- Coeff##.dat: Monthly ionospheric coefficient data (38,480 bytes)
- FOF2CCIR##.dat: F2 critical frequency data (7,904 bytes)

Author: Port from Pascal implementation by Alex Shovkoplyas, VE3NEA
License: Mozilla Public License Version 1.1
"""

import numpy as np
from pathlib import Path
from enum import IntEnum
from typing import Any


class VarMapKind(IntEnum):
    """Types of variable ionospheric maps"""
    VM_ES_U = 0  # foEs upper decile
    VM_ES_M = 1  # foEs median
    VM_ES_L = 2  # foEs lower decile
    VM_F2 = 3    # foF2
    VM_FM3 = 4   # M3000
    VM_ER = 5    # foE


class FixedMapKind(IntEnum):
    """Types of fixed ionospheric maps"""
    FM_NOISE1 = 0
    FM_NOISE2 = 1
    FM_NOISE3 = 2
    FM_NOISE4 = 3
    FM_NOISE5 = 4
    FM_NOISE6 = 5
    FM_LAND_MASS = 6
    FM_YM_F2 = 7


class FixedCoeff:
    """
    Fixed coefficient data structure.

    This corresponds to the TFixedCoeff record in FrMaps.pas.
    Contains arrays used for computing fixed ionospheric maps.
    """

    def __init__(self) -> None:
        # P: array[TFixedMapKind, 0..15, 0..28] of Single
        # This is structured as FAKP (6x16x29) + FAKMAP (16x29) + HMYM (16x29)
        self.P = np.zeros((8, 16, 29), dtype=np.float32)

        # ABP: array[TFixedMapKind, 0..1] of Single
        # This is structured as FAKABP (6x2) + ABMAP (3x2)
        self.ABP = np.zeros((8, 2), dtype=np.float32)

    def load_from_arrays(self, fakp: np.ndarray, fakmap: np.ndarray,
                         hmym: np.ndarray, fakabp: np.ndarray,
                         abmap: np.ndarray) -> None:
        """Load coefficients from separate arrays"""
        # Fill P array: first 6 are from FAKP
        self.P[0:6, :, :] = fakp
        # Index 6 is FAKMAP (land mass)
        self.P[6, :, :] = fakmap
        # Index 7 is HMYM (YmF2)
        self.P[7, :, :] = hmym

        # Fill ABP array: first 6 are from FAKABP
        self.ABP[0:6, :] = fakabp
        # Last 2 rows are from ABMAP (but ABMAP is 3x2)
        self.ABP[6:8, :] = abmap[0:2, :]


class CoeffData:
    """
    Complete coefficient data for one month.

    This corresponds to the data loaded by TFourierMaps.LoadCoeffResource()
    from the Coeff##.dat files.
    """

    def __init__(self) -> None:
        # Integer array indices for variable maps
        self.ikim = np.zeros((6, 10), dtype=np.int32)

        # System parameters
        self.dud = np.zeros((5, 12, 5), dtype=np.float32)
        self.fam = np.zeros((12, 2, 7), dtype=np.float32)
        self.sys = np.zeros((6, 16, 9), dtype=np.float32)

        # Fixed coefficients
        self.fixed_coeff = FixedCoeff()

        # Variable map coefficients (for SSN interpolation)
        self.xfm3cf = np.zeros((2, 49, 9), dtype=np.float32)
        self.anew = np.zeros(3, dtype=np.float32)
        self.bnew = np.zeros(3, dtype=np.float32)
        self.achi = np.zeros(2, dtype=np.float32)
        self.bchi = np.zeros(2, dtype=np.float32)
        self.f2d = np.zeros((6, 6, 16), dtype=np.float32)
        self.perr = np.zeros((6, 4, 9), dtype=np.float32)
        self.xesmcf = np.zeros((2, 61, 7), dtype=np.float32)
        self.xpmap = np.zeros((2, 16, 29), dtype=np.float32)
        self.xeslcf = np.zeros((2, 55, 5), dtype=np.float32)
        self.xesucf = np.zeros((2, 55, 5), dtype=np.float32)
        self.xercof = np.zeros((2, 22, 9), dtype=np.float32)


class F2Data:
    """
    F2 critical frequency coefficient data.

    This corresponds to the data loaded from FOF2CCIR##.dat files.
    """

    def __init__(self) -> None:
        # XF2COF: array[0..1, 0..75, 0..12] of Single
        self.xf2cof = np.zeros((2, 76, 13), dtype=np.float32)


class VoacapParser:
    """
    Parser for VOACAP binary coefficient data files.

    This class provides methods to read and parse the binary coefficient
    files used by VOACAP for ionospheric propagation predictions.
    """

    @staticmethod
    def parse_coeff_file(filepath: Path) -> CoeffData:
        """
        Parse a Coeff##.dat binary file.

        Args:
            filepath: Path to the Coeff##.dat file

        Returns:
            CoeffData object containing all coefficient arrays

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file size is incorrect
        """
        if not filepath.exists():
            raise FileNotFoundError(f"Coefficient file not found: {filepath}")

        # Expected file size: 60 integers + 9560 floats = 38,480 bytes
        expected_size = 60 * 4 + 9560 * 4
        actual_size = filepath.stat().st_size

        if actual_size != expected_size:
            raise ValueError(
                f"Invalid Coeff file size: expected {expected_size} bytes, "
                f"got {actual_size} bytes"
            )

        data = CoeffData()

        with open(filepath, 'rb') as f:
            # Read in the exact order specified in FrMaps.pas LoadCoeffResource()

            # 1. IKIM: array[TVarMapKind, 0..9] of integer (6x10)
            data.ikim = np.fromfile(f, dtype=np.int32, count=60).reshape((6, 10))

            # 2. DUD: array[0..4, 0..11, 0..4] of Single (5x12x5)
            data.dud = np.fromfile(f, dtype=np.float32, count=300).reshape((5, 12, 5))

            # 3. FAM: array[0..11, 0..1, 0..6] of Single (12x2x7)
            data.fam = np.fromfile(f, dtype=np.float32, count=168).reshape((12, 2, 7))

            # 4. SYS: array[0..5, 0..15, 0..8] of Single (6x16x9)
            data.sys = np.fromfile(f, dtype=np.float32, count=864).reshape((6, 16, 9))

            # 5. FAKP: array[0..5, 0..15, 0..28] of Single (6x16x29)
            fakp = np.fromfile(f, dtype=np.float32, count=2784).reshape((6, 16, 29))

            # 6. FAKABP: array[0..5, 0..1] of Single (6x2)
            fakabp = np.fromfile(f, dtype=np.float32, count=12).reshape((6, 2))

            # 7. XFM3CF: array[0..1, 0..48, 0..8] of Single (2x49x9)
            data.xfm3cf = np.fromfile(f, dtype=np.float32, count=882).reshape((2, 49, 9))

            # 8. ANEW: array[0..2] of Single (3)
            data.anew = np.fromfile(f, dtype=np.float32, count=3)

            # 9. BNEW: array[0..2] of Single (3)
            data.bnew = np.fromfile(f, dtype=np.float32, count=3)

            # 10. ACHI: array[0..1] of Single (2)
            data.achi = np.fromfile(f, dtype=np.float32, count=2)

            # 11. BCHI: array[0..1] of Single (2)
            data.bchi = np.fromfile(f, dtype=np.float32, count=2)

            # 12. FAKMAP: array[0..15, 0..28] of Single (16x29)
            fakmap = np.fromfile(f, dtype=np.float32, count=464).reshape((16, 29))

            # 13. ABMAP: array[0..2, 0..1] of Single (3x2)
            abmap = np.fromfile(f, dtype=np.float32, count=6).reshape((3, 2))

            # 14. F2D: array[0..5, 0..5, 0..15] of Single (6x6x16)
            data.f2d = np.fromfile(f, dtype=np.float32, count=576).reshape((6, 6, 16))

            # 15. PERR: array[0..5, 0..3, 0..8] of Single (6x4x9)
            data.perr = np.fromfile(f, dtype=np.float32, count=216).reshape((6, 4, 9))

            # 16. XESMCF: array[0..1, 0..60, 0..6] of Single (2x61x7)
            data.xesmcf = np.fromfile(f, dtype=np.float32, count=854).reshape((2, 61, 7))

            # 17. XPMAP: array[0..1, 0..15, 0..28] of Single (2x16x29)
            data.xpmap = np.fromfile(f, dtype=np.float32, count=928).reshape((2, 16, 29))

            # 18. XESLCF: array[0..1, 0..54, 0..4] of Single (2x55x5)
            data.xeslcf = np.fromfile(f, dtype=np.float32, count=550).reshape((2, 55, 5))

            # 19. XESUCF: array[0..1, 0..54, 0..4] of Single (2x55x5)
            data.xesucf = np.fromfile(f, dtype=np.float32, count=550).reshape((2, 55, 5))

            # 20. XERCOF: array[0..1, 0..21, 0..8] of Single (2x22x9)
            data.xercof = np.fromfile(f, dtype=np.float32, count=396).reshape((2, 22, 9))

            # 21. HMYM is actually loaded as XPMAP initially (see line 180 vs 225-227)
            # It gets computed later during SSN interpolation, but we need to read it
            # Actually, looking more carefully, HMYM is stored in CoefF but computed
            # from XPMAP during interpolation. The file only contains XPMAP.
            hmym = np.zeros((16, 29), dtype=np.float32)  # Will be computed later

            # Load the fixed coefficients
            data.fixed_coeff.load_from_arrays(fakp, fakmap, hmym, fakabp, abmap)

        return data

    @staticmethod
    def parse_f2_file(filepath: Path) -> F2Data:
        """
        Parse a FOF2CCIR##.dat binary file.

        Args:
            filepath: Path to the FOF2CCIR##.dat file

        Returns:
            F2Data object containing F2 coefficient arrays

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file size is incorrect
        """
        if not filepath.exists():
            raise FileNotFoundError(f"F2 file not found: {filepath}")

        # Expected file size: 2x76x13 floats = 1976 floats = 7,904 bytes
        expected_size = 1976 * 4
        actual_size = filepath.stat().st_size

        if actual_size != expected_size:
            raise ValueError(
                f"Invalid F2 file size: expected {expected_size} bytes, "
                f"got {actual_size} bytes"
            )

        data = F2Data()

        with open(filepath, 'rb') as f:
            # XF2COF: array[0..1, 0..75, 0..12] of Single (2x76x13)
            data.xf2cof = np.fromfile(f, dtype=np.float32, count=1976).reshape((2, 76, 13))

        return data

    @staticmethod
    def load_monthly_data(data_dir: Path, month: int) -> tuple[CoeffData, F2Data]:
        """
        Load both coefficient and F2 data files for a given month.

        Args:
            data_dir: Directory containing the DVoaData files
            month: Month number (1-12)

        Returns:
            Tuple of (CoeffData, F2Data)

        Raises:
            ValueError: If month is not in range 1-12
            FileNotFoundError: If data files don't exist
        """
        if not (1 <= month <= 12):
            raise ValueError(f"Month must be 1-12, got {month}")

        coeff_file = data_dir / f"Coeff{month:02d}.dat"
        f2_file = data_dir / f"FOF2CCIR{month:02d}.dat"

        coeff_data = VoacapParser.parse_coeff_file(coeff_file)
        f2_data = VoacapParser.parse_f2_file(f2_file)

        return coeff_data, f2_data

    @staticmethod
    def get_data_summary(coeff_data: CoeffData) -> dict[str, Any]:
        """
        Get a summary of the coefficient data for inspection.

        Args:
            coeff_data: CoeffData object

        Returns:
            Dictionary with summary information
        """
        return {
            'ikim_shape': coeff_data.ikim.shape,
            'ikim_sample': coeff_data.ikim[0, :].tolist(),
            'dud_shape': coeff_data.dud.shape,
            'dud_range': (float(coeff_data.dud.min()), float(coeff_data.dud.max())),
            'fam_shape': coeff_data.fam.shape,
            'sys_shape': coeff_data.sys.shape,
            'fixed_coeff_P_shape': coeff_data.fixed_coeff.P.shape,
            'fixed_coeff_ABP_shape': coeff_data.fixed_coeff.ABP.shape,
            'xfm3cf_shape': coeff_data.xfm3cf.shape,
            'anew': coeff_data.anew.tolist(),
            'bnew': coeff_data.bnew.tolist(),
            'achi': coeff_data.achi.tolist(),
            'bchi': coeff_data.bchi.tolist(),
            'f2d_shape': coeff_data.f2d.shape,
            'perr_shape': coeff_data.perr.shape,
            'xesmcf_shape': coeff_data.xesmcf.shape,
            'xpmap_shape': coeff_data.xpmap.shape,
            'xeslcf_shape': coeff_data.xeslcf.shape,
            'xesucf_shape': coeff_data.xesucf.shape,
            'xercof_shape': coeff_data.xercof.shape,
        }


# Convenience functions
def load_coeff_file(filepath: str) -> CoeffData:
    """
    Load a Coeff##.dat file.

    Args:
        filepath: Path to the coefficient file

    Returns:
        CoeffData object
    """
    return VoacapParser.parse_coeff_file(Path(filepath))


def load_f2_file(filepath: str) -> F2Data:
    """
    Load a FOF2CCIR##.dat file.

    Args:
        filepath: Path to the F2 file

    Returns:
        F2Data object
    """
    return VoacapParser.parse_f2_file(Path(filepath))


def load_month(data_dir: str, month: int) -> tuple[CoeffData, F2Data]:
    """
    Load monthly coefficient data.

    Args:
        data_dir: Directory containing DVoaData files
        month: Month number (1-12)

    Returns:
        Tuple of (CoeffData, F2Data)
    """
    return VoacapParser.load_monthly_data(Path(data_dir), month)
