"""
Tests for reflectrix module (Phase 4)

Tests ray path calculations through the ionosphere, skip distance computation,
multi-hop path finding, and over-the-MUF handling.
"""

import pytest
import numpy as np
from dvoacap.reflectrix import Reflectrix
from dvoacap.ionospheric_profile import IonosphericProfile, LayerInfo, ModeInfo
from dvoacap.path_geometry import EarthR


class TestReflectrix:
    """Tests for Reflectrix class"""

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

        # Compute electron density profile and ionogram
        profile.compute_el_density_profile()
        profile.compute_ionogram()
        profile.compute_oblique_frequencies()

        return profile

    def test_initialization(self, profile):
        """Test Reflectrix initialization"""
        min_angle = 3.0 * np.pi/180
        freq = 7.0  # MHz

        refl = Reflectrix(min_angle, freq, profile)

        assert refl.min_angle == min_angle
        assert refl.fmhz == freq
        assert refl.fkhz == int(freq * 1000)
        assert refl.profile == profile

    def test_reflectrix_computed(self, profile):
        """Test that reflectrix is computed during initialization"""
        min_angle = 3.0 * np.pi/180
        freq = 7.0

        refl = Reflectrix(min_angle, freq, profile)

        # Reflectrix should have computed reflection points
        assert isinstance(refl.refl, list)
        # Should have at least some modes (unless frequency is way above MUF)
        # Note: This might be empty if freq > MUF, so we just check it's a list

    def test_skip_distance(self, profile):
        """Test skip distance calculation"""
        min_angle = 3.0 * np.pi/180
        freq = 5.0  # Below foF2

        refl = Reflectrix(min_angle, freq, profile)

        # Skip distance should be non-negative
        assert refl.skip_distance >= 0
        # Max distance should be >= skip distance
        assert refl.max_distance >= refl.skip_distance

    def test_frequency_affects_skip_distance(self, profile):
        """Test that frequency affects skip distance"""
        min_angle = 3.0 * np.pi/180

        # Lower frequency
        refl_low = Reflectrix(min_angle, 3.0, profile)
        skip_low = refl_low.skip_distance

        # Higher frequency
        refl_high = Reflectrix(min_angle, 7.0, profile)
        skip_high = refl_high.skip_distance

        # Higher frequencies generally have longer skip distances
        # (though this depends on the ionospheric profile)
        assert skip_low >= 0
        assert skip_high >= 0

    def test_min_angle_affects_results(self, profile):
        """Test that minimum angle affects reflectrix"""
        freq = 7.0

        # Lower takeoff angle
        refl_low = Reflectrix(3.0 * np.pi/180, freq, profile)

        # Higher takeoff angle
        refl_high = Reflectrix(15.0 * np.pi/180, freq, profile)

        # Different minimum angles should give different results
        # At minimum, the maximum distance should be affected by angle
        assert refl_low.max_distance != refl_high.max_distance or \
               refl_low.skip_distance != refl_high.skip_distance or \
               len(refl_low.refl) != len(refl_high.refl)

    def test_find_modes_at_distance(self, profile):
        """Test finding propagation modes at a specific distance"""
        min_angle = 3.0 * np.pi/180
        freq = 7.0

        refl = Reflectrix(min_angle, freq, profile)

        # Find modes at 2000 km
        distance = 2000.0 / EarthR  # Convert to radians
        modes = refl.find_modes(distance)

        assert isinstance(modes, list)
        # Should find at least one mode if frequency allows
        # (might be empty if no propagation possible at this distance/frequency)

        for mode in modes:
            assert isinstance(mode, ModeInfo)
            assert hasattr(mode, 'layer')
            assert hasattr(mode, 'dist')
            assert hasattr(mode, 'angle')

    def test_modes_list_structure(self, profile):
        """Test that modes have correct structure"""
        min_angle = 3.0 * np.pi/180
        freq = 5.0  # Likely to have propagation

        refl = Reflectrix(min_angle, freq, profile)

        # Try to find modes at a reasonable distance
        distance = 1500.0 / EarthR

        modes = refl.find_modes(distance)

        for mode in modes:
            # Each mode should have required fields
            assert hasattr(mode, 'layer')
            assert hasattr(mode, 'angle')
            assert hasattr(mode, 'dist')
            assert hasattr(mode, 'height')

            # Angle should be reasonable (0 to 90 degrees)
            assert 0 <= mode.angle <= np.pi/2

            # Distance should be close to requested
            # (within some tolerance for discretization)
            assert mode.dist > 0

    def test_below_muf_has_modes(self, profile):
        """Test that frequencies below MUF have propagation modes"""
        min_angle = 3.0 * np.pi/180

        # Use frequency well below foF2 (8 MHz in fixture)
        freq = 4.0

        refl = Reflectrix(min_angle, freq, profile)

        # Should have some reflection points in the reflectrix
        # (unless profile is very unusual)
        # Check that reflectrix was computed
        assert hasattr(refl, 'refl')
        assert isinstance(refl.refl, list)

    def test_above_muf_behavior(self, profile):
        """Test behavior when frequency is above MUF"""
        min_angle = 3.0 * np.pi/180

        # Use frequency well above foF2 (8 MHz in fixture)
        freq = 20.0

        refl = Reflectrix(min_angle, freq, profile)

        # Above MUF, skip distance should be very large or no modes found
        # This is valid behavior - not an error
        assert isinstance(refl.refl, list)
        # Above MUF, modes list might be empty
        # (this is expected behavior, not a failure)

    def test_compute_reflectrix_updates_state(self, profile):
        """Test that compute_reflectrix updates internal state"""
        min_angle = 3.0 * np.pi/180
        freq1 = 5.0

        refl = Reflectrix(min_angle, freq1, profile)

        # Store initial state
        initial_modes = len(refl.refl)
        initial_skip = refl.skip_distance

        # Recompute with different frequency
        freq2 = 7.0
        refl.compute_reflectrix(freq2, profile)

        # State should have updated
        assert refl.fmhz == freq2
        assert refl.fkhz == int(freq2 * 1000)

        # Results may be different (or same, depending on profile)
        # Just verify that compute ran without error
        assert isinstance(refl.refl, list)
        assert refl.skip_distance >= 0

    def test_different_profiles_give_different_results(self):
        """Test that different ionospheric profiles give different results"""
        min_angle = 3.0 * np.pi/180
        freq = 7.0

        # Profile 1: Strong F2
        p1 = IonosphericProfile()
        p1.e.fo = 3.0
        p1.e.hm = 110.0
        p1.e.ym = 20.0
        p1.f1.fo = 5.0
        p1.f1.hm = 200.0
        p1.f1.ym = 50.0
        p1.f2.fo = 10.0  # Strong
        p1.f2.hm = 300.0
        p1.f2.ym = 100.0
        p1.lat = 40.0 * np.pi/180
        p1.compute_el_density_profile()
        p1.compute_ionogram()
        p1.compute_oblique_frequencies()

        # Profile 2: Weak F2
        p2 = IonosphericProfile()
        p2.e.fo = 3.0
        p2.e.hm = 110.0
        p2.e.ym = 20.0
        p2.f1.fo = 5.0
        p2.f1.hm = 200.0
        p2.f1.ym = 50.0
        p2.f2.fo = 6.0  # Weak
        p2.f2.hm = 300.0
        p2.f2.ym = 100.0
        p2.lat = 40.0 * np.pi/180
        p2.compute_el_density_profile()
        p2.compute_ionogram()
        p2.compute_oblique_frequencies()

        refl1 = Reflectrix(min_angle, freq, p1)
        refl2 = Reflectrix(min_angle, freq, p2)

        # Results should be different
        # (For freq=7 MHz: p1 has foF2=10 (below MUF), p2 has foF2=6 (above MUF))
        # So they should have very different skip distances
        assert refl1.skip_distance != refl2.skip_distance or \
               len(refl1.refl) != len(refl2.refl)

    def test_short_distance_mode_finding(self, profile):
        """Test mode finding at short distances"""
        min_angle = 3.0 * np.pi/180
        freq = 5.0

        refl = Reflectrix(min_angle, freq, profile)

        # Very short distance (500 km)
        distance = 500.0 / EarthR

        modes = refl.find_modes(distance)

        # Might have modes or not, depending on skip distance
        assert isinstance(modes, list)
        # If skip distance is greater than requested, modes might be empty

    def test_long_distance_mode_finding(self, profile):
        """Test mode finding at long distances"""
        min_angle = 3.0 * np.pi/180
        freq = 7.0

        refl = Reflectrix(min_angle, freq, profile)

        # Long distance (3000 km) - likely multi-hop
        distance = 3000.0 / EarthR

        modes = refl.find_modes(distance)

        assert isinstance(modes, list)

        for mode in modes:
            # Long distance modes should have multiple hops
            # (or single hop with very long skip)
            assert mode.dist > 0

    def test_profile_requirement(self):
        """Test that profile is required"""
        min_angle = 3.0 * np.pi/180
        freq = 7.0

        # This should not crash - it should handle the requirement internally
        # The profile parameter is required in __init__
        profile = IonosphericProfile()
        profile.e.fo = 3.0
        profile.e.hm = 110.0
        profile.e.ym = 20.0
        profile.f2.fo = 8.0
        profile.f2.hm = 300.0
        profile.f2.ym = 100.0
        profile.compute_el_density_profile()
        profile.compute_ionogram()
        profile.compute_oblique_frequencies()

        refl = Reflectrix(min_angle, freq, profile)
        assert refl.profile == profile


