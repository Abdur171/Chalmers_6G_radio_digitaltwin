# -*- coding: utf-8 -*-

import os 
import pandas as pd
import tensorflow as tf
import sionna
import pickle

# Set random seed for reproducibility
sionna.config.seed = 42

# Commented out IPython magic to ensure Python compatibility.
import matplotlib.pyplot as plt
import numpy as np
import time
import json

# Import Sionna RT components
from sionna.rt import load_scene, Transmitter, Receiver, PlanarArray, Camera

# For link-level simulations
from sionna.channel import cir_to_ofdm_channel, subcarrier_frequencies, OFDMChannel, ApplyOFDMChannel, CIRDataset
from sionna.nr import PUSCHConfig, PUSCHTransmitter, PUSCHReceiver
from sionna.utils import compute_ber, ebnodb2no, PlotBER
from sionna.ofdm import KBestDetector, LinearDetector
from sionna.mimo import StreamManagement
import copy


# Load integrated scene from the xml file
scene = load_scene("Data_Generation/V2_XML/chalmers_map_v2.xml")
# Configure antenna array for all transmitters
scene.tx_array = PlanarArray(num_rows=4, num_cols=4, vertical_spacing=0.5,horizontal_spacing=0.5, pattern="tr38901",polarization="V")
# Configure antenna array for all receivers
scene.rx_array = PlanarArray(num_rows=1, num_cols=1, vertical_spacing=0.5,horizontal_spacing=0.5, pattern="iso",polarization="V")
# Create transmitter
tx2 = Transmitter("tx2", [0.5, -343, 30], [0.0, 0.0, 0.0])   #Chalmers coordinates
scene.add(tx2)
tx3 = Transmitter("tx3", [65, -181.5, 35], [0.0, 0.0, 0.0])  #Chalmers coordinates
scene.add(tx3)
tx4 = Transmitter("tx4", [22, 182, 28], [0.0, 0.0, 0.0])  #Chalmers coordinates
scene.add(tx4)
tx5 = Transmitter("tx5", [-147, 327, 28], [0.0, 0.0, 0.0])  #Chalmers coordinates
scene.add(tx5)
tx6 = Transmitter("tx6", [-212, -33, 15], [0.0, 0.0, 0.0])  #Chalmers coordinates
scene.add(tx6)
# compute the coverage map which only depend upon the transmitter
#cm = scene.coverage_map(cm_cell_size=[1,1], num_samples=10e6, diffraction=True, scattering=True)

# initiate the path data dictionary
path_data = {}
path_data_array = {}
# initiate the CIR data dictionary
# notice that they are separated because they are going to be used by different people
h_freqency_data = {}
h_avg_power_data = {}
# define a grid of positions for data collection
#ue_grid= []
#ue_grid= [[10, 1.4, 1.2], [10, 1, 1]]
# Replace 'grid_points.csv' with the path to your CSV file.
file_path = "Toy model/grid_points_toy.csv"
    
# Read the CSV file into a DataFrame.
data = pd.read_csv(file_path)
X = data['X']
Y = data['Y']
Z = data['Z']

