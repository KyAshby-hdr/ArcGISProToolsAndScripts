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
    Union,
    Select
)
from arcpy.cartography import (
    AggregatePolygons
)
from arcpy.management import (
    MultipartToSinglepart,
    SelectLayerByAttribute,
)
from arcpy.conversion import (
    ExportFeatures
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

        aggregate_polygons_distance = Parameter(
            displayName="Aggregate polygons distance",
            name="aggregate_polygons_distance",
            datatype="Long",
            parameterType="Required",
            direction="Input"
        )
        aggregate_unit = Parameter(
            displayName="Aggregate distance unit",
            name="aggregate_unit",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )

        aggregate_unit.filter.type = "ValueList"

        aggregate_unit.filter.list = ["Feet", "Miles"]

        aggregate_hole_size = Parameter(
            displayName="Minimum aggregate hole size",
            name="aggregate_hole_size",
            datatype="Double",
            parameterType="Required",
            direction="Input"
        )
        hole_size_unit = Parameter(
            displayName="Hole size unit",
            name="hole_size_unit",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )

        hole_size_unit.filter.type = "ValueList"

        hole_size_unit.filter.list = ["SquareFeetUS", "AcresUS", "SquareMilesUS"]

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
            aggregate_polygons_distance,
            aggregate_unit,
            aggregate_hole_size,
            hole_size_unit,
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
        aggregate_polygons_distance = parameters[1].valueAsText
        aggregate_unit = parameters[2].valueAsText
        aggregate_hole_size = parameters[3].valueAsText
        hole_size_unit = parameters[4].valueAsText
        buffer_distance = parameters[5].valueAsText
        buffer_unit = parameters[6].valueAsText
        output_gdb = parameters[7].valueAsText

        env.workspace = output_gdb
        AddMessage(f"{output_gdb} is the output gdb")

        AddMessage(f"Aggregating polygons within {aggregate_polygons_distance} {aggregate_unit}, removing holes less than {aggregate_hole_size} {hole_size_unit}")
        aggregate_polygons_fc  = AggregatePolygons(
            in_features=input_inundation_boundary,
            out_feature_class=f"{output_gdb}\\AggregatePolygons",
            aggregation_distance=f"{aggregate_polygons_distance} {aggregate_unit}",
            minimum_area="0 SquareMilesUS",
            minimum_hole_size=f"{aggregate_hole_size} {hole_size_unit}",
            orthogonality_option="NON_ORTHOGONAL",
            barrier_features=None,
            out_table=f"{output_gdb}\\AggregatePolygonsTable",
            aggregate_field=None
        )
        AddMessage(f"Aggregate process finished!")

        AddMessage(f"Starting multipart to singlepart process...")
        multi_to_single_fc = MultipartToSinglepart(
            in_features=aggregate_polygons_fc,
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

        AddMessage(f"Starting positive buffer process...")
        positive_buffer_fc = PairwiseBuffer(
            in_features=largest_polygon,
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

        AddMessage(f"Removing holes created from buffer process...")
        AggregatePolygons(
            in_features=negative_buffer_fc,
            out_feature_class=f"{output_gdb}\\FinalPolygon",
            aggregation_distance=f"{aggregate_polygons_distance} {aggregate_unit}",
            minimum_area="0 SquareMilesUS",
            minimum_hole_size=f"{aggregate_hole_size} {hole_size_unit}",
            orthogonality_option="NON_ORTHOGONAL",
            barrier_features=None,
            out_table=f"{output_gdb}\\AggregatePolygonsTable",
            aggregate_field=None
        )
        AddMessage(f"Aggregate process part two finished!")
        
        return


    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return
