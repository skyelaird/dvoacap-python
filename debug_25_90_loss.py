#!/usr/bin/env python3
"""Debug 25.90 MHz loss calculation at hour 06"""

import sys
sys.path.insert(0, 'src')

import numpy as np
from dvoacap.prediction_engine import PredictionEngine
from dvoacap.path_geometry import GeoPoint

# Run test - worst failure case
engine = PredictionEngine()
engine.params.ssn = 100.0
engine.params.month = 6
engine.params.tx_power = 500000.0  # 500 kW
engine.params.tx_location = GeoPoint.from_degrees(35.80, -5.90)
engine.params.min_angle = np.deg2rad(0.1)

rx_location = GeoPoint.from_degrees(44.90, 20.50)
utc_fraction = 6.0 / 24.0  # Hour 06
freq = 25.89

print("=" * 80)
print("LOSS DEBUGGING: 25.90 MHz at Hour 06 (Worst Failure)")
print("=" * 80)
print(f"Expected VOACAP: Loss=186 dB, SNR=42 dB")
print(f"Current DVOACAP: Loss=233 dB, SNR=-5 dB")
print(f"Excess loss: 47 dB")
print("=" * 80)
print()

# Monkey patch to capture loss details
orig_compute_signal = PredictionEngine._compute_signal

loss_details = {}

def debug_compute_signal(self, mode, freq_arg):
    """Capture loss calculation"""

    # Call original BEFORE modifications
    layer_name = mode.layer if isinstance(mode.layer, str) else mode.layer.name
    muf_info = self.circuit_muf.muf_info[layer_name]
    hop_count = mode.hop_cnt

    # Store initial total
    initial_total = (
        mode.free_space_loss +
        hop_count * (mode.absorption_loss + mode.deviation_term) +
        mode.ground_loss * (hop_count - 1) +
        min(2, hop_count) * mode.obscuration +
        self._adj_auroral -
        mode.signal.rx_gain_db -
        mode.signal.tx_gain_db
    )

    # Call original
    orig_compute_signal(self, mode, freq_arg)

    # Calculate XLS that was added
    from dvoacap.geomagnetic import GeomagneticField
    gmf = GeomagneticField()
    pnt = self.path.midpoint
    mag_lat = gmf.calc_mag_lat(pnt.lat, pnt.lon)
    local_time = self._utc_to_local(self.utc_time, pnt.lon)

    sec = 1.0 / self._cos_of_incidence(mode.ref.elevation, mode.ref.true_height)
    xls = self._maps.compute_excessive_system_loss(mag_lat, local_time, freq_arg, sec)
    xls_db = -self._to_db(max(1e-6, xls)) * sec
    total_xls = hop_count * xls_db

    # Calculate low MUF penalty
    low_muf_penalty = 0.0
    if mode.signal.muf_day < 1e-4:
        low_muf_penalty = -max(-24.0, 8.0 * np.log10(mode.signal.muf_day) + 32.0)

    loss_details['freq'] = freq_arg
    loss_details['free_space'] = mode.free_space_loss
    loss_details['absorption'] = mode.absorption_loss * hop_count
    loss_details['deviation'] = mode.deviation_term * hop_count
    loss_details['ground'] = mode.ground_loss * (hop_count - 1)
    loss_details['obscuration'] = min(2, hop_count) * mode.obscuration
    loss_details['auroral'] = self._adj_auroral
    loss_details['tx_gain'] = -mode.signal.tx_gain_db
    loss_details['rx_gain'] = -mode.signal.rx_gain_db
    loss_details['initial_total'] = initial_total
    loss_details['xls_raw'] = xls
    loss_details['xls_db_per_hop'] = xls_db
    loss_details['xls_total'] = total_xls
    loss_details['muf_day'] = mode.signal.muf_day
    loss_details['low_muf_penalty'] = low_muf_penalty
    loss_details['final_total'] = mode.signal.total_loss_db
    loss_details['hop_count'] = hop_count

PredictionEngine._compute_signal = debug_compute_signal

# Run prediction
engine.predict(rx_location=rx_location, utc_time=utc_fraction, frequencies=[freq])

# Display results
if loss_details:
    print("LOSS COMPONENT BREAKDOWN:")
    print(f"  Free space loss:        {loss_details['free_space']:8.2f} dB")
    print(f"  Absorption (x{loss_details['hop_count']} hop):        {loss_details['absorption']:8.2f} dB")
    print(f"  Deviation (x{loss_details['hop_count']} hop):         {loss_details['deviation']:8.2f} dB")
    print(f"  Ground (x{loss_details['hop_count']-1} refl):          {loss_details['ground']:8.2f} dB")
    print(f"  Obscuration:            {loss_details['obscuration']:8.2f} dB")
    print(f"  Auroral adjustment:     {loss_details['auroral']:8.2f} dB")
    print(f"  TX gain:                {loss_details['tx_gain']:8.2f} dB")
    print(f"  RX gain:                {loss_details['rx_gain']:8.2f} dB")
    print(f"  " + "-" * 40)
    print(f"  Subtotal (basic):       {loss_details['initial_total']:8.2f} dB")
    print()
    print(f"  MUF day factor:         {loss_details['muf_day']:8.6f}")
    print(f"  Low MUF penalty:        {loss_details['low_muf_penalty']:8.2f} dB")
    print(f"  XLS (raw):              {loss_details['xls_raw']:8.6f}")
    print(f"  XLS per hop:            {loss_details['xls_db_per_hop']:8.2f} dB")
    print(f"  XLS total (x{loss_details['hop_count']} hop):       {loss_details['xls_total']:8.2f} dB")
    print(f"  " + "-" * 40)
    print(f"  FINAL TOTAL LOSS:       {loss_details['final_total']:8.2f} dB")
    print()
    print(f"COMPARISON:")
    print(f"  VOACAP loss:            186.00 dB")
    print(f"  DVOACAP loss:           {loss_details['final_total']:.2f} dB")
    print(f"  Difference:             {loss_details['final_total'] - 186:.2f} dB")
    print()
    print(f"KEY ISSUE:")
    excess = loss_details['final_total'] - loss_details['initial_total']
    print(f"  Excess loss added: {excess:.2f} dB")
    print(f"    - Low MUF penalty: {loss_details['low_muf_penalty']:.2f} dB")
    print(f"    - XLS total: {loss_details['xls_total']:.2f} dB")
else:
    print("No prediction generated!")

print("=" * 80)
