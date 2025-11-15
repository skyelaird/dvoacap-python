#!/usr/bin/env python3
"""
Reflectrix (Raytracing) Module for VOACAP
Ported from Reflx.pas (DVOACAP)

Original Author: Alex Shovkoplyas, VE3NEA
Python Port: 2025

This module performs ray path calculations through the ionosphere:
- Ray reflection calculations for E, F1, F2 layers
- Skip distance computation
- Multi-hop path finding
- Reflectrix (frequency vs elevation angle)
- Over-the-MUF and vertical mode calculations
"""

import math
from dataclasses import dataclass, field
import numpy as np

from .ionospheric_profile import (
    IonosphericProfile,
    LayerInfo,
    Reflection,
    ModeInfo,
    corr_to_martyns_theorem,
    interpolate_table,
    get_index_of,
    ANGLES
)
from .path_geometry import (
    hop_distance,
    calc_elevation_angle,
    sin_of_incidence,
    cos_of_incidence,
    EarthR,
    RinD,
    MAX_ELEV_ANGLE,
    JUST_BELOW_MAX_ELEV,
    MAX_NON_POLE_LAT
)
from .muf_calculator import CircuitMuf, MufInfo


# ============================================================================
# Constants
# ============================================================================

MAX_MODES = 6  # Maximum number of propagation modes per hop
MAXINT = 2**31 - 1  # Maximum integer value


# ============================================================================
# Reflectrix Class
# ============================================================================

