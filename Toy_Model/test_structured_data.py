# -*- coding: utf-8 -*- 

import os 
import pandas as pd
import tensorflow as tf
import sionna
import pickle
import matplotlib.pyplot as plt
import numpy as np
import time
import json
import csv

from sionna.rt import load_scene, PlanarArray, Transmitter, Receiver, Camera, PathSolver, RadioMapSolver, subcarrier_frequencies
from sionna.phy.channel import cir_to_ofdm_channel, OFDMChannel, ApplyOFDMChannel, CIRDataset
from sionna.phy.nr import PUSCHConfig, PUSCHTransmitter, PUSCHReceiver
from sionna.phy.utils import ebnodb2no, PlotBER, dbm_to_watt, lin_to_db, log2, db_to_lin
from sionna.phy.ofdm import KBestDetector, LinearDetector, ResourceGrid
from sionna.phy.constants import BOLTZMANN_CONSTANT
from sionna.phy.mimo import StreamManagement

tf.random.set_seed(42)

# Load integrated scene from the xml file
scene = load_scene("Toy_Model/toy_XML/Chalmers_entrance.xml")
fc = 3.5e9
scene.frequency = fc
c = 3e8
Lambda = c / fc
antenna_dist = float(Lambda / 2)

# Configure arrays
scene.tx_array = PlanarArray(num_rows=2, 
                             num_cols=2, 
                             vertical_spacing=antenna_dist, 
                             horizontal_spacing=antenna_dist, 
                             pattern="iso", 
                             polarization="V")

scene.rx_array = PlanarArray(num_rows=1, 
                             num_cols=1, 
                             vertical_spacing=antenna_dist, 
                             horizontal_spacing=antenna_dist, 
                             pattern="iso", 
                             polarization="V")

# Transmitters
tx1 = Transmitter("tx1", [0.5, -3, 18], [0.0, 0.0, 0.0])
scene.add(tx1)

# Receiver grid
grid_position = pd.read_csv("Toy_Model/grid_points_toy_1x1.csv")
ue_grid = grid_position[['X','Y','Z']].values.tolist()
ue_positions = tf.squeeze(ue_grid)

# Data collection
data_combined = []
desired_parameters = [
    "_a_real","_a_imag", "_doppler", "_num_rx", "_num_tx",
    "_phi_r", "_phi_t", "_rx_array", "_tau",
    "_theta_t", "_theta_r", "_tx_array"
]

h_freqency_data = {}
h_avg_power_data = {}

p_solver = PathSolver()

for i in range(len(ue_positions[0:6])):
    rx = Receiver(name=f"rx-{i}", position=ue_positions[i])
    scene.add(rx)

    paths = p_solver(scene=scene, max_depth=4, los=True,
                     specular_reflection=True, diffuse_reflection=False, refraction=True)

    path_dict = paths.__dict__

    position_key = tuple(np.squeeze(rx.position.numpy()))

    subcarrier_spacing = 15e3
    fft_size = 48
    frequencies = subcarrier_frequencies(fft_size, subcarrier_spacing)
    h_freq = paths.cfr(frequencies=frequencies, normalize=True,
                       normalize_delays=True, out_type="numpy")
    h_avg_power = tf.reduce_mean(tf.abs(h_freq)**2).numpy()
    h_freqency_data[position_key] = h_freq
    h_avg_power_data[position_key] = h_avg_power

    scene.remove(f"rx-{i}")

    pos_data = {"position": position_key,
                "h_avg_power": h_avg_power,
                "h_frequency_data": h_freq}
    for param in desired_parameters:
        if param in ['_a_real', '_a_imag']:
            real = np.squeeze(path_dict['_a_real'])
            imag = np.squeeze(path_dict['_a_imag'])
            a_complex = real + 1j*imag
            pos_data['_a_complex'] = a_complex
        else:
            pos_data[param] = np.squeeze(path_dict[param])

    data_combined.append(pos_data)

# Save combined summary CSV
df = pd.DataFrame(data_combined)
df.to_csv("all_data.csv", index=True)

# Create detailed per-receiver output
output_root = "structured_output"
os.makedirs(output_root, exist_ok=True)

for i, pos_data in enumerate(data_combined):
    rx_dir = os.path.join(output_root, f"rx_{i}")
    os.makedirs(rx_dir, exist_ok=True)

    # Save 'a' coefficients
    a = pos_data.get("_a_complex")
    if a is not None:
        a = np.array(a).flatten()  # Flatten to 1D (if it's not already)
        with open(os.path.join(rx_dir, "a_coeffs.csv"), "w", newline="") as f:
            writer = csv.writer(f)
            for c in a:
                writer.writerow([str(c)])

    # Save h_frequency data (CFR)
    h_freq = pos_data.get("h_frequency_data")
    if h_freq is not None:
        h_freq = np.array(h_freq)
        np.savetxt(os.path.join(rx_dir, "h_frequency.csv"), h_freq.reshape(-1), delimiter=",")
    

    # Save other parameters
    with open(os.path.join(rx_dir, "other_params.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["parameter", "shape", "value (preview)"])
        for param in desired_parameters:
            if param in ["_a_real", "_a_imag", "_a_complex", "h_frequency_data"]:
                continue
            value = pos_data.get(param)
            if isinstance(value, np.ndarray):
                preview = value.flatten()[:2]
                writer.writerow([param, value.shape, preview])
            else:
                writer.writerow([param, type(value).__name__, str(value)])


# Save global transmitter mapping
tx_info_path = os.path.join(output_root, "tx_mapping.csv")
with open(tx_info_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Transmitter", "X", "Y", "Z"])
    for tx_name in scene.transmitters:
        tx_obj = scene.get(tx_name)  # Get the actual transmitter object
        coords = tx_obj.position.numpy()
        writer.writerow([tx_name] + list(coords))