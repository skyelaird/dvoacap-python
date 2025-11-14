"""
DVOACAP Prediction Engine - Phase 5

This module implements the complete HF radio propagation prediction engine,
integrating all phases (1-5) to compute signal strength, reliability, and
system performance metrics.

Based on VOACAP's VoaCapEng.pas implementation.

Author: Ported from VOACAP Pascal source (VE3NEA)
"""

import numpy as np
from typing import List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from .path_geometry import PathGeometry, GeoPoint
from .geomagnetic import GeomagneticField
from .solar import compute_zenith_angle, compute_local_time
from .fourier_maps import FourierMaps, FixedMapKind
from .ionospheric_profile import IonosphericProfile, LayerInfo
from .layer_parameters import compute_iono_params, ControlPoint, GeographicPoint
from .muf_calculator import CircuitMuf, MufCalculator, MufInfo, calc_muf_prob, select_profile
from .reflectrix import Reflectrix, Reflection
from .noise_model import NoiseModel, TripleValue
from .antenna_gain import AntennaFarm, IsotropicAntenna


class IonosphericLayer(Enum):
    """Ionospheric layer types."""
    E = 0
    F1 = 1
    F2 = 2


class PredictionMethod(Enum):
    """Method used for prediction."""
    SHORT = "short"  # Short path model (< 7000 km)
    LONG = "long"    # Long path model (> 10000 km)
    SMOOTH = "smooth"  # Smoothed combination (7000-10000 km)


@dataclass
class SignalInfo:
    """Complete signal information for a propagation mode."""
    delay_ms: float = 0.0          # Time delay in milliseconds
    tx_gain_db: float = 0.0        # Transmit antenna gain (dBi)
    rx_gain_db: float = 0.0        # Receive antenna gain (dBi)
    muf_day: float = 0.0           # MUF probability for this mode
    total_loss_db: float = 0.0     # Total path loss (dB)
    power10: float = 0.0           # Lower decile signal power (dB)
    power90: float = 0.0           # Upper decile signal power (dB)
    field_dbuv: float = 0.0        # Field strength (dB above 1 µV/m)
    power_dbw: float = 0.0         # Received signal power (dBW)
    snr_db: float = 0.0            # Signal-to-noise ratio (dB)
    snr10: float = 0.0             # Lower decile SNR (dB)
    snr90: float = 0.0             # Upper decile SNR (dB)
    reliability: float = 0.0       # Circuit reliability (0-1)


@dataclass
class ModeInfo:
    """Information about a single propagation mode."""
    reflection: Reflection = field(default_factory=Reflection)
    signal: SignalInfo = field(default_factory=SignalInfo)
    hop_distance: float = 0.0      # Distance per hop (radians)
    hop_count: int = 0             # Number of hops
    layer: IonosphericLayer = IonosphericLayer.F2
    free_space_loss: float = 0.0   # Free space loss (dB)
    absorption_loss: float = 0.0   # D-layer absorption (dB per hop)
    obscuration: float = 0.0       # Sporadic E obscuration (dB)
    deviation_term: float = 0.0    # High-angle ray deviation (dB)
    ground_loss: float = 0.0       # Ground reflection loss (dB per hop)


@dataclass
class Prediction:
    """Complete propagation prediction for one frequency."""
    # Method and mode
    method: PredictionMethod = PredictionMethod.SHORT
    mode_tx: IonosphericLayer = IonosphericLayer.F2
    mode_rx: IonosphericLayer = IonosphericLayer.F2
    hop_count: int = 0

    # Path parameters
    tx_elevation: float = 0.0      # Transmit elevation angle (radians)
    rx_elevation: float = 0.0      # Receive elevation angle (radians)
    virt_height: float = 0.0       # Virtual height (km)

    # Signal
    signal: SignalInfo = field(default_factory=SignalInfo)

    # Performance metrics
    noise_dbw: float = 0.0         # Noise power (dBW)
    required_power: float = 0.0    # Power for required reliability (dB)
    multipath_prob: float = 0.0    # Multipath probability (0-1)
    service_prob: float = 0.0      # Service probability (0-1)
    snr_xx: float = 0.0            # SNR at required reliability

    def get_mode_name(self, distance_rad: float) -> str:
        """Get mode name string (e.g., '2F2', 'F2F1')."""
        # mode_tx/mode_rx can be either enum or string
        tx_name = self.mode_tx.name if hasattr(self.mode_tx, 'name') else str(self.mode_tx)
        rx_name = self.mode_rx.name if hasattr(self.mode_rx, 'name') else str(self.mode_rx)

        if distance_rad < 7000.0 / 6370.0:  # < 7000 km
            return f"{self.hop_count}{tx_name}"
        else:
            return f"{tx_name}{rx_name}"


@dataclass
class VoacapParams:
    """VOACAP input parameters."""
    ssn: float = 100.0                      # Sunspot number
    month: int = 1                          # Month (1-12)
    tx_location: GeoPoint = field(default_factory=lambda: GeoPoint(lat=0.0, lon=0.0))
    tx_power: float = 1500.0                # Transmit power (watts)
    min_angle: float = np.deg2rad(3.0)      # Minimum takeoff angle (radians)
    man_made_noise_at_3mhz: float = 145.0   # Man-made noise at 3 MHz (dB)
    long_path: bool = False                 # Use long path
    required_snr: float = 73.0              # Required SNR for reliability calc (dB)
    required_reliability: float = 0.9       # Required circuit reliability (0-1)
    multipath_power_tolerance: float = 3.0  # Multipath power tolerance (dB)
    max_tolerable_delay: float = 0.1        # Max tolerable delay (ms)


