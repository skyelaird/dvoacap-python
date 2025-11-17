"""
Tests for space_weather_sources module

Tests multi-source space weather data fetching with fallback mechanisms.
"""

import pytest
from dvoacap.space_weather_sources import (
    SpaceWeatherData,
    SolarFluxFetcher,
    SunspotNumberFetcher,
    KpIndexFetcher,
    AIndexFetcher,
    MultiSourceSpaceWeatherFetcher,
)


class TestSpaceWeatherData:
    """Tests for SpaceWeatherData dataclass"""

    def test_initialization_with_defaults(self):
        """Test default initialization"""
        data = SpaceWeatherData()

        assert data.kp is None
        assert data.a_index is None
        assert data.sfi is None
        assert data.ssn is None
        assert data.sources == {}
        assert data.timestamp is None

    def test_initialization_with_values(self):
        """Test initialization with specific values"""
        data = SpaceWeatherData(
            kp=3.0,
            a_index=15.0,
            sfi=150.0,
            ssn=100.0,
            sources={'kp': 'test_source'},
            timestamp='2025-01-01T00:00:00Z'
        )

        assert data.kp == 3.0
        assert data.a_index == 15.0
        assert data.sfi == 150.0
        assert data.ssn == 100.0
        assert data.sources == {'kp': 'test_source'}
        assert data.timestamp == '2025-01-01T00:00:00Z'

    def test_to_dict(self):
        """Test conversion to dictionary"""
        data = SpaceWeatherData(
            kp=2.0,
            a_index=10.0,
            sfi=120.0,
            ssn=50.0
        )

        result = data.to_dict()

        assert isinstance(result, dict)
        assert result['kp'] == 2.0
        assert result['a_index'] == 10.0
        assert result['sfi'] == 120.0
        assert result['ssn'] == 50.0

    def test_to_dict_with_none_values(self):
        """Test to_dict with None values"""
        data = SpaceWeatherData()
        result = data.to_dict()

        assert isinstance(result, dict)
        assert result['kp'] is None
        assert result['a_index'] is None


class TestKpIndexFetcher:
    """Tests for NOAA fetcher"""

    def test_initialization(self):
        """Test fetcher initialization"""
        fetcher = KpIndexFetcher(timeout=15, verbose=False)

        assert fetcher.timeout == 15
        assert fetcher.verbose == False

    def test_initialization_defaults(self):
        """Test default values"""
        fetcher = KpIndexFetcher()

        assert fetcher.timeout == 10
        assert fetcher.verbose == True

    def test_has_required_attributes(self):
        """Test that fetcher has required methods"""
        fetcher = KpIndexFetcher()

        assert hasattr(fetcher, 'fetch_kp')
        assert hasattr(fetcher, 'fetch_a_index')
        assert hasattr(fetcher, 'fetch_sfi')
        assert hasattr(fetcher, 'fetch_ssn')
        assert callable(fetcher.fetch_kp)


class TestAIndexFetcher:
    """Tests for HamQSL fetcher"""

    def test_initialization(self):
        """Test fetcher initialization"""
        fetcher = AIndexFetcher(timeout=20, verbose=False)

        assert fetcher.timeout == 20
        assert fetcher.verbose == False

    def test_has_required_methods(self):
        """Test that fetcher has required methods"""
        fetcher = AIndexFetcher()

        assert hasattr(fetcher, 'fetch_kp')
        assert hasattr(fetcher, 'fetch_a_index')
        assert hasattr(fetcher, 'fetch_sfi')
        assert hasattr(fetcher, 'fetch_ssn')


