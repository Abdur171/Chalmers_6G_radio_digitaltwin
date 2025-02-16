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

# Import Sionna RT components
from sionna.rt import load_scene, Transmitter, Receiver, PlanarArray, Camera

# For link-level simulations
from sionna.channel import cir_to_ofdm_channel, subcarrier_frequencies, OFDMChannel, ApplyOFDMChannel, CIRDataset
from sionna.nr import PUSCHConfig, PUSCHTransmitter, PUSCHReceiver
from sionna.utils import compute_ber, ebnodb2no, PlotBER
from sionna.ofdm import KBestDetector, LinearDetector
from sionna.mimo import StreamManagement


# Load integrated scene
scene = load_scene("Map/chalmers_map_v9.xml")



# Configure antenna array for all transmitters
scene.tx_array = PlanarArray(num_rows=1,
                             num_cols=1,
                             vertical_spacing=0.5,
                             horizontal_spacing=0.5,
                             pattern="tr38901",
                             polarization="V")

# Configure antenna array for all receivers
scene.rx_array = PlanarArray(num_rows=1,
                             num_cols=1,
                             vertical_spacing=0.5,
                             horizontal_spacing=0.5,
                             pattern="dipole",
                             polarization="cross")

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


# Create a receiver
rx7 = Receiver("rx7", [-40, -428, 1.3], [0.0, 0.0, 0.0])  #Chalmers coordinates
scene.add(rx7)

rx8 = Receiver("rx8", [60, -294, 1.6], [0.0, 0.0, 0.0])  #Chalmers coordinates
scene.add(rx8)

scene.frequency = 2.14e9 # in Hz; implicitly updates RadioMaterials

scene.synthetic_array = True # If set to False, ray tracing will be done per antenna element (slower for large arrays)

cm = scene.coverage_map(cm_cell_size=[1,1], num_samples=10e6, diffraction=True, scattering=True)
paths = scene.compute_paths(max_depth=4)

#Create new camera with different configuration

camera = Camera("my_cam", position=[150, 61, 90], look_at=[19,3,1.5])
scene.add(camera)
scene.preview(paths=paths,coverage_map=cm)

image = scene.render("preview", paths=paths, coverage_map=cm)

print("Source coordinates: ", paths.sources.numpy())
print("Transmitter coordinates: ", list(scene.transmitters.values())[0].position.numpy())

# Show the coordinates of the endpoints of all rays.
# These coincide with the location of the receivers.
print("Target coordinates: ",paths.targets.numpy())
print("Receiver coordinates: ",list(scene.receivers.values())[0].position.numpy())

# Show the types of all paths:
# 0 - LoS, 1 - Reflected, 2 - Diffracted, 3 - Scattered
# Note that Diffraction and scattering are turned off by default.
print("Path types: ", paths.types.numpy())

# Let us inspect a specific path in detail
path_idx = 1 # Try out other values in the range [0, 13]

# For a detailed overview of the dimensions of all properties, have a look at the API documentation
print(f"\n--- Detailed results for path {path_idx} ---")
print(f"Channel coefficient: {paths.a[0,0,0,0,0,path_idx, 0].numpy()}")
print(f"Propagation delay: {paths.tau[0,0,0,path_idx].numpy()*1e6:.5f} us")
print(f"Zenith angle of departure: {paths.theta_t[0,0,0,path_idx]:.4f} rad")
print(f"Azimuth angle of departure: {paths.phi_t[0,0,0,path_idx]:.4f} rad")
print(f"Zenith angle of arrival: {paths.theta_r[0,0,0,path_idx]:.4f} rad")
print(f"Azimuth angle of arrival: {paths.phi_r[0,0,0,path_idx]:.4f} rad")

"""## From Paths to Channel Impulse Responses

Once paths are computed, they can be transformed into channel impulse responses (CIRs).
The class method [apply_doppler](https://nvlabs.github.io/sionna/api/rt.html#Paths.apply_doppler) can simulate time evolution of the CIR based on arbitrary velocity vectors of all transmitters and receivers for a desired sampling frequency and number of time steps.
The class method [cir](https://nvlabs.github.io/sionna/api/rt.html#Paths.cir) generates the channel impulse responses which can be used by other components for link-level simulations in either time or frequency domains. The method also allows you to only consider certain types of paths, e.g., line-of-sight, reflections, etc.
"""

