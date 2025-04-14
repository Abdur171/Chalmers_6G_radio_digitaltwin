# -*- coding: utf-8 -*-

import os 
import pandas as pd
import tensorflow as tf
import sionna
import pickle

# Set random seed for reproducibility
tf.random.set_seed(42)

# Commented out IPython magic to ensure Python compatibility.
import matplotlib.pyplot as plt
import numpy as np
import time
import json
import csv

# Import Sionna RT components
from sionna.rt import load_scene, PlanarArray, Transmitter, Receiver, Camera, PathSolver, RadioMapSolver, subcarrier_frequencies

# For link-level simulations
from sionna.phy.channel import cir_to_ofdm_channel, OFDMChannel, ApplyOFDMChannel, CIRDataset
from sionna.phy.nr import PUSCHConfig, PUSCHTransmitter, PUSCHReceiver
from sionna.phy.utils import ebnodb2no, PlotBER, dbm_to_watt, lin_to_db, log2, db_to_lin
from sionna.phy.ofdm import KBestDetector, LinearDetector, ResourceGrid
from sionna.phy.constants import BOLTZMANN_CONSTANT
from sionna.phy.mimo import StreamManagement

import copy


# Load integrated scene from the xml file
scene = load_scene("Toy_Model/toy_XML/Chalmers_entrance.xml")
# Set the carrier frequency 
fc = 3.5e9 # from band n78 in 3GPP TS 38.104. Can be changed later when testing out mmWave or sub-THz
scene.frequency = fc
# Define the wavelength of the signal and calculate the antenna distance 
c = 3e8
Lambda = c/fc
antenna_dist = Lambda/2
# Configure antenna array for all transmitters
scene.tx_array = PlanarArray(num_rows=4, num_cols=4, vertical_spacing=0.5, horizontal_spacing=0.5, pattern="tr38901", polarization="cross") # changed it to cross-polarization as described in 3GPP TR 38.901
# Configure antenna array for all receivers
scene.rx_array = PlanarArray(num_rows=2, num_cols=2, vertical_spacing=antenna_dist, horizontal_spacing=antenna_dist, pattern="tr38901", polarization="cross")

# Create transmitter 
# TODO determine appropriate locations of the transmitters
tx1 = Transmitter("tx1", [0.5, -3, 18], [0.0, 0.0, 0.0])   #Toymodel coordinates
scene.add(tx1)


#tx2 = Transmitter("tx2", [0.5, -343, 30], [0.0, 0.0, 0.0])   #Chalmers coordinates
#scene.add(tx2)
#tx3 = Transmitter("tx3", [65, -181.5, 35], [0.0, 0.0, 0.0])  #Chalmers coordinates
#scene.add(tx3)
#tx4 = Transmitter("tx4", [22, 182, 28], [0.0, 0.0, 0.0])  #Chalmers coordinates
#scene.add(tx4)
#tx5 = Transmitter("tx5", [-147, 327, 28], [0.0, 0.0, 0.0])  #Chalmers coordinates
#scene.add(tx5)
#tx6 = Transmitter("tx6", [-212, -33, 15], [0.0, 0.0, 0.0])  #Chalmers coordinates
#scene.add(tx6)

# compute the coverage map which only depend upon the transmitter
#cm = scene.coverage_map(cm_cell_size=[1,1], num_samples=10e6, diffraction=True, scattering=True)

# initiate the path data dictionary
path_data = {}
path_data_array = {}
# initiate the CIR data dictionary
# notice that they are separated because they are going to be used by different people
h_freqency_data = {}
h_avg_power_data = {}
# TODO generate 1 by 1 grid for the entire campus 
file_path = "Toy_Model/grid_points_toy_1x1.csv" 
grid_position = pd.read_csv(file_path)
ue_grid = grid_position[['X','Y','Z']].values.tolist()
ue_positions = tf.squeeze(ue_grid)


# Create batch_size receivers for the data generation
p_solver = PathSolver()
for i in range(len(ue_positions[0:6])): # only the first five positions for debugging purposes, we later change this 
    rx = Receiver(name=f"rx-{i}",
                  position=ue_positions[i])
    scene.add(rx)
    # compute the path for that receiver
    paths = p_solver(scene=scene, max_depth=4, los=True,
                     specular_reflection=True,
                     diffuse_reflection=False,
                     refraction=True,) # Added diffraction and scattering effects, can be changed later
    
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

     # Manually build dictionaries for the paths object (instead of using .to_dict())
    path_dict = {}
    path_dict_array = {}
    for key in dir(paths):
        # Skip private attributes and callables
        if key.startswith("_") or callable(getattr(paths, key)):
            continue
        value = getattr(paths, key)
        # Save the raw value (similar to the old path_dict)
        path_dict[key] = value
        # Build the numpy-converted version (similar to the old path_dict_array)
        if isinstance(value, tf.Tensor):
            if not value.dtype.is_complex:
                path_dict_array[key] = tf.cast(value, tf.float64).numpy()
            else:
                path_dict_array[key] = value.numpy()
        else:
            path_dict_array[key] = value


    
    # append the path data to the position, which is the key of the dictionary
    #position_key = (ue_positions[i].numpy()[0],ue_positions[i].numpy()[1],ue_positions[i].numpy()[2])
    # TODO can we use position instead of position_key as key? that would be the best
    position_key = tuple(ue_grid[i])
    path_data[position_key]=path_dict
    path_data_array[position_key]=path_dict_array
    


    # Default parameters in the PUSCHConfig
    subcarrier_spacing = 15e3
    fft_size = 48

    # Disable normalization of delays
    #paths.normalize_delays = False
    # Get only the LoS path
    #_, tau = paths.cir(los=True, reflection=False)

    # Retrieve the channel impulse response as tensors 
    tau = paths.cir()

    # Compute frequencies of subcarriers and center around carrier frequency
    frequencies = subcarrier_frequencies(fft_size, subcarrier_spacing)

    
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
    
    # New 1.0.2
    # Compute channel frequency response
    h_freq = paths.cfr(frequencies=frequencies,
                    normalize=True, # Normalize energy
                    normalize_delays=True,
                    out_type="numpy")
    h_avg_power = tf.reduce_mean(tf.abs(h_freq)**2).numpy()
    h_freqency_data[position_key] = h_freq
    h_avg_power_data[position_key] = h_avg_power

    # remove the rx from the scene
    scene.remove(f"rx-{i}")

# Create a list to hold the combined data for each position key.
data_combined = []

# Assuming all dictionaries (h_avg_power_data, h_frequency_data, path_data, path_data_array)
for key in h_avg_power_data.keys():
    pos_data = {
        "position": key,
        "h_avg_power": h_avg_power_data.get(key),
        "h_frequency_data": h_freqency_data.get(key),
        "path_data": path_data_array.get(key),
    }
    data_combined.append(pos_data)

# Convert the list of dictionaries into a pandas DataFrame.
df = pd.DataFrame(data_combined)
df.to_csv("all_data.csv", index=True)
