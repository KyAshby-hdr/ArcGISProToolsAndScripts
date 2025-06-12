# -*- coding: utf-8 -*-
import arcpy
from arcpy import (
    Parameter,
    Raster,
    ListRasters,
    AddMessage,
    AddError,
    env,
    SetProgressorLabel,
    SetProgressor,
    SetProgressorPosition,
)
from arcpy.management import (
    Delete,
)
from arcpy.ia import Con, RasterCalculator

class Toolbox:
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = "toolbox"

        # List of tool classes associated with this toolbox
        self.tools = [mussel_hsi_calc]

class mussel_hsi_calc:
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Mussel HSI Calc"
        self.description = "Tool to create HSI rasters for mussel species"

    def getParameterInfo(self):
        """Define the tool parameters."""
        input_gdb = Parameter(
            displayName="Specify input gdb",
            name="input_gdb",
            datatype="Workspace",
            parameterType="Required",
            direction="Input"
        )

        input_gdb.filter.list = ["Local Database"]

        output_gdb = Parameter(
            displayName="Specify output gdb",
            name="output_gdb",
            datatype="Workspace",
            parameterType="Required",
            direction="Input"
        )
        params = [
            input_gdb,
            output_gdb
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
        output_gdb = parameters[1].valueAsText

        env.workspace = input_gdb

        AddMessage(f"{input_gdb} is the input gdb")

        raster_list = ListRasters("*")
        depth_rasters = []
        velocity_rasters = []

        for raster in raster_list:
            if "dep" in raster.lower():
                depth_rasters.append(raster)
            elif "vel" in raster.lower():
                velocity_rasters.append(raster)
        
        AddMessage(f"Depth Rasters:{depth_rasters}")
        AddMessage(f"Velocity Rasters:{velocity_rasters}")
        
        #* This code block pairs the velocity and depth rasters
        #* The raster names should have a unique identifier (i.e. "High", "6500", "6500cfs") that is separated by an underscore
        dep_vel_ras_pairs_dict = {}
        for dep_ras in depth_rasters:
            for vel_ras in velocity_rasters:
                dep_ras_split = dep_ras.split("_")
                vel_ras_split = vel_ras.split("_")
                for dep_str in dep_ras_split:
                    for vel_str in vel_ras_split:
                        if dep_str.lower() == vel_str.lower():
                            unique_id = dep_str.lower()
                            dep_vel_pair = [dep_ras, vel_ras]
                            dep_vel_ras_pairs_dict[f"{unique_id}"] = dep_vel_pair

        if not dep_vel_ras_pairs_dict:
            AddError(f"No depth and velocity raster pairings found. Confirm naming schema for depth and velocity rasters")
            return

        #* This code block iterates over the created dictionary and creates the morphological unit rasters
        AddMessage(f"Depth and velocity pairings created")
        prog_pos = 0
        num_ras_pairs = len(dep_vel_ras_pairs_dict)
        for unique_id, ras_pair in dep_vel_ras_pairs_dict.items():
            for ras in ras_pair:
                if "dep" in ras.lower():
                    dep_raster = Raster(ras)
                if "vel" in ras.lower():
                    vel_raster = Raster(ras)
            AddMessage(f"Calculating MorphUnit_{unique_id} raster")
            SetProgressorLabel(f"Calculating MorphUnit_{unique_id} raster")
            SetProgressorPosition(prog_pos)
            prog_pos += int((1/num_ras_pairs) * 100)
            morph_unit_raster = RasterCalculator(
                rasters=[dep_raster, vel_raster],
                input_names=["dep_raster", "vel_raster"],
                expression="Con((dep_raster<2) & (vel_raster<1),1,Con((dep_raster<2) & (vel_raster>2),2,Con(((dep_raster>2) & (dep_raster<4)) & (vel_raster<1),3,Con((dep_raster>4) & (vel_raster<1),4,Con((dep_raster<2) & ((vel_raster>1) & (vel_raster<2)),5,Con(((dep_raster>2) & (dep_raster<4)) & (vel_raster>1),6,Con((dep_raster>4) & (vel_raster>1),7,0)))))))",
            )
            #* The expression in the "RasterCalculator" function determines the morph unit based on depth and velocity rasters
            #* The morph unit raster is given an integer to denote which morph unit it is classified as
            #* For reference:
            #* 1 = Plane Bed
            #* 2 = Riffle
            #* 3 = Run
            #* 4 = Pool
            #* 5 = Glide
            #* 6 = Chute
            #* 7 = Deep Channel
            save_location = f"{output_gdb}\\MorphUnit_{unique_id}"
            morph_unit_raster.save(save_location)
        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return
