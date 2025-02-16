import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import cv2
import os
from sionna.rt import load_scene, Transmitter, Receiver, PlanarArray, Camera

# Load integrated scene from the xml file
scene = load_scene("Map/V2_XML/chalmers_map_v2.xml")
starting_point = [-50, 30, 1.2]
end_point = [55, -30, 1.2]  
initial_velocity = starting_point - end_point / np.norm(starting_point - end_point)

initial_state = [starting_point[0], initial_velocity[0],starting_point[1], initial_velocity[1]]
T = 0.1 # time step
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
time_steps = 100
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
    three_d_position = convert_2d_to_3d(two_d_position)
    # Update receiver position
    rx.position = three_d_position

    paths = scene.compute_paths()
    # Render frame
    frame_filename = f"frames/frame_{t:03d}.png"
    # Render the scene from the camera's viewpoint
    fig = scene.render("my_cam2", paths=paths)

    # Save the rendered figure as an image
    fig.savefig(frame_filename)
    plt.close(fig)  # Close the figure to free memory

    frame_files.append(frame_filename)
