# -*- coding: utf-8 -*-
import pandas as pd
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
        reach_boundaries = Parameter(
            displayName="Reach boundaries",
            name="reach_boundaries",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input"
        )
        out_table_path = Parameter(
            displayName="Output table save location",
            name="out_table_path",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input"
        )
        rasters = Parameter(
            displayName="Input rasters",
            name="rasters",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Input",
            multiValue=True
        )
        run_extract_multivalues = Parameter(
            displayName="Extract raster values to points?",
            name="run_extract_multivalues",
            datatype="GPBoolean",
            parameterType="Optional",
        )
        params = [input_gdb,
                  structure_points,
                  reach_boundaries,
                  out_table_path,
                  rasters,
                  run_extract_multivalues
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
        """The source code of the tool."""
        input_gdb = parameters[0].valueAsText
        structure_points = parameters[1].valueAsText
        reach_boundaries = parameters[2].valueAsText
        out_table_path = parameters[3].valueAsText
        rasters = parameters[4].valueAsText
        run_extract_multivalues = parameters[5].value

        #* Set the workspace/geodatabase to pull data
        env.workspace = input_gdb
        AddMessage(f"{input_gdb} is the input gdb")


        if run_extract_multivalues:
            AddMessage("Extracting values to points...")
            ExtractMultiValuesToPoints(structure_points, rasters)
            AddMessage("Points extracted")
        elif not run_extract_multivalues:
            AddMessage(f"Skipping extracting multivalues to points")


        #* Get unique IDs for reach boundaries
        object_id_list = []
        with SearchCursor(reach_boundaries, ["OBJECTID"]) as cursor:
            for row in cursor:
                object_id_list.append(row[0])
        
        dv_threshold_expression_list = [
            "DV_0_to_less_than_50",
            "DV_50_to_less_than_160",
            "DV_greater_than_160",
        ]

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
                selected_field_list.append(field.name)
            elif "_ArrivalTime" in field.name:
                selected_field_list.append(field.name)
            elif "_DV" in field.name:
                dv_field = field.name
                selected_field_list.append(field.name)
            elif "Pop2" in field.name:
                selected_field_list.append(field.name)
        selected_field_list = ';'.join(selected_field_list)

        dv_threshold_list = [
            f"{dv_field} >= 0 And {dv_field} < 50",
            f"{dv_field} >= 50 And {dv_field} < 160",
            f"{dv_field} >= 160",
        ]

        for object_id in object_id_list:
            AddMessage(f"Reach with OBJECTID {object_id} selected")
            for dv_expression in dv_threshold_list:
                selected_reach = SelectLayerByAttribute(
                                    in_layer_or_view=reach_boundaries,
                                    selection_type="NEW_SELECTION",
                                    where_clause=f"OBJECTID = {object_id}")

                selected_points = SelectLayerByLocation(
                                    in_layer=structure_points,
                                    overlap_type="COMPLETELY_WITHIN",
                                    select_features=selected_reach,
                                    selection_type="NEW_SELECTION"
                                    )

                subset_points = SelectLayerByAttribute(
                        in_layer_or_view=selected_points,
                        selection_type="SUBSET_SELECTION",
                        where_clause=f"{depth_field} > 0.1 And {depth_field} IS NOT NULL")

                dv_subset_points = SelectLayerByAttribute(
                        in_layer_or_view=subset_points,
                        selection_type="SUBSET_SELECTION",
                        where_clause=dv_expression
                    )
                AddMessage(f"The number of points selected is {GetCount(subset_points)}")
                #* Use field statistics to table to get stats
                if dv_expression == f"{dv_field} >= 0 And {dv_field} < 50":
                    out_tables_expression = dv_threshold_expression_list[0]
                elif dv_expression == f"{dv_field} >= 50 And {dv_field} < 160":
                    out_tables_expression = dv_threshold_expression_list[1]
                elif dv_expression == f"{dv_field} >= 160":
                    out_tables_expression = dv_threshold_expression_list[2]
                FieldStatisticsToTable(
                    in_table=dv_subset_points,
                    in_fields=selected_field_list,
                    out_location=input_gdb,
                    out_tables=f"NUMERIC REACH_ID_{object_id}_{out_tables_expression}",
                    out_statistics= "ALIAS Alias;COUNT Count;FIRSTQUARTILE FirstQuartile;SUM Sum;THIRDQUARTILE ThirdQuartile"
                )
        
        table_list = ListTables("REACH_ID*")
        new_field_list = ["Table_Name", "PAR_2AM", "PAR_2PM"]
        for table in table_list:
            field_name_list = []
            field_list = ListFields(table)
            for field in field_list:
                field_name_list.append(field.name)
            for new_field in new_field_list:
                if new_field not in field_name_list:
                    if new_field == "Table_Name":
                        AddField(
                            in_table=table,
                            field_name=new_field,
                            field_type="TEXT"
                        )
                    else:
                        AddField(
                            in_table=table,
                            field_name=new_field,
                            field_type="LONG"
                        )
        
        for table in table_list:
            CalculateField(
                in_table=table,
                field="Table_Name",
                expression='"' + table + '"'
                )
        # #* List tables, loop through tables, extracting necessary info, append to final table/dataframe, export to Excel
        table_list = ListTables("*")
        if "CombinedTable" in table_list:
            Delete("CombinedTable")
            AddMessage("Previously existing CombinedTable deleted. Generating new table for output results.")
        table_list = ListTables("*")
        table_template = table_list[0]
        CreateTable(
            out_path=input_gdb,
            out_name="CombinedTable",
            template=table_template
        )
        Append(
            inputs=table_list,
            target="CombinedTable",
            schema_type="TEST"
        )

        ExportTable("CombinedTable", out_table=f"{out_table_path}\\OutputDamStats.csv")
        AddMessage(f"CSV file exported to {out_table_path}\\OutputDamStats.csv")

        #* Pandas processing
        AddMessage(f"Processing CSV output...")

        df = pd.read_csv(f"{out_table_path}\\OutputDamStats.csv")
        df = df.rename(
            columns={
                "Count": "# of structures",
                "Alias": "Field"
            }
        )
        df["REACH_ID"] = None
        df["DV_THRESHOLD"] = None
        for object_id in object_id_list:
            for dv_threshold in dv_threshold_expression_list:
                if dv_threshold == "DV_0_to_less_than_50":
                    dv_threshold_num = "0 <= DV < 50"
                if dv_threshold == "DV_50_to_less_than_160":
                    dv_threshold_num = "50 <= DV < 160"
                if dv_threshold == "DV_greater_than_160":
                    dv_threshold_num = "DV > 160"
                df.loc[df["Table_Name"] == f"REACH_ID_{object_id}_{dv_threshold}", "REACH_ID"] = object_id
                df.loc[df["Table_Name"] == f"REACH_ID_{object_id}_{dv_threshold}", "DV_THRESHOLD"] = dv_threshold_num
                morning_pop_sum = df.loc[((df["Field"] == "Pop2amU65") | (df["Field"] == "Pop2amO65")) & (df["Table_Name"] == f"REACH_ID_{object_id}_{dv_threshold}"),"Sum"].sum()
                df.loc[df["Table_Name"] == f"REACH_ID_{object_id}_{dv_threshold}","PAR_2AM"] = morning_pop_sum
                afternoon_pop_sum = df.loc[((df["Field"] == "Pop2pmU65") | (df["Field"] == "Pop2pmO65")) & (df["Table_Name"] == f"REACH_ID_{object_id}_{dv_threshold}"),"Sum"].sum()
                df.loc[df["Table_Name"] == f"REACH_ID_{object_id}_{dv_threshold}","PAR_2PM"] = afternoon_pop_sum
        df = df.drop("Table_Name", axis=1)
        df = df.drop("Sum", axis=1)
        col = df.pop("REACH_ID")
        col2 = df.pop("DV_THRESHOLD")
        df.insert(1, "REACH_ID", col)
        df.insert(2, "DV_THRESHOLD", col2)
        field_drop_list = [
            "Pop2amU65",
            "Pop2amO65",
            "Pop2pmU65",
            "Pop2pmO65",
        ]
        df = df[df.Field.isin(field_drop_list) == False]
        df.to_csv(f"{out_table_path}\\OutputDamStatsEdit.csv")
        AddMessage(f"New CSV file exported to {out_table_path}\\OutputDamStatsEdit.csv ")

        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return