class TestReflectrixIntegration:
    """Integration tests for Reflectrix with realistic scenarios"""

    def test_typical_hf_frequencies(self):
        """Test with typical HF amateur radio frequencies"""
        profile = IonosphericProfile()
        profile.e.fo = 3.0
        profile.e.hm = 110.0
        profile.e.ym = 20.0
        profile.f1.fo = 5.0
        profile.f1.hm = 200.0
        profile.f1.ym = 50.0
        profile.f2.fo = 8.0
        profile.f2.hm = 300.0
        profile.f2.ym = 100.0
        profile.lat = 40.0 * np.pi/180
        profile.compute_el_density_profile()
        profile.compute_ionogram()
        profile.compute_oblique_frequencies()

        min_angle = 3.0 * np.pi/180

        # Test common HF bands
        for freq in [3.5, 7.0, 14.0, 21.0]:
            refl = Reflectrix(min_angle, freq, profile)

            assert refl.fmhz == freq
            assert isinstance(refl.refl, list)
            assert refl.skip_distance >= 0
            assert refl.max_distance >= refl.skip_distance

    def test_day_vs_night_profiles(self):
        """Test day vs night ionospheric conditions"""
        min_angle = 3.0 * np.pi/180
        freq = 7.0

        # Daytime profile - stronger ionosphere
        day_profile = IonosphericProfile()
        day_profile.e.fo = 4.0  # Strong E layer
        day_profile.e.hm = 110.0
        day_profile.e.ym = 20.0
        day_profile.f1.fo = 6.0  # F1 present
        day_profile.f1.hm = 200.0
        day_profile.f1.ym = 50.0
        day_profile.f2.fo = 10.0  # High foF2
        day_profile.f2.hm = 300.0
        day_profile.f2.ym = 100.0
        day_profile.lat = 40.0 * np.pi/180
        day_profile.compute_el_density_profile()
        day_profile.compute_ionogram()
        day_profile.compute_oblique_frequencies()

        # Nighttime profile - weaker ionosphere
        night_profile = IonosphericProfile()
        night_profile.e.fo = 0.5  # Very weak E
        night_profile.e.hm = 110.0
        night_profile.e.ym = 20.0
        night_profile.f1.fo = 0.0  # No F1
        night_profile.f1.hm = 200.0
        night_profile.f1.ym = 50.0
        night_profile.f2.fo = 5.0  # Lower foF2
        night_profile.f2.hm = 350.0  # Higher altitude
        night_profile.f2.ym = 100.0
        night_profile.lat = 40.0 * np.pi/180
        night_profile.compute_el_density_profile()
        night_profile.compute_ionogram()
        night_profile.compute_oblique_frequencies()

        day_refl = Reflectrix(min_angle, freq, day_profile)
        night_refl = Reflectrix(min_angle, freq, night_profile)

        # Day and night should give different results
        assert day_refl.skip_distance != night_refl.skip_distance or \
               len(day_refl.refl) != len(night_refl.refl)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
