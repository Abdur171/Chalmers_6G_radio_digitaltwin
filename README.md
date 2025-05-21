# Digital Radio Twin of Chalmers for 6G Integrated Sensing, Positioning, and Communication

This repository contains the Pipeline for generating wave propagation data on a Digital 3D Environment. It is built with [Sionna RT](https://nvlabs.github.io/sionna/rt/index.html) (a ray tracing package in Python) and [Blender](https://www.blender.org/) (a 3D modeling tool). It includes the Digital Twin of Chalmers University, a grid field for User Equipment (UE) positions, and the Data Generation code (for the generation of path data, data handling, and storage).

## Installation

### Sionna RT
For the installation of [Sionna RT](https://github.com/NVlabs/sionna-rt?tab=readme-ov-file), follow their installation guide on their repository or see the [Sionna Installation Documentation](https://nvlabs.github.io/sionna/installation.html) on their website.  
> ℹ️ Both GPU and CPU work; see their installation guide for how to use either  
> ⚠️ Make sure to install LLVM by Dr.Jit (for CPU) and the correct version of Tensorflow

### Blender and Blender add-ons
The installation of [Blender](https://www.blender.org/download/) can be made from the Blender website. Make sure to install a version compatible with the listed add-ons. (Their latest stable version should be fine, but check the add-on requirements)

#### add-ons
- [BLOSM](https://github.com/vvoovv/blosm?tab=readme-ov-file) is used to generate real-world terrain data and can set a foundation for the development of a Digital Twin. For installation and other information, see their repository [BLOSM](https://github.com/vvoovv/blosm?tab=readme-ov-file) or their [detailed documentation](https://github.com/vvoovv/blosm/wiki/Documentation). (This add-on can be used in the creation of a new Digital twin, instead of the one provided in the repository)

- [Mitsuba-blender](https://github.com/mitsuba-renderer/mitsuba-blender?tab=readme-ov-file) enables the export of scenes in Blender as an XML file format, making it compatible with [Sionna RT](https://github.com/NVlabs/sionna-rt?tab=readme-ov-file). For installation, read the [Mitsuba-Blender installation & Update guide](https://github.com/mitsuba-renderer/mitsuba-blender/wiki/Installation-&-Update-Guide) or see their repository. (This add-on can be used if a new scene is created, instead of the provided XML files in the repository)

### Versions of the software that were used (newer versions might also work)
- [Python 3.10.9](https://www.python.org/downloads/release/python-3109/)
- [Sionna v1.0.2](https://github.com/NVlabs/sionna-rt/releases/tag/v1.0.2)
- [Blender 3.6 LTS](https://www.blender.org/download/lts/3-6/) (newer versions exist; make sure the version is compatible with the add-ons)
- Blender Add-ons:
  - [BLOSM](https://prochitecture.gumroad.com/l/blender-osm)
  - [Mitsuba-Blender v0.3.0](https://github.com/mitsuba-renderer/mitsuba-blender/releases/tag/v0.3.0) (works with Blender up to 3.6 LTS, newer versions of Mitsuba exist and should work with Blender versions up to 4.0)
- [MATLAB R2024a](https://se.mathworks.com/support/requirements/previous-releases.html) (for KPI analysis)

### Beginner tutorial on Sionna, Blender, OSM, and Mitsuba (a little bit old but can still be useful)
https://www.youtube.com/watch?v=7xHLDxUaQ7c&t=309s

  
## Tutorial

### Creating the model with Blender (optional)

- Begin by installing the required software (Blender and the Blender add-ons). For more installation information, please see the installation section above.

- Use BLOSM (OpenStreetMap) to import the desired map (both structures and roads). A tutorial can be seen in the video linked above, or in their [Documentation](https://github.com/vvoovv/blosm/wiki/Documentation). If the structural data is missing for the desired location, preset measurements of the user's choosing will be applied for these structures. The structures will need to be manually adjusted to reflect the real world.

- Make the desired changes and add desired details to the model (optional). Add the desired materials to all the surfaces and rename the materials for compatibility with Sionna. The material definitions can be found in the [Sionna Material Documentation](https://nvlabs.github.io/sionna/rt/api/radio_materials.html).  
> ℹ️ If you have never used Blender before, a beginner's guide could be helpful

- Topography can be added, either manually or with online data (optional).

- (Only if Topography is added) Use Blender's function "shrinkwrap" to attach the roads to the elevated ground.

- Use the code in the file "Grid_1x1_adjustable", located in the folder "Python code for Blender" in /Map, inside the Python text editor in Blender, while the desired road is selected, to generate a grid of meshes on the road. The grid field is adjustable in height above ground and width. After the grid has been generated, use the code "Save_Collection_as_CSV" located in the same folder, while the grid collection is selected, to save the coordinates of each grid point to a CSV file. To delete larger hierarchies in Blender, use the file "Delete_Collection".

- Export the map in an XML file format to be used with Sionna for the data generation.
> ⚠️⚠️⚠️ When exporting the XML file, remember to set the coordinates to "Y Forward" and "Z Up" and tick the box "Export IDs"

> ℹ️ Available models and exported XML files for these models can be found under /MAP and /Data_Generation, respectively, and can be used for the Ray Tracing simulation (data generation).

### Data Generation using Python
For information on how to use Sionna RT, see the [Sionna RT Documentation](https://nvlabs.github.io/sionna/rt/index.html).

- Install Sionna using pip install. For more installation information, please see the installation section above.

- The file "Data_Generation" under the folder "Data_Generation" is the complete code for the data generation and data storage. Make sure that the correct map and grid field (for UE positions) are used. Also, make sure the radio aspects of the signal, BSs, and UEs are configured as desired.

## Data Storage and Structure

- The generated data is sorted in a big folder "structured_data". On this Git, it is named simply "Data". It includes folders for each transmitter (tx_x), which in turn include folders for each receiver (rx_x). 
- Each receiver folder includes four files (if paths are present), which are:

  - Complex Channel Gains (a_coeffs.csv), α ∈ ℂ^{num_paths × (num_tx_ant × 2)}: Each row corresponds to one propagation path followed by the values for each antenna element at the transmitter side. 2 marks the alternation between real and imaginary parts of the complex channel gain for each antenna element.
  
  - Channel Frequency Response (h_frequency.csv), CFR ∈ ℂ^{num_subcarriers × (num_tx_ant × 2): Each row represents one subcarrier followed by the values for each antenna element at the transmitter side. 2 marks the alternation between real and imaginary parts of the CFR for each antenna element.

  - Other Path Parameters (other_params.csv), params ∈ ℝ^{num_paths × 6}: Additional path-specific parameters received from Sionna RT's path data. Each row corresponds to one propagation path followed by the propagation delay (_tau), Doppler shift (_doppler), azimuth AoA/AoD (_phi_r/_phi_t), and zenith AoA/AoD (_theta_r/_theta_t) in the stated order. 6 marks the total number of parameters listed in the file (changes if other available path parameters from Sionna RT's path data are used).

  - Reflection and Scattering Points (vertices.csv), vertices ∈ ℝ^{(max_depth × num_paths) × 4}: Each row corresponds to one interaction point per path, followed by the 3D coordinates (x, y, z). For example, in a two-bounce scenario, each path will contribute to two rows, one for each interaction point.
   
- The outer most folder (structured_data) includes the file (tx_rx_mapping.csv) for the positioning of every BS and UE, mapping ∈ ℝ^{(num_tx + num_rx) × 4}: Each row includes a unique identifier for the BS/UE followed by the 3D coordinates (x, y, z). BSs are listed first, followed by UEs.

## Git Files Explained
### Data
- Includes the generated data on the Digital twin of Chalmers campus; however, UEs are only placed around the entrance, "Kårhuset", and "Kårrestaurangen". The data can be directly used for KPI analysis. Includes folders for each transmitter, which in turn include folders for each receiver. 
- Each receiver folder named rx_x includes four files, which are: Complex Channel coefficients (a_coeffs.csv), Channel Frequency Response (h_frequency.csv), Other Path Parameters (other_params.csv), and Reflection and Scattering Points (vertices.csv).
- Inside outer most folder "structured_data", the positioning of BSs and UEs can be found (tx_rx_mapping.csv).

### Data Generation
- A folder containing the Python script and files used for the data generation. 
- The folder "Campus_XML" and "Entrance_XML" include the map information for the whole campus and the map information for only the entrance of the campus, respectively. 
- The "Code_validation.ipynb" file can be used for validating the simulation parameters, where a visualization of the BS and UE locations as well as the propagation paths can be seen.
- The "Data_Generation" file is the complete code necessary for data generation. Read the code and make the desired changes to the files and parameters being used.
- The "grid_points" files are for grid fields for both the entrance and the whole campus. 
- The "plot_grid" files are for visualization of the grids.

### Map
- The folder includes three different versions of maps from Blender:
1. "Chalmers_map_full" represents the map for the whole Chalmers Campus with roads across the entire map,
2. "Chalmers_map_entrance" is the same as the "Chalmers_map_full", but the roads are only placed around the entrance, "Kårhuset", and "Kårrestaurangen".
3. "Chalmers_toy_entrance" represents the map for only the entrance, "Kårhuset", and "Kårrestaurangen", and is referred to as the "toy model".

### Poster Designs and Thesis
- The Thesis and a Poster for the project are uploaded here. Have a look at our work!


