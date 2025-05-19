## Prerequisites
### Hardware
- NVIDIA GPU (RTX 2080 or higher recommended) 
- 16GB+ RAM
- 50GB+ free storage for datasets
- One could run the toy model if the above requirments are not meant.

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
- One can also use the models that have been created under /MAP or the already exported XML file under 
/Toy_Model for the Ray Tracing.

### Data Generation using Python
- Using Python install Sionna. For more information on installation, please visit the website.
- The file test_structured_data.py is the complete code necessary for the data generation. 
- Please go through the code before running the file. Make sure the map file being imported is correct and the parameters are configured correctly. 
- Using the file, you can get all the desired data parameters in different files for each transmitter and reciever pair. 
- These parameter files can then be used for KPI analysis using Matlab. 