class Reflectrix:
    """
    Computes ray paths (reflectrix) through the ionosphere.

    The reflectrix is a graph of elevation angle vs ground distance for
    a given frequency, showing all possible propagation modes.
    """

    def __init__(self, min_angle: float, freq: float, profile: IonosphericProfile):
        """
        Initialize reflectrix calculator.

        Args:
            min_angle: Minimum elevation angle (radians)
            freq: Frequency (MHz)
            profile: Ionospheric profile
        """
        self.min_angle = min_angle
        self.fmhz = 0.0  # Frequency in MHz
        self.fkhz = 0  # Frequency in kHz
        self.profile: IonosphericProfile | None = None

        # Reflection points (reflectrix)
        self.refl: list[ModeInfo] = []
        self.skip_distance = 0.0  # Minimum ground distance (radians)
        self.max_distance = 0.0  # Maximum ground distance (radians)

        # Modes for a specific hop distance
        self.modes: list[ModeInfo] = []

        # Working variables
        self._layer = 'F2'  # Current layer being processed
        self._ht_idx = 0  # Height index in oblique frequency table
        self._low_h = 0  # Lower height index for current layer
        self._high_h = 0  # Upper height index for current layer
        self._ang_idx = 0  # Angle index
        self._pen_angles = {}  # Penetration angles for each layer
        self._mode_cnt = 0  # Number of modes found
        self._done = False  # Search complete flag

        # Compute reflectrix
        self.compute_reflectrix(freq, profile)

    def compute_reflectrix(self, freq_mhz: float, profile: IonosphericProfile) -> None:
        """
        Compute reflectrix (all modes) for a given frequency.

        Args:
            freq_mhz: Frequency in MHz
            profile: Ionospheric profile
        """
        # Store parameters
        self.fmhz = freq_mhz
        self.fkhz = int(freq_mhz * 1000)
        self.profile = profile

        # Compute penetration angles for all layers at this frequency
        self._pen_angles = profile.compute_penetration_angles(freq_mhz)

        # Initialize
        self.skip_distance = MAXINT
        self.max_distance = 0
        self.refl = []
        self._mode_cnt = 0
        self._high_h = 0
        self._ang_idx = 0
        self._done = False

        # Find propagation modes for each layer
        self._find_modes_for_layer('E')

        if (not self._done) and (profile.f1.fo > 0):
            self._find_modes_for_layer('F1')

        if not self._done:
            self._find_modes_for_layer('F2')

    def _find_modes_for_layer(self, layer: str) -> None:
        """
        Find all reflection points for a specific layer.

        Args:
            layer: Layer name ('E', 'F1', or 'F2')
        """
        self._set_layer(layer)

        # Check if any modes from this layer
        if self._pen_angles.get(layer, 0) <= 0:
            self._done = False
            return

        # Check if penetrated all layers
        if self._pen_angles[layer] > MAX_ELEV_ANGLE:
            self._done = True
            return

        # Search for reflection points at each angle
        while True:
            self._ang_idx += 1

            # Stop if too many hops
            if self._ang_idx >= len(ANGLES):
                self._done = True
                return

            # Check if layer was penetrated
            if ANGLES[self._ang_idx] >= self._pen_angles[layer]:
                self._add_refl_cusp()
                return

            # Search for frequency at this angle
            while True:
                # Check if frequency found at lowest height
                if self.profile.oblique_freq[self._ang_idx, self._low_h] >= self.fkhz:
                    self._add_refl_exact()
                    break

                # Check if reached highest height
                elif self._ht_idx >= self._high_h:
                    break

                # Check for exact match
                elif self.fkhz == self.profile.oblique_freq[self._ang_idx, self._ht_idx]:
                    self._add_refl_exact()
                    break

                # Check if frequency is between two heights (interpolation needed)
                elif (self.fkhz > self.profile.oblique_freq[self._ang_idx, self._ht_idx] and
                      self.fkhz <= self.profile.oblique_freq[self._ang_idx, self._ht_idx + 1]):
                    self._add_refl_interp()
                    break

                else:
                    self._ht_idx += 1

            if self._done:
                return

    def _set_layer(self, layer: str) -> None:
        """Set the current layer and height range."""
        layer_end = {'E': 10, 'F1': 20, 'F2': 30}

        self._low_h = self._high_h + 1
        self._high_h = layer_end[layer]
        self._ht_idx = self._low_h
        self._layer = layer

    def _add_refl_exact(self) -> None:
        """Add reflection point with exact frequency match."""
        mode = ModeInfo()
        mode.ref.elevation = ANGLES[self._ang_idx]
        mode.layer = self._layer

        # Populate mode info from ionogram
        self.profile.populate_mode_info(mode, self._ht_idx)

        self._add_refl(mode)

    def _add_refl_interp(self) -> None:
        """Add reflection point with interpolated frequency."""
        mode = ModeInfo()
        mode.ref.elevation = ANGLES[self._ang_idx]
        mode.layer = self._layer

        # Interpolation ratio
        freq_diff = (self.profile.oblique_freq[self._ang_idx, self._ht_idx + 1] -
                     self.profile.oblique_freq[self._ang_idx, self._ht_idx])
        r = (self.fkhz - self.profile.oblique_freq[self._ang_idx, self._ht_idx]) / max(1, freq_diff)

        # Populate mode info with interpolation
        self.profile.populate_mode_info(mode, self._ht_idx, r)

        self._add_refl(mode)

    def _add_refl_cusp(self) -> None:
        """Add cusp point where ray penetrates to next layer."""
        # Keep angle count correct
        self._ang_idx -= 1

        # Insert cusp for current layer
        mode = ModeInfo()
        mode.ref.elevation = self._pen_angles[self._layer]
        mode.layer = self._layer
        self.profile.populate_mode_info(mode, self._high_h)
        self._add_refl(mode)

        # Check if done (F2 is last layer or at pole)
        self._done = (self._layer == 'F2' or
                      self._pen_angles[self._layer] >= MAX_NON_POLE_LAT)
        if self._done:
            return

        # Insert cusp for next layer
        mode = ModeInfo()
        mode.ref.elevation = self.refl[-1].ref.elevation + 0.001 * RinD

        if self.profile.f1.fo > 0:
            # Go to F1 if it exists
            mode.layer = 'F1' if self._layer == 'E' else 'F2'
        else:
            mode.layer = 'F2'

        self.profile.populate_mode_info(mode, self._high_h + 1)
        self._add_refl(mode)

    def _add_refl(self, mode: ModeInfo) -> None:
        """
        Add reflection point to reflectrix.

        Args:
            mode: ModeInfo to add
        """
        # Correct Martyn's theorem
        xfsq = (self.fmhz / self.profile.f2.fo) ** 2
        xmut = 1 - (mode.ref.vert_freq / self.fmhz) ** 2
        corr = xfsq * xmut * corr_to_martyns_theorem(mode.ref)
        mode.ref.virt_height = mode.ref.virt_height + corr

        # Ground distance (radians)
        mode.hop_dist = hop_distance(mode.ref.elevation, mode.ref.virt_height)

        # Update min and max distance
        if mode.hop_dist < self.skip_distance:
            self.skip_distance = mode.hop_dist

        if (mode.hop_dist >= self.max_distance and
            mode.ref.elevation >= self.min_angle):
            self.max_distance = mode.hop_dist

        # Add to list
        self.refl.append(mode)
        self._mode_cnt += 1

        # Check if array full
        if self._mode_cnt > 45:
            self._done = True

    def find_modes(self, hop_dist: float, hop_cnt: int) -> None:
        """
        Find propagation modes for a specific hop distance.

        Args:
            hop_dist: Single hop ground distance (radians)
            hop_cnt: Number of hops
        """
        self.modes = []

        if hop_dist >= self.max_distance:
            return

        r = 0
        while r < len(self.refl) - 1:
            if self.refl[r].hop_dist < self.refl[r + 1].hop_dist:
                # Ascending branch
                if hop_dist < self.refl[r].hop_dist:
                    r += 1
                    continue
                elif hop_dist == self.refl[r].hop_dist:
                    self._add_mode_exact(r, hop_dist, hop_cnt)
                elif hop_dist > self.refl[r + 1].hop_dist:
                    r += 1
                    continue
                elif hop_dist == self.refl[r + 1].hop_dist:
                    r += 1
                    self._add_mode_exact(r, hop_dist, hop_cnt)
                elif abs(self.refl[r + 1].hop_dist - self.refl[r].hop_dist) <= (0.001 / EarthR):
                    self._add_mode_exact(r, hop_dist, hop_cnt)
                else:
                    self._add_mode_interp(r, hop_dist, hop_cnt)

            elif self.refl[r].hop_dist > self.refl[r + 1].hop_dist:
                # Descending branch
                if self.refl[r].hop_dist < hop_dist:
                    r += 1
                    continue
                elif self.refl[r].hop_dist == hop_dist:
                    self._add_mode_exact(r, hop_dist, hop_cnt)
                elif hop_dist < self.refl[r + 1].hop_dist:
                    r += 1
                    continue
                elif hop_dist == self.refl[r + 1].hop_dist:
                    r += 1
                    self._add_mode_exact(r, hop_dist, hop_cnt)
                elif abs(self.refl[r + 1].hop_dist - self.refl[r].hop_dist) <= (0.001 / EarthR):
                    self._add_mode_exact(r, hop_dist, hop_cnt)
                else:
                    self._add_mode_interp(r, hop_dist, hop_cnt)

            else:
                # Flat region
                if abs(hop_dist - self.refl[r].hop_dist) > (0.001 / EarthR):
                    self._add_mode_exact(r, hop_dist, hop_cnt)

            r += 1

            if len(self.modes) >= MAX_MODES:
                break

    def _add_mode_exact(self, idx: int, hop_dist: float, hop_cnt: int) -> None:
        """Add mode with exact distance match."""
        mode = ModeInfo()
        mode.ref = Reflection(
            elevation=self.refl[idx].ref.elevation,
            true_height=self.refl[idx].ref.true_height,
            virt_height=self.refl[idx].ref.virt_height,
            vert_freq=self.refl[idx].ref.vert_freq,
            dev_loss=self.refl[idx].ref.dev_loss
        )
        mode.layer = self.refl[idx].layer
        mode.hop_dist = hop_dist
        mode.hop_cnt = hop_cnt

        if mode.ref.elevation >= self.min_angle:
            # Sanity check
            assert mode.ref.virt_height > 70, f"Virtual height too low: {mode.ref.virt_height}"
            self.modes.append(mode)

    def _add_mode_interp(self, idx: int, hop_dist: float, hop_cnt: int) -> None:
        """Add mode with interpolated parameters."""
        mode = ModeInfo()
        mode.layer = self.refl[idx].layer
        mode.hop_dist = hop_dist
        mode.hop_cnt = hop_cnt

        # Linear interpolation
        r = ((hop_dist - self.refl[idx].hop_dist) /
             (self.refl[idx + 1].hop_dist - self.refl[idx].hop_dist))

        mode.ref.true_height = (self.refl[idx].ref.true_height * (1 - r) +
                                self.refl[idx + 1].ref.true_height * r)
        mode.ref.virt_height = (self.refl[idx].ref.virt_height * (1 - r) +
                                self.refl[idx + 1].ref.virt_height * r)
        mode.ref.dev_loss = (self.refl[idx].ref.dev_loss * (1 - r) +
                             self.refl[idx + 1].ref.dev_loss * r)

        # Force correct geometry by calculating radiation angle and Snell's law
        mode.ref.elevation = calc_elevation_angle(hop_dist, mode.ref.virt_height)
        mode.ref.vert_freq = (self.fmhz *
                              cos_of_incidence(mode.ref.elevation, mode.ref.true_height))

        if mode.ref.elevation >= self.min_angle:
            assert mode.ref.virt_height > 70, f"Virtual height too low: {mode.ref.virt_height}"
            self.modes.append(mode)

    def add_over_the_muf_and_vert_modes(self, hop_dist: float, hop_cnt: int,
                                       circuit_muf: CircuitMuf) -> None:
        """
        Add over-the-MUF and vertical incidence modes.

        Args:
            hop_dist: Single hop ground distance (radians)
            hop_cnt: Number of hops
            circuit_muf: Circuit MUF information
        """
        EPS = 0.4001  # MHz

        # Determine which layers are already in modes list
        layers_present = set(mode.layer for mode in self.modes)

        # Check for very short distance (take-off angle >= 89.9°)
        muf_layer = circuit_muf.layer
        if circuit_muf.muf_info[muf_layer].ref.elevation > JUST_BELOW_MAX_ELEV:
            self._add_vertical_mode(hop_dist, hop_cnt)
            return

        # Add over-the-MUF modes for layers not present
        for layer in ['E', 'F1', 'F2']:
            if len(self.modes) >= (MAX_MODES - 1):
                break

            if layer in layers_present:
                continue

            if layer == 'F1' and self.profile.f1.fo <= 0:
                continue

            muf_info = circuit_muf.muf_info[layer]

            if ((self.fmhz + EPS) >= muf_info.muf and
                hop_cnt == muf_info.hop_count):
                mode = ModeInfo()
                mode.ref = Reflection(
                    elevation=muf_info.ref.elevation,
                    true_height=muf_info.ref.true_height,
                    virt_height=muf_info.ref.virt_height,
                    vert_freq=muf_info.ref.vert_freq,
                    dev_loss=muf_info.ref.dev_loss
                )
                mode.layer = layer
                mode.hop_dist = hop_dist
                mode.hop_cnt = hop_cnt
                self.modes.append(mode)
                layers_present.add(layer)

        # Check if MUF mode hop count matches requested
        if circuit_muf.muf_info[muf_layer].hop_count == hop_cnt:
            if not self.modes:
                self._add_vertical_mode(hop_dist, hop_cnt)
            return

        # Add modes for higher hop counts
        for layer in ['E', 'F1', 'F2']:
            if len(self.modes) >= (MAX_MODES - 1):
                break

            if layer in layers_present:
                continue

            if layer == 'F1' and self.profile.f1.fo <= 0:
                continue

            muf_info = circuit_muf.muf_info[layer]

            if hop_cnt < muf_info.hop_count:
                continue

            mode = ModeInfo()
            mode.ref.true_height = muf_info.ref.true_height
            mode.ref.vert_freq = muf_info.ref.vert_freq
            mode.ref.dev_loss = muf_info.ref.dev_loss
            mode.layer = layer
            mode.hop_dist = hop_dist
            mode.hop_cnt = hop_cnt

            # Get virtual height from ionogram
            mode.ref.virt_height = interpolate_table(
                mode.ref.vert_freq,
                self.profile.igram_vert_freq,
                self.profile.igram_virt_height
            )

            mode.ref.elevation = calc_elevation_angle(hop_dist, mode.ref.virt_height)

            # Calculate mode MUF
            mode_muf = (muf_info.ref.vert_freq /
                       cos_of_incidence(mode.ref.elevation, mode.ref.true_height))

            # Apply Martyn's theorem correction
            layer_info = getattr(self.profile, layer.lower())
            mode.ref.virt_height = mode.ref.virt_height + (
                (mode_muf / layer_info.fo) ** 2 *
                sin_of_incidence(mode.ref.elevation, mode.ref.true_height) ** 2 *
                corr_to_martyns_theorem(mode.ref)
            )

            mode.ref.elevation = calc_elevation_angle(hop_dist, mode.ref.virt_height)
            mode_muf = (muf_info.ref.vert_freq /
                       cos_of_incidence(mode.ref.elevation, mode.ref.true_height))

            if mode_muf > (self.fmhz + EPS):
                continue

            self.modes.append(mode)

    def _add_vertical_mode(self, hop_dist: float, hop_cnt: int) -> None:
        """Add vertical incidence mode (zero distance)."""
        freq = self.fmhz - 0.001  # Slightly below frequency

        # Find frequency in ionogram
        idx = get_index_of(freq, self.profile.igram_vert_freq)

        if freq == self.profile.igram_vert_freq[idx]:
            r = 0
        elif idx == len(self.profile.igram_vert_freq) - 1:
            return  # Can't extrapolate
        else:
            r = ((freq - self.profile.igram_vert_freq[idx]) /
                 (self.profile.igram_vert_freq[idx + 1] - self.profile.igram_vert_freq[idx]))

        # Create mode
        mode = ModeInfo()
        self.profile.populate_mode_info(mode, idx, r)
        mode.ref.elevation = math.pi / 2  # Vertical
        mode.hop_dist = hop_dist
        mode.hop_cnt = hop_cnt

        # Determine which layer reflects
        for layer in ['E', 'F1', 'F2']:
            layer_info = getattr(self.profile, layer.lower())
            if mode.ref.true_height < layer_info.hm:
                mode.layer = layer
                break

        self.modes.append(mode)


# ============================================================================
# Example/Test Code
# ============================================================================

def example_usage():
    """Demonstrate usage of the Reflectrix module"""
    print("=" * 70)
    print("Reflectrix (Raytracing) Module - Example Usage")
    print("=" * 70)
    print()
    print("This module performs ray path calculations through the ionosphere.")
    print("See examples/phase4_raytracing_example.py for complete demonstration")


if __name__ == "__main__":
    example_usage()