# Default parameters in the PUSCHConfig
subcarrier_spacing = 15e3
fft_size = 48

# Print shape of channel coefficients before the application of Doppler shifts
# The last dimension corresponds to the number of time steps which defaults to one
# as there is no mobility
print("Shape of `a` before applying Doppler shifts: ", paths.a.shape)

# Apply Doppler shifts
paths.apply_doppler(sampling_frequency=subcarrier_spacing, # Set to 15e3 Hz
                    num_time_steps=14, # Number of OFDM symbols
                    tx_velocities=[3.,0,0], # We can set additional tx speeds
                    rx_velocities=[0,7.,0]) # Or rx speeds

print("Shape of `a` after applying Doppler shifts: ", paths.a.shape)

a, tau = paths.cir()
print("Shape of tau: ", tau.shape)

"""Let us have a look at the channel impulse response for the 14 incoming paths from the simulation above."""

t = tau[0,0,0,:]/1e-9 # Scale to ns
a_abs = np.abs(a)[0,0,0,0,0,:,0]
a_max = np.max(a_abs)
# Add dummy entry at start/end for nicer figure
t = np.concatenate([(0.,), t, (np.max(t)*1.1,)])
a_abs = np.concatenate([(np.nan,), a_abs, (np.nan,)])

# And plot the CIR
plt.figure()
plt.title("Channel impulse response realization")

plt.stem(t, a_abs)
plt.xlim([0, np.max(t)])
plt.ylim([-2e-6, a_max*1.1])
plt.xlabel(r"$\tau$ [ns]")
plt.ylabel(r"$|a|$");

"""Note that the delay of the first arriving path is normalized to zero. This behavior can be changed using the Paths' call property ``normalize_delays``. For link-level simulations, it is recommended to work with normalized delays, unless perfect synchronization is explicitly desired."""

# Disable normalization of delays
paths.normalize_delays = False

# Get only the LoS path
_, tau = paths.cir(los=True, reflection=False)
print("Delay of first path without normalization: ", np.squeeze(tau))

paths.normalize_delays = True
_, tau = paths.cir(los=True, reflection=False)
print("Delay of first path with normalization: ", np.squeeze(tau))

"""The CIRs can now be loaded either in the time-domain or frequency-domain channel models, respectively.
Please see [cir_to_ofdm_channel](https://nvlabs.github.io/sionna/api/channel.wireless.html#sionna.channel.cir_to_ofdm_channel) and [cir_to_time_channel](https://nvlabs.github.io/sionna/api/channel.wireless.html#sionna.channel.cir_to_time_channel) for further details.
"""

# Compute frequencies of subcarriers and center around carrier frequency
frequencies = subcarrier_frequencies(fft_size, subcarrier_spacing)

# Compute the frequency response of the channel at frequencies.
h_freq = cir_to_ofdm_channel(frequencies,
                             a,
                             tau,
                             normalize=True) # Non-normalized includes path-loss

# Verify that the channel power is normalized
h_avg_power = tf.reduce_mean(tf.abs(h_freq)**2).numpy()

print("Shape of h_freq: ", h_freq.shape)
print("Average power h_freq: ", h_avg_power) # Channel is normalized

"""The frequency responses `h_freq` are now ready to be processed by the [ApplyOFDMChannel](https://nvlabs.github.io/sionna/api/channel.wireless.html#sionna.channel.ApplyOFDMChannel) Layer."""

# Placeholder for tx signal of shape
# [batch size, num_tx, num_tx_ant, num_ofdm_symbols, fft_size]
x = tf.zeros([h_freq.shape.as_list()[i] for i in [0,3,4,5,6]], tf.complex64)

no = 0.1 # noise variance

