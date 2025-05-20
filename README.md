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

- [Mitsuba-blender](https://github.com/mitsuba-renderer/mitsuba-blender?tab=readme-ov-file) enables the export of the scene  in Blender in an XML file format, making it compatible with [Sionna RT](https://github.com/NVlabs/sionna-rt?tab=readme-ov- file). For installation, read the [Mitsuba-Blender installation & Update guide](https://github.com/mitsuba-renderer/mitsuba-blender/wiki/Installation-&-Update-Guide) or see their repository. (This add-on can be used if a new scene is created, instead of the provided XML files in the repository)

#### Versions of the software that were used (newer versions might also work)
- [Python 3.10.9](https://www.python.org/downloads/release/python-3109/)
- [Sionna v1.0.2](https://github.com/NVlabs/sionna-rt/releases/tag/v1.0.2)
- [Blender 3.6 LTS](https://www.blender.org/download/lts/3-6/) (newer versions exist; make sure the version is compatible with the add-ons)
- Required Blender Add-ons:
  - [BLOSM](https://prochitecture.gumroad.com/l/blender-osm)
  - [Mitsuba-Blender](https://github.com/mitsuba-renderer/mitsuba-blender/releases/tag/v0.3.0) (works with Blender up to 3.6 LTS, newer versions of Mitsuba exist and should work with Blender versions up to 4.0)
- MATLAB (for KPI analysis)

### Beginner tutorial on Sionna, Blender, OSM, and Mitsuba (a little bit old but can still be useful)
https://www.youtube.com/watch?v=7xHLDxUaQ7c&t=309s

  
## Tutorial

### Creating the model with Blender (optional)

- Begin by installing the required software (Blender and the Blender add-ons). For more installation information, please see the installation section.

- Use BLOSM (OpenStreetMap) to import the desired map. A tutorial can be seen in the video linked above, or in their [Documentation](https://github.com/vvoovv/blosm/wiki/Documentation). If the structural data is missing for the desired location, preset measurements of the user's choosing will be applied for these structures. The structures will need to be manually adjusted to reflect the real world.

- Make the desired changes and add desired details to the model (optional). Add the desired materials to all the surfaces and rename the materials for compatibility with Sionna. The material definitions can be found in the [Sionna Material Documentation](https://nvlabs.github.io/sionna/rt/api/radio_materials.html).  
> ℹ️ if you have never used Blender before, a beginner's guide could be helpful

- Topography can be added, either manually or with online data (optional).

- Export the map in an XML file format to be used with Sionna for the data generation.

> ℹ️ Available models and exported XML files for these models can be found under /MAP and /Data_Generation, respectively, and can be used for the Ray Tracing simulation (data generation).

### Data Generation using Python
For information on how to use Sionna RT, see the [Sionna RT Documentation](https://nvlabs.github.io/sionna/rt/index.html).

- Using Python, install Sionna. For more information on installation, please visit the website.
- The file Data_Generation under the folder Data_Generation is the complete code necessary for the data generation. 
- Please go through the code before running the file. Make sure the map file being imported is correct and the parameters are configured correctly. 
- Using the file, you can get all the desired data parameters in different files for each transmitter and receiver pair. 
- These parameter files can then be used for KPI analysis using MATLAB. 

## Git Files Explained
### Data
- Data that has been generated and can be directly used for KPI analysis. Includes folders for each transmitter, which in turn include a folder for each receiver. 
- Each receiver folder named rx_x includes four files, which are: Multi-path Fading Coefficients 
(a_coeffs.csv), Channel Frequency Responses (h_frequency.csv), Path Parameters (other_params.csv), and Reflection and Scattering Points (vertices.csv). 
- The outer most folder (Data) includes the file Base Staion/User Equipment Mapping (tx_rx_mapping.csv).

### Data Generation
- A folder that contains the Python script and map files necessary for data generation. 
- The folder Campus_XML and Entrance_XML includes the map for the whole campus and the map for only the entrance, respectively. 
- Code_validation.ipynb file that can be used for validating the parameter values generated to make sure they are correct.
- Data Generation file that is the complete code necessary for data generation. Please read the code beforehand and make changes to the parameters and files being imported as necessary. 
- grid_points files for both the entrance and the whole map. 
- plot_grid files for visualization of the grids.

### Extra
- The folder contains the code for creating a simulated path for user equipment and waypoint navigation. There is also a visualization of collision avoidance. These features have not been thoroughly tested or used in this project. 

### Map
- The folder includes three different versions of maps from Blender. One is the full map for the whole Chalmers Campus, one is the entrance for the Johanneberg Campus with details, and the other is the toy model for the entrance. 

### Poster Designs
- Posters for the project are uploaded here. Have a look at our work. 

## ReadME
Includes the necessary information to get familiarised with the project. Please feel free to contact us if you have any questions.


