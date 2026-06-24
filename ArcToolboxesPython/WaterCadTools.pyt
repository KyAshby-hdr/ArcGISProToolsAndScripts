# -*- coding: utf-8 -*-

import arcpy


class Toolbox:
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Tools used for WaterCAD"
        self.alias = "WaterCadTools"

        # List of tool classes associated with this toolbox
        self.tools = [assign_start_end_nodes]


class assign_start_end_nodes:
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Assign Start and End Nodes"
        self.description = "Assigns start/end nodes using specified point and line features"

    def getParameterInfo(self):
        """Define the tool parameters."""
        pipes_fc = arcpy.Parameter(
            displayName="Pipes feature class/shapefile",
            name="pipes_fc",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input"
        )

        pipes_start_node_field = arcpy.Parameter(
            displayName="Start node field",
            name="pipes_start_node_field",
            datatype="Field",
            parameterType="Required",
            direction="Input"
        )
        pipes_start_node_field.parameterDependencies = [pipes_fc.name]

        pipes_end_node_field = arcpy.Parameter(
            displayName="End node field",
            name="pipes_end_node_field",
            datatype="Field",
            parameterType="Required",
            direction="Input"
        )
        pipes_end_node_field.parameterDependencies = [pipes_fc.name]

        points_fc = arcpy.Parameter(
            displayName="Points/junctions feature class/shapefile",
            name="points_fc",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input"
        )

        points_elevation_field = arcpy.Parameter(
            displayName="Points elevation field",
            name="points_elevation_field",
            datatype="Field",
            parameterType="Required",
            direction="Input"
        )
        points_elevation_field.parameterDependencies = [points_fc.name]

        points_label_field = arcpy.Parameter(
            displayName="Points label field",
            name="points_label_field",
            datatype="Field",
            parameterType="Required",
            direction="Input"
        )
        points_label_field.parameterDependencies = [points_fc.name]

        output_gdb = arcpy.Parameter(
            displayName="Output geodatabase",
            name="output_gdb",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input"
        )
        params = [
            pipes_fc,
            pipes_start_node_field,
            pipes_end_node_field,
            points_fc,
            points_elevation_field,
            points_label_field,
            output_gdb,
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
        pipes_fc = parameters[0].valueAsText
        pipes_start_node_field = parameters[1].valueAsText
        pipes_end_node_field = parameters[2].valueAsText
        points_fc = parameters[3].valueAsText
        points_elevation_field = parameters[4].valueAsText
        points_label_field = parameters[5].valueAsText
        output_gdb = parameters[6].valueAsText

        pipes_dict = {}

        arcpy.AddMessage(f"Copying pipe features")
        pipes_fc_copy = arcpy.conversion.ExportFeatures(
            in_features=pipes_fc,
            out_features=f"{output_gdb}\\pipes_fc_COPY"
        )
        arcpy.AddMessage(f"Finished copying!")

        arcpy.AddMessage(f"Finding pipe points...")
        with arcpy.da.SearchCursor(pipes_fc_copy, "OID@") as cursor:
            for row in cursor:
                object_id_pipe = row[0]
                pipes_dict[object_id_pipe] = None
                select_pipe = arcpy.management.SelectLayerByAttribute(
                    in_layer_or_view=pipes_fc_copy,
                    selection_type="NEW_SELECTION",
                    where_clause=f"OBJECTID = {object_id_pipe}"
                )
                select_nodes = arcpy.management.SelectLayerByLocation(
                    in_layer=points_fc,
                    overlap_type="INTERSECT",
                    select_features=select_pipe,
                    selection_type="NEW_SELECTION"
                )
                rows_list = []
                # with arcpy.da.SearchCursor(select_nodes, ["label", "elevation_ft"]) as cursor:
                with arcpy.da.SearchCursor(select_nodes, [points_label_field, points_elevation_field]) as cursor:
                    for row in cursor:
                        rows_list.append(row)
                label_one = rows_list[0][0]
                elevation_one = rows_list[0][1]
                label_two = rows_list[1][0]
                elevation_two = rows_list[1][1]
                if elevation_one > elevation_two:
                    start_end_dict = {
                        "start_node": label_one,
                        "end_node": label_two
                    }
                else:
                    start_end_dict = {
                        "start_node": label_two,
                        "end_node": label_one
                    }
                pipes_dict[object_id_pipe] = start_end_dict
        arcpy.AddMessage(f"Finished finding end points!")

        arcpy.AddMessage(f"Updating pipe start and end points...")
        # with arcpy.da.UpdateCursor(pipes_fc_copy, ["OID@", "start_node", "end_node"]) as cursor:
        with arcpy.da.UpdateCursor(pipes_fc_copy, ["OID@", pipes_start_node_field, pipes_end_node_field]) as cursor:
            for row in cursor:
                oid_fc = row[0]
                row[1] = pipes_dict[oid_fc]['start_node']
                row[2] = pipes_dict[oid_fc]['end_node']
                cursor.updateRow(row)
        arcpy.AddMessage(f"Finished updating start and end points!")

        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return
