# -*- coding: utf-8 -*-
import arcpy
import requests
import pandas as pd
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
    BuildRasterAttributeTable,
    CalculateField,
    AddField,
)
from arcpy.ia import RasterCalculator
from arcpy.sa import Int

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
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input"
        )

        input_gdb.filter.list = ["Local Database"]

        output_gdb = Parameter(
            displayName="Specify output gdb",
            name="output_gdb",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input"
        )

        coefficient_of_variation = Parameter(
            displayName="Specify coefficient of variation",
            name="coefficient_of_variation",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )

        fish_cover_hsi_raster = Parameter(
            displayName="Select fish cover HSI raster",
            name="fish_cover_raster",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Input"
        )

        substrate_hsi_raster = Parameter(
            displayName="Select substrate HSI raster",
            name="substrate_hsi_raster",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Input"
        )

        percent_silt_hsi_raster = Parameter(
            displayName="Select percent silt HSI raster",
            name="percent_silt_hsi_raster",
            datatype="GPRasterLayer",
            parameterType="Required",
            direction="Input"
        )

        western_pearlshell_option = Parameter(
            displayName="Generate HSI for Western Pearlshell",
            name="western_pearlshell_option",
            datatype="GPBoolean",
            parameterType="Optional",
        )

        california_floater_option = Parameter(
            displayName="Generate HSI for California Floater",
            name="california_floater_option",
            datatype="GPBoolean",
            parameterType="Optional",
        )
        params = [
            input_gdb,
            output_gdb,
            coefficient_of_variation,
            fish_cover_hsi_raster,
            substrate_hsi_raster,
            percent_silt_hsi_raster,
            western_pearlshell_option,
            california_floater_option,
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
        coefficient_of_variation = parameters[2].value
        fish_cover_hsi_raster = parameters[3].valueAsText
        substrate_hsi_raster = parameters[4].valueAsText
        percent_silt_hsi_raster = parameters[5].valueAsText
        western_pearlshell_option = parameters[6].value
        california_floater_option = parameters[7].value
        
        if not western_pearlshell_option and not california_floater_option:
            AddError(f"Choose species to generate HSI")
            return

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
        unique_id_list = []
        dep_vel_ras_pairs_dict = {}
        for dep_ras in depth_rasters:
            for vel_ras in velocity_rasters:
                dep_ras_split = dep_ras.split("_")
                vel_ras_split = vel_ras.split("_")
                for dep_str in dep_ras_split:
                    for vel_str in vel_ras_split:
                        if dep_str.lower() == vel_str.lower():
                            unique_id = dep_str.lower()
                            unique_id_list.append(unique_id)
                            dep_vel_pair = [dep_ras, vel_ras]
                            dep_vel_ras_pairs_dict[f"{unique_id}"] = dep_vel_pair

        if not dep_vel_ras_pairs_dict:
            AddError(f"No depth and velocity raster pairings found. Confirm naming schema for depth and velocity rasters")
            return

        for unique_id in unique_id_list:
            for vel_ras in velocity_rasters:
                if unique_id in vel_ras.lower():
                    AddMessage(f"Calculating VelRas_{unique_id}_HSI")
                    vel_ras_hsi = RasterCalculator(
                        rasters=[vel_ras],
                        input_names=["vel_ras"],
                        expression="Con(vel_ras <= 3.281,1,0.5)",
                    )
                    AddMessage(f"Saving VelRas_{unique_id}_HSI")
                    vel_ras_hsi.save(f"{output_gdb}\\VelRas_{unique_id}_HSI")

        #* This code block iterates over the created dictionary and creates the morphological unit rasters
        AddMessage(f"Depth and velocity pairings created")
        for unique_id, ras_pair in dep_vel_ras_pairs_dict.items():
            for ras in ras_pair:
                if "dep" in ras.lower():
                    dep_raster = Raster(ras)
                if "vel" in ras.lower():
                    vel_raster = Raster(ras)
            AddMessage(f"Calculating MorphUnit_{unique_id} raster")
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
            AddMessage(f"Saving MorphUnit_{unique_id}")
            morph_unit_save_location = f"{output_gdb}\\MorphUnit_{unique_id}"
            morph_unit_raster.save(morph_unit_save_location)
        
        env.workspace = output_gdb
        morph_unit_raster_list = []
        full_raster_list = ListRasters("*")
        for ras in full_raster_list:
            if ("morphunit" in ras.lower()) and ("hsi" not in ras.lower()):
                morph_unit_raster_list.append(ras)
        for morph_unit_raster in morph_unit_raster_list:
            AddMessage(f"Calculating {morph_unit_raster}_HSI")
            hsi_value_raster = RasterCalculator(
                rasters=[morph_unit_raster],
                input_names=["morph_unit_raster"],
                expression="Con(morph_unit_raster == 1 | morph_unit_raster == 2 | morph_unit_raster == 3 | morph_unit_raster == 5 | morph_unit_raster == 6, 1, Con(morph_unit_raster == 4 | morph_unit_raster == 7, 0.5, 0))"
            )
            AddMessage(f"Saving {morph_unit_raster}_HSI")
            hsi_value_raster.save(f"{output_gdb}\\{morph_unit_raster}_HSI")
        
        morph_unit_ras_hsi_list = []
        vel_ras_hsi_list = []
        full_raster_list = ListRasters("*")
        for ras in full_raster_list:
            if ("vel" in ras.lower()) and ("hsi" in ras.lower()):
                vel_ras_hsi_list.append(ras)
            elif ("morphunit" in ras.lower()) and ("hsi" in ras.lower()):
                morph_unit_ras_hsi_list.append(ras)
        for unique_id in unique_id_list:
            for vel_ras_hsi in vel_ras_hsi_list:
                for morph_unit_ras_hsi in morph_unit_ras_hsi_list:
                    if (unique_id.lower() in vel_ras_hsi.lower()) and (unique_id.lower() in morph_unit_ras_hsi.lower()) and (western_pearlshell_option and not california_floater_option):
                        AddMessage(f"Calculating only WesternPearl_HSI_{unique_id}")
                        final_hsi_raster = RasterCalculator(
                            rasters=[vel_ras_hsi, morph_unit_ras_hsi, fish_cover_hsi_raster, substrate_hsi_raster, percent_silt_hsi_raster],
                            input_names=["vel_ras_hsi", "morph_unit_ras_hsi", "fish_cover_hsi_raster", "substrate_hsi_raster", "percent_silt_hsi_raster"],
                            expression=f"({coefficient_of_variation} + morph_unit_ras_hsi + fish_cover_hsi_raster + vel_ras_hsi + substrate_hsi_raster + percent_silt_hsi_raster) / 6"
                        )
                        AddMessage(f"Saving WesternPearl_HSI_{unique_id}")
                        final_hsi_raster.save(f"{output_gdb}\\WesternPearl_HSI_{unique_id}")
                    elif (unique_id.lower() in vel_ras_hsi.lower()) and (unique_id.lower() in morph_unit_ras_hsi.lower()) and (california_floater_option and not western_pearlshell_option):
                        AddMessage(f"Calculating only CaliFloater_HSI_{unique_id}")
                        final_hsi_raster = RasterCalculator(
                            rasters=[morph_unit_ras_hsi],
                            input_names=["morph_unit_ras_hsi"],
                            expression=f"({coefficient_of_variation} + morph_unit_ras_hsi) / 2"
                        )
                        AddMessage(f"Saving CaliFloater_HSI_{unique_id}")
                        final_hsi_raster.save(f"{output_gdb}\\CaliFloater_HSI_{unique_id}")
                    elif (unique_id.lower() in vel_ras_hsi.lower()) and (unique_id.lower() in morph_unit_ras_hsi.lower()) and (western_pearlshell_option and california_floater_option):
                        AddMessage(f"Calculating WesternPearl_HSI_{unique_id} and CaliFloater_HSI_{unique_id}")
                        final_hsi_raster = RasterCalculator(
                            rasters=[vel_ras_hsi, morph_unit_ras_hsi, fish_cover_hsi_raster, substrate_hsi_raster, percent_silt_hsi_raster],
                            input_names=["vel_ras_hsi", "morph_unit_ras_hsi", "fish_cover_hsi_raster", "substrate_hsi_raster", "percent_silt_hsi_raster"],
                            expression=f"({coefficient_of_variation} + morph_unit_ras_hsi + fish_cover_hsi_raster + vel_ras_hsi + substrate_hsi_raster + percent_silt_hsi_raster) / 6"
                        )
                        AddMessage(f"Saving WesternPearl_HSI_{unique_id}")
                        final_hsi_raster.save(f"{output_gdb}\\WesternPearl_HSI_{unique_id}")
                        final_hsi_raster = RasterCalculator(
                            rasters=[morph_unit_ras_hsi],
                            input_names=["morph_unit_ras_hsi"],
                            expression=f"({coefficient_of_variation} + morph_unit_ras_hsi) / 2"
                        )
                        AddMessage(f"Saving CaliFloater_HSI_{unique_id}")
                        final_hsi_raster.save(f"{output_gdb}\\CaliFloater_HSI_{unique_id}")
        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return
