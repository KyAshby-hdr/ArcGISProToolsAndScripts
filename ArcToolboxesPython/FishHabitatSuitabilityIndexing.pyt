# -*- coding: utf-8 -*-

import arcpy
from arcpy import Parameter, RasterToNumPyArray
from arcpy.da import TableToNumPyArray, SearchCursor
import pandas as pd
import numpy as np
from arcpy.sa import Raster


class Toolbox:
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = "toolbox"

        # List of tool classes associated with this toolbox
        self.tools = [Tool]


class Tool:
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Fish Habitat Suitability Indexing"
        self.description = ""

    def getParameterInfo(self):
        """Define the tool parameters."""
        batch_lookup_table = Parameter(
            displayName="Batch Lookup Table",
            name="batch_lookup_table",
            datatype="GPTableView",
            parameterType="Required",
            direction="Input"
        )
        depth_lookup_table = Parameter(
            displayName="Depth Lookup Table",
            name="depth_lookup_table",
            datatype="GPTableView",
            parameterType="Required",
            direction="Input"
        )
        substrate_feature_class = Parameter(
            displayName="Substrate Feature Class",
            name="substrate_feature_class",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input"
        )
        substrate_fc_code_field = Parameter(
            displayName="Substrate Feature Class Code Field",
            name="substrate_fc_code_field",
            datatype="Field",
            parameterType="Required",
            direction="Input"
        )
        substrate_lookup_code_field = Parameter(
            displayName="Substrate Lookup Code Field",
            name="substrate_lookup_code_field",
            datatype="Field",
            parameterType="Required",
            direction="Input"
        )
        substrate_lookup_table = Parameter(
            displayName="Substrate Lookup Table",
            name="substrate_lookup_table",
            datatype="GPTableView",
            parameterType="Required",
            direction="Input"
        )
        velocity_lookup_table = Parameter(
            displayName="Velocity Lookup Table",
            name="velocity_lookup_table",
            datatype="GPTableView",
            parameterType="Required",
            direction="Input"
        )
        cover_lookup_table = Parameter(
            displayName="Cover Lookup Table",
            name="cover_lookup_table",
            datatype="GPTableView",
            parameterType="Required",
            direction="Input"
        )
        cover_feature_class = Parameter(
            displayName="Cover Feature Class",
            name="cover_feature_class",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input"
        )
        cover_feature_class_code_field = Parameter(
            displayName="Cover Feature Class Code",
            name="cover_feature_class_code_field",
            datatype="Field",
            parameterType="Required",
            direction="Input"
        )
        cover_lookup_code_field = Parameter(
            displayName="Cover Lookup Code Field",
            name="cover_lookup_code_field",
            datatype="Field",
            parameterType="Required",
            direction="Input"
        )
        cellsize = Parameter(
            displayName="Cellsize",
            name="cellsize",
            datatype="analysis_cell_size",
            parameterType="Required",
            direction="Input"
        )
        processing_extent_feature_class = Parameter(
            displayName="Processing Extent Feature Class",
            name="processing_extent_feature_class",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input"
        )
        output_gdb = Parameter(
            displayName="Output GDB",
            name="output_gdb",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input"
        )
        input_gdb = Parameter(
            displayName="Input GDB",
            name="input_gdb",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input"
        )
        processing_extent_zonal_field = Parameter(
            displayName="Processing Extent Zonal Field",
            name="processing_extent_zonal_field",
            datatype="Field",
            parameterType="Required",
            direction="Input"
        )
        params = [
            # batch_lookup_table,
            depth_lookup_table,
            # velocity_lookup_table,
            # substrate_lookup_table,
            # substrate_lookup_code_field,
            # substrate_feature_class,
            # substrate_fc_code_field,
            # cover_lookup_table,
            # cover_lookup_code_field,
            # cover_feature_class,
            # cover_feature_class_code_field,
            # cellsize,
            # processing_extent_feature_class,
            # processing_extent_zonal_field,
            # output_gdb,
            input_gdb,
        ]
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
        depth_lookup_table = parameters[0].valueAsText
        input_gdb = parameters[1].valueAsText


        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return
