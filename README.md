# ArcGIS Pro Tools And Scripts

This repository contains scripts, toolboxes and other code to perform various functions and processes in ArcGIS Pro.

Scroll down to find instructions for the various toolboxes

## Arc Toolboxes - Python

This is where Python Arc Toolboxes are stored and managed.

### Boise River Assessment Tools

This is a python toolbox, which currently holds the following tools:

#### Calculate HSI

This tool calculates Habitat Suitability Index (HSI) rasters for adult, juvenile, spawn, and (in some cases) fry fish for the following species:

- Brown Trout
- Rainbow Trout
- Mountain Whitefish
- Sculpin

The HSI rasters are created from velocity and depth rasters, and calculated using habitat suitability curves provided from academic sources.

Basic use of the tool is as follows:

1. Export your depth and velocity rasters to a file geodatabase in ArcGIS Pro. Make sure the depth and velocity rasters start with "Dep" or "Vel", respectively, followed by a unique identifier for each depth and velocity pair. For example, if you have depth and velocity results from a simulated 100 cfs flow, you could name each raster "Dep100" and "Vel100".
2. Upon opening the tool, specify the file geodatabase where you have the velocity and depth rasters saved.
3. Check the boxes for which fish species and life stages you would like to calculate HSI rasters.
4. Hit "Run". Run time is mainly dependent on the size and resolution of the velocity and/or depth rasters.

### Dam Breach Stats

This is a Python toolbox, which currently holds the following tools:

#### Dam Breach Stats
This tool can process statistics for multiple dam breach scenarios. Important information for using this tool can be found below:
1. It is recommended that the spatial point data for the structures be saved as a feature class in a geodatabase. Shapefiles have limitations that prevent the tool from working as intended.
2. When using the tool, be sure the spatial point data being used in the tool is not included on the working map. You can select the point spatial data by navigating to the geodatabase where the spatial data is stored. Selecting the linked data in the map using the dropdown menu will cause the tool to fail.
3. For each scenario, raster names should include "_Depth", "_ArrivalTime", and "_DV". Text can be included before or after. The names just need to include the text in each raster, respectively. The tool will throw an error otherwise.
4. The tool will export a .csv file titled "OutputDamStats.csv". This contains the statistics data for the dam breach scenario.

If you have any questions or problems using the tools described above, please reach out to Kyler Ashby
