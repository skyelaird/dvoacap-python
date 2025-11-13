"""
Tests for VOACAP binary file parser.

This module tests the parsing of VOACAP coefficient data files.
"""

import pytest
import numpy as np
from pathlib import Path
from dvoacap.voacap_parser import (
    VoacapParser,
    CoeffData,
    F2Data,
    FixedCoeff,
    VarMapKind,
    FixedMapKind,
    load_coeff_file,
    load_f2_file,
    load_month
)


# Fixture for data directory
@pytest.fixture
def data_dir():
    """Get the DVoaData directory path"""
    repo_root = Path(__file__).parent.parent
    return repo_root / "DVoaData"


@pytest.fixture
def sample_coeff_file(data_dir):
    """Get a sample coefficient file (January)"""
    return data_dir / "Coeff01.dat"


@pytest.fixture
def sample_f2_file(data_dir):
    """Get a sample F2 file (January)"""
    return data_dir / "FOF2CCIR01.dat"


class TestFixedCoeff:
    """Tests for FixedCoeff class"""

    def test_initialization(self):
        """Test FixedCoeff initialization"""
        fc = FixedCoeff()
        assert fc.P.shape == (8, 16, 29)
        assert fc.ABP.shape == (8, 2)
        assert fc.P.dtype == np.float32
        assert fc.ABP.dtype == np.float32

    def test_load_from_arrays(self):
        """Test loading coefficients from arrays"""
        fc = FixedCoeff()

        # Create test arrays with known values
        fakp = np.ones((6, 16, 29), dtype=np.float32) * 1.0
        fakmap = np.ones((16, 29), dtype=np.float32) * 2.0
        hmym = np.ones((16, 29), dtype=np.float32) * 3.0
        fakabp = np.ones((6, 2), dtype=np.float32) * 4.0
        abmap = np.ones((3, 2), dtype=np.float32) * 5.0

        fc.load_from_arrays(fakp, fakmap, hmym, fakabp, abmap)

        # Check that arrays were loaded correctly
        assert np.allclose(fc.P[0:6, :, :], 1.0)
        assert np.allclose(fc.P[6, :, :], 2.0)
        assert np.allclose(fc.P[7, :, :], 3.0)
        assert np.allclose(fc.ABP[0:6, :], 4.0)
        assert np.allclose(fc.ABP[6:8, :], 5.0)


class TestCoeffData:
    """Tests for CoeffData class"""

    def test_initialization(self):
        """Test CoeffData initialization"""
        cd = CoeffData()

        # Check all arrays are initialized with correct shapes
        assert cd.ikim.shape == (6, 10)
        assert cd.dud.shape == (5, 12, 5)
        assert cd.fam.shape == (12, 2, 7)
        assert cd.sys.shape == (6, 16, 9)
        assert cd.xfm3cf.shape == (2, 49, 9)
        assert cd.anew.shape == (3,)
        assert cd.bnew.shape == (3,)
        assert cd.achi.shape == (2,)
        assert cd.bchi.shape == (2,)
        assert cd.f2d.shape == (6, 6, 16)
        assert cd.perr.shape == (6, 4, 9)
        assert cd.xesmcf.shape == (2, 61, 7)
        assert cd.xpmap.shape == (2, 16, 29)
        assert cd.xeslcf.shape == (2, 55, 5)
        assert cd.xesucf.shape == (2, 55, 5)
        assert cd.xercof.shape == (2, 22, 9)

        # Check dtypes
        assert cd.ikim.dtype == np.int32
        assert cd.dud.dtype == np.float32
        assert cd.fixed_coeff.P.dtype == np.float32


class TestF2Data:
    """Tests for F2Data class"""

    def test_initialization(self):
        """Test F2Data initialization"""
        f2 = F2Data()
        assert f2.xf2cof.shape == (2, 76, 13)
        assert f2.xf2cof.dtype == np.float32


