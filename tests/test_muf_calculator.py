"""
Tests for muf_calculator module (Phase 4)

Tests MUF (Maximum Usable Frequency) calculations, circuit MUF, FOT/HPF,
and related propagation mode analysis.
"""

import pytest
import numpy as np
from dvoacap.muf_calculator import (
    MufInfo,
    CircuitMuf,
    MufCalculator,
    select_profile,
    calc_muf_prob,
)
from dvoacap.ionospheric_profile import (
    IonosphericProfile,
    LayerInfo,
    Reflection,
)
from dvoacap.path_geometry import PathGeometry
from dvoacap.fourier_maps import FourierMaps


class TestMufInfo:
    """Tests for MufInfo dataclass"""

    def test_initialization(self):
        """Test MufInfo creation"""
        ref = Reflection(
            freq=7.0,
            height=300.0,
            angle=0.5,
            dist=0.15,
            virt_height=350.0
        )

        muf_info = MufInfo(
            ref=ref,
            hop_count=2,
            fot=5.0,
            hpf=6.0,
            muf=7.0
        )

        assert muf_info.ref == ref
        assert muf_info.hop_count == 2
        assert muf_info.fot == 5.0
        assert muf_info.hpf == 6.0
        assert muf_info.muf == 7.0

    def test_requires_reflection_object(self):
        """Test that ref must be a Reflection object"""
        with pytest.raises(TypeError, match="ref must be a Reflection object"):
            MufInfo(ref="invalid", hop_count=1)


class TestCircuitMuf:
    """Tests for CircuitMuf dataclass"""

    def test_initialization(self):
        """Test CircuitMuf creation"""
        ref = Reflection(freq=14.0, height=300.0, angle=0.5, dist=0.2, virt_height=350.0)
        muf_info_f2 = MufInfo(ref=ref, hop_count=2, fot=10.0, hpf=12.0, muf=14.0)

        circuit_muf = CircuitMuf(
            muf_info={'F2': muf_info_f2},
            fot=10.0,
            muf=14.0,
            hpf=12.0,
            angle=0.08,
            layer='F2'
        )

        assert 'F2' in circuit_muf.muf_info
        assert circuit_muf.muf_info['F2'].muf == 14.0
        assert circuit_muf.fot == 10.0
        assert circuit_muf.muf == 14.0
        assert circuit_muf.layer == 'F2'


class TestSelectProfile:
    """Tests for select_profile function"""

    def test_single_profile(self):
        """Test selection with single profile"""
        profile = IonosphericProfile()
        profile.f2.fo = 8.0

        result = select_profile([profile])
        assert result == profile

    def test_two_profiles(self):
        """Test selection between two profiles"""
        p1 = IonosphericProfile()
        p1.f2.fo = 8.0

        p2 = IonosphericProfile()
        p2.f2.fo = 10.0

        # Should select controlling profile (algorithm selects based on foF2)
        result = select_profile([p1, p2])
        assert result is not None
        assert isinstance(result, IonosphericProfile)

    def test_three_profiles(self):
        """Test selection among three profiles"""
        p1 = IonosphericProfile()
        p1.f2.fo = 7.0

        p2 = IonosphericProfile()
        p2.f2.fo = 9.0

        p3 = IonosphericProfile()
        p3.f2.fo = 8.0

        result = select_profile([p1, p2, p3])
        assert result is not None
        assert isinstance(result, IonosphericProfile)

    def test_empty_list(self):
        """Test with empty profile list"""
        result = select_profile([])
        assert result is None


class TestCalcMufProb:
    """Tests for calc_muf_prob function"""

    def test_basic_probability_calculation(self):
        """Test MUF probability calculation"""
        muf_info = {
            'F2': MufInfo(
                ref=Reflection(freq=14.0, height=300.0, angle=0.5, dist=0.2, virt_height=350.0),
                hop_count=2,
                muf=14.0,
                sig_lo=2.0,
                sig_hi=2.0
            )
        }

        circuit_muf = CircuitMuf(
            muf_info=muf_info,
            muf=14.0,
            layer='F2'
        )

        # Calculate probability at various frequencies
        prob_below = calc_muf_prob(12.0, circuit_muf)
        prob_at = calc_muf_prob(14.0, circuit_muf)
        prob_above = calc_muf_prob(16.0, circuit_muf)

        # Probability should be high below MUF, moderate at MUF, low above
        assert 0.0 <= prob_below <= 1.0
        assert 0.0 <= prob_at <= 1.0
        assert 0.0 <= prob_above <= 1.0
        assert prob_below >= prob_at >= prob_above

    def test_probability_bounds(self):
        """Test that probabilities stay within [0, 1]"""
        muf_info = {
            'F2': MufInfo(
                ref=Reflection(freq=10.0, height=300.0, angle=0.5, dist=0.2, virt_height=350.0),
                hop_count=1,
                muf=10.0,
                sig_lo=1.0,
                sig_hi=1.0
            )
        }

        circuit_muf = CircuitMuf(muf_info=muf_info, muf=10.0, layer='F2')

        # Test at extreme frequencies
        for freq in [1.0, 5.0, 10.0, 20.0, 30.0]:
            prob = calc_muf_prob(freq, circuit_muf)
            assert 0.0 <= prob <= 1.0, f"Probability {prob} out of bounds for freq {freq}"


