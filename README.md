# ArcGIS Pro Tools And Scripts

This repository contains scripts, toolboxes and other code to perform various functions and processes in ArcGIS Pro.

Below list the various folders and the kinds of code they contain:

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
