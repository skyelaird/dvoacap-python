"""
DVOACAP Antenna Gain Module - Phase 5

This module implements antenna gain calculations for HF propagation predictions.
Provides base classes for antenna models with elevation and azimuth-dependent gain patterns.

Based on VOACAP's AntGain.pas implementation.

Author: Ported from VOACAP Pascal source (VE3NEA)
"""

import numpy as np


class AntennaModel:
    """
    Base class for antenna gain models.

    Provides interface for computing antenna gain as a function of elevation angle,
    azimuth, and frequency. Subclasses can implement specific antenna patterns.

    Attributes:
        extra_gain_db: Additional gain to add to computed gain (dB)
        tx_power_dbw: Transmit power in dBW
    """

    def __init__(
        self,
        low_frequency: float = 0.0,
        high_frequency: float = 1e9,
        extra_gain_db: float = 0.0,
        tx_power_dbw: float = 1.0
    ) -> None:
        """
        Initialize antenna model.

        Args:
            low_frequency: Lower frequency limit in MHz (default: 0)
            high_frequency: Upper frequency limit in MHz (default: very large)
            extra_gain_db: Extra gain in dB to add to result (default: 0)
            tx_power_dbw: Transmit power in dBW (default: 1 = 10W)
        """
        self._frequency = 0.0
        self._azimuth = 0.0
        self._low_frequency = low_frequency
        self._high_frequency = high_frequency

        self.extra_gain_db = extra_gain_db
        self.tx_power_dbw = tx_power_dbw

    @property
    def frequency(self) -> float:
        """Get current operating frequency in MHz."""
        return self._frequency

    @frequency.setter
    def frequency(self, value: float):
        """
        Set operating frequency in MHz.

        Args:
            value: Frequency in MHz

        Raises:
            ValueError: If frequency is outside antenna's frequency range
        """
        if value < self._low_frequency or value > self._high_frequency:
            raise ValueError(
                f"Frequency {value} MHz outside antenna range "
                f"[{self._low_frequency}, {self._high_frequency}] MHz"
            )
        self._frequency = value

    @property
    def azimuth(self) -> float:
        """Get antenna azimuth in radians."""
        return self._azimuth

    @azimuth.setter
    def azimuth(self, value: float):
        """
        Set antenna azimuth in radians.

        Args:
            value: Azimuth angle in radians
        """
        self._azimuth = value

    @property
    def low_frequency(self) -> float:
        """Get lower frequency limit in MHz."""
        return self._low_frequency

    @property
    def high_frequency(self) -> float:
        """Get upper frequency limit in MHz."""
        return self._high_frequency

    def get_gain_db(self, elevation: float) -> float:
        """
        Get antenna gain at specified elevation angle.

        This base implementation returns only the extra gain.
        Subclasses should override to implement specific antenna patterns.

        Args:
            elevation: Elevation angle in radians

        Returns:
            Antenna gain in dBi
        """
        return self.extra_gain_db


class IsotropicAntenna(AntennaModel):
    """
    Isotropic antenna model (0 dBi gain in all directions).

    This is the default antenna used when no specific antenna is selected
    for a given frequency range.
    """

    def __init__(self, tx_power_dbw: float = 1.0) -> None:
        """
        Initialize isotropic antenna.

        Args:
            tx_power_dbw: Transmit power in dBW (default: 1 = 10W)
        """
        # Isotropic antenna works at all frequencies
        super().__init__(
            low_frequency=0.0,
            high_frequency=1e9,
            extra_gain_db=0.0,
            tx_power_dbw=tx_power_dbw
        )

    def get_gain_db(self, elevation: float) -> float:
        """
        Get isotropic antenna gain (always 0 dBi).

        Args:
            elevation: Elevation angle in radians (unused)

        Returns:
            0.0 dBi (isotropic gain)
        """
        return 0.0