# Define the grid for the UE positions
# EVENTUALLY THIS SHOULD BE OBTAINED FROM A DATA FILE
# TODO: Define the grid for the UE positions at 50cm resolution for now
# This grid should be obtained from Blender
#ue_positions = tf.squeeze(ue_grid)
ue_positions = tf.squeeze(ue_grid)
# Create batch_size receivers for the data generation
for i in range(len(ue_positions)):
    rx = Receiver(name=f"rx-{i}",
                  position=ue_positions[i])
    scene.add(rx)
    # compute the path for that receiver
    paths = scene.compute_paths(max_depth=4)
    '''
    # mask : [batch_size, num_rx, num_rx_ant, num_tx, num_tx_ant, max_num_paths] or [batch_size, num_rx, num_tx, max_num_paths], tf.bool
    #   Set to `False` for non-existent paths.
    #   When there are multiple transmitters or receivers, path counts may vary between links. This is used to identify non-existent paths.
    #   For such paths, the channel coefficient is set to `0` and the delay to `-1`.

    # a : [batch_size, num_rx, num_rx_ant, num_tx, num_tx_ant, max_num_paths, num_time_steps], tf.complex
    #     Channel coefficients :math:`a_i` as defined in :eq:`T_tilde`.
    #     If there are less than `max_num_path` valid paths between a
    #     transmit and receive antenna, the irrelevant elements are
    #     filled with zeros.

    # tau : [batch_size, num_rx, num_rx_ant, num_tx, num_tx_ant, max_num_paths] or [batch_size, num_rx, num_tx, max_num_paths], tf.float
    #     Propagation delay of each path [s].
    #     If :attr:`~sionna.rt.Scene.synthetic_array` is `True`, the shape of this tensor
    #     is `[1, num_rx, num_tx, max_num_paths]` as the delays for the
    #     individual antenna elements are assumed to be equal.
    #     If there are less than `max_num_path` valid paths between a
    #     transmit and receive antenna, the irrelevant elements are
    #     filled with -1.

    # theta_t : [batch_size, num_rx, num_rx_ant, num_tx, num_tx_ant, max_num_paths] or [batch_size, num_rx, num_tx, max_num_paths], tf.float
    #     Zenith  angles of departure :math:`\theta_{\text{T},i}` [rad].
    #     If :attr:`~sionna.rt.Scene.synthetic_array` is `True`, the shape of this tensor
    #     is `[1, num_rx, num_tx, max_num_paths]` as the angles for the
    #     individual antenna elements are assumed to be equal.

    # phi_t : [batch_size, num_rx, num_rx_ant, num_tx, num_tx_ant, max_num_paths] or [batch_size, num_rx, num_tx, max_num_paths], tf.float
    #     Azimuth angles of departure :math:`\varphi_{\text{T},i}` [rad].
    #     See description of ``theta_t``.

    # theta_r : [batch_size, num_rx, num_rx_ant, num_tx, num_tx_ant, max_num_paths] or [batch_size, num_rx, num_tx, max_num_paths], tf.float
    #     Zenith angles of arrival :math:`\theta_{\text{R},i}` [rad].
    #     See description of ``theta_t``.

    # phi_r : [batch_size, num_rx, num_rx_ant, num_tx, num_tx_ant, max_num_paths] or [batch_size, num_rx, num_tx, max_num_paths], tf.float
    #     Azimuth angles of arrival :math:`\varphi_{\text{T},i}` [rad].
    #     See description of ``theta_t``.

    # types : [batch_size, max_num_paths], tf.int
    #     Type of path:

    #     - 0 : LoS
    #     - 1 : Reflected
    #     - 2 : Diffracted
    #     - 3 : Scattered
    '''

    # convert the paths to dictionary for data storage
    path_dict_array = {}
    path_dict = paths.to_dict()
    # TODO convert the path_dict to a dictionary with numpy arrays
    # for instance path_dict_array['path_1'] = path_dict['path_1'].numpy()
    # we need to do this for all the keys in the path_dict
    # we also need to confirm that data at every level are numpy arrays
    path_dict_array['mask'] = path_dict['mask'].numpy()
    path_dict_array['a'] = path_dict['a'].numpy()
    path_dict_array['tau'] = path_dict['tau'].numpy()
    path_dict_array['theta_t'] = path_dict['theta_t'].numpy()
    path_dict_array['phi_t'] = path_dict['phi_t'].numpy()
    path_dict_array['theta_r'] = path_dict['theta_r'].numpy()
    path_dict_array['phi_r'] = path_dict['phi_r'].numpy()
    path_dict_array['types'] = path_dict['types'].numpy()

    
    # append the path data to the position, which is the key of the dictionary
    #position_key = (ue_positions[i].numpy()[0],ue_positions[i].numpy()[1],ue_positions[i].numpy()[2])
    position_key = i
    path_data[position_key]=path_dict
    path_data_array[position_key]=path_dict_array

    # Default parameters in the PUSCHConfig
    subcarrier_spacing = 15e3
    fft_size = 48
    a, tau = paths.cir()
    # Disable normalization of delays
    #paths.normalize_delays = False
    # Get only the LoS path
    #_, tau = paths.cir(los=True, reflection=False)

    paths.normalize_delays = True
    _, tau = paths.cir(los=True, reflection=True, diffraction=False, scattering=False)
    # Compute frequencies of subcarriers and center around carrier frequency
    frequencies = subcarrier_frequencies(fft_size, subcarrier_spacing)

    # Compute the frequency response of the channel at frequencies.
    '''
    Dimensions
    a : [batch size, num_rx, num_rx_ant, num_tx, num_tx_ant, num_paths, num_time_steps], tf.complex
        Path coefficients

    tau : [batch size, num_rx, num_tx, num_paths] or [batch size, num_rx, num_rx_ant, num_tx, num_tx_ant, num_paths], tf.float
        Path delays

    normalize : bool
        If set to `True`, the channel is normalized over the resource grid
        to ensure unit average energy per resource element. Defaults to `False`.

    h_f : [batch size, num_rx, num_rx_ant, num_tx, num_tx_ant, num_time_steps, fft_size], tf.complex
        Channel frequency responses at ``frequencies``
    '''
    h_freq = cir_to_ofdm_channel(frequencies,a,tau,normalize=True) # Non-normalized includes path-loss
    # Verify that the channel power is normalized
    h_avg_power = tf.reduce_mean(tf.abs(h_freq)**2).numpy()
    h_freqency_data[position_key] = h_freq.numpy()
    h_avg_power_data[position_key] = h_avg_power

    # remove the rx from the scene
    scene.remove(f"rx-{i}")