class PredictionEngine:
    """
    Complete VOACAP prediction engine.

    Integrates all phases to compute HF radio propagation predictions including
    signal strength, reliability, and system performance metrics.

    Example:
        >>> engine = PredictionEngine()
        >>> engine.params.tx_location = GeoPoint(lat=40.0*np.pi/180, lon=-75.0*np.pi/180)
        >>> rx_location = GeoPoint(lat=51.5*np.pi/180, lon=-0.1*np.pi/180)
        >>> engine.predict(rx_location, utc_time=0.5, frequencies=[7.0, 14.0, 21.0])
        >>> for freq, pred in zip(engine.frequencies, engine.predictions):
        ...     print(f"{freq} MHz: SNR={pred.signal.snr_db:.1f} dB")
    """

    # Physical constants
    EARTH_RADIUS = 6370.0  # km
    VELOCITY_OF_LIGHT = 299.79246  # Mm/s
    DB_IN_NP = 4.34294  # dB per Neper
    NP_IN_DB = 1.0 / DB_IN_NP
    NORM_DECILE = 1.28  # Normal distribution 10% point

    # Distance thresholds (radians)
    RAD_1000_KM = 1000.0 / EARTH_RADIUS
    RAD_2000_KM = 2000.0 / EARTH_RADIUS
    RAD_2000_KM_01 = 2000.01 / EARTH_RADIUS
    RAD_2500_KM = 2500.0 / EARTH_RADIUS
    RAD_4000_KM = 4000.0 / EARTH_RADIUS
    RAD_7000_KM = 7000.0 / EARTH_RADIUS
    RAD_10000_KM = 10000.0 / EARTH_RADIUS

    # Constants from SIGDIS.FOR
    HTLOSS = 88.0
    XNUZ = 63.07
    HNU = 4.39

    # Normal distribution percentage points
    TME = np.array([0.0, 0.1257, 0.2533, 0.3853, 0.5244, 0.6745,
                    0.8416, 1.0364, 1.2815, 1.6449])

    # Angle count lookup table
    NANGX = np.array([40, 34, 29, 24, 19, 14, 12, 9])

    def __init__(self):
        """Initialize prediction engine."""
        # Parameters
        self.params = VoacapParams()

        # Core modules
        self.path = PathGeometry()
        self.magnetic_field = GeomagneticField()
        self.fourier_maps = FourierMaps()
        self.noise_model = NoiseModel(self.fourier_maps)
        self.muf_calculator = MufCalculator(self.path, self.fourier_maps)

        # Antennas
        self.tx_antennas = AntennaFarm()
        self.rx_antennas = AntennaFarm()

        # Input/output
        self.rx_location = GeoPoint(lat=0.0, lon=0.0)
        self.utc_time = 0.0
        self.frequencies: List[float] = []
        self.predictions: List[Prediction] = []

        # Internal state
        self._control_points: List[ControlPoint] = []
        self._profiles: List[IonosphericProfile] = []
        self._current_profile: Optional[IonosphericProfile] = None
        self.circuit_muf: Optional[CircuitMuf] = None
        self._modes: List[ModeInfo] = []
        self._avg_loss = TripleValue()
        self._best_mode: Optional[ModeInfo] = None
        self._absorption_index = 0.0
        self._adj_de_loss = 0.0
        self._adj_ccir252_a = 0.0
        self._adj_ccir252_b = 0.0
        self._adj_signal_10 = 0.0
        self._adj_signal_90 = 0.0
        self._adj_auroral = 0.0

    def predict(
        self,
        rx_location: GeoPoint,
        utc_time: float,
        frequencies: List[float]
    ):
        """
        Perform complete propagation prediction.

        Args:
            rx_location: Receiver location (lat/lon in radians)
            utc_time: UTC time as fraction of day (0.0 to 1.0)
            frequencies: List of frequencies to predict (MHz)
        """
        self.rx_location = rx_location
        self.utc_time = utc_time
        self.frequencies = frequencies.copy()

        # Initialize transmit power
        self.tx_antennas.current_antenna.tx_power_dbw = self._to_db(self.params.tx_power)
        self.muf_calculator.min_angle = self.params.min_angle

        # Allocate results array
        self.predictions = [Prediction() for _ in frequencies]

        # Compute Fourier maps for month, SSN, UTC
        self.fourier_maps.set_conditions(self.params.month, self.params.ssn, utc_time)

        # Path geometry
        self.path.long_path = self.params.long_path
        self.path.set_tx_rx(self.params.tx_location, rx_location)

        # Accept any adjustments made in path
        self.rx_location = self.path.rx
        self.params.tx_location = self.path.tx

        # Rotate antennas
        self.tx_antennas.current_antenna.azimuth = self.path.azim_tr
        self.rx_antennas.current_antenna.azimuth = self.path.azim_rt

        # Compute control points and their parameters
        self._compute_control_points()
        for ctrl_pt in self._control_points:
            self._compute_geo_params(ctrl_pt)
            compute_iono_params(ctrl_pt, self.fourier_maps)

        # Prepare noise model
        self.noise_model.man_made_noise_at_3mhz = self.params.man_made_noise_at_3mhz
        local_time = compute_local_time(utc_time, rx_location.lon)
        self.noise_model.compute_noise_at_1mhz(rx_location, local_time)

        # Create ionospheric profiles
        self._create_iono_profiles()

        # Compute circuit MUF
        self.circuit_muf = self.muf_calculator.compute_circuit_muf(self._profiles)

        # If last frequency is zero, replace with MUF
        if self.frequencies[-1] == 0:
            self.frequencies[-1] = self.circuit_muf.muf

        # Select profile for short model
        self._current_profile = self._select_profile()

        # Compute profile for short model
        angle_count = self._get_angle_count()
        self._current_profile.compute_ionogram()
        self._current_profile.compute_oblique_frequencies()
        self._current_profile.compute_derivative_loss(self.circuit_muf.muf_info)

        # Adjust signal distribution tables
        self._adjust_signal_distribution_tables()

        # Compute profiles for long model if needed
        if self.path.dist >= self.RAD_7000_KM:
            self._profiles[0].compute_ionogram()
            self._profiles[0].compute_oblique_frequencies()
            self._profiles[0].compute_derivative_loss(self.circuit_muf.muf_info)

            self._profiles[-1].compute_ionogram()
            self._profiles[-1].compute_oblique_frequencies()
            self._profiles[-1].compute_derivative_loss(self.circuit_muf.muf_info)

        # Predict for each frequency
        for f, freq in enumerate(self.frequencies):
            self.tx_antennas.select_antenna(freq)
            self.rx_antennas.select_antenna(freq)

            # Compute noise distribution
            fof2 = self._profiles[-1].f2.fo
            self.noise_model.compute_distribution(freq, fof2)

            # Create reflectrix and evaluate
            reflectrix = Reflectrix(
                min_angle=self.params.min_angle,
                freq=freq,
                profile=self._current_profile
            )

            # Evaluate short model
            prediction = self._evaluate_short_model(reflectrix, f)

            # Combine with long model if needed
            if self.path.dist >= self.RAD_7000_KM:
                long_pred = self._evaluate_long_model(freq)
                prediction = self._combine_short_and_long(prediction, long_pred)

            self.predictions[f] = prediction

    def _compute_control_points(self):
        """Compute control points along the path."""
        self._control_points = []

        def geopoint_to_geographicpoint(gp: GeoPoint) -> GeographicPoint:
            """Convert GeoPoint to GeographicPoint."""
            return GeographicPoint(latitude=gp.lat, longitude=gp.lon)

        if self.path.dist <= self.RAD_2000_KM_01:
            # One control point at midpoint
            ctrl_pt = ControlPoint()
            ctrl_pt.location = geopoint_to_geographicpoint(
                self.path.get_point_at_dist(0.5 * self.path.dist)
            )
            self._control_points.append(ctrl_pt)

        elif self.path.dist <= self.RAD_4000_KM:
            # Three control points
            for dist in [self.RAD_1000_KM, 0.5 * self.path.dist, self.path.dist - self.RAD_1000_KM]:
                ctrl_pt = ControlPoint()
                ctrl_pt.location = geopoint_to_geographicpoint(
                    self.path.get_point_at_dist(dist)
                )
                self._control_points.append(ctrl_pt)

        else:
            # Five control points
            for dist in [self.RAD_1000_KM, self.RAD_2000_KM, 0.5 * self.path.dist,
                         self.path.dist - self.RAD_2000_KM, self.path.dist - self.RAD_1000_KM]:
                ctrl_pt = ControlPoint()
                ctrl_pt.location = geopoint_to_geographicpoint(
                    self.path.get_point_at_dist(dist)
                )
                self._control_points.append(ctrl_pt)

    def _compute_geo_params(self, ctrl_pt: ControlPoint):
        """Compute geophysical parameters for a control point."""
        # East longitude (0..2π)
        if ctrl_pt.location.longitude >= 0:
            ctrl_pt.east_lon = ctrl_pt.location.longitude
        else:
            ctrl_pt.east_lon = 2 * np.pi + ctrl_pt.location.longitude

        # Magnetic field parameters
        geo_params = self.magnetic_field.compute(ctrl_pt.location)
        ctrl_pt.mag_lat = geo_params.magnetic_latitude
        ctrl_pt.mag_dip = geo_params.magnetic_dip
        ctrl_pt.gyro_freq = geo_params.gyrofrequency

        # Ground constants (land vs sea)
        landmass = self.fourier_maps.compute_fixed_map(
            FixedMapKind.LAND_MASS, ctrl_pt.location.latitude, ctrl_pt.east_lon
        )
        if landmass >= 0:
            # Land
            ctrl_pt.gnd_sig = 0.001
            ctrl_pt.gnd_eps = 4.0
        else:
            # Sea
            ctrl_pt.gnd_sig = 5.0
            ctrl_pt.gnd_eps = 80.0

        # Solar zenith angle
        ctrl_pt.zen_angle = compute_zenith_angle(
            ctrl_pt.location, self.utc_time, self.params.month
        )

        # Local time
        ctrl_pt.local_time = compute_local_time(self.utc_time, ctrl_pt.location.longitude)

    def _create_iono_profiles(self):
        """Create ionospheric profiles from control points."""
        # Clear existing profiles
        self._profiles = []

        # Number of profiles based on control points
        num_profiles = 1 + (len(self._control_points) // 2)
        self._profiles = [IonosphericProfile() for _ in range(num_profiles)]

        # Assign control point parameters to profiles
        if num_profiles == 1:
            prof = self._profiles[0]
            prof.e = self._control_points[0].e
            prof.f1 = self._control_points[0].f1
            prof.f2 = self._control_points[0].f2
            prof.latitude = self._control_points[0].location.latitude
            prof.mag_latitude = self._control_points[0].mag_lat
            prof.local_time_e = self._control_points[0].local_time
            prof.local_time_f2 = self._control_points[0].local_time
            prof.gyro_freq = self._control_points[0].gyro_freq

        elif num_profiles == 2:
            # First profile
            prof = self._profiles[0]
            prof.e = self._control_points[0].e
            prof.f1 = self._control_points[0].f1
            prof.f2 = self._control_points[1].f2
            prof.latitude = self._control_points[1].location.latitude
            prof.mag_latitude = self._control_points[0].mag_lat
            prof.local_time_e = self._control_points[0].local_time
            prof.local_time_f2 = self._control_points[1].local_time
            prof.gyro_freq = self._control_points[0].gyro_freq

            # Second profile
            prof = self._profiles[1]
            prof.e = self._control_points[2].e
            prof.f1 = self._control_points[2].f1
            prof.f2 = self._control_points[1].f2
            prof.latitude = self._control_points[1].location.latitude
            prof.mag_latitude = self._control_points[2].mag_lat
            prof.local_time_e = self._control_points[2].local_time
            prof.local_time_f2 = self._control_points[1].local_time
            prof.gyro_freq = self._control_points[2].gyro_freq

        elif num_profiles == 3:
            # Three profiles for long paths
            # Profile 0
            prof = self._profiles[0]
            prof.e = self._control_points[0].e
            prof.f1 = self._control_points[0].f1
            prof.f2 = self._control_points[1].f2
            prof.latitude = self._control_points[1].location.latitude
            prof.mag_latitude = self._control_points[0].mag_lat
            prof.local_time_e = self._control_points[0].local_time
            prof.local_time_f2 = self._control_points[1].local_time
            prof.gyro_freq = self._control_points[0].gyro_freq

            # Profile 1
            prof = self._profiles[1]
            prof.e = self._control_points[2].e
            prof.f1 = self._control_points[2].f1
            prof.f2 = self._control_points[2].f2
            prof.latitude = self._control_points[2].location.latitude
            prof.mag_latitude = self._control_points[2].mag_lat
            prof.local_time_e = self._control_points[2].local_time
            prof.local_time_f2 = self._control_points[2].local_time
            prof.gyro_freq = self._control_points[2].gyro_freq

            # Profile 2
            prof = self._profiles[2]
            prof.e = self._control_points[4].e
            prof.f1 = self._control_points[4].f1
            prof.f2 = self._control_points[3].f2
            prof.latitude = self._control_points[3].location.latitude
            prof.mag_latitude = self._control_points[4].mag_lat
            prof.local_time_e = self._control_points[4].local_time
            prof.local_time_f2 = self._control_points[3].local_time
            prof.gyro_freq = self._control_points[4].gyro_freq

        # Check consistency of ionospheric parameters
        for prof in self._profiles:
            if prof.f1.fo > 0:
                if prof.f1.fo <= (prof.e.fo + 0.2):
                    prof.f1.fo = 0.0
                elif prof.f2.fo <= (prof.f1.fo + 0.2):
                    prof.f1.fo = 0.0
                else:
                    prof.f1.hm = min(prof.f1.hm, prof.f2.hm)

            prof.f2.ym = min(prof.f2.ym, prof.f2.hm - prof.e.hm - 2.0)

    def _select_profile(self) -> IonosphericProfile:
        """Select profile for short model (middle profile)."""
        return self._profiles[len(self._profiles) // 2]

    def _get_angle_count(self) -> int:
        """Get number of elevation angles to compute."""
        idx = min(7, int(self.path.dist / self.RAD_2000_KM))
        return self.NANGX[idx]

    def _adjust_signal_distribution_tables(self):
        """Adjust signal distribution tables (SIGDIS/SYSSY)."""
        # Average over all profiles
        self._absorption_index = 0.0
        avg_foe = 0.0
        avg_mag_lat = 0.0
        avg_loss_mdn = 0.0
        avg_loss_lo = 0.0
        avg_loss_hi = 0.0

        for prof in self._profiles:
            avg_foe += prof.e.fo
            avg_mag_lat += abs(prof.mag_latitude)

            # Absorption index
            absorp_idx = max(0.1, -0.04 + np.exp(-2.937 + 0.8445 * prof.e.fo))
            self._absorption_index += absorp_idx
            prof.absorption_index = absorp_idx

            # Excessive system loss
            long_path = self.path.dist > self.RAD_2500_KM
            excessive_loss = self.fourier_maps.compute_excessive_system_loss(
                prof.mag_latitude, prof.local_time_e, long_path
            )
            prof.excessive_system_loss = excessive_loss

            avg_loss_mdn += excessive_loss.median
            avg_loss_lo += excessive_loss.lo
            avg_loss_hi += excessive_loss.hi

        n_prof = len(self._profiles)
        avg_foe /= n_prof
        avg_mag_lat /= n_prof
        self._absorption_index /= n_prof

        self._avg_loss.median = avg_loss_mdn / n_prof
        self._avg_loss.lower = avg_loss_lo / n_prof
        self._avg_loss.upper = avg_loss_hi / n_prof

        # D-E region loss adjustment factor
        self._adj_de_loss = (
            self._interpolate_table(90.0, self._current_profile.igram_true_height,
                                   self._current_profile.igram_vert_freq) /
            self._current_profile.e.fo
        )

        # Adjustment to CCIR 252 loss equation for E modes
        if avg_foe > 2.0:
            self._adj_ccir252_a = 1.359
            self._adj_ccir252_b = 8.617
        elif avg_foe > 0.5:
            self._adj_ccir252_a = 1.359 * (avg_foe - 0.5) / 1.5
            self._adj_ccir252_b = 8.617 * (avg_foe - 0.5) / 1.5
        else:
            self._adj_ccir252_a = 0.0
            self._adj_ccir252_b = 0.0

        # Frequency table for adjustments
        muf_f2 = self.circuit_muf.muf_info[IonosphericLayer.F2.name]
        if avg_mag_lat <= np.deg2rad(40):
            ftab = muf_f2.fot
        elif avg_mag_lat <= np.deg2rad(50):
            ftab = muf_f2.fot - (avg_mag_lat - np.deg2rad(40)) * (muf_f2.fot - 10.0) / np.deg2rad(10)
        else:
            ftab = 10.0

        # F2 over-the-MUF contribution
        from .muf_calculator import calc_muf_prob
        pf2 = max(0.1, calc_muf_prob(ftab, muf_f2.muf, muf_f2.muf,
                                     muf_f2.sig_lo, muf_f2.sig_hi))
        f2lsm = -self._to_db(pf2)

        # Residual (auroral) loss adjustment
        self._adj_auroral = max(0.0, self._avg_loss.median - f2lsm)

        # Upper decile signal level adjustment
        pf2 = max(0.1, calc_muf_prob(ftab, muf_f2.hpf, muf_f2.hpf,
                                     muf_f2.sig_lo, muf_f2.sig_hi))
        self._adj_signal_90 = max(
            0.5,
            self.NORM_DECILE * self._avg_loss.lower - self._to_db(pf2) - f2lsm
        )

        # Lower decile
        pf2 = max(0.1, calc_muf_prob(ftab, muf_f2.fot, muf_f2.fot,
                                     muf_f2.sig_lo, muf_f2.sig_hi))
        self._adj_signal_10 = max(
            1.0,
            self.NORM_DECILE * self._avg_loss.upper + self._to_db(pf2) + f2lsm
        )

    def _evaluate_short_model(self, reflectrix: Reflectrix, freq_idx: int) -> Prediction:
        """Evaluate short path model."""
        self._modes = []
        freq = self.frequencies[freq_idx]

        # Determine hop count range
        min_hops = min(
            self.circuit_muf.muf_info[IonosphericLayer.E.name].hop_count,
            self.circuit_muf.muf_info[IonosphericLayer.F2.name].hop_count
        )
        if self._current_profile.f1.fo > 0:
            min_hops = min(min_hops,
                          self.circuit_muf.muf_info[IonosphericLayer.F1.name].hop_count)

        if reflectrix.max_distance <= 0:
            # Only one over-the-MUF mode
            hops_begin = min_hops
            hops_end = min_hops
        else:
            # Up to three hops
            hops_begin = int(self.path.dist / reflectrix.max_distance) + 1
            hops_begin = max(min_hops, hops_begin)
            max_hops = int(self.path.dist / reflectrix.skip_distance)
            max_hops = max(hops_begin, max_hops)
            hops_end = min(max_hops, hops_begin + 2)
            if hops_begin > min_hops:
                hops_begin = max(min_hops, hops_end - 2)

        # Find all rays for all hop counts
        for hop_count in range(hops_begin, hops_end + 1):
            hop_dist = self.path.dist / hop_count
            reflectrix.find_modes(hop_dist, hop_count)

            # Add over-the-MUF modes if needed (e.g., freq > foF2)
            reflectrix.add_over_the_muf_and_vert_modes(hop_dist, hop_count, self.circuit_muf)

            if reflectrix.modes:
                self._modes.extend(reflectrix.modes)

        # Compute signal strength for each mode
        for mode in self._modes:
            self._compute_signal(mode, freq)

        # Analyze reliability and select best mode
        prediction = self._analyze_reliability(freq)

        # Service probability
        prediction.service_prob = self._calc_service_prob()

        # Multipath probability
        prediction.multipath_prob = self._calc_multipath_prob()

        # Short model - path is symmetric
        prediction.method = PredictionMethod.SHORT
        prediction.mode_rx = prediction.mode_tx
        prediction.rx_elevation = prediction.tx_elevation

        return prediction

    def _compute_signal(self, mode: ModeInfo, frequency: float):
        """Compute signal parameters for a mode (REGMOD)."""
        # Initialize signal info if not already present
        if mode.signal is None:
            mode.signal = SignalInfo()

        layer_name = mode.layer
        muf_info = self.circuit_muf.muf_info[layer_name]

        # Absorption parameters
        # Coefficient from VOACAP REGMOD.FOR line 57: AC = 677.2 * ACAV
        # This produces correct D-layer absorption (~100-150 dB/hop for daytime E-layer modes)
        ac = 677.2 * self._absorption_index
        bc = (frequency + self._current_profile.gyro_freq) ** 1.98
        hop_count = mode.hop_cnt
        hop_count2 = min(2, hop_count)

        # Path length
        path_length = hop_count * self._hop_length_3d(
            mode.ref.elevation,
            mode.hop_dist,
            mode.ref.virt_height
        )

        # Time delay
        mode.signal.delay_ms = path_length / self.VELOCITY_OF_LIGHT

        # Free space loss
        mode.free_space_loss = 32.45 + 2 * self._to_db(path_length * frequency)

        # Absorption loss
        if mode.ref.vert_freq <= self._current_profile.e.fo:
            # D-E mode
            if mode.ref.true_height >= self.HTLOSS:
                nsqr = 10.2
            else:
                nsqr = self.XNUZ * np.exp(
                    -2 * (1 + 3 * (mode.ref.true_height - 70) / 18) / self.HNU
                )
            # BUG FIX: Use fixed height of 100 km for D-layer absorption instead
            # of variable reflection height to avoid excessive absorption
            h_eff = 100.0
            # CCIR 252 adjustment for E-layer modes (ADX term)
            # Ensure argument to ln() is >= 1.0 to prevent negative ADX
            xv = max(mode.ref.vert_freq / self._current_profile.e.fo, self._adj_de_loss)
            xv = max(1.0, xv)  # Clamp to 1.0 minimum to prevent negative logarithm
            adx = self._adj_ccir252_a + self._adj_ccir252_b * np.log(xv)
        else:
            # F layer modes
            nsqr = 10.2
            h_eff = 100.0
            adx = 0.0

        mode.absorption_loss = (
            ac / (bc + nsqr) /
            self._cos_of_incidence(mode.ref.elevation, h_eff)
        )

        # Ground reflection loss
        mode.ground_loss = sum(
            self._compute_ground_reflection_loss(i, mode.ref.elevation, frequency)
            for i in range(len(self._control_points))
        ) / len(self._control_points)

        # Deviation term
        mode.deviation_term = (
            mode.ref.dev_loss / (bc + nsqr) *
            ((mode.ref.vert_freq + self._current_profile.gyro_freq) ** 1.98 + nsqr) /
            self._cos_of_incidence(mode.ref.elevation, mode.ref.virt_height) +
            adx
        )

        # Obscuration (Es layer) - not implemented yet
        mode.obscuration = 0.0

        # Antenna gains
        mode.signal.tx_gain_db = self.tx_antennas.current_antenna.get_gain_db(
            mode.ref.elevation
        )
        mode.signal.rx_gain_db = self.rx_antennas.current_antenna.get_gain_db(
            mode.ref.elevation
        )

        # Total transmission loss
        mode.signal.total_loss_db = (
            mode.free_space_loss +
            hop_count * (mode.absorption_loss + mode.deviation_term) +
            mode.ground_loss * (hop_count - 1) +
            hop_count2 * mode.obscuration +
            self._adj_auroral -
            mode.signal.rx_gain_db -
            mode.signal.tx_gain_db
        )

        # MUF probability for this mode
        from .muf_calculator import calc_muf_prob
        mode_muf_elev = self._calc_elevation_angle(mode.hop_dist, muf_info.ref.virt_height)
        mode_muf = (muf_info.ref.vert_freq /
                   self._cos_of_incidence(mode_muf_elev, muf_info.ref.true_height))
        mode.signal.muf_day = calc_muf_prob(
            frequency, mode_muf, muf_info.muf,
            muf_info.sig_lo, muf_info.sig_hi
        )

        # Add more loss when MUF_DAY gets very low
        if mode.signal.muf_day < 1e-4:
            mode.signal.total_loss_db += -max(-24.0, 8.0 * np.log10(mode.signal.muf_day) + 32.0)

        # Additional losses
        sec = 1.0 / self._cos_of_incidence(mode.ref.elevation, mode.ref.true_height)
        xmuf = muf_info.ref.vert_freq * sec
        xls = calc_muf_prob(frequency, xmuf, muf_info.muf, muf_info.sig_lo, muf_info.sig_hi)
        xls = -self._to_db(max(1e-6, xls)) * sec
        mode.signal.total_loss_db += hop_count * xls

        # Deciles
        cpr = muf_info.ref.vert_freq / muf_info.muf
        xls_lo = calc_muf_prob(
            frequency, muf_info.fot * sec * cpr, muf_info.fot,
            muf_info.sig_lo, muf_info.sig_hi
        )
        xls_lo = -self._to_db(max(1e-6, xls_lo)) * sec

        xls_hi = calc_muf_prob(
            frequency, muf_info.hpf * sec * cpr, muf_info.hpf,
            muf_info.sig_lo, muf_info.sig_hi
        )
        xls_hi = -self._to_db(max(1e-6, xls_hi)) * sec

        mode.signal.power10 = min(25.0, self._adj_signal_10 + hop_count * (xls_lo - xls))
        mode.signal.power90 = min(25.0, self._adj_signal_90 + hop_count * (xls - xls_hi))

        # Field strength
        mode.signal.field_dbuv = (
            107.2 + self.tx_antennas.current_antenna.tx_power_dbw +
            2 * self._to_db(frequency) - mode.signal.total_loss_db - mode.signal.rx_gain_db
        )

        # Received power
        mode.signal.power_dbw = (
            self.tx_antennas.current_antenna.tx_power_dbw - mode.signal.total_loss_db
        )

        # SNR
        mode.signal.snr_db = mode.signal.power_dbw - self.noise_model.combined

    def _analyze_reliability(self, frequency: float) -> Prediction:
        """Analyze reliability and select best mode."""
        prediction = Prediction()

        if not self._modes:
            return prediction

        # Calculate reliability for each mode
        for mode in self._modes:
            if mode.ref.virt_height <= 70:
                mode.signal.reliability = 0.001
            else:
                self._calc_reliability(mode.signal)

        # Find most reliable mode
        self._best_mode = self._find_best_mode()

        # Fill prediction from best mode
        prediction.tx_elevation = self._best_mode.ref.elevation
        prediction.virt_height = self._best_mode.ref.virt_height
        prediction.hop_count = self._best_mode.hop_cnt
        prediction.signal = self._best_mode.signal
        prediction.noise_dbw = self.noise_model.combined_noise.value.median
        prediction.mode_tx = self._best_mode.layer

        # Add signals from all modes (random phase)
        if len(self._modes) > 1:
            self._calc_sum_of_modes(prediction)
            prediction.signal.snr_db = (
                self._best_mode.signal.snr_db +
                prediction.signal.power_dbw -
                self._best_mode.signal.power_dbw
            )
            self._calc_reliability(prediction.signal, clamp=True)

        # Required power for specified reliability
        prediction.required_power = self._calc_required_power(prediction.signal)
        prediction.snr_xx = self.params.required_snr - prediction.required_power

        return prediction

    def _calc_reliability(self, signal: SignalInfo, clamp: bool = False):
        """Calculate circuit reliability."""
        # SNR distribution variables
        signal.snr10 = np.sqrt(
            self.noise_model.combined_noise.value.upper ** 2 + signal.power10 ** 2
        )
        signal.snr90 = np.sqrt(
            self.noise_model.combined_noise.value.lower ** 2 + signal.power90 ** 2
        )

        if clamp:
            signal.snr10 = max(0.2, signal.snr10)
            signal.snr90 = min(30.0, signal.snr90)

        # Reliability calculation
        z = self.params.required_snr - signal.snr_db
        if z <= 0:
            z = z / (signal.snr10 / self.NORM_DECILE)
        else:
            z = z / (signal.snr90 / self.NORM_DECILE)

        signal.reliability = 1.0 - self._cumulative_normal(z)

    def _find_best_mode(self) -> ModeInfo:
        """Find best propagation mode based on reliability, hops, and SNR."""
        best = self._modes[0]

        for mode in self._modes[1:]:
            if mode.signal.reliability > (best.signal.reliability + 0.05):
                best = mode
            elif mode.signal.reliability < (best.signal.reliability - 0.05):
                continue
            elif mode.hop_cnt < best.hop_cnt:
                best = mode
            elif mode.hop_cnt > best.hop_cnt:
                continue
            elif mode.signal.snr_db > best.signal.snr_db:
                best = mode

        return best

    def _calc_required_power(self, signal: SignalInfo) -> float:
        """Calculate required power gain for specified reliability."""
        idx = min(
            len(self.TME) - 1,
            abs(round(self.params.required_reliability * 100) - 50) // 5
        )

        if self.params.required_reliability < 0.5:
            return (self.params.required_snr - signal.snr_db -
                   self.TME[idx] / self.TME[8] * signal.snr90)
        else:
            return (self.params.required_snr - signal.snr_db +
                   self.TME[idx] / self.TME[8] * signal.snr10)

    def _calc_sum_of_modes(self, prediction: Prediction):
        """Sum power from all modes (random phase addition)."""
        # Find maximum values
        max_pwr = max(m.signal.power_dbw for m in self._modes)
        max_pwr_lo = max(m.signal.power_dbw - m.signal.power10 for m in self._modes)
        max_pwr_hi = max(m.signal.power_dbw + m.signal.power90 for m in self._modes)
        max_fld = max(m.signal.field_dbuv for m in self._modes)

        # Sum powers
        sum_pwr = sum(
            self._from_db(m.signal.power_dbw - max_pwr)
            for m in self._modes
            if (m.signal.power_dbw - max_pwr) > -100
        )

        sum_pwr_lo = sum(
            self._from_db(m.signal.power_dbw - m.signal.power10 - max_pwr_lo)
            for m in self._modes
            if (m.signal.power_dbw - m.signal.power10 - max_pwr_lo) > -100
        )

        sum_pwr_hi = sum(
            self._from_db(m.signal.power_dbw + m.signal.power90 - max_pwr_hi)
            for m in self._modes
            if (m.signal.power_dbw + m.signal.power90 - max_pwr_hi) > -100
        )

        sum_fld = sum(
            self._from_db(m.signal.field_dbuv - max_fld)
            for m in self._modes
            if (m.signal.field_dbuv - max_fld) > -100
        )

        # Compute combined values
        if sum_pwr > 0:
            prediction.signal.power_dbw = max_pwr + self._to_db(sum_pwr)
        else:
            prediction.signal.power_dbw = -500.0

        if sum_pwr_lo > 0:
            prediction.signal.power10 = abs(
                prediction.signal.power_dbw - self._to_db(sum_pwr_lo) - max_pwr_lo
            )
        else:
            prediction.signal.power10 = 0.0
        prediction.signal.power10 = max(0.2, min(30.0, prediction.signal.power10))

        if sum_pwr_hi > 0:
            prediction.signal.power90 = abs(
                max_pwr_hi + self._to_db(sum_pwr_hi) - prediction.signal.power_dbw
            )
        else:
            prediction.signal.power90 = 0.0
        prediction.signal.power90 = max(0.2, min(30.0, prediction.signal.power90))

        if sum_fld > 0:
            prediction.signal.field_dbuv = max_fld + self._to_db(sum_fld)
        else:
            prediction.signal.field_dbuv = -500.0

    def _calc_service_prob(self) -> float:
        """Calculate service probability."""
        DR = 2.0  # Prediction error in required SNR

        idx = min(
            len(self.TME) - 1,
            abs(round(self.params.required_reliability * 100) - 50) // 5
        )
        tmx = self.TME[idx]

        if self.params.required_reliability >= 0.5:
            noise_pwr = tmx * self.noise_model.combined_noise.value.upper / self.NORM_DECILE
            noise_err = tmx * self.noise_model.combined_noise.error.upper / self.NORM_DECILE
            sgn = -1.0
        else:
            noise_pwr = tmx * self.noise_model.combined_noise.value.lower / self.NORM_DECILE
            noise_err = tmx * self.noise_model.combined_noise.error.lower / self.NORM_DECILE
            sgn = 1.0

        max_prob = 0.001

        for mode in self._modes:
            if mode.ref.virt_height > 70:
                if self.params.required_reliability >= 0.5:
                    signal_pwr = tmx * mode.signal.power10 / self.NORM_DECILE
                else:
                    signal_pwr = tmx * mode.signal.power90 / self.NORM_DECILE

                pwr50 = np.sqrt(signal_pwr ** 2 + noise_pwr ** 2)
                pwr10 = pwr50 + np.sqrt(
                    self.noise_model.combined_noise.error.median ** 2 +
                    noise_err ** 2 + DR ** 2
                )
                pwr50 = mode.signal.snr_db + sgn * pwr50
                z = (self.params.required_snr - pwr50) / pwr10
                prob = 1.0 - self._cumulative_normal(z)

                max_prob = max(max_prob, prob)

        return max_prob

    def _calc_multipath_prob(self) -> float:
        """Calculate multipath probability."""
        if self.path.dist > self.RAD_7000_KM:
            return 0.001

        if not self._best_mode:
            return 0.001

        power_limit = (self._best_mode.signal.power_dbw -
                      self.params.multipath_power_tolerance)

        max_prob = 0.001

        for mode in self._modes:
            delay_diff = abs(mode.signal.delay_ms - self._best_mode.signal.delay_ms)
            if (delay_diff > self.params.max_tolerable_delay and
                mode.signal.power_dbw > power_limit):
                max_prob = max(max_prob, mode.signal.reliability)

        return max_prob

    def _evaluate_long_model(self, frequency: float) -> Prediction:
        """Evaluate long path model (not fully implemented)."""
        # Simplified implementation - would need two Reflectrix objects
        # For now, return a basic prediction
        return Prediction()

    def _combine_short_and_long(
        self,
        short_pred: Prediction,
        long_pred: Prediction
    ) -> Prediction:
        """Combine short and long path predictions."""
        short_pwr10 = short_pred.signal.power_dbw - abs(short_pred.signal.power10)
        long_pwr10 = long_pred.signal.power_dbw - abs(long_pred.signal.power10)

        if self.path.dist < self.RAD_7000_KM:
            return short_pred
        elif short_pwr10 > long_pwr10:
            return short_pred
        elif self.path.dist >= self.RAD_10000_KM:
            return long_pred
        else:
            # Smoothed combination
            result = long_pred
            result.method = PredictionMethod.SMOOTH

            r = (self.path.dist - self.RAD_7000_KM) / (self.RAD_10000_KM - self.RAD_7000_KM)
            pwr = short_pwr10 + self._to_db(
                r * (self._from_db(long_pwr10 - short_pwr10) - 1.0) + 1.0
            )

            result.signal.power_dbw = pwr + long_pred.signal.power10
            result.signal.total_loss_db = (
                self.tx_antennas.current_antenna.tx_power_dbw - result.signal.power_dbw
            )
            result.signal.snr_db = result.signal.power_dbw - self.noise_model.combined
            result.signal.field_dbuv = (
                107.2 + self.tx_antennas.current_antenna.tx_power_dbw +
                2 * self._to_db(self.frequencies[0]) -
                result.signal.total_loss_db - result.signal.rx_gain_db
            )

            self._calc_reliability(result.signal, clamp=True)
            result.required_power = self._calc_required_power(result.signal)
            result.snr_xx = self.params.required_snr - result.required_power

            return result

    # Utility methods
    @staticmethod
    def _to_db(power: float) -> float:
        """Convert power ratio to dB."""
        return 10.0 * np.log10(max(1e-30, power))

    @staticmethod
    def _from_db(db: float) -> float:
        """Convert dB to power ratio."""
        if db > 375:
            return 3e37
        return 10.0 ** (0.1 * db)

    @staticmethod
    def _cumulative_normal(x: float) -> float:
        """Cumulative normal distribution."""
        C = [0.196854, 0.115194, 0.000344, 0.019527]
        y = min(5.0, abs(x))
        result = 1.0 + y * (C[0] + y * (C[1] + y * (C[2] + y * C[3])))
        result = result ** 4
        result = 0.5 / result
        if x > 0:
            result = 1.0 - result
        return result

    @staticmethod
    def _hop_length_3d(elevation: float, hop_distance: float, virt_height: float) -> float:
        """Calculate 3D hop length."""
        return np.sqrt(
            (hop_distance * PredictionEngine.EARTH_RADIUS) ** 2 +
            (2.0 * virt_height) ** 2
        )

    @staticmethod
    def _cos_of_incidence(elevation: float, height: float) -> float:
        """Calculate cosine of incidence angle."""
        # Correct formula: cos(i) = sqrt(1 - (R/(R+h))^2 * cos(elev)^2)
        # where R = Earth radius, h = ionospheric height
        r_ratio = PredictionEngine.EARTH_RADIUS / (PredictionEngine.EARTH_RADIUS + height)
        cos_elev = np.cos(elevation)
        # Guard against negative values under sqrt
        value = 1.0 - (r_ratio ** 2) * (cos_elev ** 2)
        if value < 0:
            # Clamp to prevent division issues (sec = 1/cos will be max ~33)
            # This happens when ray geometry is at the edge of viability
            return 0.03
        return np.sqrt(value)

    @staticmethod
    def _calc_elevation_angle(distance: float, virt_height: float) -> float:
        """Calculate elevation angle for given distance and virtual height."""
        psi = distance / 2.0
        return np.arctan(
            (virt_height / PredictionEngine.EARTH_RADIUS - (1.0 - np.cos(psi))) /
            np.sin(psi)
        )

    def _compute_ground_reflection_loss(
        self, ctrl_pt_idx: int, elevation: float, frequency: float
    ) -> float:
        """Compute ground reflection loss using Fresnel coefficients."""
        if elevation < 1e-8:
            return 6.0

        ctrl_pt = self._control_points[ctrl_pt_idx]

        # Fresnel reflection coefficients (from Volume I of OT report)
        x = 18000.0 * ctrl_pt.gnd_sig / frequency
        t = np.cos(elevation)
        q = np.sin(elevation)
        r = q ** 2
        s = r ** 2
        ert = ctrl_pt.gnd_eps - t ** 2
        rho = np.sqrt(ert ** 2 + x ** 2)
        a = -np.arctan(x / ert) if ert != 0 else -np.pi / 2
        u = ctrl_pt.gnd_eps ** 2 + x ** 2
        v = np.sqrt(u)
        asxv = np.arcsin(x / v) if v != 0 else 0

        # Guard against negative values under sqrt
        cv_arg = rho ** 2 + u * s - 2.0 * rho * u * r * np.cos(a + 2.0 * asxv)
        cv = np.sqrt(max(0.0, cv_arg)) / (rho + u * r + 2.0 * np.sqrt(rho) * v * q * np.cos(0.5 * a + asxv))

        ch_arg = rho ** 2 + s - 2.0 * rho * r * np.cos(a)
        ch = np.sqrt(max(0.0, ch_arg)) / (rho + r + 2.0 * np.sqrt(rho) * q * np.cos(0.5 * a))

        return abs(4.3429 * np.log(0.5 * (ch ** 2 + cv ** 2)))

    @staticmethod
    def _interpolate_table(target_height: float, heights: np.ndarray, values: np.ndarray) -> float:
        """Interpolate value from table."""
        if len(heights) == 0:
            return 0.0

        # Find bracketing indices
        if target_height <= heights[0]:
            return values[0]
        if target_height >= heights[-1]:
            return values[-1]

        for i in range(len(heights) - 1):
            if heights[i] <= target_height <= heights[i + 1]:
                # Linear interpolation
                t = (target_height - heights[i]) / (heights[i + 1] - heights[i])
                return values[i] * (1.0 - t) + values[i + 1] * t

        return values[-1]
