# -*- coding: utf-8 -*-

from arcpy import (Raster,
                   Parameter,
                   ListRasters,
                   AddMessage,
                   env,
                   Delete_management,
                   SetProgressorLabel,
                   )
from arcpy.ia import Con

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = "toolbox"

        # * List of tool classes associated with this toolbox.
        self.tools = [CalcHsi]

class CalcHsi(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Calculate HSI"
        self.description = "Calculate HSI for various fish species at different life stages"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        input_gdb = Parameter(
                displayName="Input Velocity and Depth rasters gdb",
                name="input_gdb",
                datatype="Workspace",
                parameterType="Required",
                direction="Input"
        )
        input_gdb.filter.list = ["Local Database"]
        brown_trout_condition = Parameter(
            displayName="Brown Trout",
            name="brown_trout_condition",
            datatype="Boolean",
            parameterType="Optional"
        )
        mountain_whitefish_condition = Parameter(
            displayName="Mountain Whitefish",
            name="mountain_whitefish_condition",
            datatype="Boolean",
            parameterType="Optional"
        )
        rainbow_trout_condition = Parameter(
            displayName="Rainbow Trout",
            name="rainbow_trout_condition",
            datatype="Boolean",
            parameterType="Optional"
        )
        sculpin_condition = Parameter(
            displayName="Sculpin",
            name="sculpin_condition",
            datatype="Boolean",
            parameterType="Optional"
        )
        adult_condition = Parameter(
            displayName="Adult",
            name="adult_condition",
            datatype="Boolean",
            parameterType="Optional"
        )
        juvenile_condition = Parameter(
            displayName="Juvenile",
            name="juvenile_condition",
            datatype="Boolean",
            parameterType="Optional"
        )
        fry_condition = Parameter(
            displayName="Fry",
            name="fry_condition",
            datatype="Boolean",
            parameterType="Optional"
        )
        spawn_condition = Parameter(
            displayName="Spawn",
            name="spawn_condition",
            datatype="Boolean",
            parameterType="Optional"
        )
        output_gdb = Parameter(
                displayName="Geodatabase to save output",
                name="output_gdb",
                datatype="Workspace",
                parameterType="Required",
                direction="Input"
        )
        output_gdb.filter.list = ["Local Database"]
        params = [input_gdb,
                  brown_trout_condition,
                  mountain_whitefish_condition,
                  rainbow_trout_condition,
                  sculpin_condition,
                  adult_condition,
                  juvenile_condition,
                  fry_condition,
                  spawn_condition,
                  output_gdb]
        return params
    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        depth_velocity_raster_gdb = parameters[0].valueAsText
        brown_trout_condition = parameters[1].valueAsText
        mountain_whitefish_condition = parameters[2].valueAsText
        rainbow_trout_condition = parameters[3].valueAsText
        sculpin_condition = parameters[4].valueAsText
        adult_condition = parameters[5].valueAsText
        juvenile_condition = parameters[6].valueAsText
        fry_condition = parameters[7].valueAsText
        spawn_condition = parameters[8].valueAsText
        output_workspace = parameters[9].valueAsText
        env.workspace = depth_velocity_raster_gdb

        AddMessage(f"{depth_velocity_raster_gdb} is the input gdb")

        raster_list = ListRasters("*")
        depth_rasters = []
        velocity_rasters = []

        for raster in raster_list:
            if "Dep" in raster:
                depth_rasters.append(raster)
            elif "Vel" in raster:
                velocity_rasters.append(raster)

        AddMessage(f"{depth_rasters} are the depth rasters")
        AddMessage(f"{velocity_rasters} are the velocity rasters")

        for dep_ras in depth_rasters:
            for vel_ras in velocity_rasters:
                if (dep_ras[3:]) == (vel_ras[3:]):
                    dep_raster = Raster(dep_ras)
                    vel_raster = Raster(vel_ras)

                    if (spawn_condition):
                        if (brown_trout_condition):
                            SetProgressorLabel("Calculating depth HSI for spawn brown trout...")
                            depth_hsi_raster = Con((dep_raster>0) & (dep_raster<0.2),0,Con((dep_raster>0.2) & (dep_raster<0.8),(1.666667*dep_raster)-0.3333333,Con(dep_raster>0.8,1)))
                            SetProgressorLabel("Calculating velocity HSI for spawn brown trout...")
                            velocity_hsi_raster = Con((vel_raster>0) & (vel_raster<0.3),0,Con((vel_raster>0.3) & (vel_raster<0.7),(2.5*vel_raster)-0.75,Con((vel_raster>0.7) & (vel_raster<1.7),1,Con((vel_raster>1.7) & (vel_raster<3.9),(-0.45455*vel_raster)+1.772727,Con(vel_raster>3.9,0)))))
                            SetProgressorLabel("Calculating final HSI raster for spawn brown trout...")
                            final_hsi_raster = Con(depth_hsi_raster < velocity_hsi_raster, depth_hsi_raster, velocity_hsi_raster)
                            final_hsi_raster.save(output_workspace + r"\BrownTroutSpawn" + dep_ras[3:] + "Hsi")
                            Delete_management(depth_hsi_raster)
                            Delete_management(velocity_hsi_raster)
                        if (mountain_whitefish_condition):
                            SetProgressorLabel("Calculating depth HSI for spawn mountain whitefish...")
                            depth_hsi_raster = Con((dep_raster>0) & (dep_raster<0.35),0,Con((dep_raster>0.35) & (dep_raster<0.45),(1.8*dep_raster)-0.63,Con((dep_raster>0.45) & (dep_raster<3.15),(0.3*dep_raster)+0.0433333,Con((dep_raster>3.15) & (dep_raster<3.25),1,Con((dep_raster>3.25) & (dep_raster<3.85),(-0.67*dep_raster)+3.1666667,Con(dep_raster>3.85,0.6))))))
                            SetProgressorLabel("Calculating velocity HSI for spawn mountain whitefish...")
                            velocity_hsi_raster = Con((vel_raster>0) & (vel_raster<1.45),(0.34*vel_raster)+0.23,Con((vel_raster>1.45) & (vel_raster<1.65),(0.85*vel_raster)-0.5025,Con((vel_raster>1.65) & (vel_raster<2.05),(0.25*vel_raster)+0.4875,Con((vel_raster>2.05) & (vel_raster<2.95),1,Con((vel_raster>2.95) & (vel_raster<3.95),(-0.72*vel_raster)+3.124,Con((vel_raster>3.95) & (vel_raster<5),(-0.266666667*vel_raster)+1.33333,Con(vel_raster>5,0)))))))
                            SetProgressorLabel("Calculating final HSI raster for spawn mountain whitefish...")
                            final_hsi_raster = Con(depth_hsi_raster < velocity_hsi_raster, depth_hsi_raster, velocity_hsi_raster)
                            final_hsi_raster.save(output_workspace + r"\MountainWhitefishSpawn" + dep_ras[3:] + "Hsi")
                            Delete_management(depth_hsi_raster)
                            Delete_management(velocity_hsi_raster)
                        if (rainbow_trout_condition):
                            SetProgressorLabel("Calculating depth HSI for spawn rainbow trout...")
                            depth_hsi_raster = Con((dep_raster>0) & (dep_raster<0.15),0,Con((dep_raster>0.15) & (dep_raster<0.35),(1.5*dep_raster)-0.225,Con((dep_raster>0.35) & (dep_raster<0.45),(5.5*dep_raster)-1.625,Con((dep_raster>0.45) & (dep_raster<0.55),(1.5*dep_raster)+0.175,Con((dep_raster>0.55) & (dep_raster<0.95),1,Con((dep_raster>0.95) & (dep_raster<1.35),(-1*dep_raster)+1.95,Con((dep_raster>1.35) & (dep_raster<1.45),(-3.5*dep_raster)+5.325,Con(dep_raster>1.45,0.25))))))))
                            SetProgressorLabel("Calculating velocity HSI for spawn rainbow trout...")
                            velocity_hsi_raster = Con((vel_raster>0) & (vel_raster<0.25),0,Con((vel_raster>0.25) & (vel_raster<1.25),(0.45*vel_raster)-0.1125,Con((vel_raster>1.25) & (vel_raster<1.65),(1.375*vel_raster)-1.26875,Con((vel_raster>1.65) & (vel_raster<2.05),1,Con((vel_raster>2.05) & (vel_raster<2.75),(-0.5*vel_raster)+2.025,Con((vel_raster>2.75) & (vel_raster<2.95),(-3.25*vel_raster)+9.5875,Con(vel_raster>2.95,0)))))))
                            SetProgressorLabel("Calculating final HSI raster for spawn rainbow trout...")
                            final_hsi_raster = Con(depth_hsi_raster < velocity_hsi_raster, depth_hsi_raster, velocity_hsi_raster)
                            final_hsi_raster.save(output_workspace + r"\RainbowTroutSpawn" + dep_ras[3:] + "Hsi")
                            Delete_management(depth_hsi_raster)
                            Delete_management(velocity_hsi_raster)
                        if (sculpin_condition):
                            AddMessage("No spawn data for sculpin")
                    
                    if (fry_condition):
                        if (brown_trout_condition):
                            SetProgressorLabel("Calculating depth HSI for fry brown trout...")
                            depth_hsi_raster = Con((dep_raster>0) & (dep_raster<=0.66),(0.287879*dep_raster),Con((dep_raster>0.66) & (dep_raster<=1.31),(1.246154*dep_raster)-0.63246,Con((dep_raster>1.31) & (dep_raster<=1.61),1,Con((dep_raster>1.61) & (dep_raster<=2.3),(-0.26087*dep_raster)+1.42,Con((dep_raster>2.3) & (dep_raster<=4.6),(-0.35652*dep_raster)+1.64,Con(dep_raster>4.6,0))))))
                            SetProgressorLabel("Calculating velocity HSI for fry brown trout...")
                            velocity_hsi_raster = Con((vel_raster>0) & (vel_raster<=0.1),(3.8*vel_raster),Con((vel_raster>0.1) & (vel_raster<=0.6),(1.24*vel_raster)+0.256,Con((vel_raster>0.6) & (vel_raster<=0.9),(-0.2*vel_raster)+1.12,Con((vel_raster>0.9) & (vel_raster<=1.2),(-1.56667*vel_raster)+2.35,Con((vel_raster>1.2) & (vel_raster<=2.9),(-0.27647*vel_raster)+0.801765,Con((vel_raster>2.9),0))))))
                            SetProgressorLabel("Calculating final HSI raster for fry brown trout...")
                            final_hsi_raster = Con(depth_hsi_raster < velocity_hsi_raster, depth_hsi_raster, velocity_hsi_raster)
                            final_hsi_raster.save(output_workspace + r"\BrownTroutFry" + dep_ras[3:] + "Hsi")
                            Delete_management(depth_hsi_raster)
                            Delete_management(velocity_hsi_raster)
                        if (rainbow_trout_condition):
                            SetProgressorLabel("Calculating depth HSI for fry rainbow trout...")
                            depth_hsi_raster = Con((dep_raster>0) & (dep_raster<=0.1),(1.1*dep_raster),Con((dep_raster>0.1) & (dep_raster<=0.5),(2.225*dep_raster)-0.1125,Con((dep_raster>0.5) & (dep_raster<=1.64),1,Con((dep_raster>1.64) & (dep_raster<=2.46),(-0.86585*dep_raster)+2.42,Con((dep_raster>2.46) & (dep_raster<=3.28),(-0.19512*dep_raster)+0.77,Con((dep_raster>3.28) & (dep_raster<=4.1),(-0.10976*dep_raster)+0.49,Con((dep_raster>4.1) & (dep_raster<=4.92),(-0.02439*dep_raster)+0.14,Con((dep_raster>4.92) & (dep_raster<=5.74),(-0.0122*dep_raster)+0.08,Con((dep_raster>5.74) & (dep_raster<=7.38),0.01,Con((dep_raster>7.38) & (dep_raster<=8.2),(-0.0122*dep_raster)+0.1,Con(dep_raster>8.2,0)))))))))))
                            SetProgressorLabel("Calculating velocity HSI for fry rainbow trout...")
                            velocity_hsi_raster = Con((vel_raster>0) & (vel_raster<=0.49),(-0.44898*vel_raster)+1,Con((vel_raster>0.49) & (vel_raster<=0.98),(-1.20408*vel_raster)+1.37,Con((vel_raster>0.98) & (vel_raster<=1.48),(-0.3*vel_raster)+0.484,Con((vel_raster>1.48) & (vel_raster<=1.97),(-0.06122*vel_raster)+0.130612,Con((vel_raster>1.97) & (vel_raster<=2.46),0.01,Con((vel_raster>2.46) & (vel_raster<=2.95),(-0.02041*vel_raster)+0.060204,Con(vel_raster>2.95,0)))))))
                            SetProgressorLabel("Calculating final HSI raster for fry rainbow trout...")
                            final_hsi_raster = Con(depth_hsi_raster < velocity_hsi_raster, depth_hsi_raster, velocity_hsi_raster)
                            final_hsi_raster.save(output_workspace + r"\RainbowTroutFry" + dep_ras[3:] + "Hsi")
                            Delete_management(depth_hsi_raster)
                            Delete_management(velocity_hsi_raster)
                        if (mountain_whitefish_condition):
                            AddMessage("No fry data for mountain whitefish")
                        if (sculpin_condition):
                            AddMessage("No fry data for sculpin")
                    
                    if (juvenile_condition):
                        if (brown_trout_condition):
                            SetProgressorLabel("Calculating depth HSI for juvenile brown trout...")
                            depth_hsi_raster = Con((dep_raster>0) & (dep_raster<0.5),(0.24*dep_raster),Con((dep_raster>0.5) & (dep_raster<1),(0.98*dep_raster)-0.37,Con((dep_raster>1) & (dep_raster<2),(0.23*dep_raster)+0.38,Con((dep_raster>2) & (dep_raster<3),(0.16*dep_raster)+0.52,Con((dep_raster>3) & (dep_raster<4),(-0.73*dep_raster)+3.19,Con((dep_raster>4) & (dep_raster<7),(-0.01*dep_raster)+0.31,Con((dep_raster>7) & (dep_raster<8),(-0.16*dep_raster)+1.36,Con(dep_raster>8,0.08))))))))
                            SetProgressorLabel("Calculating velocity HSI for juvenile brown trout...")
                            velocity_hsi_raster = Con((vel_raster>0) & (vel_raster<0.1),(3*vel_raster)+0.58,Con((vel_raster>0.1) & (vel_raster<0.5),(0.3*vel_raster)+0.85,Con((vel_raster>0.5) & (vel_raster<1),(-0.16*vel_raster)+1.08,Con((vel_raster>1) & (vel_raster<1.5),(-0.44*vel_raster)+1.36,Con((vel_raster>1.5) & (vel_raster<2),(-0.88*vel_raster)+2.02,Con((vel_raster>2) & (vel_raster<3.5),(-0.14*vel_raster)+0.54,Con((vel_raster>3.5) & (vel_raster<4.3),(-0.0625*vel_raster)+0.26875,Con(vel_raster>4.3,0))))))))
                            SetProgressorLabel("Calculating final HSI raster for juvenile brown trout...")
                            final_hsi_raster = Con(depth_hsi_raster < velocity_hsi_raster, depth_hsi_raster, velocity_hsi_raster)
                            final_hsi_raster.save(output_workspace + r"\BrownTroutJuvenile" + dep_ras[3:] + "Hsi")
                            Delete_management(depth_hsi_raster)
                            Delete_management(velocity_hsi_raster)
                        if (mountain_whitefish_condition):
                            SetProgressorLabel("Calculating depth HSI for juvenile mountain whitefish...")
                            depth_hsi_raster = Con((dep_raster>0) & (dep_raster<0.45),0,Con((dep_raster>0.45) & (dep_raster<0.75),(0.7*dep_raster)-0.315,Con((dep_raster>0.75) & (dep_raster<2.05),(0.45*dep_raster)-0.130384615,Con((dep_raster>2.05) & (dep_raster<2.85),(0.25*dep_raster)+0.2875,Con((dep_raster>2.85) & (dep_raster<2.95),1,Con((dep_raster>2.95) & (dep_raster<3.25),(-0.17*dep_raster)+1.491666667,Con((dep_raster>3.25) & (dep_raster<3.95),(-0.61*dep_raster)+2.946428571,Con((dep_raster>3.95) & (dep_raster<4.75),(-0.28*dep_raster)+1.60625,Con(dep_raster>4.75,0.3)))))))))
                            SetProgressorLabel("Calculating velocity HSI for juvenile mountain whitefish...")
                            velocity_hsi_raster = Con((vel_raster>0) & (vel_raster<0.85),(0.647*vel_raster)+0.25,Con((vel_raster>0.85) & (vel_raster<1.85),(0.2*vel_raster)+0.63,Con((vel_raster>1.85) & (vel_raster<2.25),1,Con((vel_raster>2.25) & (vel_raster<3.45),(-0.125*vel_raster)+1.28125,Con((vel_raster>3.45) & (vel_raster<5),(-0.548*vel_raster)+2.741935484,Con(vel_raster>5,0))))))
                            SetProgressorLabel("Calculating final HSI raster for juvenile mountain whitefish...")
                            final_hsi_raster = Con(depth_hsi_raster < velocity_hsi_raster, depth_hsi_raster, velocity_hsi_raster)
                            final_hsi_raster.save(output_workspace + r"\MountainWhitefishJuvenile" + dep_ras[3:] + "Hsi")
                            Delete_management(depth_hsi_raster)
                            Delete_management(velocity_hsi_raster)
                        if (rainbow_trout_condition):
                            SetProgressorLabel("Calculating depth HSI for juvenile rainbow trout...")
                            depth_hsi_raster = Con((dep_raster>0) & (dep_raster<0.15),0,Con((dep_raster>0.15) & (dep_raster<0.65),(0.2*dep_raster)-0.03,Con((dep_raster>0.65) & (dep_raster<1.35),(0.757142857*dep_raster)-0.392142857,Con((dep_raster>1.35) & (dep_raster<2.65),(0.284615385*dep_raster)+0.245769231,Con(dep_raster>2.65,1)))))
                            SetProgressorLabel("Calculating velocity HSI for juvenile rainbow trout...")
                            velocity_hsi_raster = Con((vel_raster>0) & (vel_raster<0.75),(0.6*vel_raster)+0.55,Con((vel_raster>0.75) & (vel_raster<0.95),1,Con((vel_raster>0.95) & (vel_raster<1.15),(-0.65*vel_raster)+1.6175,Con((vel_raster>1.15) & (vel_raster<1.55),(-0.225*vel_raster)+1.12875,Con((vel_raster>1.55) & (vel_raster<1.85),(-0.8*vel_raster)+2.02,Con((vel_raster>1.85) & (vel_raster<3.15),(-0.184615385*vel_raster)+0.881538462,Con((vel_raster>3.15) & (vel_raster<3.85),(-0.328571429*vel_raster)+1.335,Con((vel_raster>3.85) & (vel_raster<5),(-0.060869565*vel_raster)+0.304347826,Con(vel_raster>5,0)))))))))
                            SetProgressorLabel("Calculating final HSI raster for juvenile rainbow trout...")
                            final_hsi_raster = Con(depth_hsi_raster < velocity_hsi_raster, depth_hsi_raster, velocity_hsi_raster)
                            final_hsi_raster.save(output_workspace + r"\RainbowTroutJuvenile" + dep_ras[3:] + "Hsi")
                            Delete_management(depth_hsi_raster)
                            Delete_management(velocity_hsi_raster)
                        if (sculpin_condition):
                            SetProgressorLabel("Calculating depth HSI for juvenile sculpin...")
                            depth_hsi_raster = Con((dep_raster>0) & (dep_raster<0.3281),(0.4572*dep_raster)+0.85,Con((dep_raster>0.3281) & (dep_raster<1.6404),(-0.4953*dep_raster)+1.1625,Con((dep_raster>1.6404) & (dep_raster<3.2808),(-0.1524*dep_raster)+0.6,Con((dep_raster>3.2808) & (dep_raster<4.9213),(-0.03048*dep_raster)+0.2,Con((dep_raster>4.9213) & (dep_raster<6.5617),(-0.03048*dep_raster)+0.2,Con(dep_raster>6.5617,0))))))
                            SetProgressorLabel("Calculating velocity HSI for juvenile sculpin ")
                            velocity_hsi_raster = Con((vel_raster>0) & (vel_raster<0.2),(1.2192*vel_raster)+0.8,Con((vel_raster>0.2) & (vel_raster<1.6),(-0.41995*vel_raster)+1.068889,Con((vel_raster>1.6) & (vel_raster<3.3),(-0.1585*vel_raster)+0.64,Con((vel_raster>3.3) & (vel_raster<4.9),(-0.04267*vel_raster)+0.26,Con((vel_raster>4.9) & (vel_raster<6.6),(-0.03048*vel_raster)+0.2,Con(vel_raster>6.6,0))))))
                            SetProgressorLabel("Calculating final HSI raster for juvenile sculpin...")
                            final_hsi_raster = Con(depth_hsi_raster < velocity_hsi_raster, depth_hsi_raster, velocity_hsi_raster)
                            final_hsi_raster.save(output_workspace + r"\SculpinJuvenile" + dep_ras[3:] + "Hsi")
                            Delete_management(depth_hsi_raster)
                            Delete_management(velocity_hsi_raster)
                    
                    if (adult_condition):
                        if (brown_trout_condition):
                            SetProgressorLabel("Calculating depth HSI for adult brown trout...")
                            depth_hsi_raster = Con((dep_raster>0) & (dep_raster<1.6),(0.54375*dep_raster),Con((dep_raster>1.6) & (dep_raster<2),(0.2*dep_raster)+0.55,Con((dep_raster>2) & (dep_raster<2.6),(0.083333*dep_raster)+0.783333,Con((dep_raster>2.6) & (dep_raster<3.6),(-0.16*dep_raster)+1.416,Con((dep_raster>3.6) & (dep_raster<4),(-0.975*dep_raster)+4.35,Con((dep_raster>4) & (dep_raster<5),(-0.15*dep_raster)+1.05,Con((dep_raster>5) & (dep_raster<7),(-0.045*dep_raster)+0.525,Con(dep_raster>7,0.21))))))))
                            SetProgressorLabel("Calculating velocity HSI for adult brown trout... ")
                            velocity_hsi_raster = Con((vel_raster>0) & (vel_raster<0.1),(4.9*vel_raster)+0.21,Con((vel_raster>0.1) & (vel_raster<0.5),(0.75*vel_raster)+0.625,Con((vel_raster>0.5) & (vel_raster<1),(-0.62*vel_raster)+1.31,Con((vel_raster>1) & (vel_raster<1.5),(-0.38*vel_raster)+1.07,Con((vel_raster>1.5) & (vel_raster<2.4),(-0.33333*vel_raster)+1,Con((vel_raster>2.4) & (vel_raster<3.1),(-0.24286*vel_raster)+0.782857,Con((vel_raster>3.1) & (vel_raster<5),0.03,Con((vel_raster>5) & (vel_raster<6),(-0.03*vel_raster)+0.18,Con(vel_raster>6,0)))))))))
                            SetProgressorLabel("Calculating final HSI raster for adult brown trout...")
                            final_hsi_raster = Con(depth_hsi_raster < velocity_hsi_raster, depth_hsi_raster, velocity_hsi_raster)
                            final_hsi_raster.save(output_workspace + r"\BrownTroutAdult" + dep_ras[3:] + "Hsi")
                            Delete_management(depth_hsi_raster)
                            Delete_management(velocity_hsi_raster)
                        if (mountain_whitefish_condition):
                            SetProgressorLabel("Calculating depth HSI for adult mountain whitefish...")
                            depth_hsi_raster = Con((dep_raster>0) & (dep_raster<0.55),0,Con((dep_raster>0.55) & (dep_raster<1.55),(0.3*dep_raster)-0.165,Con((dep_raster>1.55) & (dep_raster<2.25),(0.143*dep_raster)+0.0785714,Con((dep_raster>2.25) & (dep_raster<3.25),(0.6*dep_raster)-0.95,Con((dep_raster>3.25) & (dep_raster<3.45),(-0.95*dep_raster)+4.0875,Con((dep_raster>3.45) & (dep_raster<3.95),0.81,Con((dep_raster>3.95) & (dep_raster<4.75),(-0.175*dep_raster)+1.50125,Con((dep_raster>4.75) & (dep_raster<5),(-0.680*dep_raster)+3.9,Con(dep_raster>5,0.5)))))))))
                            SetProgressorLabel("Calculating velocity HSI for adult mountain whitefish...")
                            velocity_hsi_raster = Con((vel_raster>0) & (vel_raster<1.45),(0.345*vel_raster)+0.2,Con((vel_raster>1.45) & (vel_raster<1.75),(0.667*vel_raster)-0.266667,Con((vel_raster>1.75) & (vel_raster<2.05),(0.333*vel_raster)+0.3166667,Con((vel_raster>2.05) & (vel_raster<2.35),1,Con((vel_raster>2.35) & (vel_raster<3.05),(-0.229*vel_raster)+1.5371429,Con((vel_raster>3.05) & (vel_raster<3.35),(-0.867*vel_raster)+3.4833333,Con((vel_raster>3.35) & (vel_raster<5.5),(-0.27*vel_raster)+1.4837209,Con(vel_raster>5.5,0))))))))
                            SetProgressorLabel("Calculating final HSI raster for adult mountain whitefish...")
                            final_hsi_raster = Con(depth_hsi_raster < velocity_hsi_raster, depth_hsi_raster, velocity_hsi_raster)
                            final_hsi_raster.save(output_workspace + r"\MountainWhitefishAdult" + dep_ras[3:] + "Hsi")
                            Delete_management(depth_hsi_raster)
                            Delete_management(velocity_hsi_raster)
                        if (rainbow_trout_condition):
                            SetProgressorLabel("Calculating depth HSI for adult rainbow trout...")
                            depth_hsi_raster = Con((dep_raster>0) & (dep_raster<0.75),(0.04*dep_raster),Con((dep_raster>0.75) & (dep_raster<3.25),(0.23*dep_raster)-0.141,Con((dep_raster>3.25) & (dep_raster<3.45),(0.95*dep_raster)-2.4875,Con((dep_raster>3.45) & (dep_raster<3.85),(0.525*dep_raster)-1.02125,Con(dep_raster>3.85,1)))))
                            SetProgressorLabel("Calculating velocity HSI for adult rainbow trout...")
                            velocity_hsi_raster = Con((vel_raster>0) & (vel_raster<0.35),(1.03*vel_raster)+0.3,Con((vel_raster>0.35) & (vel_raster<0.95),(0.57*vel_raster)+0.461666667,Con((vel_raster>0.95) & (vel_raster<1.05),1,Con((vel_raster>1.05) & (vel_raster<1.15),(-0.4*vel_raster)+1.42,Con((vel_raster>1.15) & (vel_raster<1.45),(-1.3*vel_raster)+2.455,Con((vel_raster>1.45) & (vel_raster<1.55),(-0.5*vel_raster)+1.295,Con((vel_raster>1.55) & (vel_raster<5),(-0.15*vel_raster)+0.753623188,Con(vel_raster>5,0))))))))
                            SetProgressorLabel("Calculating final HSI raster for adult rainbow trout...")
                            final_hsi_raster = Con(depth_hsi_raster < velocity_hsi_raster, depth_hsi_raster, velocity_hsi_raster)
                            final_hsi_raster.save(output_workspace + r"\RainbowTroutAdult" + dep_ras[3:] + "Hsi")
                            Delete_management(depth_hsi_raster)
                            Delete_management(velocity_hsi_raster)
                        if (sculpin_condition):
                            SetProgressorLabel("Calculating depth HSI for adult sculpin ")
                            depth_hsi_raster = Con((dep_raster>0) & (dep_raster<0.3281),(0.4572*dep_raster)+0.85,Con((dep_raster>0.3281) & (dep_raster<1.6404),(-0.4953*dep_raster)+1.1625,Con((dep_raster>1.6404) & (dep_raster<3.2808),(-0.1524*dep_raster)+0.6,Con((dep_raster>3.2808) & (dep_raster<4.9213),(-0.03048*dep_raster)+0.2,Con((dep_raster>4.9213) & (dep_raster<6.5617),(-0.03048*dep_raster)+0.2,Con(dep_raster>6.5617,0))))))
                            SetProgressorLabel("Calculating velocity HSI for adult sculpin ")
                            velocity_hsi_raster = Con((vel_raster>0) & (vel_raster<0.2),(1.2192*vel_raster)+0.8,Con((vel_raster>0.2) & (vel_raster<1.6),(-0.41995*vel_raster)+1.068889,Con((vel_raster>1.6) & (vel_raster<3.3),(-0.1585*vel_raster)+0.64,Con((vel_raster>3.3) & (vel_raster<4.9),(-0.04267*vel_raster)+0.26,Con((vel_raster>4.9) & (vel_raster<6.6),(-0.03048*vel_raster)+0.2,Con(vel_raster>6.6,0))))))
                            SetProgressorLabel("Calculating final HSI raster for adult sculpin...")
                            final_hsi_raster = Con(depth_hsi_raster < velocity_hsi_raster, depth_hsi_raster, velocity_hsi_raster)
                            final_hsi_raster.save(output_workspace + r"\SculpinAdult" + dep_ras[3:] + "Hsi")
                            Delete_management(depth_hsi_raster)
                            Delete_management(velocity_hsi_raster)
        return