def make_hashable(item):
    """
    Recursively convert an item to a hashable representation.
    - tf.Tensor: converts to a Python scalar or tuple.
    - list: converts to a tuple.
    - dict: converts to a tuple of sorted key-value pairs.
    - Other types are returned as is.
    """
    if isinstance(item, tf.Tensor):
        # Convert the EagerTensor to a numpy array.
        arr = item.numpy()
        # If it's a scalar, return the Python scalar.
        if arr.ndim == 0:
            return arr.item()
        # Otherwise, convert the array to a tuple.
        else:
            return tuple(arr.tolist())
    elif isinstance(item, list):
        return tuple(make_hashable(elem) for elem in item)
    elif isinstance(item, dict):
        # Sort the keys to ensure consistent ordering.
        return tuple((k, make_hashable(item[k])) for k in sorted(item))
    else:
        return item
#h_freqency_data = {make_hashable(k): v for k, v in h_freqency_data.items()}
#h_avg_power_data = {make_hashable(k): v for k, v in h_avg_power_data.items()}
#path_data = {make_hashable(k): v for k, v in path_data.items()}
# Save the h_frequency data
#with open("h_frequency_data.pkl", "wb") as f:
#    pickle.dump(h_freqency_data, f)
# Save the h_avg_power_data
#with open("h_avg_power_data.pkl", "wb") as f:
#    pickle.dump(h_avg_power_data, f)
# Save the path data
#with open("path_data.pkl", "wb") as f:
#    pickle.dump(path_data, f)
# Save the path data array
#with open("path_data_array.json", "wb") as f:
#    pickle.dump(path_data_array, f)

# Create a list to hold the combined data for each position key.
data_combined = []

# Assuming all dictionaries (h_avg_power_data, h_frequency_data, path_data, path_data_array)
for key in h_avg_power_data.keys():
    pos_data = {
        "position": key,
        "h_avg_power": h_avg_power_data.get(key),
        "h_frequency_data": h_frequency_data.get(key),
        "path_data": path_data.get(key),
    }
    data_combined.append(pos_data)

# Convert the list of dictionaries into a pandas DataFrame.
df = pd.DataFrame(data_combined)
df.to_csv("all_data.csv", index=True)
df.to_json("all_data.json", orient="records")