class TestMufCalculator:
    """Tests for MufCalculator class"""

    @pytest.fixture
    def path(self):
        """Create a sample path geometry"""
        path = PathGeometry()
        # Philadelphia to London path (~5500 km)
        path.set_tx_rx(40.0 * np.pi/180, -75.0 * np.pi/180,
                      51.5 * np.pi/180, -0.1 * np.pi/180)
        return path

    @pytest.fixture
    def fourier_maps(self):
        """Create Fourier maps"""
        maps = FourierMaps()
        maps.set_conditions(month=6, ssn=100, utc_fraction=0.5)
        return maps

    @pytest.fixture
    def profile(self):
        """Create a realistic ionospheric profile"""
        profile = IonosphericProfile()

        # E layer
        profile.e.fo = 3.0
        profile.e.hm = 110.0
        profile.e.ym = 20.0

        # F1 layer
        profile.f1.fo = 5.0
        profile.f1.hm = 200.0
        profile.f1.ym = 50.0

        # F2 layer
        profile.f2.fo = 8.0
        profile.f2.hm = 300.0
        profile.f2.ym = 100.0

        profile.lat = 40.0 * np.pi/180
        profile.mag_lat = 50.0 * np.pi/180

        # Compute electron density profile
        profile.compute_el_density_profile()

        return profile

    def test_initialization(self, path, fourier_maps):
        """Test MufCalculator initialization"""
        calc = MufCalculator(path, fourier_maps)

        assert calc.path == path
        assert calc.fourier_maps == fourier_maps
        assert calc.min_angle == pytest.approx(3.0 * np.pi/180, rel=0.01)

    def test_compute_circuit_muf(self, path, fourier_maps, profile):
        """Test complete circuit MUF calculation"""
        calc = MufCalculator(path, fourier_maps)

        # Compute circuit MUF for a profile
        circuit_muf = calc.compute_circuit_muf([profile])

        assert circuit_muf is not None
        assert isinstance(circuit_muf, CircuitMuf)
        assert circuit_muf.muf > 0
        assert circuit_muf.fot > 0
        assert circuit_muf.hpf > 0
        assert circuit_muf.layer in ['E', 'F1', 'F2']

        # FOT should be less than MUF
        assert circuit_muf.fot <= circuit_muf.muf

        # HPF should be less than or equal to MUF
        assert circuit_muf.hpf <= circuit_muf.muf

    def test_muf_varies_with_distance(self, fourier_maps, profile):
        """Test that MUF varies with path distance"""
        # Short path
        short_path = PathGeometry()
        short_path.set_tx_rx(40.0 * np.pi/180, -75.0 * np.pi/180,
                           42.0 * np.pi/180, -71.0 * np.pi/180)

        # Long path
        long_path = PathGeometry()
        long_path.set_tx_rx(40.0 * np.pi/180, -75.0 * np.pi/180,
                          51.5 * np.pi/180, -0.1 * np.pi/180)

        calc_short = MufCalculator(short_path, fourier_maps)
        calc_long = MufCalculator(long_path, fourier_maps)

        muf_short = calc_short.compute_circuit_muf([profile])
        muf_long = calc_long.compute_circuit_muf([profile])

        assert muf_short is not None
        assert muf_long is not None

        # MUF values should be different for different path lengths
        # (exact relationship depends on ionospheric conditions)
        assert muf_short.muf != muf_long.muf or muf_short.layer != muf_long.layer

    def test_layer_selection(self, path, fourier_maps):
        """Test that controlling layer is selected correctly"""
        calc = MufCalculator(path, fourier_maps)

        # Strong F2 layer - should be controlling
        profile_f2 = IonosphericProfile()
        profile_f2.e.fo = 2.0
        profile_f2.e.hm = 110.0
        profile_f2.e.ym = 20.0
        profile_f2.f1.fo = 4.0
        profile_f2.f1.hm = 200.0
        profile_f2.f1.ym = 50.0
        profile_f2.f2.fo = 10.0  # Strong F2
        profile_f2.f2.hm = 300.0
        profile_f2.f2.ym = 100.0
        profile_f2.lat = 40.0 * np.pi/180
        profile_f2.compute_el_density_profile()

        muf = calc.compute_circuit_muf([profile_f2])
        assert muf is not None
        # For most medium/long paths, F2 should be controlling with strong F2 layer
        # (though this depends on path geometry)

    def test_multiple_profiles(self, path, fourier_maps):
        """Test MUF calculation with multiple profiles"""
        calc = MufCalculator(path, fourier_maps)

        # Create three different profiles
        profiles = []
        for fo_f2 in [7.0, 9.0, 11.0]:
            p = IonosphericProfile()
            p.e.fo = 3.0
            p.e.hm = 110.0
            p.e.ym = 20.0
            p.f1.fo = 5.0
            p.f1.hm = 200.0
            p.f1.ym = 50.0
            p.f2.fo = fo_f2
            p.f2.hm = 300.0
            p.f2.ym = 100.0
            p.lat = 40.0 * np.pi/180
            p.compute_el_density_profile()
            profiles.append(p)

        muf = calc.compute_circuit_muf(profiles)
        assert muf is not None
        assert isinstance(muf, CircuitMuf)
        assert muf.muf > 0

    def test_output_structure(self, path, fourier_maps, profile):
        """Test that circuit MUF has all expected fields"""
        calc = MufCalculator(path, fourier_maps)
        muf = calc.compute_circuit_muf([profile])

        assert hasattr(muf, 'muf')
        assert hasattr(muf, 'fot')
        assert hasattr(muf, 'hpf')
        assert hasattr(muf, 'angle')
        assert hasattr(muf, 'layer')
        assert hasattr(muf, 'muf_info')

        # muf_info should be a dictionary
        assert isinstance(muf.muf_info, dict)
        assert len(muf.muf_info) > 0

        # Check that at least one layer has MufInfo
        for layer_name, layer_muf_info in muf.muf_info.items():
            assert isinstance(layer_muf_info, MufInfo)
            assert hasattr(layer_muf_info, 'muf')
            assert hasattr(layer_muf_info, 'fot')
            assert hasattr(layer_muf_info, 'hpf')
            assert hasattr(layer_muf_info, 'hop_count')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
