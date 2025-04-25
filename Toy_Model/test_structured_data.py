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
num_rows_tx = 2
num_cols_tx = 2

num_rows_rx = 1
num_cols_rx = 1

scene.tx_array = PlanarArray(num_rows=num_rows_tx, 
                             num_cols=num_cols_tx, 
                             vertical_spacing=antenna_dist, 
                             horizontal_spacing=antenna_dist, 
                             pattern="iso", 
                             polarization="V")

scene.rx_array = PlanarArray(num_rows=num_rows_rx, 
                             num_cols=num_cols_rx, 
                             vertical_spacing=antenna_dist, 
                             horizontal_spacing=antenna_dist, 
                             pattern="iso", 
                             polarization="V")

# Transmitters
tx0 = Transmitter("tx-0", [0.5, -3, 18], [0.0, 0.0, 0.0])
scene.add(tx0)
tx1 = Transmitter("tx-1", [0.5, -3, 30], [0.0, 0.0, 0.0])
scene.add(tx1)
tx2 = Transmitter("tx-2", [0.5, -3, 17], [0.0, 0.0, 0.0])  #Toymodel coordinates
scene.add(tx2)

# Receiver grid
grid_position = pd.read_csv("Toy_Model/grid_points_toy_1x1.csv")
ue_grid = grid_position[['X','Y','Z']].values.tolist()
ue_positions = tf.squeeze(ue_grid)

# Data collection
data_combined = []
desired_parameters = [
    "_a_complex", "_tau", "_doppler",
    "_phi_r", "_phi_t",
    "_theta_t", "_theta_r", "_vertices"
]

h_freqency_data = {}
h_avg_power_data = {}

p_solver = PathSolver()

for i in range(len(ue_positions[0:10])):
    rx = Receiver(name=f"rx-{i}", position=ue_positions[i])
    scene.add(rx)

    paths = p_solver(scene=scene, max_depth=4, los=True,
                     specular_reflection=True, diffuse_reflection=False, refraction=False)

    path_dict = paths.__dict__
    path_dict['_vertices'] = paths.vertices

    position_key = tuple(np.squeeze(rx.position.numpy()))

    a_complex, tau = paths.cir(normalize_delays=False)
    path_dict['_a_complex'] = np.squeeze(a_complex)

    subcarrier_spacing = 15e3
    fft_size = 48
    frequencies = subcarrier_frequencies(fft_size, subcarrier_spacing)
    h_freq = paths.cfr(frequencies=frequencies, normalize=False,
                       normalize_delays=False, out_type="numpy")
    h_avg_power = tf.reduce_mean(tf.abs(h_freq)**2).numpy()
    h_freqency_data[position_key] = h_freq
    h_avg_power_data[position_key] = h_avg_power
    
    scene.remove(f"rx-{i}")

    all_data = {"Position": position_key,
                "h_avg_power": h_avg_power,
                "h_frequency_data": h_freq}
    for param in desired_parameters:
        all_data[param] = np.squeeze(path_dict[param])

    data_combined.append(all_data)

# Save combined summary CSV
df = pd.DataFrame(data_combined)
df.to_csv("all_data.csv", index=True)



"""
Organizing the generated data for easier visualization and export to Matlab

"""


# Create detailed per-receiver output
output_root = "structured_output"
os.makedirs(output_root, exist_ok=True)