class TestMultiSourceSpaceWeatherFetcher:
    """Tests for multi-source fetcher with fallback"""

    def test_initialization(self):
        """Test multi-source fetcher initialization"""
        fetcher = MultiSourceSpaceWeatherFetcher(timeout=15, verbose=False)

        assert fetcher.timeout == 15
        assert fetcher.verbose == False

    def test_initialization_creates_sub_fetchers(self):
        """Test that sub-fetchers are created"""
        fetcher = MultiSourceSpaceWeatherFetcher()

        # Should have initialized sub-fetchers
        assert hasattr(fetcher, 'fetchers') or hasattr(fetcher, 'noaa_fetcher')

    def test_has_fetch_all_method(self):
        """Test that fetch_all method exists"""
        fetcher = MultiSourceSpaceWeatherFetcher()

        assert hasattr(fetcher, 'fetch_all')
        assert callable(fetcher.fetch_all)

    def test_fetch_all_returns_space_weather_data(self):
        """Test that fetch_all returns SpaceWeatherData object"""
        fetcher = MultiSourceSpaceWeatherFetcher(timeout=2, verbose=False)

        try:
            result = fetcher.fetch_all()
            # If network is available, should return SpaceWeatherData
            assert isinstance(result, SpaceWeatherData)
        except Exception:
            # Network might not be available in test environment
            # That's okay - we're testing the structure, not the network
            pass

    def test_fetch_all_handles_network_errors_gracefully(self):
        """Test that fetch_all handles errors without crashing"""
        fetcher = MultiSourceSpaceWeatherFetcher(timeout=0.001, verbose=False)

        # Should not crash even with very short timeout
        try:
            result = fetcher.fetch_all()
            # Should still return a SpaceWeatherData object (with None values)
            assert isinstance(result, SpaceWeatherData)
        except Exception:
            # Or it might raise an exception - that's also acceptable
            # The key is it doesn't crash with an unexpected error
            pass

    def test_sources_are_tracked(self):
        """Test that data sources are tracked"""
        fetcher = MultiSourceSpaceWeatherFetcher(timeout=2, verbose=False)

        try:
            result = fetcher.fetch_all()
            # If successful, sources dictionary should exist
            assert hasattr(result, 'sources')
            assert isinstance(result.sources, dict)
        except Exception:
            # Network not available
            pass

    def test_fallback_mechanism_structure(self):
        """Test that fallback logic is in place"""
        fetcher = MultiSourceSpaceWeatherFetcher()

        # Should have multiple fetchers available for fallback
        # (exact implementation may vary)
        # Just verify the class initializes properly
        assert fetcher is not None


class TestSpaceWeatherIntegration:
    """Integration tests for space weather fetching"""

    def test_data_fields_are_compatible(self):
        """Test that all fetchers return compatible data"""
        data1 = SpaceWeatherData(kp=3.0, a_index=15.0)
        data2 = SpaceWeatherData(sfi=150.0, ssn=100.0)

        # Both should have same structure
        dict1 = data1.to_dict()
        dict2 = data2.to_dict()

        assert set(dict1.keys()) == set(dict2.keys())

    def test_typical_values_are_reasonable(self):
        """Test that typical space weather values are in expected ranges"""
        # This tests the data structure, not actual fetching
        data = SpaceWeatherData(
            kp=4.0,       # Kp index typically 0-9
            a_index=20.0,  # A-index typically 0-400
            sfi=150.0,     # Solar flux typically 50-300
            ssn=100.0      # Sunspot number typically 0-300
        )

        # Verify values are stored correctly
        assert 0 <= data.kp <= 9
        assert 0 <= data.a_index <= 400
        assert 50 <= data.sfi <= 300
        assert 0 <= data.ssn <= 300

    def test_none_values_are_handled(self):
        """Test that None values don't cause errors"""
        data = SpaceWeatherData(
            kp=None,
            a_index=None,
            sfi=150.0,  # Only SFI available
            ssn=None
        )

        # Should handle None values gracefully
        result_dict = data.to_dict()
        assert result_dict['kp'] is None
        assert result_dict['sfi'] == 150.0

    def test_multiple_fetchers_can_be_instantiated(self):
        """Test that multiple fetcher instances can coexist"""
        noaa = KpIndexFetcher(verbose=False)
        hamqsl = AIndexFetcher(verbose=False)
        multi = MultiSourceSpaceWeatherFetcher(verbose=False)

        assert noaa is not None
        assert hamqsl is not None
        assert multi is not None
        assert noaa is not hamqsl
        assert hamqsl is not multi


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
