# -*- coding: utf-8 -*-

from arcpy import (Raster,
                   ListFields,
                   Parameter,
                   ListRasters,
                   AddMessage,
                   env,
                   SetProgressorLabel,
                   AddError,
                   ListTables
                   )
from arcpy.sa import ExtractValuesToPoints
from arcpy.management import SelectLayerByAttribute, SelectLayerByLocation, GetCount, FieldStatisticsToTable
from arcpy.da import SearchCursor

class Toolbox:
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Dam Stats"
        self.alias = "damStats"

        #* List of tool classes associated with this toolbox
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
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input"
        )
        #TODO Add filter to structure_points parameter to only include point shapefiles/feature classes
        reach_boundaries = Parameter(
            displayName="Reach boundaries",
            name="reach_boundaries",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input"
        )
        #TODO Add filter to reach_boundaries parameter to only include polygon shapefiles/feature classes
        #? This can be used eventually to include user specified field names
        # multipoint_new_fields = Parameter(
        #    displayName="New point field names",
        #    name="multipoint_new_fields",
        #    datatype="GPString",
        #    parameterType="Required",
        #    direction="Input",
        #    multiValue=True
        #)
        params = [input_gdb, structure_points, reach_boundaries]
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

        # #* Set the workspace/geodatabase to pull data
        # env.workspace = input_gdb
        # AddMessage(f"{input_gdb} is the input gdb")

        # #* Get unique IDs for reach boundaries
        # attribute_list = []
        # with SearchCursor(reach_boundaries, ["OBJECTID"]) as cursor:
        #     for row in cursor:
        #         attribute_list.append(row[0])

        # #* Create list of all field names in the point structure shapefile/feature class
        # point_field_name_list = []
        # point_field_list = ListFields(structure_points)
        # for field in point_field_list:
        #     point_field_name_list.append(field.name)

        # #* Combine all field names into one long string, to check if substring "Depth" is included
        # #* If no "Depth" substring/field found, process will terminate with error message
        # AddMessage("Evaluating if 'Depth' in existing fields")
        # combined_point_field_list = '\t'.join(point_field_name_list)
        # if "Depth" not in combined_point_field_list:
        #     AddError("No depth field in point feature class. Check raster selection or naming")
        #     return
        
        # #* Field with "Depth" in name will be assigned "depth_field" variable to be used in clause for subset selection tool
        # selected_field_list = []
        # for field in point_field_list:
        #     if "_Depth" in field.name:
        #         depth_field = field.name
        #         AddMessage(f"{depth_field} will be used as to subset the point selection")
        #         selected_field_list.append(field.name)
        #     elif "_ArrivalTime" in field.name:
        #         selected_field_list.append(field.name)
        #     elif "_DV" in field.name:
        #         selected_field_list.append(field.name)
        # selected_field_list = ';'.join(selected_field_list)
        # AddMessage(selected_field_list)


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
        #                         where_clause=f"{depth_field} > 0.1 And {depth_field} IS NOT NULL")
        #     AddMessage(f"The number of points selected is {GetCount(subset_points)}")
        #     #* Use field statistics to table to get stats
        #     FieldStatisticsToTable(subset_points, selected_field_list, input_gdb, f"NUMERIC OBJECTID_{attribute}")

        #* List tables, loop through tables, extracting necessary info, append to final table/dataframe, export to Excel
        table_list = ListTables("*")
        # for table in table_list:

        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return
