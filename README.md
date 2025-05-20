This repository contains the Pipeline for generating wave propagation data on a Digital 3D Environment. It is built with [Sionna RT](https://nvlabs.github.io/sionna/rt/index.html) (a ray tracing package in Python) and [Blender](https://www.blender.org/) (a 3D modeling tool). A Digital Twin of the University of Chalmers, the grid field for User Equipment positions, Data generation Code, as well as Data Handling and storage code, are included.

## Installation

### Sionna RT
For the installation of [Sionna RT](https://github.com/NVlabs/sionna-rt?tab=readme-ov-file), follow their installation guide on their repository or see the [Sionna Installation Documentation](https://nvlabs.github.io/sionna/installation.html) on their website.  
> ℹ️ Both GPU and CPU work; see their installation guide for how to use either  
> ⚠️ Make sure to install LLVM by Dr.Jit and the correct version of Tensorflow

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
### Creating the model with Blender
- Begin by installing the required software. For more installation information, please visit the respective website for each software. 
- Use BLOSM(OpenStreetMap) to import the desired map. 
- Using Blender, make the changes and add details to your map, and rename the parameters for sionna ray tracing. 
- Once this is done, export the map in XML file to be used for Sionna Ray Tracing.
- One can also use the models that have been created under /MAP or the already exported XML files under 
/Data_Generation for the Ray Tracing.

### Data Generation using Python
- Using Python install Sionna. For more information on installation, please visit the website.
- The file Data_Generation under folder Data_Generation is the complete code necessary for the data generation. 
- Please go through the code before running the file. Make sure the map file being imported is correct and the parameters are configured correctly. 
- Using the file, you can get all the desired data parameters in different files for each transmitter and reciever pair. 
- These parameter files can then be used for KPI analysis using Matlab. 

## Git files Explained
### Data
- Data that has been generated and can be directly used for KPI analysis. Includes folders for each transmitter which in turn includes folder for each reciever. 
- Each reciever folder named rx_x includes four files which are : Multi-path Fading Coefficients 
(a_coeffs.csv), Channel Frequency Responses (h_frequency.csv), Path Parameters (other_params.csv) and Reflection and Scattering Points (vertices.csv). 
- The outer most folder (Data) includes the file Base Staion/User Equipment Mapping (tx_rx_mapping.csv).

### Data Generation
- Folder that contains the python script and map files necessary for data generation. 
- The folder Campus_XML and Enterance_XML includes the map for the whole campus and map for only the enterance respectively. 
- Code_validation.ipynb file that can be used for validating the parameter values generated to make sure they are correct.
- Data Generation file that is the complete code necessary for data generation. Please read the code beforehand and make changes to the parameters and files being imported as necessary. 
- grid_points files for both the enterance and the whole map. 
- plot_grid files for visualization of the grids.

### Extra
- Folder contains the code for creating simulated path for user equipment and waypoint navigation. There is also visualtization of collision avoidence. These features have not been thorughly tested or used in this project. 

### Map
- Folder includes three different versions of maps from blender. One is the full map for the whole Chalmers Campus, one is the enterance for the Johanneberg Campus with details and the other is the toy model for the enterance. 

### Poster Designs
- Posters for the project are uploaded here, have a look at our work. 

## ReadME
Includes the necessary information to get familiarised with the Git for our project. Please feel free to contact us if you have any questions.