class TestVoacapParser:
    """Tests for VoacapParser class"""

    def test_parse_coeff_file_exists(self, sample_coeff_file):
        """Test parsing a real coefficient file"""
        assert sample_coeff_file.exists(), f"Test file not found: {sample_coeff_file}"

        data = VoacapParser.parse_coeff_file(sample_coeff_file)

        # Check that data was loaded
        assert isinstance(data, CoeffData)

        # Check array shapes
        assert data.ikim.shape == (6, 10)
        assert data.dud.shape == (5, 12, 5)
        assert data.fam.shape == (12, 2, 7)
        assert data.sys.shape == (6, 16, 9)
        assert data.fixed_coeff.P.shape == (8, 16, 29)
        assert data.fixed_coeff.ABP.shape == (8, 2)

        # Check that IKIM contains reasonable integer values
        # IKIM should contain indices, typically small positive integers
        assert data.ikim.min() >= 0
        assert data.ikim.max() < 100  # Reasonable upper bound

        # Check that coefficient arrays contain finite values
        assert np.all(np.isfinite(data.dud))
        assert np.all(np.isfinite(data.fam))
        assert np.all(np.isfinite(data.sys))
        assert np.all(np.isfinite(data.fixed_coeff.P))

    def test_parse_coeff_file_not_found(self):
        """Test error handling for missing file"""
        with pytest.raises(FileNotFoundError):
            VoacapParser.parse_coeff_file(Path("/nonexistent/file.dat"))

    def test_parse_f2_file_exists(self, sample_f2_file):
        """Test parsing a real F2 file"""
        assert sample_f2_file.exists(), f"Test file not found: {sample_f2_file}"

        data = VoacapParser.parse_f2_file(sample_f2_file)

        # Check that data was loaded
        assert isinstance(data, F2Data)
        assert data.xf2cof.shape == (2, 76, 13)

        # Check that coefficient arrays contain finite values
        assert np.all(np.isfinite(data.xf2cof))

    def test_parse_f2_file_not_found(self):
        """Test error handling for missing F2 file"""
        with pytest.raises(FileNotFoundError):
            VoacapParser.parse_f2_file(Path("/nonexistent/file.dat"))

    def test_load_monthly_data(self, data_dir):
        """Test loading complete monthly data"""
        coeff_data, f2_data = VoacapParser.load_monthly_data(data_dir, 1)

        assert isinstance(coeff_data, CoeffData)
        assert isinstance(f2_data, F2Data)

        # Verify data was loaded
        assert coeff_data.ikim.shape == (6, 10)
        assert f2_data.xf2cof.shape == (2, 76, 13)

    def test_load_monthly_data_invalid_month(self, data_dir):
        """Test error handling for invalid month"""
        with pytest.raises(ValueError, match="Month must be 1-12"):
            VoacapParser.load_monthly_data(data_dir, 0)

        with pytest.raises(ValueError, match="Month must be 1-12"):
            VoacapParser.load_monthly_data(data_dir, 13)

    def test_get_data_summary(self, sample_coeff_file):
        """Test getting data summary"""
        data = VoacapParser.parse_coeff_file(sample_coeff_file)
        summary = VoacapParser.get_data_summary(data)

        # Check that summary contains expected keys
        assert 'ikim_shape' in summary
        assert 'ikim_sample' in summary
        assert 'dud_shape' in summary
        assert 'dud_range' in summary
        assert 'anew' in summary
        assert 'bnew' in summary
        assert 'achi' in summary
        assert 'bchi' in summary

        # Check that shapes are correct
        assert summary['ikim_shape'] == (6, 10)
        assert summary['dud_shape'] == (5, 12, 5)
        assert summary['fixed_coeff_P_shape'] == (8, 16, 29)

        # Check that sample data is returned as list
        assert isinstance(summary['ikim_sample'], list)
        assert len(summary['ikim_sample']) == 10

        # Check that coefficient arrays have reasonable values
        assert isinstance(summary['anew'], list)
        assert len(summary['anew']) == 3
        assert isinstance(summary['bnew'], list)
        assert len(summary['bnew']) == 3


