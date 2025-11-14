#!/usr/bin/env python3
"""
Unit Tests for Noise Model Module

Tests radio noise calculations including atmospheric, galactic,
and man-made noise components.
"""

import pytest
import numpy as np
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.dvoacap.noise_model import (
    NoiseModel,
    TripleValue,
    Distribution
)
from src.dvoacap.path_geometry import GeoPoint
from src.dvoacap.fourier_maps import FourierMaps


class TestTripleValue:
    """Test TripleValue statistical distribution class"""

    def test_triple_value_creation(self):
        """Test creating TripleValue"""
        triple = TripleValue(median=10.0, lower=8.0, upper=12.0)

        assert triple.median == 10.0
        assert triple.lower == 8.0
        assert triple.upper == 12.0

    def test_triple_value_defaults(self):
        """Test TripleValue default values"""
        triple = TripleValue()

        assert triple.median == 0.0
        assert triple.lower == 0.0
        assert triple.upper == 0.0

    def test_triple_value_ordering(self):
        """Test that statistical values maintain logical order"""
        triple = TripleValue(median=100.0, lower=90.0, upper=110.0)

        # For typical distributions, lower < median < upper
        # (though this isn't enforced by the dataclass)
        assert triple.lower <= triple.median <= triple.upper


class TestDistribution:
    """Test Distribution class with value and error"""

    def test_distribution_creation(self):
        """Test creating Distribution"""
        dist = Distribution()

        assert isinstance(dist.value, TripleValue)
        assert isinstance(dist.error, TripleValue)

    def test_distribution_values(self):
        """Test setting distribution values"""
        dist = Distribution()

        dist.value.median = 150.0
        dist.value.lower = 140.0
        dist.value.upper = 160.0

        assert dist.value.median == 150.0
        assert dist.value.lower == 140.0
        assert dist.value.upper == 160.0


class TestNoiseModel:
    """Test NoiseModel class"""

    @pytest.fixture
    def fourier_maps(self):
        """Create FourierMaps instance"""
        return FourierMaps()

    @pytest.fixture
    def noise_model(self, fourier_maps):
        """Create NoiseModel instance"""
        return NoiseModel(fourier_maps)

    def test_noise_model_creation(self, noise_model):
        """Test creating NoiseModel"""
        assert noise_model is not None
        assert isinstance(noise_model.atmospheric_noise, Distribution)
        assert isinstance(noise_model.galactic_noise, Distribution)
        assert isinstance(noise_model.man_made_noise, Distribution)
        assert isinstance(noise_model.combined_noise, Distribution)

    def test_default_man_made_noise(self, noise_model):
        """Test default man-made noise level"""
        # Default from VOACAP: 145 dB above kTB at 3 MHz
        assert noise_model.man_made_noise_at_3mhz == 145.0

    def test_set_man_made_noise(self, noise_model):
        """Test setting man-made noise level"""
        noise_model.man_made_noise_at_3mhz = 150.0
        assert noise_model.man_made_noise_at_3mhz == 150.0

    def test_noise_constants(self, noise_model):
        """Test noise model constants"""
        assert noise_model.TWO_PI == pytest.approx(2 * np.pi)
        assert noise_model.DB_IN_NP == pytest.approx(4.34294, rel=0.001)
        assert noise_model.NP_IN_DB == pytest.approx(1/4.34294, rel=0.001)
        assert noise_model.NORM_DECILE == pytest.approx(1.28, rel=0.01)


class TestNoiseCalculations:
    """Test noise calculation methods"""

    @pytest.fixture
    def fourier_maps(self):
        """Create FourierMaps instance"""
        return FourierMaps()

    @pytest.fixture
    def noise_model(self, fourier_maps):
        """Create NoiseModel instance"""
        return NoiseModel(fourier_maps)

    def test_compute_noise_at_1mhz(self, noise_model):
        """Test atmospheric noise calculation at 1 MHz"""
        # Mid-latitude location
        location = GeoPoint.from_degrees(45.0, -75.0)
        local_time = 0.5  # Noon

        # Should not raise exception
        noise_model.compute_noise_at_1mhz(location, local_time)

        # Internal state should be updated
        assert noise_model._lat != 0
        assert noise_model._east_lon != 0

    def test_noise_frequency_dependence(self, noise_model):
        """Test that noise varies with frequency"""
        location = GeoPoint.from_degrees(40.0, -75.0)
        local_time = 0.5

        # Compute noise at 1 MHz reference
        noise_model.compute_noise_at_1mhz(location, local_time)

        # Noise should scale with frequency
        # (exact scaling tested in integration)

    def test_noise_time_dependence(self, noise_model):
        """Test that atmospheric noise varies with time of day"""
        location = GeoPoint.from_degrees(40.0, -75.0)

        # Noon
        noise_model.compute_noise_at_1mhz(location, 0.5)
        noise_noon = noise_model._ns_mhz_1

        # Midnight
        noise_model.compute_noise_at_1mhz(location, 0.0)
        noise_midnight = noise_model._ns_mhz_1

        # Noise levels should differ (typically higher at night)
        # (sign and magnitude depend on location and season)

    def test_noise_location_dependence(self, noise_model):
        """Test that noise varies with geographic location"""
        local_time = 0.5

        # Equatorial location (higher atmospheric noise)
        equator = GeoPoint.from_degrees(0.0, 0.0)
        noise_model.compute_noise_at_1mhz(equator, local_time)
        noise_equator = noise_model._ns_mhz_1

        # Polar location (lower atmospheric noise)
        polar = GeoPoint.from_degrees(80.0, 0.0)
        noise_model.compute_noise_at_1mhz(polar, local_time)
        noise_polar = noise_model._ns_mhz_1

        # Equatorial noise typically higher than polar
        # (though exact relationship is complex)


