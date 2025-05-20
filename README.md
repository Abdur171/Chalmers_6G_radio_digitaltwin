## Prerequisites
### Hardware
- NVIDIA GPU (RTX 2080 or higher recommended) 
- 16GB+ RAM
- 50GB+ free storage for datasets
- One could run the toy model if the above requirments are not met, it is also possible to only use the CPU.

### Software
- [Blender 3.3+](https://www.blender.org/download/)
- [Python 3.8+](https://www.python.org/downloads/)
- [Sionna RT](https://nvlabs.github.io/sionna/)
- MATLAB (for KPI analysis)
- Required Blender Add-ons:
  - [BLOSM](https://github.com/vvoovv/blosm)
  - [Mitsuba Exporter](https://github.com/mitsuba-renderer/mitsuba-blender)
  
  
## Tutorial
### Creating the model with Blender
- Begin with installing the required softwares. For more information on installation please visit the respective website for each software. 
- Once the installations are done, use BLOSM(OpenStreetMap) to import the desired map. 
- Using Blender, make the changes and add details to your map and rename the parameters for sionna ray tracing. 
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


