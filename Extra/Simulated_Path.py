# -*- coding: utf-8 -*-

import os 

import tensorflow as tf
import sionna
import pickle

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
# define starting point and end point
# notice that the end point is just a reference point
# it won't reaches the end point
starting_point = [-50, 30, 1.2]
end_point = [55, -30, 1.2]  
initial_velocity = starting_point - end_point / np.norm(starting_point - end_point)
# the average velocity for human is 0.8m/s
initial_velocity = 0.8* initial_velocity/np.norm(initial_velocity)
initial_state = [starting_point[0], initial_velocity[0],starting_point[1], initial_velocity[1]]
T = 1 # time step
# constant velocity model
# X = F*X + w
sigma_v = 0.1
F = np.array([[1, T, 0, 0],
              [0, 1, 0, 0],
              [0, 0, 1, T],
              [0, 0, 0, 1]])
Q = np.array([[T**4/4, T**3/2, 0, 0],
              [T**3/2, T**2, 0, 0],
              [0, 0, T**4/4, T**3/2],
              [0, 0, T**3/2, T**2]]) * sigma_v**2
time_steps = 10
x = initial_state

# Initialize transmitter and receiver
scene.tx_array = PlanarArray(num_rows=4, num_cols=4, vertical_spacing=0.5, horizontal_spacing=0.5, pattern="tr38901", polarization="V")
scene.rx_array = PlanarArray(num_rows=1, num_cols=1, vertical_spacing=0.5, horizontal_spacing=0.5, pattern="iso", polarization="V")

tx = Transmitter("tx", [1.5, 36, 16], [0.0, 0.0, 0.0])
scene.add(tx)

rx = Receiver("rx", starting_point)
# Add camera
my_cam = Camera("my_cam2", position=[150, 61, 90], look_at=[19, 3, 1.5])
scene.add(my_cam)
scene.add(rx)


# Iterate through time steps
frame_files = []
for t in range(time_steps):
    # updated state
    x = F @ x + np.random.multivariate_normal(np.zeros(4), Q)

    two_d_position = [x[0], x[2]]
    # TODO need to convert from 2D to 3D by reading the position file
    three_d_position = convert_2d_to_3d(two_d_position)
    # Update receiver position
    rx.position = three_d_position

    paths = scene.compute_paths()

    position_key = t
    path_dict = paths.to_dict()
    path_data[position_key]=path_dict
        # Default parameters in the PUSCHConfig
    subcarrier_spacing = 15e3
    fft_size = 48
    # Apply Doppler shifts if there are velocity
    # for now, we are not using this
    # apply_doppler Apply Doppler shifts to all paths according to the velocities
    # of objects in the scene as well as the provided transmitter and receiver velocities.
    paths.apply_doppler(sampling_frequency=subcarrier_spacing, # Set to 15e3 Hz
                    num_time_steps=14, # Number of OFDM symbols
                    tx_velocities=[3.,0,0], # We can set additional tx speeds
                    rx_velocities=[0,7.,0]) # Or rx speeds
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

    # Render frame
    frame_filename = f"frames/frame_{t:03d}.png"
    # Render the scene from the camera's viewpoint
    fig = scene.render("my_cam2", paths=paths)

    # Save the rendered figure as an image
    fig.savefig(frame_filename)
    plt.close(fig)  # Close the figure to free memory

    frame_files.append(frame_filename)
with open("h_frequency_data.pkl", "wb") as f:
    pickle.dump(h_freqency_data, f)
# Save the h_avg_power_data
with open("h_avg_power_data.pkl", "wb") as f:
    pickle.dump(h_avg_power_data, f)
# Save the path data
with open("path_data.pkl", "wb") as f:
    pickle.dump(path_data, f)
# Save the path data array
with open("path_data_array.json", "wb") as f:
    pickle.dump(path_data_array, f)

