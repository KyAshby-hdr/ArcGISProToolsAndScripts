# -*- coding: utf-8 -*-

from arcpy import (Raster,
                   Parameter,
                   ListRasters,
                   AddMessage,
                   env,
                   Delete_management,
                   SetProgressorLabel,
                   )
from arcpy.sa import ExtractMultiValuesToPoints
from arcpy.management import SelectLayerByAttribute, SelectLayerByLocation, GetCount
from arcpy.da import SearchCursor

class Toolbox:
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Dam Stats"
        self.alias = "damStats"

        # List of tool classes associated with this toolbox
        self.tools = [dam_breach_tool]


class dam_breach_tool:
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Dam Breach Stats"
        self.description = "Calculates Q1 and Q3 statistics for depth, depth times velocity and arrival time for a dam breach scenario"

    def getParameterInfo(self):
        """Define the tool parameters."""
        input_gdb = Parameter(
            displayName="Input geodatabase",
            name="input_gdb",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input"
        )
        structure_points = Parameter(
            displayName="Structure points",
            name="structure_points",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input"
        )
        reach_boundaries = Parameter(
            displayName="Reach boundaries",
            name="reach_boundaries",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Input"
        )
        rasters = Parameter(
            displayName="List of rasters",
            name="rasters",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Input",
            multiValue=True
        )
        multipoint_new_fields = Parameter(
            displayName="New point field names",
            name="multipoint_new_fields",
            datatype="GPString",
            parameterType="Required",
            direction="Input",
            multiValue=True
        )
        params = [input_gdb, structure_points, reach_boundaries, rasters, multipoint_new_fields]
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
        input_gdb = parameters[0].valueAsText
        structure_points = parameters[1].valueAsText
        reach_boundaries = parameters[2].valueAsText
        rasters = parameters[3].valueAsText
        multipoint_new_fields = parameters[4].valueAsText

        # Set the workspace/geodatabase to pull data
        env.workspace = input_gdb
        AddMessage(f"{input_gdb} is the input gdb")
        multipoint_new_fields_list = multipoint_new_fields.split(";")
        AddMessage(f"{multipoint_new_fields_list}")
        # Get list of rasters
        rasters_list = rasters.split(";")
        AddMessage(f"{rasters_list}")

        #TODO Uncomment this mess you made below
        # Extract raster values and add them to point feature class
        # ExtractMultiValuesToPoints(structure_points, rasters)
        # AddMessage(f"Extract Multivalues to Points tool successful")

        # # Get unique IDs for reach boundaries
        # attribute_list = []
        # with SearchCursor(reach_boundaries, ["OBJECTID"]) as cursor:
        #     for row in cursor:
        #         attribute_list.append(row[0])
        
        # for attribute in attribute_list:
        #     AddMessage(f"The OBJECTID is {attribute}")
        #     selected_reach = SelectLayerByAttribute(
        #                         in_layer_or_view=reach_boundaries,
        #                         selection_type="NEW_SELECTION",
        #                         where_clause=f"OBJECTID = {attribute}")

        #     selected_points = SelectLayerByLocation(
        #                         in_layer=structure_points,
        #                         overlap_type="COMPLETELY_WITHIN",
        #                         select_features=selected_reach,
        #                         selection_type="NEW_SELECTION")

        #     subset_points = SelectLayerByAttribute(
        #                         in_layer_or_view=selected_points,
        #                         selection_type="SUBSET_SELECTION",
        #                         where_clause=f"")
        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return
