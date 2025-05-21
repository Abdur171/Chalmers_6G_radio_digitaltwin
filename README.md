# Digital Radio Twin of Chalmers for 6G Integrated Sensing, Positioning, and Communication

This repository contains the Pipeline for generating wave propagation data on a Digital 3D Environment. It is built with [Sionna RT](https://nvlabs.github.io/sionna/rt/index.html) (a ray tracing package in Python) and [Blender](https://www.blender.org/) (a 3D modeling tool). A Digital Twin of the University of Chalmers, the grid field for User Equipment positions, Data generation Code, as well as Data Handling and storage code, are included.

## Installation

### Sionna RT
For the installation of [Sionna RT](https://github.com/NVlabs/sionna-rt?tab=readme-ov-file), follow their installation guide on their repository or see the [Sionna Installation Documentation](https://nvlabs.github.io/sionna/installation.html) on their website.  
> ℹ️ Both GPU and CPU work; see their installation guide for how to use either  
> ⚠️ Make sure to install LLVM by Dr.Jit (for CPU) and the correct version of Tensorflow

### Blender and Blender add-ons
The installation of [Blender](https://www.blender.org/download/) can be made from the Blender website. Make sure to install a version compatible with the listed add-ons. (Their latest stable version should be fine, but check the add-ons requirements)

#### add-ons
- [BLOSM](https://github.com/vvoovv/blosm?tab=readme-ov-file) is used to generate real-world terrain data and can set a   foundation for the development of a Digital Twin. For installation and other information, see their repository [BLOSM](https://github.com/vvoovv/blosm?tab=readme-ov-file) or their [detailed documentation](https://github.com/vvoovv/blosm/wiki/Documentation). (This add-on can be used in the creation of a new Digital twin, instead of the one provided in the repository)

- [Mitsuba-blender](https://github.com/mitsuba-renderer/mitsuba-blender?tab=readme-ov-file) enables the export of the scene  in Blender in an XML file format, making it compatible with [Sionna RT](https://github.com/NVlabs/sionna-rt?tab=readme-ov-file). For installation, read the [Mitsuba-Blender installation & Update guide](https://github.com/mitsuba-renderer/mitsuba-blender/wiki/Installation-&-Update-Guide) or see their repository. (This add-on can be used if a new scene is created, instead of the provided XML files in the repository)

### Versions of the software that were used (newer versions might also work)
- [Python 3.10.9](https://www.python.org/downloads/release/python-3109/)
- [Sionna v1.0.2](https://github.com/NVlabs/sionna-rt/releases/tag/v1.0.2)
- [Blender 3.6 LTS](https://www.blender.org/download/lts/3-6/) (newer versions exist; make sure the version is compatible with the add-ons)
- Blender Add-ons:
  - [BLOSM](https://prochitecture.gumroad.com/l/blender-osm)
  - [Mitsuba-Blender v0.3.0](https://github.com/mitsuba-renderer/mitsuba-blender/releases/tag/v0.3.0) (works with Blender up to 3.6 LTS, newer versions of Mitsuba exist and should work with Blender versions up to 4.0)
- MATLAB (for KPI analysis)

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

- Use the code in the file"Grid_1x1_adjustable", located in the folder "Python code for Blender" in /Map, inside the Python text editor in Blender, while the desired road is selected, to generate a grid of meshes on the road. The grid field is adjustable in height above ground and width. After the grid has been generated, use the code "Save_Collection_as_CSV" located in the same folder, while the grid collection is selected, to save the coordinates of each grid point to a CSV file. To delete larger hierarchies in Blender, use the file "Delete_Collection".

- Export the map in an XML file format to be used with Sionna for the data generation.

> ℹ️ Available models and exported XML files for these models can be found under /MAP and /Data_Generation, respectively, and can be used for the Ray Tracing simulation (data generation).

### Data Generation using Python
For information on how to use Sionna RT, see the [Sionna RT Documentation](https://nvlabs.github.io/sionna/rt/index.html).

- Using Python, install Sionna. For more installation information, please see the installation section above.

- The file "Data_Generation" under the folder "Data_Generation" is the complete code for the data generation and data storage. Make sure that the correct map and grid field (for User Equipment (UE)) are used. Also, make sure that the parameters for the wave, Base stations, and UEs are configured as desired.

## Data Storage Structure

- Data that is generated is sorted in one big folder "Structured Data". On this Git, it is named simply "Data". It includes folders for each transmitter(tx_x) which in turn includes folder for each reciever. 
- Each reciever folder named rx_x includes four files which are:
1) Multi-path Fading Coefficients(a_coeffs.csv): Each row corresponds to
one propagation path, and the columns alternate between the real and imaginary
parts of the fading coefficients
2) Channel Frequency Responses (h_frequency.csv): Each row represents one subcarrier, and the columns provide the real and imaginary parts of the CFR for each BS-UE antenna pair.
3) Path Parameters (other_params.csv):Additional path-specific parameters, such as the time delay (_tau), Doppler shift(_doppler), azimuth AoA/AoD (_phi_r/_phi_t), and zenith AoA/AoD (_theta_r/_theta_t) were saved into the other_params.csv file. Each row corresponds to a single path, and each column represents one of the parameters in their respective order.
4) Reflection and Scattering Points (vertices.csv): Each row corresponds to one interaction point per path and includes the 3D co-ordinates (x, y, z), prefixed with a label indicating the reflection order (e.g., first bounce, second bounce, etc.). For example, in a two-bounce scenario, each path will contribute two rows, one for each interaction point.
- The outer most folder (Structured Data) includes the file Base Staion/User Equipment Mapping (tx_rx_mapping.csv). Each row includes a unique identifier followed by the (x, y, z) coordinates. BSs are listed first, followed by UEs.

## Git Files Explained
### Data
- Generated data on the Digital twin of Chalmers campus; however, UEs are only placed around the Entrance, "Kårhuset", and "Kårrestaurangen". The data can be directly used for KPI analysis. Includes folders for each transmitter, which in turn include a folder for each receiver. 
- Each receiver folder named rx_x includes four files, which are: Multi-path Fading Coefficients (a_coeffs.csv), Channel Frequency Responses (h_frequency.csv), Path Parameters (other_params.csv), and Reflection and Scattering Points (vertices.csv). In a separate folder, the data of Base Station/User Equipment Mapping (tx_rx_mapping.csv) can be found.

### Data Generation
- A folder that contains the Python script and files used for the data generation. 
- The folder "Campus_XML" and "Entrance_XML" include the map information for the whole campus and the map information for only the entrance of the campus, respectively. 
- The "Code_validation.ipynb" file can be used for validating the simulation, where a visualization of the simulation, including the BS and UE locations as well as the paths, can be seen.
- The "Data_Generation" file is the complete code necessary for data generation. Read the code and make the desired changes to the files and parameters being used.
- The "grid_points" files are for grid fields for both the entrance and the whole campus. 
- The "plot_grid" files are for visualization of the grids.

### Map
- The folder includes three different versions of maps from Blender. The first one, "Chalmers_map_full", is the map for the whole Chalmers Campus with roads across the entire map, the second one, "Chalmers_map_entrance", is the same as the first one, but the roads are only placed around the entrance, "Kårhuset", and "Kårrestaurangen". The last one, "Chalmers_toy_entrance" is the map for only the entrance, "Kårhuset", and "Kårrestaurangen", and is the "toy model".

### Poster Designs and Thesis
- The Thesis and a Poster for the project are uploaded here. Have a look at our work.


