"""Regression tests for PredictionEngine.

Guards against the long-path stub bug where _evaluate_long_model returned an
empty Prediction() and _combine_short_and_long mixed it into the result for
paths >= 7000 km, producing absurdly high signal_dbw / SNR for mid-range
distances and an all-zero prediction beyond 10000 km.
"""

from __future__ import annotations

import numpy as np
import pytest

from dvoacap.path_geometry import GeoPoint
from dvoacap.prediction_engine import PredictionEngine


def _run_prediction(distance_km_target: float, freq_mhz: float = 14.1):
    """Run a prediction along the equator at roughly the requested distance."""
    eng = PredictionEngine()
    eng.params.ssn = 60
    eng.params.month = 5
    eng.params.tx_power = 100.0
    eng.params.tx_location = GeoPoint.from_degrees(0.0, 0.0)

    # Approximate longitude offset for a great-circle distance along the equator.
    # Earth radius is 6370 km in the engine.
    lon_deg = float(distance_km_target / 6370.0 * 180.0 / np.pi)
    rx = GeoPoint.from_degrees(0.0, lon_deg)

    eng.predict(rx_location=rx, utc_time=18 / 24.0, frequencies=[freq_mhz])
    return eng.predictions[0], eng.path.dist * 6370.0


@pytest.mark.parametrize("distance_km", [4500, 8500, 11000])
def test_long_distance_signal_is_physically_plausible(distance_km):
    """Signal level must reflect a real path-loss budget, not a stub bypass.

    For HF on 20 m at these distances, received power against a 100 W TX with
    isotropic antennas should sit well below 0 dBW; SNR likewise capped well
    below the dB regime that signaled the stub-mixing bug (>+100 dB).
    """
    pred, actual_distance = _run_prediction(distance_km)

    assert pred.signal.power_dbw < -50.0, (
        f"Received power {pred.signal.power_dbw:.1f} dBW at "
        f"{actual_distance:.0f} km is implausibly high for HF; long-path stub "
        f"likely leaking back in."
    )
    assert pred.signal.snr_db < 100.0, (
        f"SNR {pred.signal.snr_db:.1f} dB at {actual_distance:.0f} km is "
        f"physically impossible; long-path stub bug regressed."
    )
    assert pred.signal.total_loss_db > 80.0, (
        f"total_loss_db {pred.signal.total_loss_db:.1f} dB at "
        f"{actual_distance:.0f} km is far too low for an HF skywave path."
    )


def test_tx_power_propagates_to_user_added_antenna():
    """tx_power_dbw must reach whichever antenna select_antenna picks, not
    just the isotropic default that current_antenna points at before the
    per-frequency loop."""
    from dvoacap.antenna_gain import VerticalMonopole

    eng = PredictionEngine()
    eng.params.ssn = 60
    eng.params.month = 5
    eng.params.tx_power = 100.0  # 100 W -> 20 dBW
    eng.params.tx_location = GeoPoint.from_degrees(0.0, 0.0)

    # Construct an antenna with a deliberately wrong placeholder power so the
    # bug, if regressed, is unmistakable.
    ant = VerticalMonopole(
        low_frequency=14.0, high_frequency=14.5, tx_power_dbw=-30.0
    )
    eng.tx_antennas.add_antenna(ant)
    eng.rx_antennas.add_antenna(ant)

    eng.predict(
        rx_location=GeoPoint.from_degrees(0.0, 40.0),
        utc_time=18 / 24.0,
        frequencies=[14.1],
    )

    assert eng.tx_antennas.current_antenna.tx_power_dbw == pytest.approx(
        20.0, abs=1e-6
    ), (
        "params.tx_power=100W must be stamped onto the selected antenna; "
        f"got {eng.tx_antennas.current_antenna.tx_power_dbw} dBW."
    )