class TestConvenienceFunctions:
    """Tests for convenience functions"""

    def test_load_coeff_file(self, sample_coeff_file):
        """Test load_coeff_file convenience function"""
        data = load_coeff_file(str(sample_coeff_file))
        assert isinstance(data, CoeffData)
        assert data.ikim.shape == (6, 10)

    def test_load_f2_file(self, sample_f2_file):
        """Test load_f2_file convenience function"""
        data = load_f2_file(str(sample_f2_file))
        assert isinstance(data, F2Data)
        assert data.xf2cof.shape == (2, 76, 13)

    def test_load_month(self, data_dir):
        """Test load_month convenience function"""
        coeff_data, f2_data = load_month(str(data_dir), 1)
        assert isinstance(coeff_data, CoeffData)
        assert isinstance(f2_data, F2Data)


class TestDataConsistency:
    """Tests for data consistency across months"""

    def test_all_months_loadable(self, data_dir):
        """Test that all 12 months can be loaded"""
        for month in range(1, 13):
            coeff_data, f2_data = VoacapParser.load_monthly_data(data_dir, month)

            # Verify shapes are consistent
            assert coeff_data.ikim.shape == (6, 10)
            assert coeff_data.dud.shape == (5, 12, 5)
            assert f2_data.xf2cof.shape == (2, 76, 13)

            # Verify data is finite
            assert np.all(np.isfinite(coeff_data.dud))
            assert np.all(np.isfinite(f2_data.xf2cof))

    def test_monthly_variations(self, data_dir):
        """Test that coefficient data varies between months"""
        # Load January and July (should be quite different)
        jan_coeff, jan_f2 = VoacapParser.load_monthly_data(data_dir, 1)
        jul_coeff, jul_f2 = VoacapParser.load_monthly_data(data_dir, 7)

        # Check that data is different between months
        # (they should NOT be identical)
        assert not np.allclose(jan_coeff.dud, jul_coeff.dud)
        assert not np.allclose(jan_f2.xf2cof, jul_f2.xf2cof)

    def test_coefficient_value_ranges(self, data_dir):
        """Test that coefficient values are in reasonable ranges"""
        coeff_data, f2_data = VoacapParser.load_monthly_data(data_dir, 1)

        # IKIM should contain small non-negative integers (array indices)
        assert coeff_data.ikim.min() >= 0
        assert coeff_data.ikim.max() < 100

        # Other arrays should contain finite values
        # (no NaN, no Inf, reasonable magnitudes)
        assert np.all(np.isfinite(coeff_data.dud))
        assert np.all(np.isfinite(coeff_data.fam))
        assert np.all(np.isfinite(coeff_data.sys))
        assert np.all(np.isfinite(coeff_data.anew))
        assert np.all(np.isfinite(coeff_data.bnew))
        assert np.all(np.isfinite(coeff_data.achi))
        assert np.all(np.isfinite(coeff_data.bchi))

        # F2 coefficients should also be finite
        assert np.all(np.isfinite(f2_data.xf2cof))


class TestEnums:
    """Tests for enum classes"""

    def test_var_map_kind_enum(self):
        """Test VarMapKind enum"""
        assert VarMapKind.VM_ES_U == 0
        assert VarMapKind.VM_ES_M == 1
        assert VarMapKind.VM_ES_L == 2
        assert VarMapKind.VM_F2 == 3
        assert VarMapKind.VM_FM3 == 4
        assert VarMapKind.VM_ER == 5
        assert len(VarMapKind) == 6

    def test_fixed_map_kind_enum(self):
        """Test FixedMapKind enum"""
        assert FixedMapKind.FM_NOISE1 == 0
        assert FixedMapKind.FM_NOISE2 == 1
        assert FixedMapKind.FM_NOISE3 == 2
        assert FixedMapKind.FM_NOISE4 == 3
        assert FixedMapKind.FM_NOISE5 == 4
        assert FixedMapKind.FM_NOISE6 == 5
        assert FixedMapKind.FM_LAND_MASS == 6
        assert FixedMapKind.FM_YM_F2 == 7
        assert len(FixedMapKind) == 8
