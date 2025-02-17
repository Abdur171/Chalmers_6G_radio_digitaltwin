# -*- coding: utf-8 -*-

import os 

import tensorflow as tf
import sionna

# Set random seed for reproducibility
sionna.config.seed = 42

# Commented out IPython magic to ensure Python compatibility.
# %matplotlib inline
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


# Load integrated scene from the xml file
scene = load_scene("Map/V2_XML/chalmers_map_v2.xml")
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
cm = scene.coverage_map(cm_cell_size=[1,1], num_samples=10e6, diffraction=True, scattering=True)

# initiate the path data dictionary
path_data = {}
# initiate the CIR data dictionary
# notice that they are separated because they are going to be used by different people
h_freqency_data = {}
h_avg_power_data = {}
# define a grid of positions for data collection
ue_grid= []
# Define the grid for the UE positions
# TODO: Define the grid for the UE positions at 50cm resolution for now
# This grid should be obtained from Blender
ue_positions = tf.squeeze(ue_grid)
# Create batch_size receivers for the data generation
for i in range(len(ue_positions)):
    rx = Receiver(name=f"rx-{i}",
                  position=ue_positions[i])
    scene.add(rx)
    # compute the path for that receiver
    paths = scene.compute_paths(max_depth=4)
    # convert the paths to dictionary for data storage
    path_dict = paths.to_direct()
    # append the path data to the position, which is the key of the dictionary
    path_data[ue_positions[i]]=path_dict

    # Default parameters in the PUSCHConfig
    subcarrier_spacing = 15e3
    fft_size = 48
    # Apply Doppler shifts
    paths.apply_doppler(sampling_frequency=subcarrier_spacing, # Set to 15e3 Hz
                    num_time_steps=14, # Number of OFDM symbols
                    tx_velocities=[3.,0,0], # We can set additional tx speeds
                    rx_velocities=[0,7.,0]) # Or rx speeds


    a, tau = paths.cir()
    # Disable normalization of delays
    paths.normalize_delays = False
    # Get only the LoS path
    _, tau = paths.cir(los=True, reflection=False)

    paths.normalize_delays = True
    _, tau = paths.cir(los=True, reflection=True, diffraction=False, scattering=False)
    # Compute frequencies of subcarriers and center around carrier frequency
    frequencies = subcarrier_frequencies(fft_size, subcarrier_spacing)

    # Compute the frequency response of the channel at frequencies.
    h_freq = cir_to_ofdm_channel(frequencies,
                             a,
                             tau,
                             normalize=True) # Non-normalized includes path-loss

    # Verify that the channel power is normalized
    h_avg_power = tf.reduce_mean(tf.abs(h_freq)**2).numpy()
    h_freqency_data[ue_positions[i]] = h_freq.numpy()
    h_avg_power_data[ue_positions[i]] = h_avg_power

    # remove the rx from the scene
    scene.remove(rx)

# Save the path data
with open("path_data.json", "w") as f:
    json.dump(path_data, f)
# Save the CIR data
with open("h_frequency_data.json", "w") as f:
    json.dump(h_freqency_data, f)

