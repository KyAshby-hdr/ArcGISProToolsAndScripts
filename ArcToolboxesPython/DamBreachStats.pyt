# -*- coding: utf-8 -*-

from arcpy import (Raster,
                   ListFields,
                   Parameter,
                   ListRasters,
                   AddMessage,
                   env,
                   SetProgressorLabel,
                   AddError,
                   ListTables,
                   ListFields,
                   )
from arcpy.sa import ExtractMultiValuesToPoints
from arcpy.management import (SelectLayerByAttribute,
                              SelectLayerByLocation,
                              GetCount,
                              FieldStatisticsToTable,
                              Append, 
                              Delete,
                              CreateTable,
                              AddField,
                              CalculateField
                              )
from arcpy.da import SearchCursor
from arcpy.conversion import ExportTable
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
        out_table_path = Parameter(
            displayName="Output table save location",
            name="out_table_path",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input"
        )
        # multipoint_new_fields = Parameter(
        #    displayName="New point field names",
        #    name="multipoint_new_fields",
        #    datatype="GPString",
        #    parameterType="Required",
        #    direction="Input",
        #    multiValue=True
        # )
        rasters = Parameter(
            displayName="Input rasters",
            name="rasters",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Input",
            multiValue=True
        )
        params = [input_gdb, structure_points, reach_boundaries, out_table_path, rasters]
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
        out_table_path = parameters[3].valueAsText
        # multipoint_new_fields = parameters[4].valueAsText
        rasters = parameters[4].valueAsText

        #* Set the workspace/geodatabase to pull data
        env.workspace = input_gdb
        AddMessage(f"{input_gdb} is the input gdb")

        AddMessage(rasters)
        # AddMessage(multipoint_new_fields)

        AddMessage("Extracting values to points...")
        ExtractMultiValuesToPoints(structure_points, rasters)
        AddMessage("Points extracted")


        #* Get unique IDs for reach boundaries
        attribute_list = []
        with SearchCursor(reach_boundaries, ["OBJECTID"]) as cursor:
            for row in cursor:
                attribute_list.append(row[0])

        #* Create list of all field names in the point structure shapefile/feature class

        #* Combine all field names into one long string, to check if substring "Depth" is included
        #* If no "Depth" substring/field found, process will terminate with error message
        AddMessage("Evaluating if 'Depth' in existing fields")
        point_field_name_list = []
        point_field_list = ListFields(structure_points)
        for field in point_field_list:
            point_field_name_list.append(field.name)
        combined_point_field_list = '\t'.join(point_field_name_list)
        if ("_Depth" not in combined_point_field_list) or ("_ArrivalTime" not in combined_point_field_list) or ("_DV" not in combined_point_field_list):
            AddError("Be sure point feature class or shapefile has _Depth, _ArrivalTime, and _DV in field or raster names.")
            return
        
        #* This will compile a list of fields that will be selected and field statistics generated for.
        #* It should find the _Depth, _ArrivalTime, and _DV fields.
        selected_field_list = []
        for field in point_field_list:
            if "_Depth" in field.name:
                depth_field = field.name
                AddMessage(f"{depth_field} will be used to subset the point selection")
                selected_field_list.append(field.name)
            elif "_ArrivalTime" in field.name:
                selected_field_list.append(field.name)
            elif "_DV" in field.name:
                selected_field_list.append(field.name)
        selected_field_list = ';'.join(selected_field_list)

        for attribute in attribute_list:
            AddMessage(f"The OBJECTID is {attribute}")
            selected_reach = SelectLayerByAttribute(
                                in_layer_or_view=reach_boundaries,
                                selection_type="NEW_SELECTION",
                                where_clause=f"OBJECTID = {attribute}")

            selected_points = SelectLayerByLocation(
                                in_layer=structure_points,
                                overlap_type="COMPLETELY_WITHIN",
                                select_features=selected_reach,
                                selection_type="NEW_SELECTION")

            subset_points = SelectLayerByAttribute(
                                in_layer_or_view=selected_points,
                                selection_type="SUBSET_SELECTION",
                                where_clause=f"{depth_field} > 0.1 And {depth_field} IS NOT NULL")
            AddMessage(f"The number of points selected is {GetCount(subset_points)}")
            #* Use field statistics to table to get stats
            FieldStatisticsToTable(subset_points, selected_field_list, input_gdb, f"NUMERIC OBJECTID_{attribute}")

        #* List tables, loop through tables, extracting necessary info, append to final table/dataframe, export to Excel
        table_list = ListTables("OBJECT*")
        unique_id_field_name = "Unique_ID"
        for table in table_list:
            field_name_list = []
            field_list = ListFields(table)
            for field in field_list:
                field_name_list.append(field.name)
            if unique_id_field_name not in field_name_list:
                AddMessage(f"{unique_id_field_name} field not found in {table}. Adding field...")
                AddField(table, unique_id_field_name, "TEXT")
            elif unique_id_field_name in field_name_list:
                AddMessage(f"{unique_id_field_name} found in {table}")

        for table in table_list:
            expression = '"' + table + '"'
            CalculateField(table,unique_id_field_name,expression=expression)

        table_list = ListTables("*")
        if "CombinedTable" in table_list:
            Delete("CombinedTable")
            AddMessage("Previously existing CombinedTable deleted. Generating new table for output results.")
        table_list = ListTables("*")
        table_template = table_list[0]
        CreateTable(input_gdb,"CombinedTable",table_template)
        Append(table_list,"CombinedTable","TEST") 

        ExportTable("CombinedTable", out_table=f"{out_table_path}\\OutputDamStats.csv")

        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return
