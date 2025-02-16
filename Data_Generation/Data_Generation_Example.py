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
CIR_data = {}
# define a grid of positions for data collection
ue_grid= []
# Define the grid for the UE positions
# TODO: Define the grid for the UE positions
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

    """## From Paths to Channel Impulse Responses
    Once paths are computed, they can be transformed into channel impulse responses (CIRs).
    The class method [apply_doppler](https://nvlabs.github.io/sionna/api/rt.html#Paths.apply_doppler) can simulate time evolution of the CIR based on arbitrary velocity vectors of all transmitters and receivers for a desired sampling frequency and number of time steps.
    The class method [cir](https://nvlabs.github.io/sionna/api/rt.html#Paths.cir) generates the channel impulse responses which can be used by other components for link-level simulations in either time or frequency domains. The method also allows you to only consider certain types of paths, e.g., line-of-sight, reflections, etc.
    """

    # data generation related code
    target_num_cirs = 50000 # Defines how many different CIRS are generated.
    # Remark: some path are removed if no path was found for this position

    max_depth = 5
    min_gain_db = -130 # in dB / ignore any position with less than -130 dB path gain
    max_gain_db = 0 # in dB / ignore any position with more than 0 dB path gain

    # Sample points within a 10-400m radius around the transmitter
    min_dist = 10 # in m
    max_dist = 400 # in m

    # Placeholder to gather channel impulse reponses
    a = None
    tau = None

    # Each simulation returns batch_size_cir results
    num_runs = int(np.ceil(target_num_cirs/batch_size_cir))
    for idx in range(num_runs):
        print(f"Progress: {idx+1}/{num_runs}", end="\r")

        # Sample random user positions
        ue_pos, _ = cm.sample_positions(
                        num_pos=batch_size_cir,
                        metric="path_gain",
                        min_val_db=min_gain_db,
                        max_val_db=max_gain_db,
                        min_dist=min_dist,
                        max_dist=max_dist)
        ue_pos = tf.squeeze(ue_pos)

        # Update all receiver positions
        for idx in range(batch_size_cir):
            scene.receivers[f"rx-{idx}"].position = ue_pos[idx]

    # Simulate CIR
    paths = scene.compute_paths(
                    max_depth=max_depth,
                    diffraction=True,
                    num_samples=1e6) # shared between all tx in a scene

    # Transform paths into channel impulse responses
    paths.reverse_direction = True # Convert to uplink direction
    paths.apply_doppler(sampling_frequency=subcarrier_spacing,
                        num_time_steps=14,
                        tx_velocities=[0.,0.,0],
                        rx_velocities=[3.,3.,0])

    # We fix here the maximum number of paths to 75 which ensures
    # that we can simply concatenate different channel impulse reponses
    a_, tau_ = paths.cir(num_paths=75)
    del paths # Free memory

    if a is None:
        a = a_.numpy()
        tau = tau_.numpy()
    else:
        # Concatenate along the num_tx dimension
        a = np.concatenate([a, a_], axis=3)
        tau = np.concatenate([tau, tau_], axis=2)

    # Store the CIR data
    path_data[ue_positions[i]]=(a,tau)

    # remove the rx from the scene
    scene.remove(rx)

# Save the path data
with open("path_data.json", "w") as f:
    json.dump(path_data, f)
# Save the CIR data
with open("CIR_data.json", "w") as f:
    json.dump(CIR_data, f)

