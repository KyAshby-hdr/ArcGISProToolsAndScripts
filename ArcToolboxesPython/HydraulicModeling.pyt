# -*- coding: utf-8 -*-
import arcpy
from arcpy import (
    ListFields,
    Parameter,
    AddMessage,
    env,
    AddError,
    ListTables,
)
from arcpy.sa import ExtractMultiValuesToPoints
from arcpy.management import (SelectLayerByAttribute,
                              SelectLayerByLocation,
                              GetCount,
                              Append,
                              Delete,
                              CreateTable,
                              AddField,
                              CalculateField)
from arcpy.da import SearchCursor, UpdateCursor
from arcpy.conversion import ExportTable

class Toolbox:
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = "toolbox"

        # List of tool classes associated with this toolbox
        self.tools = [ProfileExtraction]


class ProfileExtraction:
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Profile Extraction"
        self.description = "Automates extracting profiles for hydraulic modeling results"

    def getParameterInfo(self):
        """Define the tool parameters."""
        rasters = Parameter(
            displayName="Input rasters",
            name="rasters",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Input",
            multiValue=True
        )
        profile_lines = Parameter(
            displayName="Profile lines",
            name="profile_lines",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input"
        )
        unique_field = Parameter(
            displayName="Field in profile lines table that will be used to distinguish profiles",
            name="unique_field",
            datatype="Field",
            parameterType="Required",
            direction="Input"
        )
        unique_field.parameterDependencies = [profile_lines.name]
        unique_field.value = None
        line_points_name = Parameter(
            displayName="Generated point feature class or shapefile",
            name="line_points_name",
            datatype="GPString",
            direction="Input"
        )
        point_spacing = Parameter(
            displayName="Spacing for points",
            name="point_spacing",
            datatype="GPString",
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
        params = [rasters,
                  profile_lines,
                  unique_field,
                  line_points_name,
                  point_spacing,
                  output_gdb]
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
        rasters = parameters[0].valueAsText
        profile_lines = parameters[1].valueAsText
        unique_field = parameters[2].valueAsText
        line_points_name = parameters[3].valueAsText
        point_spacing = parameters[4].valueAsText
        output_gdb = parameters[5].valueAsText
        
        #* Generate points along lines at specified spacing
        line_points_fc = f"{output_gdb}\\{line_points_name}" 
        arcpy.management.GeneratePointsAlongLines(
            Input_Features=profile_lines,
            Output_Feature_Class=line_points_fc,
            Point_Placement="DISTANCE",
            Distance=f"{point_spacing} Feet",
            Percentage=None,
            Include_End_Points="END_POINTS",
            Add_Chainage_Fields="NO_CHAINAGE"
        )

        #* Extract the values of the specified rasters to the generated points
        ExtractMultiValuesToPoints(
            in_point_features=line_points_fc,
            in_rasters=rasters,
            bilinear_interpolate_values="NONE"
        )

        #* Function to calculate the point distance along lines
        def calculate_distance_along_line(points_fc, lines_fc, line_id_field, out_field):
            if out_field not in [f.name for f in arcpy.ListFields(points_fc)]:
                AddField(points_fc, out_field, "DOUBLE")
            line_geoms = {}
            with SearchCursor(lines_fc, [line_id_field, "SHAPE@"]) as lcur:
                for line_id, geom in lcur:
                    line_geoms[line_id] = geom
            with UpdateCursor(points_fc, ["SHAPE@", line_id_field, out_field]) as pcur:
                for shape, line_id, _ in pcur:
                    line_geom = line_geoms.get(line_id)
                    if line_geom:
                        dist = line_geom.measureOnLine(shape)
                        pcur.updateRow((shape, line_id, dist))
        calculate_distance_along_line(
            points_fc=line_points_fc,
            lines_fc=profile_lines,
            line_id_field="profile",
            out_field="DistanceMeasured"
        )

        #* Put unique profile names into list
        with SearchCursor(line_points_fc, [unique_field]) as cursor:
            profile_line_names = sorted({row[0] for row in cursor if row[0] is not None})
        
        #* Generate separate tables for each profile line
        for profile in profile_line_names:
            selected_points = SelectLayerByAttribute(
                in_layer_or_view=line_points_fc,
                selection_type="NEW_SELECTION",
                where_clause=f"{unique_field} = '{profile}'"
            )
            profile_nowhitespace = profile.replace(" ","")
            ExportTable(
                in_table=selected_points,
                out_table=f"{output_gdb}\\{profile_nowhitespace}Table"
            )

        #* Combine individual tables into one combined table
        env.workspace = output_gdb
        table_list = ListTables("*")
        if "CombinedTable" in table_list:
            Delete("CombinedTable")
            AddMessage("Previously existing CombinedTable deleted. Generating new table for output results.")
        table_list = ListTables("*")
        table_template = table_list[0]
        CreateTable(
            out_path=output_gdb,
            out_name="CombinedTable",
            template=table_template
        )
        Append(
            inputs=table_list,
            target="CombinedTable",
            schema_type="TEST"
        )
        combined_table = ListTables("CombinedTable*")[0]
        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return