class AntennaFarm:
    """
    Antenna farm manager for selecting appropriate antenna based on frequency.

    Manages a collection of antennas with different frequency ranges and
    automatically selects the appropriate antenna for each operating frequency.
    If no antenna covers the requested frequency, an isotropic antenna is used.

    Attributes:
        antennas: List of available antenna models
    """

    def __init__(self) -> None:
        """Initialize antenna farm with isotropic default antenna."""
        self._isotropic_antenna = IsotropicAntenna()
        self._current_antenna = self._isotropic_antenna
        self.antennas: list[AntennaModel] = []

    @property
    def current_antenna(self) -> AntennaModel:
        """Get currently selected antenna."""
        return self._current_antenna

    def add_antenna(self, antenna: AntennaModel) -> None:
        """
        Add an antenna to the farm.

        Args:
            antenna: AntennaModel instance to add
        """
        self.antennas.append(antenna)

    def select_antenna(self, frequency: float) -> None:
        """
        Select antenna for specified frequency.

        Searches through available antennas and selects the first one whose
        frequency range includes the specified frequency. If no suitable
        antenna is found, the isotropic antenna is selected.

        Args:
            frequency: Operating frequency in MHz
        """
        for antenna in self.antennas:
            if antenna.low_frequency <= frequency <= antenna.high_frequency:
                self._current_antenna = antenna
                self._current_antenna.frequency = frequency
                return

        # No antenna found for this frequency, use isotropic
        self._current_antenna = self._isotropic_antenna
        self._current_antenna.frequency = frequency


# Example custom antenna implementation
class HalfWaveDipole(AntennaModel):
    """
    Half-wave dipole antenna model.

    Simple dipole antenna with frequency-dependent gain pattern.
    Peak gain is approximately 2.15 dBi at the horizon.
    """

    def __init__(
        self,
        low_frequency: float,
        high_frequency: float,
        tx_power_dbw: float = 1.0
    ) -> None:
        """
        Initialize half-wave dipole antenna.

        Args:
            low_frequency: Lower frequency limit in MHz
            high_frequency: Upper frequency limit in MHz
            tx_power_dbw: Transmit power in dBW (default: 1 = 10W)
        """
        super().__init__(
            low_frequency=low_frequency,
            high_frequency=high_frequency,
            extra_gain_db=0.0,
            tx_power_dbw=tx_power_dbw
        )

    def get_gain_db(self, elevation: float) -> float:
        """
        Get dipole antenna gain at specified elevation.

        Args:
            elevation: Elevation angle in radians

        Returns:
            Antenna gain in dBi
        """
        # Simple cosine pattern with 2.15 dBi peak gain
        if elevation < 0 or elevation > np.pi / 2:
            return -40.0  # Very low gain below horizon or overhead

        gain = 2.15 + 10.0 * np.log10(max(0.001, np.cos(elevation)))
        return gain + self.extra_gain_db


class VerticalMonopole(AntennaModel):
    """
    Vertical monopole antenna model.

    Ground-mounted vertical antenna with omnidirectional azimuth pattern.
    Good low-angle radiation for DX communications.
    """

    def __init__(
        self,
        low_frequency: float,
        high_frequency: float,
        tx_power_dbw: float = 1.0
    ) -> None:
        """
        Initialize vertical monopole antenna.

        Args:
            low_frequency: Lower frequency limit in MHz
            high_frequency: Upper frequency limit in MHz
            tx_power_dbw: Transmit power in dBW (default: 1 = 10W)
        """
        super().__init__(
            low_frequency=low_frequency,
            high_frequency=high_frequency,
            extra_gain_db=0.0,
            tx_power_dbw=tx_power_dbw
        )

    def get_gain_db(self, elevation: float) -> float:
        """
        Get vertical monopole gain at specified elevation.

        Args:
            elevation: Elevation angle in radians

        Returns:
            Antenna gain in dBi
        """
        # Omnidirectional pattern with peak gain at low angles
        if elevation < 0:
            return -40.0  # No radiation below horizon

        if elevation > np.pi / 2:
            return -40.0  # No radiation overhead

        # Simple model: gain decreases with elevation
        # Peak gain of ~5 dBi at low angles
        gain = 5.0 - 10.0 * (elevation / (np.pi / 2))
        return gain + self.extra_gain_db