for tx in range(len(scene.transmitters)):
    tx_dir = os.path.join(output_root, f"tx_{tx+1}")

    for i, data in enumerate(data_combined):
        rx_dir = os.path.join(tx_dir, f"rx_{i+1}")
        os.makedirs(rx_dir, exist_ok=True)

        
        
        # Save 'a' coefficients
        a = data.get("_a_complex")
        if a is not None:
            with open(os.path.join(rx_dir, "a_coeffs.csv"), "w", newline="") as f:
                writer = csv.writer(f)
                if len(a.shape) == 4:
                    for path in range(a.shape[-1]):
                        row = []
                        for Ntxrx in range(num_cols_rx*num_cols_tx*num_rows_rx*num_rows_tx):
                            row.append(a[0,tx,Ntxrx,path]) # real part
                            row.append(a[1,tx,Ntxrx,path]) # imaginary part
                        writer.writerow(row) 
                else:
                    row = []
                    for Ntxrx in range(num_cols_rx*num_cols_tx*num_rows_rx*num_rows_tx):
                        row.append(a[0,tx,Ntxrx]) # real part
                        row.append(a[1,tx,Ntxrx]) # imaginary part
                    writer.writerow(row)


        
        # Save h_frequency data (CFR)
        h_freq = data.get("h_frequency_data")
        if h_freq is not None:
            h_freq = np.squeeze(h_freq)
            with open(os.path.join(rx_dir, "h_frequency.csv"), "w", newline="") as f:
                writer = csv.writer(f)

                num_antennas = num_cols_rx * num_cols_tx * num_rows_rx * num_rows_tx

                if h_freq.ndim == 3:
                    for sub_num in range(fft_size):
                        row = []
                        for Ntxrx in range(num_antennas):
                            row.append(np.real(h_freq[tx, Ntxrx, sub_num]))  # Real part
                            row.append(np.imag(h_freq[tx, Ntxrx, sub_num]))  # Imaginary part
                        writer.writerow(row)

                else:
                    for sub_num in range(fft_size):
                        row = []
                        for Ntxrx in range(num_antennas):
                            row.append(np.real(h_freq[Ntxrx, sub_num]))  # Real part
                            row.append(np.imag(h_freq[Ntxrx, sub_num]))  # Imaginary part
                        writer.writerow(row)



        # Save other parameters. See desired_parameters to know the order of the parameters
        with open(os.path.join(rx_dir, "other_params.csv"), "w", newline="") as f:
            writer = csv.writer(f)
            filtered_params = [param for param in desired_parameters if param not in ["_a_complex", "_vertices"]]
            val = data.get('_tau')
            if len(val.shape) > 1:

                for path in range(val.shape[-1]):
                    row = []
                    for param in filtered_params:
                        value = data.get(param)
                        if len(value.shape) > 1:
                            row.append(value[tx, path])
                        else:
                            row.append(value[tx])
                    writer.writerow(row)
            else:
                row = []
                for param in filtered_params:
                    value = data.get(param)
                    if len(value.shape) > 1:
                        row.append(value[tx, path])
                    else:
                        row.append(value[tx])
                writer.writerow(row)

        
        
        # Save vertices.
        with open(os.path.join(rx_dir, "vertices.csv"), "w", newline="") as f:
            writer = csv.writer(f)
            vertices = data.get('_vertices')

            if vertices is not None:
                if vertices.ndim == 4:
                    for max_depth in range(vertices.shape[0]):
                        this_vertices = vertices[max_depth, tx]  # shape: (num_paths, 3)
                        for path in range(this_vertices.shape[0]):
                            row = [f"max_depth {max_depth+1}"]
                            row.extend(this_vertices[path, coord] for coord in range(3))
                            writer.writerow(row)

                elif vertices.ndim == 3:
                    for max_depth in range(vertices.shape[0]):
                        row = [f"max_depth {max_depth+1}"]
                        row.extend(vertices[max_depth, tx, coord] for coord in range(3))
                        writer.writerow(row)



# Save global transmitter mapping
tx_info_path = os.path.join(output_root, "tx_rx_mapping.csv")
with open(tx_info_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Transmitter", "X", "Y", "Z"])
    for tx_name in scene.transmitters:
        tx_obj = scene.get(tx_name)  # Get the actual transmitter object
        coords = np.squeeze(tx_obj.position)
        writer.writerow([tx_name] + list(coords))
    
    for i, pos_data in enumerate(data_combined):
        rx_name = f"rx-{i}"
        coords = pos_data["Position"]
        writer.writerow([rx_name] + list(coords))

"""FIXA vertices"""