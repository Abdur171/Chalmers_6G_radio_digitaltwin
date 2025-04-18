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
scene = load_scene("Undergraduate_Thesis_Project/Toy_Model/toy_XML/Chalmers_entrance.xml")
# Set the carrier frequency 
fc = 3.5e9 # from band n78 in 3GPP TS 38.104. Can be changed later when testing out mmWave or sub-THz
scene.frequency = fc
# Define the wavelength of the signal and calculate the antenna distance 
c = 3e8
Lambda = c/fc
antenna_dist = Lambda/2
# Configure antenna array for all transmitters
scene.tx_array = PlanarArray(num_rows=2, num_cols=2, vertical_spacing=0.5, horizontal_spacing=0.5,
                             pattern="tr38901", polarization="H")  # changed to cross-polarization as described in 3GPP TR 38.901
# Configure antenna array for all receivers
scene.rx_array = PlanarArray(num_rows=1, num_cols=1, vertical_spacing=antenna_dist, horizontal_spacing=antenna_dist,
                             pattern="tr38901", polarization="H")

# Create transmitter 
tx1 = Transmitter("tx1", [0.5, -3, 18], [0.0, 0.0, 0.0])   # Toymodel coordinates
scene.add(tx1)

# Uncomment and add additional transmitters as needed
# tx2 = Transmitter("tx2", [0.5, -343, 30], [0.0, 0.0, 0.0])
# scene.add(tx2)
# tx3 = Transmitter("tx3", [65, -181.5, 35], [0.0, 0.0, 0.0])
# scene.add(tx3)
# tx4 = Transmitter("tx4", [22, 182, 28], [0.0, 0.0, 0.0])
# scene.add(tx4)
# tx5 = Transmitter("tx5", [-147, 327, 28], [0.0, 0.0, 0.0])
# scene.add(tx5)
# tx6 = Transmitter("tx6", [-212, -33, 15], [0.0, 0.0, 0.0])
# scene.add(tx6)

<<<<<<< HEAD
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
file_path = "Undergraduate_Thesis_Project/Toy_Model/grid_points_toy_1x1.csv" 
=======
# Load grid positions from CSV file and create list of UE positions
file_path = "Toy_Model/grid_points_toy_1x1.csv" 
>>>>>>> 4c459b992a444e44f2525699a9abc2e53fa18df6
grid_position = pd.read_csv(file_path)
ue_grid = grid_position[['X','Y','Z']].values.tolist()
ue_positions = tf.squeeze(ue_grid)

# Create a list to hold combined data for each receiver position
data_combined = []

# Specify the desired parameters to extract from each paths object
desired_parameters = [
    "a",          # Channel coefficients
    "doppler",    # Doppler shift (if computed)
    "interactions",  # Interactions information
    "num_rx",     # Number of receiver antennas/path-related info
    "num_tx",     # Number of transmitter antennas/path-related info
    "objects",    # Objects (e.g., reflecting or diffracting objects)
    "phi_r",      # Azimuth angles of arrival
    "phi_t",      # Azimuth angles of departure
    "primitives", # Primitive shapes used in the scene
    "rx_array",   # Receiver antenna array details
    "tau",        # Path delays
    "theta_t",    # Zenith angles of departure
    "theta_r",    # Zenith angles of arrival
    "tx_array",   # Transmitter antenna array details
    "vertices"    # Vertices used in path computations
]

# Dictionaries for storing additional channel data
h_freqency_data = {}
h_avg_power_data = {}

# Create batch_size receivers for the data generation
p_solver = PathSolver()

# Loop over a subset of positions (adjust the range as needed)
for i in range(len(ue_positions[0:6])):
    rx = Receiver(name=f"rx-{i}", position=ue_positions[i])
    scene.add(rx)
    
    # Compute the paths for the given receiver
    paths = p_solver(scene=scene, max_depth=4, los=True,
                     specular_reflection=True,
                     diffuse_reflection=False,
                     refraction=True)
    
    # Organize the desired path parameters into a dictionary
    organized_params = {}
    for param in desired_parameters:
        if hasattr(paths, param):
            value = getattr(paths, param)
            # Convert TensorFlow tensors to numpy arrays; if not complex, cast to float64
            if isinstance(value, tf.Tensor):
                if not value.dtype.is_complex:
                    organized_params[param] = tf.cast(value, tf.float64).numpy()
                else:
                    organized_params[param] = value.numpy()
            else:
                organized_params[param] = value
        else:
            path_dict_array[key] = value

    # Flatten the receiver's position into a 1D list of floats 
    pos_arr = rx.position.numpy()
    pos_arr = np.squeeze(pos_arr)  # now shape [3], not [1,3]
    position_key = tuple(pos_arr)

    path_data[position_key] = path_dict
    path_data_array[position_key] = path_dict_array
    



    """# convert the paths to dictionary for data storage
    path_dict_array = {}
    path_dict = paths.to_dict()
    # TODO convert the path_dict to a dictionary with numpy arrays
    # for instance path_dict_array['path_1'] = path_dict['path_1'].numpy()
    # we need to do this for all the keys in the path_dict
    # we also need to confirm that data at every level are numpy arrays
    # Convert all TensorFlow tensors in path_dict to numpy arrays
    for keys in path_dict:
        if isinstance(path_dict[keys], tf.Tensor) and not path_dict[keys].dtype.is_complex:
            path_dict_array[keys] = tf.cast(path_dict[keys], tf.float64).numpy()
        elif isinstance(path_dict[keys], tf.Tensor):
            path_dict_array[keys] = path_dict[keys].numpy()
        else:
            path_dict_array[keys] = path_dict[keys]
    """

    
    # append the path data to the position, which is the key of the dictionary
    #position_key = (ue_positions[i].numpy()[0],ue_positions[i].numpy()[1],ue_positions[i].numpy()[2])
    # TODO can we use position instead of position_key as key? that would be the best
    position_key = tuple(ue_grid[i])
    path_data[position_key]=path_dict
    path_data_array[position_key]=path_dict_array
    


    # Default parameters in the PUSCHConfig
    subcarrier_spacing = 15e3
    fft_size = 48

    # Retrieve the channel impulse response as tensors 
    tau = paths.cir()

    # Compute frequencies of subcarriers
    frequencies = subcarrier_frequencies(fft_size, subcarrier_spacing)
    
    # Compute channel frequency response (normalized over energy and delays)
    h_freq = paths.cfr(frequencies=frequencies,
                       normalize=True,
                       normalize_delays=True,
                       out_type="numpy")
    h_avg_power = tf.reduce_mean(tf.abs(h_freq)**2).numpy()
    h_freqency_data[position_key] = h_freq
    h_avg_power_data[position_key] = h_avg_power

    # Remove the receiver from the scene (for the next iteration)
    scene.remove(f"rx-{i}")

    # Combine the data for this receiver
    pos_data = {"position": position_key,
                "h_avg_power": h_avg_power_data.get(position_key),
                "h_frequency_data": h_freqency_data.get(position_key)}
    # Add each of the desired path parameters as separate entries
    for param in desired_parameters:
        pos_data[param] = organized_params.get(param)
    
    data_combined.append(pos_data)

# Convert the combined data list into a pandas DataFrame and save to CSV
df = pd.DataFrame(data_combined)
df.to_csv("all_data.csv", index=True)