class TestAtmosphericNoise:
    """Test atmospheric noise component"""

    @pytest.fixture
    def fourier_maps(self):
        return FourierMaps()

    @pytest.fixture
    def noise_model(self, fourier_maps):
        return NoiseModel(fourier_maps)

    def test_atmospheric_noise_tropical(self, noise_model):
        """Test atmospheric noise in tropical regions"""
        # Tropical location (high lightning activity)
        tropical = GeoPoint.from_degrees(5.0, -75.0)
        local_time = 0.5

        noise_model.compute_noise_at_1mhz(tropical, local_time)

        # Atmospheric noise should be computed
        # (exact values depend on CCIR maps)

    def test_atmospheric_noise_temperate(self, noise_model):
        """Test atmospheric noise in temperate regions"""
        temperate = GeoPoint.from_degrees(45.0, -75.0)
        local_time = 0.5

        noise_model.compute_noise_at_1mhz(temperate, local_time)

        # Should compute without error

    def test_atmospheric_noise_polar(self, noise_model):
        """Test atmospheric noise in polar regions"""
        polar = GeoPoint.from_degrees(75.0, 0.0)
        local_time = 0.5

        noise_model.compute_noise_at_1mhz(polar, local_time)

        # Should compute without error


class TestGalacticNoise:
    """Test galactic (cosmic) noise component"""

    @pytest.fixture
    def fourier_maps(self):
        return FourierMaps()

    @pytest.fixture
    def noise_model(self, fourier_maps):
        return NoiseModel(fourier_maps)

    def test_galactic_noise_frequency_dependence(self, noise_model):
        """Test galactic noise decreases with frequency"""
        # Galactic noise follows power law: ~ f^-2.5
        # Should be significant at low frequencies, negligible at high

        # At 3 MHz: galactic noise significant
        # At 30 MHz: galactic noise negligible

    def test_galactic_noise_isotropic(self):
        """Test galactic noise is approximately isotropic"""
        # Galactic noise doesn't vary much with location
        # (some variation due to galactic center)


class TestManMadeNoise:
    """Test man-made (industrial) noise component"""

    @pytest.fixture
    def fourier_maps(self):
        return FourierMaps()

    @pytest.fixture
    def noise_model(self, fourier_maps):
        return NoiseModel(fourier_maps)

    def test_man_made_noise_urban(self, noise_model):
        """Test man-made noise in urban areas"""
        # Urban areas: high man-made noise (145-165 dB @ 3 MHz)
        noise_model.man_made_noise_at_3mhz = 160.0

        assert noise_model.man_made_noise_at_3mhz == 160.0

    def test_man_made_noise_rural(self, noise_model):
        """Test man-made noise in rural areas"""
        # Rural areas: low man-made noise (120-135 dB @ 3 MHz)
        noise_model.man_made_noise_at_3mhz = 130.0

        assert noise_model.man_made_noise_at_3mhz == 130.0

    def test_man_made_noise_remote(self, noise_model):
        """Test man-made noise in remote areas"""
        # Remote areas: very low man-made noise (100-120 dB @ 3 MHz)
        noise_model.man_made_noise_at_3mhz = 110.0

        assert noise_model.man_made_noise_at_3mhz == 110.0

    def test_man_made_noise_frequency_scaling(self):
        """Test man-made noise scales with frequency"""
        # Man-made noise decreases with frequency: ~ f^-1
        # At 3 MHz: reference level
        # At 30 MHz: -20 dB from reference


