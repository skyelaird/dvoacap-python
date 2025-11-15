"""
DVOACAP Noise Model - Phase 5

This module implements radio noise modeling for HF propagation predictions,
including atmospheric, galactic, and man-made noise sources.

Based on ITU-R P.372 noise models and VOACAP's NoiseMdl.pas implementation.

Author: Ported from VOACAP Pascal source (VE3NEA)
"""

import numpy as np
from dataclasses import dataclass

from .path_geometry import GeoPoint
from .fourier_maps import FourierMaps, FixedMapKind


@dataclass
class TripleValue:
    """Statistical distribution with median and deciles."""
    median: float = 0.0
    lower: float = 0.0  # Lower decile (10%)
    upper: float = 0.0  # Upper decile (90%)


@dataclass
class Distribution:
    """Complete statistical distribution with values and errors."""
    value: TripleValue
    error: TripleValue

    def __init__(self):
        self.value = TripleValue()
        self.error = TripleValue()


class NoiseModel:
    """
    Radio noise model implementing atmospheric, galactic, and man-made noise calculations.

    The model computes noise power distributions as a function of frequency, location,
    and time of day, following ITU recommendations.

    Attributes:
        man_made_noise_at_3mhz: Man-made noise level at 3 MHz (dB above kTB)
        atmospheric_noise: Atmospheric noise distribution
        galactic_noise: Galactic (cosmic) noise distribution
        man_made_noise: Man-made (industrial) noise distribution
        combined_noise: Combined noise from all sources
    """

    # Constants from VoaTypes
    TWO_PI = 2 * np.pi
    DB_IN_NP = 4.34294  # dB's in Neper, 10/Ln(10)
    NP_IN_DB = 1 / DB_IN_NP  # Nepers in dB
    NORM_DECILE = 1.28  # Normal distribution 10% point

    def __init__(self, fourier_maps: FourierMaps):
        """
        Initialize the noise model.

        Args:
            fourier_maps: FourierMaps instance for accessing coefficient data
        """
        self.fourier_maps = fourier_maps

        # Input parameter - default value from VOACAP
        self.man_made_noise_at_3mhz = 145.0  # dB above kTB

        # Output distributions
        self.atmospheric_noise = Distribution()
        self.galactic_noise = Distribution()
        self.man_made_noise = Distribution()
        self.combined_noise = Distribution()

        # Internal state for 1MHz noise computation
        self._lat = 0.0
        self._east_lon = 0.0
        self._t1 = 0
        self._t2 = 0
        self._dt = 0.0
        self._ns_mhz_1 = 0.0
        self._ns_mhz_2 = 0.0

    def compute_noise_at_1mhz(self, location: GeoPoint, local_time: float) -> None:
        """
        Prepare 1MHz noise coefficients for use in compute_distribution.

        This method computes and caches the atmospheric noise parameters at 1 MHz,
        which are then scaled for other frequencies in compute_distribution().

        Args:
            location: Geographic location (lat/lon in radians)
            local_time: Local time as fraction of day (0.0 to 1.0)
        """
        # Convert local time from fraction to hours
        local_time_hours = 24.0 * local_time

        # East longitude, 0..2*Pi
        if location.lon >= 0:
            self._east_lon = location.lon
        else:
            self._east_lon = self.TWO_PI + location.lon

        self._lat = location.lat

        # Noise map selection (fmNoise1..fmNoise6)
        # Maps correspond to 4-hour time blocks: 0-4, 4-8, 8-12, 12-16, 16-20, 20-24 UTC
        if local_time_hours < 22:
            self._t1 = int(local_time_hours / 4)
        else:
            self._t1 = 5  # fmNoise6 (index 5 for 0-based)

        # Interpolation factor between time blocks
        self._dt = (local_time_hours - (4 * self._t1 + 2)) * 0.25

        # Select adjacent time block for interpolation
        if self._dt < 0:
            self._t2 = self._t1 - 1
        elif self._dt > 0:
            self._t2 = self._t1 + 1
        else:
            self._t2 = self._t1

        # Wrap around time indices (0-5 for six 4-hour blocks)
        if self._t2 < 0:
            self._t2 = 5
        elif self._t2 > 5:
            self._t2 = 0

        # Get 1-MHz noise from Fourier maps
        # Noise maps are indexed from NOISE1 (0) to NOISE6 (5)
        self._ns_mhz_1 = self.fourier_maps.compute_fixed_map(
            FixedMapKind.NOISE1 + self._t1, self._lat, self._east_lon
        )
        self._ns_mhz_2 = self.fourier_maps.compute_fixed_map(
            FixedMapKind.NOISE1 + self._t2, self._lat, self._east_lon
        )

    def compute_distribution(self, frequency: float, fof2: float) -> None:
        """
        Compute noise probability density functions for a specific frequency.

        This method calculates atmospheric, galactic, and man-made noise distributions,
        then combines them into a total noise distribution with median and decile values.

        Args:
            frequency: Operating frequency in MHz
            fof2: F2 layer critical frequency in MHz (for galactic noise penetration)
        """
        # FREQUENCY DEPENDENT ATMOSPHERIC NOISE
        d1 = self._compute_noise_at_freq(self._t1, frequency, self._ns_mhz_1)
        d2 = self._compute_noise_at_freq(self._t2, frequency, self._ns_mhz_2)
        self.atmospheric_noise = self._interpolate_distribution(d1, d2, abs(self._dt))
        av_atm = self._calc_av(self.atmospheric_noise)

        # GALACTIC NOISE
        # Default distribution values
        self.galactic_noise.value = TripleValue(median=0.0, lower=2.0, upper=2.0)
        self.galactic_noise.error = TripleValue(median=0.5, lower=0.2, upper=0.2)

        if frequency > fof2:
            # Galactic noise penetrates when f > foF2
            self.galactic_noise.value.median = 52.0 - 23.0 * np.log10(frequency)
            av_gal = self._calc_av(self.galactic_noise)
        else:
            # Galactic noise does not penetrate - ignore
            self.galactic_noise.value.median = 0.0
            av_gal = {'AU': 0.0, 'VU': 0.0, 'AL': 0.0, 'VL': 0.0}

        # MAN MADE NOISE
        # Default distribution values
        self.man_made_noise.value = TripleValue(median=0.0, lower=6.0, upper=9.7)
        self.man_made_noise.error = TripleValue(median=5.4, lower=1.5, upper=1.5)

        self.man_made_noise.value.median = (
            204.0 - self.man_made_noise_at_3mhz + 13.22 - 27.7 * np.log10(frequency)
        )
        av_man = self._calc_av(self.man_made_noise)

        # COMBINED AVERAGE AND VARIANCE
        av_sum_au = av_atm['AU'] + av_gal['AU'] + av_man['AU']
        av_sum_vu = av_atm['VU'] + av_gal['VU'] + av_man['VU']
        av_sum_al = av_atm['AL'] + av_gal['AL'] + av_man['AL']
        av_sum_vl = av_atm['VL'] + av_gal['VL'] + av_man['VL']

        # SWITCH TO DB RELATIVE TO 1 WATT
        self.atmospheric_noise.value.median -= 204.0
        self.galactic_noise.value.median -= 204.0
        self.man_made_noise.value.median -= 204.0

        # DETERMINATION OF NOISE LEVEL (ITS-78)
        self.combined_noise.value.median = self._to_db(
            self._from_db(self.atmospheric_noise.value.median) +
            self._from_db(self.galactic_noise.value.median) +
            self._from_db(self.man_made_noise.value.median)
        )

        # SPAULDING'S ORIGINAL FORMULA
        sig_hi = np.log(1.0 + av_sum_vu / (av_sum_au ** 2)) if av_sum_au > 0 else 0.0
        sig_lo = np.log(1.0 + av_sum_vl / (av_sum_al ** 2)) if av_sum_al > 0 else 0.0

        # CARUANA'S MODIFICATION
        # See http://www.greg-hand.com/noise/itu_submission.doc
        if (self.atmospheric_noise.value.upper > 12) or (self.atmospheric_noise.value.lower > 12):
            sig = 2.0 * (np.log(av_sum_au) - (self.combined_noise.value.median + 204.0) * self.NP_IN_DB)
            if sig > 0:
                sig_hi = min(sig, sig_hi)

            sig = 2.0 * (np.log(av_sum_al) - (self.combined_noise.value.median + 204.0) * self.NP_IN_DB)
            if sig > 0:
                sig_lo = min(sig, sig_lo)

        self.combined_noise.value.median = (
            self.DB_IN_NP * (np.log(av_sum_au) - sig_hi / 2.0) - 204.0
        )

        # UPPER AND LOWER DECILES
        cfac = 5.56765  # = DB_IN_NP * NORM_DECILE
        self.combined_noise.value.upper = cfac * np.sqrt(sig_hi)
        self.combined_noise.value.lower = cfac * np.sqrt(sig_lo)

        # PREDICTION ERRORS
        qp_atm = self._from_db(
            self.atmospheric_noise.value.median - self.combined_noise.value.median
        )
        qp_gal = self._from_db(
            self.galactic_noise.value.median - self.combined_noise.value.median
        ) if frequency > fof2 else 0.0
        qp_man = self._from_db(
            self.man_made_noise.value.median - self.combined_noise.value.median
        )

        self.combined_noise.error.median = np.sqrt(
            (qp_atm * self.atmospheric_noise.error.median) ** 2 +
            (qp_gal * self.galactic_noise.error.median) ** 2 +
            (qp_man * self.man_made_noise.error.median) ** 2
        )

        # Upper decile error
        pv = qp_atm * self._from_db(
            self.atmospheric_noise.value.upper - self.combined_noise.value.upper
        )
        self.combined_noise.error.upper = (
            (pv * self.atmospheric_noise.error.upper) ** 2 +
            ((pv - qp_atm) * self.atmospheric_noise.error.median) ** 2
        )

        pv = qp_gal * self._from_db(
            self.galactic_noise.value.upper - self.combined_noise.value.upper
        )
        self.combined_noise.error.upper += (
            (pv * self.galactic_noise.error.upper) ** 2 +
            ((pv - qp_gal) * self.galactic_noise.error.median) ** 2
        )

        pv = qp_man * self._from_db(
            self.man_made_noise.value.upper - self.combined_noise.value.upper
        )
        self.combined_noise.error.upper = np.sqrt(
            self.combined_noise.error.upper +
            (pv * self.man_made_noise.error.upper) ** 2 +
            ((pv - qp_man) * self.man_made_noise.error.median) ** 2
        )

        # Lower decile error
        pv = qp_atm * self._from_db(
            self.atmospheric_noise.value.lower - self.combined_noise.value.lower
        )
        self.combined_noise.error.lower = (
            (pv * self.atmospheric_noise.error.lower) ** 2 +
            ((pv - qp_atm) * self.atmospheric_noise.error.median) ** 2
        )

        pv = qp_gal * self._from_db(
            self.galactic_noise.value.lower - self.combined_noise.value.lower
        )
        self.combined_noise.error.lower += (
            (pv * self.galactic_noise.error.lower) ** 2 +
            ((pv - qp_gal) * self.galactic_noise.error.median) ** 2
        )

        pv = qp_man * self._from_db(
            self.man_made_noise.value.lower - self.combined_noise.value.lower
        )
        self.combined_noise.error.lower = np.sqrt(
            self.combined_noise.error.lower +
            (pv * self.man_made_noise.error.lower) ** 2 +
            ((pv - qp_man) * self.man_made_noise.error.median) ** 2
        )

    @property
    def combined(self) -> float:
        """Get median combined noise level in dB."""
        return self.combined_noise.value.median

    def _compute_noise_at_freq(
        self, idx: int, frequency: float, noise_1mhz: float
    ) -> Distribution:
        """
        Compute noise at a specific frequency using Fourier coefficients.

        Args:
            idx: Time block index (0-5)
            frequency: Frequency in MHz
            noise_1mhz: Noise level at 1 MHz

        Returns:
            Distribution of noise at the specified frequency
        """
        result = Distribution()

        # Adjust index for southern hemisphere
        if self._lat < 0:
            idx += 6

        # Compute median noise
        pz = self.fourier_maps.compute_fam(idx, 0, -0.75)
        px = self.fourier_maps.compute_fam(idx, 1, -0.75)
        result.value.median = noise_1mhz * (2.0 - pz) - px

        x = (8.0 * (2.0 ** np.log10(frequency)) - 11.0) / 4.0
        pz = self.fourier_maps.compute_fam(idx, 0, x)
        px = self.fourier_maps.compute_fam(idx, 1, x)
        result.value.median = result.value.median * pz + px

        # Compute deciles and errors
        x = np.log10(min(20.0, frequency))
        result.value.upper = self.fourier_maps.compute_dud(0, idx, x)
        result.value.lower = self.fourier_maps.compute_dud(1, idx, x)
        result.error.upper = self.fourier_maps.compute_dud(2, idx, x)
        result.error.lower = self.fourier_maps.compute_dud(3, idx, x)
        result.error.median = self.fourier_maps.compute_dud(4, idx, min(1.0, x))

        return result

    def _interpolate_distribution(
        self, d1: Distribution, d2: Distribution, ratio: float
    ) -> Distribution:
        """
        Linearly interpolate between two distributions.

        Args:
            d1: First distribution
            d2: Second distribution
            ratio: Interpolation ratio (0.0 to 1.0)

        Returns:
            Interpolated distribution
        """
        result = Distribution()

        result.value.median = d1.value.median * (1 - ratio) + d2.value.median * ratio
        result.value.lower = d1.value.lower * (1 - ratio) + d2.value.lower * ratio
        result.value.upper = d1.value.upper * (1 - ratio) + d2.value.upper * ratio

        result.error.median = d1.error.median * (1 - ratio) + d2.error.median * ratio
        result.error.lower = d1.error.lower * (1 - ratio) + d2.error.lower * ratio
        result.error.upper = d1.error.upper * (1 - ratio) + d2.error.upper * ratio

        return result

    def _calc_av(self, dist: Distribution) -> dict:
        """
        Calculate noise factor distribution (average and variance).

        Args:
            dist: Input distribution

        Returns:
            Dictionary with AU, VU, AL, VL values
        """
        DFAC = 7.87384
        BFAC = 30.99872

        au = np.exp((dist.value.upper / DFAC) ** 2 + dist.value.median * self.NP_IN_DB)
        vu = (au ** 2) * (np.exp((dist.value.upper ** 2) / BFAC) - 1.0)

        al = np.exp((dist.value.lower / DFAC) ** 2 + dist.value.median * self.NP_IN_DB)
        vl = (al ** 2) * (np.exp((dist.value.lower ** 2) / BFAC) - 1.0)

        return {'AU': au, 'VU': vu, 'AL': al, 'VL': vl}

    @staticmethod
    def _to_db(power: float) -> float:
        """Convert power ratio to dB."""
        return 10.0 * np.log10(max(1e-30, power))

    @staticmethod
    def _from_db(db: float) -> float:
        """Convert dB to power ratio."""
        return 10.0 ** (db / 10.0)
