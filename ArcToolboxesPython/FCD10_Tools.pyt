# -*- coding: utf-8 -*-

import arcpy
from arcpy import Parameter, AddMessage, SetProgressorLabel
from arcpy.management import GetCount
from arcpy.da import SearchCursor
import shutil
import os
import fnmatch

class Toolbox:
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = "toolbox"

        # List of tool classes associated with this toolbox
        self.tools = [RetrieveRasters]


class RetrieveRasters:
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Retrieve rasters from folder"
        self.description = "Gets rasters from specified folder location using corresponding tile index shapefile or feature class"

    def getParameterInfo(self):
        """Define the tool parameters."""
        raster_file_location = Parameter(
            displayName="Rasters location",
            name="raster_file_location",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input"
        )
        tile_index_shp_fc = Parameter(
            displayName="Tile index shapefile or feature class",
            name="tile_index_shp_fc",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input"
        )
        tile_index_field = Parameter(
            displayName="Select tile index field",
            name="tile_index_field",
            datatype="Field",
            parameterType="Required",
            direction="Input"
        )
        selected_map = Parameter(
            displayName="Select map to add rasters",
            name="selected_map",
            datatype="GPMap",
            parameterType="Required",
            direction="Input"
        )
        tile_index_field.parameterDependencies = [tile_index_shp_fc.name]

        params = [raster_file_location, tile_index_shp_fc, tile_index_field, selected_map]
        return params

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        raster_file_location = parameters[0].valueAsText
        tile_index_shp_fc = parameters[1].valueAsText
        tile_index_field = parameters[2].valueAsText
        selected_map = parameters[3].valueAsText

        
        tile_index_list = []
        with SearchCursor(tile_index_shp_fc,tile_index_field) as cursor:
            for row in cursor:
                tile_index_list.append(row[0][3:])

        AddMessage(f"Tile index list compiled")

        aprx = arcpy.mp.ArcGISProject("CURRENT")
        map = aprx.listMaps(selected_map)[0]
        map_lyr_list = []
        for lyr in map.listLayers():
            map_lyr_list.append(lyr.name)
        
        for map_lyr in map_lyr_list:
            for index_num in tile_index_list:
                if index_num in map_lyr:
                    AddMessage(f"Raster with index {index_num} already included")
                    tile_index_list.remove(index_num)
        
        AddMessage(f"Tile index list modified, as needed")
        
        if (len(tile_index_list) > 0):
            AddMessage(f"Compiling list of selected rasters from specified source...")
            raster_tif_list = fnmatch.filter(os.listdir(raster_file_location), "*.tif")
            raster_path_list = []
            for index_num in tile_index_list:
                for raster_tif in raster_tif_list:
                    if index_num in raster_tif:
                        raster_path_list.append(os.path.join(raster_file_location, raster_tif))

            
            for raster_path in raster_path_list:
                map.addDataFromPath(raster_path)
        elif (len(tile_index_list) == 0):
            AddMessage(f"Rasters already included in selected map Contents pane")
        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return