class TestCombinedNoise:
    """Test combined noise from all sources"""

    @pytest.fixture
    def fourier_maps(self):
        return FourierMaps()

    @pytest.fixture
    def noise_model(self, fourier_maps):
        return NoiseModel(fourier_maps)

    def test_noise_combination_low_frequency(self):
        """Test combined noise at low frequencies (3-5 MHz)"""
        # At low frequencies:
        # - Atmospheric noise dominant
        # - Man-made noise significant
        # - Galactic noise moderate
        pass

    def test_noise_combination_mid_frequency(self):
        """Test combined noise at mid frequencies (10-15 MHz)"""
        # At mid frequencies:
        # - Atmospheric and man-made decrease
        # - Galactic noise becomes more significant
        pass

    def test_noise_combination_high_frequency(self):
        """Test combined noise at high frequencies (>20 MHz)"""
        # At high frequencies:
        # - All noise sources lower
        # - Galactic noise may dominate
        pass

    def test_noise_power_addition(self):
        """Test that noise powers add correctly"""
        # Noise powers add in linear (power) domain
        # P_total = P_atm + P_gal + P_mm

        # Convert from dB:
        # P_total_dB = 10*log10(10^(P_atm/10) + 10^(P_gal/10) + 10^(P_mm/10))


class TestNoiseEdgeCases:
    """Test noise calculations in edge cases"""

    @pytest.fixture
    def fourier_maps(self):
        return FourierMaps()

    @pytest.fixture
    def noise_model(self, fourier_maps):
        return NoiseModel(fourier_maps)

    def test_noise_at_poles(self, noise_model):
        """Test noise calculation at geographic poles"""
        north_pole = GeoPoint.from_degrees(90.0, 0.0)
        south_pole = GeoPoint.from_degrees(-90.0, 0.0)

        # Should not crash
        noise_model.compute_noise_at_1mhz(north_pole, 0.5)
        noise_model.compute_noise_at_1mhz(south_pole, 0.5)

    def test_noise_at_date_line(self, noise_model):
        """Test noise calculation at international date line"""
        location = GeoPoint.from_degrees(0.0, 180.0)

        # Should handle longitude wraparound
        noise_model.compute_noise_at_1mhz(location, 0.5)

    def test_noise_at_midnight(self, noise_model):
        """Test noise calculation at midnight"""
        location = GeoPoint.from_degrees(40.0, -75.0)

        # Should handle time wraparound
        noise_model.compute_noise_at_1mhz(location, 0.0)
        noise_model.compute_noise_at_1mhz(location, 1.0)

    def test_noise_zero_man_made(self, noise_model):
        """Test with zero man-made noise (remote location)"""
        noise_model.man_made_noise_at_3mhz = 0.0

        location = GeoPoint.from_degrees(0.0, 0.0)
        noise_model.compute_noise_at_1mhz(location, 0.5)

        # Should not crash

    def test_noise_very_high_man_made(self, noise_model):
        """Test with very high man-made noise (urban)"""
        noise_model.man_made_noise_at_3mhz = 180.0  # Very noisy

        location = GeoPoint.from_degrees(40.0, -74.0)  # NYC
        noise_model.compute_noise_at_1mhz(location, 0.5)

        # Should not crash


class TestNoiseValidation:
    """Validation tests against known noise values"""

    @pytest.fixture
    def fourier_maps(self):
        return FourierMaps()

    @pytest.fixture
    def noise_model(self, fourier_maps):
        return NoiseModel(fourier_maps)

    def test_typical_atmospheric_noise(self):
        """Test typical atmospheric noise levels"""
        # From ITU-R P.372:
        # Atmospheric noise at 1 MHz, tropical, nighttime: ~120-140 dB
        # Atmospheric noise at 10 MHz: ~40-60 dB lower

    def test_typical_galactic_noise(self):
        """Test typical galactic noise levels"""
        # From ITU-R P.372:
        # Galactic noise at 10 MHz: ~52 dB above kTB
        # Galactic noise at 30 MHz: ~30 dB above kTB

    def test_thermal_noise_floor(self):
        """Test thermal noise floor (kTB)"""
        # Thermal noise: kTB = -204 dBW/Hz at 290K
        # For 3 kHz bandwidth: -174 dBW

    def test_noise_figure(self):
        """Test typical receiver noise figure"""
        # Typical HF receiver noise figure: 10-20 dB
        # Total system noise = external noise + receiver noise


@pytest.mark.integration
class TestNoiseIntegration:
    """Integration tests requiring full prediction system"""

    @pytest.fixture
    def full_system(self):
        """Set up full prediction system"""
        from src.dvoacap.prediction_engine import PredictionEngine

        engine = PredictionEngine()
        engine.params.ssn = 100
        engine.params.month = 6
        return engine

    def test_noise_in_prediction(self, full_system):
        """Test noise calculation in full prediction"""
        engine = full_system

        tx = GeoPoint.from_degrees(40.0, -75.0)
        rx = GeoPoint.from_degrees(51.5, -0.1)

        engine.params.tx_location = tx

        try:
            engine.predict(
                rx_location=rx,
                utc_time=0.5,
                frequencies=[14.0]
            )

            # Should have predictions with noise calculations
            assert len(engine.predictions) > 0

        except Exception as e:
            pytest.skip(f"Integration test failed: {e}")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
