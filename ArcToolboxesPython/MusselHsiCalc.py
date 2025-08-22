"""
Script documentation
- Tool parameters are accessed using arcpy.GetParameter() or 
                                     arcpy.GetParameterAsText()
- Update derived parameter values using arcpy.SetParameter() or
                                        arcpy.SetParameterAsText()
"""
import arcpy
import numpy as np
from arcpy import (
    Raster,
    ListRasters,
    AddMessage,
    AddError,
    env,
)
from arcpy.sa import RasterCalculator, ZonalStatisticsAsTable
from arcpy.management import CalculateField
def script_tool(
    input_gdb,
    output_gdb,
    coefficient_of_variation,
    fish_cover_hsi_raster,
    substrate_hsi_raster,
    percent_silt_hsi_raster,
    western_pearlshell_option,
    california_floater_option,
    zones_fc,
    zones_shp,
    zone_field,
    seasonal_high_flow_velocity_raster
):
    env.overwriteOutput = True
    arcpy.CheckOutExtension("Spatial")
    if not western_pearlshell_option and not california_floater_option:
            AddError(f"Choose species to generate HSI")
            return
    if zones_fc != "":
        zone_data = zones_fc
        AddMessage(f"The feature class {zone_data} will be used for zonal stats")
    if zones_shp != "":
        zone_data = zones_shp
        AddMessage(f"The shapefile {zone_data} will be used for zonal stats")
    if (zones_fc == "") and (zones_shp == ""):
        AddError(f"Include a shapefile or feature class to be used for zonal stats")
        return
    env.workspace = input_gdb
    AddMessage(f"{input_gdb} is the input gdb")
    if float(coefficient_of_variation) <= 0.9:
        coefficient_of_variation_hsi = 1
    elif (float(coefficient_of_variation) > 0.9) and (float(coefficient_of_variation) <= 1.05):
        coefficient_of_variation_hsi = 0.75
    elif (float(coefficient_of_variation) > 1.05) and (float(coefficient_of_variation) <= 1.15):
        coefficient_of_variation_hsi = 0.6
    elif float(coefficient_of_variation) > 1.15:
        coefficient_of_variation_hsi = 0.3
    
    AddMessage(f"With a coefficient of variation value of {coefficient_of_variation}, the HSI value is {coefficient_of_variation_hsi}")
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
    #* The raster names should follow this basic naming formulas to ensure the code works as intended:
    #* RasterNameText_UNIQUEID or UNIQUEID_RasterNameText
    #* The unique ID can be text or numbers, making sure that the unique IDs match for velocity and depth pairs.
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
    AddMessage(f"Calculating seasonal high flow velocity HSI raster")
    seasonal_high_flow_vel_ras_hsi = RasterCalculator(
        rasters=[seasonal_high_flow_velocity_raster],
        input_names=["seasonal_high_flow_velocity_raster"],
        expression="Con(seasonal_high_flow_velocity_raster <= 3.281,1,0.5)",
    )
    AddMessage(f"Saving SeasHighFlowVelRas_HSI raster")
    seasonal_high_flow_vel_ras_hsi.save(f"{output_gdb}\\SeasHighFlowVelRas_HSI")
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
    seas_high_flow_hsi_ras = f"{output_gdb}\\SeasHighFlowVelRas_HSI"
    for ras in full_raster_list:
        if ("morphunit" in ras.lower()) and ("hsi" not in ras.lower()):
            morph_unit_raster_list.append(ras)
    for morph_unit_raster in morph_unit_raster_list:
        AddMessage(f"Calculating {morph_unit_raster}_HSI_Pearlshell")
        hsi_value_raster_pearlshell = RasterCalculator(
            rasters=[morph_unit_raster],
            input_names=["morph_unit_raster"],
            expression="Con(morph_unit_raster == 1 | morph_unit_raster == 2 | morph_unit_raster == 3 | morph_unit_raster == 5 | morph_unit_raster == 6, 1, Con(morph_unit_raster == 4 | morph_unit_raster == 7, 0.5, 0))"
        )
        AddMessage(f"Saving {morph_unit_raster}_HSI_Pearlshell")
        hsi_value_raster_pearlshell.save(f"{output_gdb}\\{morph_unit_raster}_HSI_Pearlshell")

        AddMessage(f"Calculating {morph_unit_raster}_HSI_CaliFloat")
        hsi_value_raster_pearlshell = RasterCalculator(
            rasters=[morph_unit_raster],
            input_names=["morph_unit_raster"],
            expression="Con(morph_unit_raster == 4, 1, 0.5)"
        )
        AddMessage(f"Saving {morph_unit_raster}_HSI")
        hsi_value_raster_pearlshell.save(f"{output_gdb}\\{morph_unit_raster}_HSI_CaliFloat")
    
    morph_unit_ras_hsi_list = []
    full_raster_list = ListRasters("*")
    for ras in full_raster_list:
        if ("morphunit" in ras.lower()) and ("hsi" in ras.lower()):
            morph_unit_ras_hsi_list.append(ras)
    for unique_id in unique_id_list:
        for morph_unit_ras_hsi in morph_unit_ras_hsi_list:
            if (unique_id.lower() in morph_unit_ras_hsi.lower()) and ("pearlshell" in morph_unit_ras_hsi.lower()) and (western_pearlshell_option and not california_floater_option):
                final_hsi_raster = RasterCalculator(
                    rasters=[seas_high_flow_hsi_ras, morph_unit_ras_hsi, fish_cover_hsi_raster, substrate_hsi_raster, percent_silt_hsi_raster],
                    input_names=["seas_high_flow_hsi_ras", "morph_unit_ras_hsi", "fish_cover_hsi_raster", "substrate_hsi_raster", "percent_silt_hsi_raster"],
                    expression=f"({coefficient_of_variation_hsi} + morph_unit_ras_hsi + fish_cover_hsi_raster + seas_high_flow_hsi_ras + substrate_hsi_raster + percent_silt_hsi_raster) / 6"
                )
                AddMessage(f"Saving WesternPearl_HSI_{unique_id}")
                final_hsi_raster.save(f"{output_gdb}\\WesternPearl_HSI_{unique_id}")
            elif (unique_id.lower() in morph_unit_ras_hsi.lower()) and ("califloat" in morph_unit_ras_hsi.lower()) and (california_floater_option and not western_pearlshell_option):
                final_hsi_raster = RasterCalculator(
                    rasters=[morph_unit_ras_hsi],
                    input_names=["morph_unit_ras_hsi"],
                    expression=f"({coefficient_of_variation_hsi} + morph_unit_ras_hsi) / 2"
                )
                AddMessage(f"Saving CaliFloater_HSI_{unique_id}")
                final_hsi_raster.save(f"{output_gdb}\\CaliFloater_HSI_{unique_id}")
            elif (unique_id.lower() in morph_unit_ras_hsi.lower()) and (western_pearlshell_option and california_floater_option):
                if ("pearlshell" in morph_unit_ras_hsi.lower()):
                    final_hsi_raster = RasterCalculator(
                        rasters=[seas_high_flow_hsi_ras, morph_unit_ras_hsi, fish_cover_hsi_raster, substrate_hsi_raster, percent_silt_hsi_raster],
                        input_names=["seas_high_flow_hsi_ras", "morph_unit_ras_hsi", "fish_cover_hsi_raster", "substrate_hsi_raster", "percent_silt_hsi_raster"],
                        expression=f"({coefficient_of_variation_hsi} + morph_unit_ras_hsi + fish_cover_hsi_raster + seas_high_flow_hsi_ras + substrate_hsi_raster + percent_silt_hsi_raster) / 6"
                    )
                    AddMessage(f"Saving WesternPearl_HSI_{unique_id}")
                    final_hsi_raster.save(f"{output_gdb}\\WesternPearl_HSI_{unique_id}")
                elif ("califloat" in morph_unit_ras_hsi.lower()):
                    final_hsi_raster = RasterCalculator(
                        rasters=[morph_unit_ras_hsi],
                        input_names=["morph_unit_ras_hsi"],
                        expression=f"({coefficient_of_variation_hsi} + morph_unit_ras_hsi) / 2"
                    )
                    AddMessage(f"Saving CaliFloater_HSI_{unique_id}")
                    final_hsi_raster.save(f"{output_gdb}\\CaliFloater_HSI_{unique_id}")

    hsi_raster_list = ListRasters("*_HSI_*")
    final_hsi_raster_list = [ras for ras in hsi_raster_list if "morphunit" not in ras.lower()]
    for hsi_ras in final_hsi_raster_list:
        AddMessage(f"Calculating {hsi_ras}_Stats")
        ZonalStatisticsAsTable(
            in_zone_data=zone_data,
            zone_field=zone_field,
            in_value_raster=f"{hsi_ras}",
            out_table=f"{output_gdb}\\{hsi_ras}_Stats",
            ignore_nodata="DATA",
            statistics_type="ALL",
            process_as_multidimensional="CURRENT_SLICE",
            percentile_values=90,
            percentile_interpolation_type="AUTO_DETECT",
            circular_calculation="ARITHMETIC",
            circular_wrap_value=360,
            out_join_layer=None
        )
        AddMessage(f"Saved {hsi_ras}_Stats")

        AddMessage(f"Calculating weighted usable area for {hsi_ras}")
        raster = Raster(hsi_ras)
        cell_width = raster.meanCellWidth
        cell_height = raster.meanCellHeight
        cell_area = cell_height * cell_width
        array = arcpy.RasterToNumPyArray(raster, nodata_to_value=np.nan)
        total_sum = np.nansum(array * cell_area)
        AddMessage(f"Saving weighted usable area value in {hsi_ras}_Stats")
        table = f"{output_gdb}\\{hsi_ras}_Stats"
        CalculateField(
            in_table=table,
            field="WUA",
            expression=total_sum,
            expression_type="PYTHON3",
            field_type="DOUBLE"
        )

    arcpy.CheckInExtension("Spatial")
    return
if __name__ == "__main__":
    input_gdb = arcpy.GetParameterAsText(0)
    output_gdb = arcpy.GetParameterAsText(1)
    coefficient_of_variation = arcpy.GetParameterAsText(2)
    fish_cover_hsi_raster = arcpy.GetParameterAsText(3)
    substrate_hsi_raster = arcpy.GetParameterAsText(4)
    percent_silt_hsi_raster = arcpy.GetParameterAsText(5)
    western_pearlshell_option = arcpy.GetParameterAsText(6)
    california_floater_option = arcpy.GetParameterAsText(7)
    zones_fc = arcpy.GetParameterAsText(8)
    zones_shp = arcpy.GetParameterAsText(9)
    zone_field = arcpy.GetParameterAsText(10)
    seasonal_high_flow_velocity_raster = arcpy.GetParameterAsText(11)
    script_tool(
        input_gdb,
        output_gdb,
        coefficient_of_variation,
        fish_cover_hsi_raster,
        substrate_hsi_raster,
        percent_silt_hsi_raster,
        western_pearlshell_option,
        california_floater_option,
        zones_fc,
        zones_shp,
        zone_field,
        seasonal_high_flow_velocity_raster
    )
