# -*- coding: utf-8 -*-

import arcpy
from arcpy import (
    Parameter,
    AddMessage,
    env,
    Describe
)
from arcpy.da import (
    SearchCursor
)
from arcpy.analysis import (
    PairwiseBuffer,
    Select
)
from arcpy.management import (
    MultipartToSinglepart,
    EliminatePolygonPart
)
from arcpy.cartography import (
    SmoothPolygon
)

class Toolbox:
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Flood Study Automated Workflows"
        self.alias = "FloodStudyAutomatedWorkflows"

        # List of tool classes associated with this toolbox
        self.tools = [evacuation_boundary_generator]


class evacuation_boundary_generator:
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Evacuation Boundary Generator"
        self.description = "Creates an evacuation boundary using an input inundation boundary from a hydraulic model"

    def getParameterInfo(self):
        """Define the tool parameters."""
        input_inundation_boundary = Parameter(
            displayName="Input inundation boundary",
            name="input_inundation_boundary",
            datatype="GPFeatureLayer",
            parameterType="Required",
            direction="Input"
        )

        eliminate_polygon_area_size = Parameter(
            displayName="Minimum polygon area to remove polygon parts (holes and polygons)",
            name="aggregate_hole_size",
            datatype="Double",
            parameterType="Required",
            direction="Input"
        )
        eliminate_polygon_area_unit = Parameter(
            displayName="Area unit for removing polygon parts",
            name="eliminate_polygon_area_unit",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )

        eliminate_polygon_area_unit.filter.type = "ValueList"

        eliminate_polygon_area_unit.filter.list = ["SquareFeetUS", "AcresUS", "SquareMilesUS"]

        eliminate_polygon_area_contained_parts = Parameter(
            displayName="Eliminate contained parts only",
            name="eliminate_polygon_area_contained_parts",
            datatype="Boolean",
            parameterType="Optional"
        )

        buffer_distance = Parameter(
            displayName="Buffer distance",
            name="buffer_distance",
            datatype="Long",
            parameterType="Required",
            direction="Input"
        )

        buffer_unit = Parameter(
            displayName="Buffer unit",
            name="buffer_unit",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )

        buffer_unit.filter.type = "ValueList"

        buffer_unit.filter.list = ["Feet", "Miles"]

        output_gdb = Parameter(
            displayName="Output geodatabase",
            name="output_gdb",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input"
        )

        params = [
            input_inundation_boundary,
            eliminate_polygon_area_size,
            eliminate_polygon_area_unit,
            eliminate_polygon_area_contained_parts,
            buffer_distance,
            buffer_unit,
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
        input_inundation_boundary = parameters[0].valueAsText
        eliminate_polygon_area_size = parameters[1].valueAsText
        eliminate_polygon_area_unit = parameters[2].valueAsText
        eliminate_polygon_area_contained_parts = parameters[3].valueAsText
        buffer_distance = parameters[4].valueAsText
        buffer_unit = parameters[5].valueAsText
        output_gdb = parameters[6].valueAsText

        env.workspace = output_gdb
        AddMessage(f"{output_gdb} is the output gdb")

        if eliminate_polygon_area_contained_parts:
            part_option = "CONTAINED_ONLY"
            eliminate_polygon_area_message = "contained parts only"
        else:
            part_option = "ANY"
            eliminate_polygon_area_message = "all parts"

        AddMessage(f"Removing {eliminate_polygon_area_message} from inundation polygon with an area less than {eliminate_polygon_area_size} {eliminate_polygon_area_unit}...")
        eliminate_polygon_part_fc = EliminatePolygonPart(
            in_features=input_inundation_boundary,
            out_feature_class=f"{output_gdb}\\EliminatePolygon",
            condition="AREA",
            part_area=f"{eliminate_polygon_area_size} {eliminate_polygon_area_unit}",
            part_area_percent=0,
            part_option=part_option
        )
        AddMessage(f"Eliminate polygon parts finished!")

        AddMessage(f"Starting positive buffer process...")
        positive_buffer_fc = PairwiseBuffer(
            in_features=eliminate_polygon_part_fc,
            out_feature_class=f"{output_gdb}\\PositiveBuffer",
            buffer_distance_or_field=f"{buffer_distance} {buffer_unit}",
            dissolve_option="ALL",
            dissolve_field=None,
            method="PLANAR",
            max_deviation="0 Feet"
        )
        AddMessage(f"Positive buffer finished!")

        AddMessage(f"Starting negative buffer process...")
        negative_buffer_fc = PairwiseBuffer(
            in_features=positive_buffer_fc,
            out_feature_class=f"{output_gdb}\\NegativeBuffer",
            buffer_distance_or_field=f"-{buffer_distance} {buffer_unit}",
            dissolve_option="ALL",
            dissolve_field=None,
            method="PLANAR",
            max_deviation="0 Feet"
        )
        AddMessage(f"Negative buffer finished!")

        AddMessage(f"Starting multipart to singlepart process...")
        multi_to_single_fc = MultipartToSinglepart(
            in_features=negative_buffer_fc,
            out_feature_class=f"{output_gdb}\\MultiToSingle",
        )
        AddMessage(f"Multipart to singlepart complete!")

        AddMessage(f"Extracting largest polygon...")
        oid_field = Describe(multi_to_single_fc).OIDFieldName

        largest_oid = None
        largest_area = -1

        with SearchCursor(multi_to_single_fc, [oid_field, "SHAPE@AREA"]) as cursor:
            for oid, area in cursor:
                if area > largest_area:
                    largest_area = area
                    largest_oid = oid
        
        where_clause = f"{oid_field} = {largest_oid}"

        largest_polygon = Select(
            in_features=multi_to_single_fc,
            out_feature_class=f"{output_gdb}\\LargestPolygon",
            where_clause=where_clause
        )
        AddMessage(f"Largest polygon extracted and saved to geodatabase!")

        AddMessage(f"Removing holes and extra polygons potentially created from buffer process...")
        eliminate_polygon_part_two = EliminatePolygonPart(
            in_features=largest_polygon,
            out_feature_class=f"{output_gdb}\\EliminatePolygonPartTwo",
            condition="AREA",
            part_area=f"{eliminate_polygon_area_size} {eliminate_polygon_area_unit}",
            part_area_percent=0,
            part_option=part_option
        )
        AddMessage(f"Eliminate polygon part part two finished!")

        AddMessage("Finalizing boundary polygon...")
        SmoothPolygon(
            in_features=eliminate_polygon_part_two,
            out_feature_class=f"{output_gdb}\\FinalPolygon",
            algorithm="PAEK",
            tolerance="1000 Feet",
            endpoint_option="FIXED_ENDPOINT",
            error_option="NO_CHECK",
            in_barriers=None
        )
        AddMessage("Final polygon created!")
        return


    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return