# Init channel layer
channel = ApplyOFDMChannel(add_awgn=True)

# Apply channel
y = channel([x, h_freq, no])

# [batch size, num_rx, num_rx_ant, num_ofdm_symbols, fft_size]
print(y.shape)

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

del cm # Free memory

# Exchange the num_tx and batchsize dimensions
a = np.transpose(a, [3, 1, 2, 0, 4, 5, 6])
tau = np.transpose(tau, [2, 1, 0, 3])

# Remove CIRs that have no active link (i.e., a is all-zero)
p_link = np.sum(np.abs(a)**2, axis=(1,2,3,4,5,6))
a = a[p_link>0.,...]
tau = tau[p_link>0.,...]

print("Shape of a:", a.shape)
print("Shape of tau: ", tau.shape)


class CIRGenerator:
    """Creates a generator from a given dataset of channel impulse responses.

    The generator samples ``num_tx`` different transmitters from the given path
    coefficients `a` and path delays `tau` and stacks the CIRs into a single tensor.

    Note that the generator internally samples ``num_tx`` random transmitters
    from the dataset. For this, the inputs ``a`` and ``tau`` must be given for
    a single transmitter (i.e., ``num_tx`` =1) which will then be stacked
    internally.

    Parameters
    ----------
    a : [batch size, num_rx, num_rx_ant, 1, num_tx_ant, num_paths, num_time_steps], complex
        Path coefficients per transmitter.

    tau : [batch size, num_rx, 1, num_paths], float
        Path delays [s] per transmitter.

    num_tx : int
        Number of transmitters

    Output
    -------
    a : [batch size, num_rx, num_rx_ant, num_tx, num_tx_ant, num_paths, num_time_steps], tf.complex
        Path coefficients

    tau : [batch size, num_rx, num_tx, num_paths], tf.float
        Path delays [s]
    """

    def __init__(self,
                 a,
                 tau,
                 num_tx):

        # Copy to tensorflow
        self._a = tf.constant(a, tf.complex64)
        self._tau = tf.constant(tau, tf.float32)
        self._dataset_size = self._a.shape[0]

        self._num_tx = num_tx

    def __call__(self):

        # Generator implements an infinite loop that yields new random samples
        while True:
            # Sample 4 random users and stack them together
            idx,_,_ = tf.random.uniform_candidate_sampler(
                            tf.expand_dims(tf.range(self._dataset_size, dtype=tf.int64), axis=0),
                            num_true=self._dataset_size,
                            num_sampled=self._num_tx,
                            unique=True,
                            range_max=self._dataset_size)

            a = tf.gather(self._a, idx)
            tau = tf.gather(self._tau, idx)

            # Transpose to remove batch dimension
            a = tf.transpose(a, (3,1,2,0,4,5,6))
            tau = tf.transpose(tau, (2,1,0,3))

            # And remove batch-dimension
            a = tf.squeeze(a, axis=0)
            tau = tf.squeeze(tau, axis=0)

            yield a, tau

"""We use Sionna's built-in [CIRDataset](https://nvlabs.github.io/sionna/api/channel.wireless.html#sionna.channel.CIRDataset) to initialize a channel model that can be directly used in Sionna's [OFDMChannel](https://nvlabs.github.io/sionna/api/channel.wireless.html#sionna.channel.OFDMChannel) layer."""

batch_size = 20 # Must be the same for the BER simulations as CIRDataset returns fixed batch_size

# Init CIR generator
cir_generator = CIRGenerator(a,tau,num_tx)
# Initialises a channel model that can be directly used by OFDMChannel layer
channel_model = CIRDataset(cir_generator,
                           batch_size,
                           num_rx,
                           num_rx_ant,
                           num_tx,
                           num_tx_ant,
                           75,
                           num_time_steps)

# Delete to free memory
del a, tau

# We need to enable sionna.config.xla_compat before we can use
# tf.function with jit_compile=True.
# See https://nvlabs.github.io/sionna/api/config.html#sionna.Config.xla_compat
sionna.config.xla_compat=False # not supported in CIRDataset

