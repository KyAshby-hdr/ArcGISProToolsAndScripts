# -*- coding: utf-8 -*-

# import arcpy
from arcpy import (Raster,
                   Parameter,
                   ListRasters,
                   AddMessage,
                   env,
                   Delete_management,
                   SetProgressorLabel,
                   AddWarning)
from arcpy.ia import Con

class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = "toolbox"

        # List of tool classes associated with this toolbox
        self.tools = [CalcHSI]

class CalcHSI(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "CalcHSIver2"
        self.description = "Calculate HSI for various fish species at different life stages"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        InputGdb = Parameter(
                displayName="Input Velocity and Depth rasters gdb",
                name="InputGdb",
                datatype="Workspace",
                parameterType="Required",
                direction="Input"
        )
        InputGdb.filter.list = ["Local Database"]
        BrownTroutCondition = Parameter(
            displayName="Brown Trout",
            name="BrownTroutCondition",
            datatype="Boolean",
            parameterType="Optional"
        )
        MountainWhitefishCondition = Parameter(
            displayName="Mountain Whitefish",
            name="MountainWhitefishCondition",
            datatype="Boolean",
            parameterType="Optional"
        )
        RainbowTroutCondition = Parameter(
            displayName="Rainbow Trout",
            name="RainbowTroutCondition",
            datatype="Boolean",
            parameterType="Optional"
        )
        SculpinCondition = Parameter(
            displayName="Sculpin",
            name="SculpinCondition",
            datatype="Boolean",
            parameterType="Optional"
        )
        AdultCondition = Parameter(
            displayName="Adult",
            name="AdultCondition",
            datatype="Boolean",
            parameterType="Optional"
        )
        JuvenileCondition = Parameter(
            displayName="Juvenile",
            name="JuvenileCondition",
            datatype="Boolean",
            parameterType="Optional"
        )
        FryCondition = Parameter(
            displayName="Fry",
            name="FryCondition",
            datatype="Boolean",
            parameterType="Optional"
        )
        SpawnCondition = Parameter(
            displayName="Spawn",
            name="SpawnCondition",
            datatype="Boolean",
            parameterType="Optional"
        )
        OutputGdb = Parameter(
                displayName="Geodatabase to save output",
                name="OutputGdb",
                datatype="Workspace",
                parameterType="Required",
                direction="Input"
        )
        OutputGdb.filter.list = ["Local Database"]
        params = [InputGdb,
                  BrownTroutCondition,
                  MountainWhitefishCondition,
                  RainbowTroutCondition,
                  SculpinCondition,
                  AdultCondition,
                  JuvenileCondition,
                  FryCondition,
                  SpawnCondition,
                  OutputGdb]
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
        DepthVelocityRasterGdb = parameters[0].valueAsText
        BrownTroutCondition = parameters[1].valueAsText
        MountainWhitefishCondition = parameters[2].valueAsText
        RainbowTroutCondition = parameters[3].valueAsText
        SculpinCondition = parameters[4].valueAsText
        AdultCondition = parameters[5].valueAsText
        JuvenileCondition = parameters[6].valueAsText
        FryCondition = parameters[7].valueAsText
        SpawnCondition = parameters[8].valueAsText
        OutputWorkspace = parameters[9].valueAsText
        env.workspace = DepthVelocityRasterGdb

        AddMessage(f"{DepthVelocityRasterGdb} is the input gdb")

        raster_list = ListRasters("*")
        DepthRasters = []
        VelocityRasters = []

        for raster in raster_list:
            if "Dep" in raster:
                DepthRasters.append(raster)
            elif "Vel" in raster:
                VelocityRasters.append(raster)

        AddMessage(f"{DepthRasters} are the depth rasters")
        AddMessage(f"{VelocityRasters} are the velocity rasters")

        for depRas in DepthRasters:
            for velRas in VelocityRasters:
                if (depRas[3:]) == (velRas[3:]):
                    DepRas = Raster(depRas)
                    VelRas = Raster(velRas)

                    if (SpawnCondition):
                        if (BrownTroutCondition):
                            SetProgressorLabel("Calculating depth HSI for spawn brown trout...")
                            DepthRaster = Con((DepRas>0) & (DepRas<0.2),0,Con((DepRas>0.2) & (DepRas<0.8),(1.666667*DepRas)-0.3333333,Con(DepRas>0.8,1)))
                            SetProgressorLabel("Calculating velocity HSI for spawn brown trout...")
                            VelocityRaster = Con((VelRas>0) & (VelRas<0.3),0,Con((VelRas>0.3) & (VelRas<0.7),(2.5*VelRas)-0.75,Con((VelRas>0.7) & (VelRas<1.7),1,Con((VelRas>1.7) & (VelRas<3.9),(-0.45455*VelRas)+1.772727,Con(VelRas>3.9,0)))))
                            SetProgressorLabel("Calculating final HSI raster for spawn brown trout...")
                            FinalRaster = Con(DepthRaster < VelocityRaster, DepthRaster, VelocityRaster)
                            FinalRaster.save(OutputWorkspace + r"\BrownTroutSpawn" + depRas[3:] + "Hsi")
                            Delete_management(DepthRaster)
                            Delete_management(VelocityRaster)
                        if (MountainWhitefishCondition):
                            SetProgressorLabel("Calculating depth HSI for spawn mountain whitefish...")
                            DepthRaster = Con((DepRas>0) & (DepRas<0.35),0,Con((DepRas>0.35) & (DepRas<0.45),(1.8*DepRas)-0.63,Con((DepRas>0.45) & (DepRas<3.15),(0.3*DepRas)+0.0433333,Con((DepRas>3.15) & (DepRas<3.25),1,Con((DepRas>3.25) & (DepRas<3.85),(-0.67*DepRas)+3.1666667,Con(DepRas>3.85,0.6))))))
                            SetProgressorLabel("Calculating velocity HSI for spawn mountain whitefish...")
                            VelocityRaster = Con((VelRas>0) & (VelRas<1.45),(0.34*VelRas)+0.23,Con((VelRas>1.45) & (VelRas<1.65),(0.85*VelRas)-0.5025,Con((VelRas>1.65) & (VelRas<2.05),(0.25*VelRas)+0.4875,Con((VelRas>2.05) & (VelRas<2.95),1,Con((VelRas>2.95) & (VelRas<3.95),(-0.72*VelRas)+3.124,Con((VelRas>3.95) & (VelRas<5),(-0.266666667*VelRas)+1.33333,Con(VelRas>5,0)))))))
                            SetProgressorLabel("Calculating final HSI raster for spawn mountain whitefish...")
                            FinalRaster = Con(DepthRaster < VelocityRaster, DepthRaster, VelocityRaster)
                            FinalRaster.save(OutputWorkspace + r"\MountainWhitefishSpawn" + depRas[3:] + "Hsi")
                            Delete_management(DepthRaster)
                            Delete_management(VelocityRaster)
                        if (RainbowTroutCondition):
                            SetProgressorLabel("Calculating depth HSI for spawn rainbow trout...")
                            DepthRaster = Con((DepRas>0) & (DepRas<0.15),0,Con((DepRas>0.15) & (DepRas<0.35),(1.5*DepRas)-0.225,Con((DepRas>0.35) & (DepRas<0.45),(5.5*DepRas)-1.625,Con((DepRas>0.45) & (DepRas<0.55),(1.5*DepRas)+0.175,Con((DepRas>0.55) & (DepRas<0.95),1,Con((DepRas>0.95) & (DepRas<1.35),(-1*DepRas)+1.95,Con((DepRas>1.35) & (DepRas<1.45),(-3.5*DepRas)+5.325,Con(DepRas>1.45,0.25))))))))
                            SetProgressorLabel("Calculating velocity HSI for spawn rainbow trout...")
                            VelocityRaster = Con((VelRas>0) & (VelRas<0.25),0,Con((VelRas>0.25) & (VelRas<1.25),(0.45*VelRas)-0.1125,Con((VelRas>1.25) & (VelRas<1.65),(1.375*VelRas)-1.26875,Con((VelRas>1.65) & (VelRas<2.05),1,Con((VelRas>2.05) & (VelRas<2.75),(-0.5*VelRas)+2.025,Con((VelRas>2.75) & (VelRas<2.95),(-3.25*VelRas)+9.5875,Con(VelRas>2.95,0)))))))
                            SetProgressorLabel("Calculating final HSI raster for spawn rainbow trout...")
                            FinalRaster = Con(DepthRaster < VelocityRaster, DepthRaster, VelocityRaster)
                            FinalRaster.save(OutputWorkspace + r"\RainbowTroutSpawn" + depRas[3:] + "Hsi")
                            Delete_management(DepthRaster)
                            Delete_management(VelocityRaster)
                        if (SculpinCondition):
                            AddMessage("No spawn data for sculpin")
                    
                    if (FryCondition):
                        if (BrownTroutCondition):
                            SetProgressorLabel("Calculating depth HSI for fry brown trout...")
                            DepthRaster = Con((DepRas>0) & (DepRas<=0.66),(0.287879*DepRas),Con((DepRas>0.66) & (DepRas<=1.31),(1.246154*DepRas)-0.63246,Con((DepRas>1.31) & (DepRas<=1.61),1,Con((DepRas>1.61) & (DepRas<=2.3),(-0.26087*DepRas)+1.42,Con((DepRas>2.3) & (DepRas<=4.6),(-0.35652*DepRas)+1.64,Con(DepRas>4.6,0))))))
                            SetProgressorLabel("Calculating velocity HSI for fry brown trout...")
                            VelocityRaster = Con((VelRas>0) & (VelRas<=0.1),(3.8*VelRas),Con((VelRas>0.1) & (VelRas<=0.6),(1.24*VelRas)+0.256,Con((VelRas>0.6) & (VelRas<=0.9),(-0.2*VelRas)+1.12,Con((VelRas>0.9) & (VelRas<=1.2),(-1.56667*VelRas)+2.35,Con((VelRas>1.2) & (VelRas<=2.9),(-0.27647*VelRas)+0.801765,Con((VelRas>2.9),0))))))
                            SetProgressorLabel("Calculating final HSI raster for fry brown trout...")
                            FinalRaster = Con(DepthRaster < VelocityRaster, DepthRaster, VelocityRaster)
                            FinalRaster.save(OutputWorkspace + r"\BrownTroutFry" + depRas[3:] + "Hsi")
                            Delete_management(DepthRaster)
                            Delete_management(VelocityRaster)
                        if (RainbowTroutCondition):
                            SetProgressorLabel("Calculating depth HSI for fry rainbow trout...")
                            DepthRaster = Con((DepRas>0) & (DepRas<=0.1),(1.1*DepRas),Con((DepRas>0.1) & (DepRas<=0.5),(2.225*DepRas)-0.1125,Con((DepRas>0.5) & (DepRas<=1.64),1,Con((DepRas>1.64) & (DepRas<=2.46),(-0.86585*DepRas)+2.42,Con((DepRas>2.46) & (DepRas<=3.28),(-0.19512*DepRas)+0.77,Con((DepRas>3.28) & (DepRas<=4.1),(-0.10976*DepRas)+0.49,Con((DepRas>4.1) & (DepRas<=4.92),(-0.02439*DepRas)+0.14,Con((DepRas>4.92) & (DepRas<=5.74),(-0.0122*DepRas)+0.08,Con((DepRas>5.74) & (DepRas<=7.38),0.01,Con((DepRas>7.38) & (DepRas<=8.2),(-0.0122*DepRas)+0.1,Con(DepRas>8.2,0)))))))))))
                            SetProgressorLabel("Calculating velocity HSI for fry rainbow trout...")
                            VelocityRaster = Con((VelRas>0) & (VelRas<=0.49),(-0.44898*VelRas)+1,Con((VelRas>0.49) & (VelRas<=0.98),(-1.20408*VelRas)+1.37,Con((VelRas>0.98) & (VelRas<=1.48),(-0.3*VelRas)+0.484,Con((VelRas>1.48) & (VelRas<=1.97),(-0.06122*VelRas)+0.130612,Con((VelRas>1.97) & (VelRas<=2.46),0.01,Con((VelRas>2.46) & (VelRas<=2.95),(-0.02041*VelRas)+0.060204,Con(VelRas>2.95,0)))))))
                            SetProgressorLabel("Calculating final HSI raster for fry rainbow trout...")
                            FinalRaster = Con(DepthRaster < VelocityRaster, DepthRaster, VelocityRaster)
                            FinalRaster.save(OutputWorkspace + r"\RainbowTroutFry" + depRas[3:] + "Hsi")
                            Delete_management(DepthRaster)
                            Delete_management(VelocityRaster)
                        if (MountainWhitefishCondition):
                            AddMessage("No fry data for mountain whitefish")
                        if (SculpinCondition):
                            AddMessage("No fry data for sculpin")
                    
                    if (JuvenileCondition):
                        if (BrownTroutCondition):
                            SetProgressorLabel("Calculating depth HSI for juvenile brown trout...")
                            DepthRaster = Con((DepRas>0) & (DepRas<0.5),(0.24*DepRas),Con((DepRas>0.5) & (DepRas<1),(0.98*DepRas)-0.37,Con((DepRas>1) & (DepRas<2),(0.23*DepRas)+0.38,Con((DepRas>2) & (DepRas<3),(0.16*DepRas)+0.52,Con((DepRas>3) & (DepRas<4),(-0.73*DepRas)+3.19,Con((DepRas>4) & (DepRas<7),(-0.01*DepRas)+0.31,Con((DepRas>7) & (DepRas<8),(-0.16*DepRas)+1.36,Con(DepRas>8,0.08))))))))
                            SetProgressorLabel("Calculating velocity HSI for juvenile brown trout...")
                            VelocityRaster = Con((VelRas>0) & (VelRas<0.1),(3*VelRas)+0.58,Con((VelRas>0.1) & (VelRas<0.5),(0.3*VelRas)+0.85,Con((VelRas>0.5) & (VelRas<1),(-0.16*VelRas)+1.08,Con((VelRas>1) & (VelRas<1.5),(-0.44*VelRas)+1.36,Con((VelRas>1.5) & (VelRas<2),(-0.88*VelRas)+2.02,Con((VelRas>2) & (VelRas<3.5),(-0.14*VelRas)+0.54,Con((VelRas>3.5) & (VelRas<4.3),(-0.0625*VelRas)+0.26875,Con(VelRas>4.3,0))))))))
                            SetProgressorLabel("Calculating final HSI raster for juvenile brown trout...")
                            FinalRaster = Con(DepthRaster < VelocityRaster, DepthRaster, VelocityRaster)
                            FinalRaster.save(OutputWorkspace + r"\BrownTroutJuvenile" + depRas[3:] + "Hsi")
                            Delete_management(DepthRaster)
                            Delete_management(VelocityRaster)
                        if (MountainWhitefishCondition):
                            SetProgressorLabel("Calculating depth HSI for juvenile mountain whitefish...")
                            DepthRaster = Con((DepRas>0) & (DepRas<0.45),0,Con((DepRas>0.45) & (DepRas<0.75),(0.7*DepRas)-0.315,Con((DepRas>0.75) & (DepRas<2.05),(0.45*DepRas)-0.130384615,Con((DepRas>2.05) & (DepRas<2.85),(0.25*DepRas)+0.2875,Con((DepRas>2.85) & (DepRas<2.95),1,Con((DepRas>2.95) & (DepRas<3.25),(-0.17*DepRas)+1.491666667,Con((DepRas>3.25) & (DepRas<3.95),(-0.61*DepRas)+2.946428571,Con((DepRas>3.95) & (DepRas<4.75),(-0.28*DepRas)+1.60625,Con(DepRas>4.75,0.3)))))))))
                            SetProgressorLabel("Calculating velocity HSI for juvenile mountain whitefish...")
                            VelocityRaster = Con((VelRas>0) & (VelRas<0.85),(0.647*VelRas)+0.25,Con((VelRas>0.85) & (VelRas<1.85),(0.2*VelRas)+0.63,Con((VelRas>1.85) & (VelRas<2.25),1,Con((VelRas>2.25) & (VelRas<3.45),(-0.125*VelRas)+1.28125,Con((VelRas>3.45) & (VelRas<5),(-0.548*VelRas)+2.741935484,Con(VelRas>5,0))))))
                            SetProgressorLabel("Calculating final HSI raster for juvenile mountain whitefish...")
                            FinalRaster = Con(DepthRaster < VelocityRaster, DepthRaster, VelocityRaster)
                            FinalRaster.save(OutputWorkspace + r"\MountainWhitefishJuvenile" + depRas[3:] + "Hsi")
                            Delete_management(DepthRaster)
                            Delete_management(VelocityRaster)
                        if (RainbowTroutCondition):
                            SetProgressorLabel("Calculating depth HSI for juvenile rainbow trout...")
                            DepthRaster = Con((DepRas>0) & (DepRas<0.15),0,Con((DepRas>0.15) & (DepRas<0.65),(0.2*DepRas)-0.03,Con((DepRas>0.65) & (DepRas<1.35),(0.757142857*DepRas)-0.392142857,Con((DepRas>1.35) & (DepRas<2.65),(0.284615385*DepRas)+0.245769231,Con(DepRas>2.65,1)))))
                            SetProgressorLabel("Calculating velocity HSI for juvenile rainbow trout...")
                            VelocityRaster = Con((VelRas>0) & (VelRas<0.75),(0.6*VelRas)+0.55,Con((VelRas>0.75) & (VelRas<0.95),1,Con((VelRas>0.95) & (VelRas<1.15),(-0.65*VelRas)+1.6175,Con((VelRas>1.15) & (VelRas<1.55),(-0.225*VelRas)+1.12875,Con((VelRas>1.55) & (VelRas<1.85),(-0.8*VelRas)+2.02,Con((VelRas>1.85) & (VelRas<3.15),(-0.184615385*VelRas)+0.881538462,Con((VelRas>3.15) & (VelRas<3.85),(-0.328571429*VelRas)+1.335,Con((VelRas>3.85) & (VelRas<5),(-0.060869565*VelRas)+0.304347826,Con(VelRas>5,0)))))))))
                            SetProgressorLabel("Calculating final HSI raster for juvenile rainbow trout...")
                            FinalRaster = Con(DepthRaster < VelocityRaster, DepthRaster, VelocityRaster)
                            FinalRaster.save(OutputWorkspace + r"\RainbowTroutJuvenile" + depRas[3:] + "Hsi")
                            Delete_management(DepthRaster)
                            Delete_management(VelocityRaster)
                        if (SculpinCondition):
                            SetProgressorLabel("Calculating depth HSI for juvenile sculpin...")
                            DepthRaster = Con((DepRas>0) & (DepRas<0.3281),(0.4572*DepRas)+0.85,Con((DepRas>0.3281) & (DepRas<1.6404),(-0.4953*DepRas)+1.1625,Con((DepRas>1.6404) & (DepRas<3.2808),(-0.1524*DepRas)+0.6,Con((DepRas>3.2808) & (DepRas<4.9213),(-0.03048*DepRas)+0.2,Con((DepRas>4.9213) & (DepRas<6.5617),(-0.03048*DepRas)+0.2,Con(DepRas>6.5617,0))))))
                            SetProgressorLabel("Calculating velocity HSI for juvenile sculpin ")
                            VelocityRaster = Con((VelRas>0) & (VelRas<0.2),(1.2192*VelRas)+0.8,Con((VelRas>0.2) & (VelRas<1.6),(-0.41995*VelRas)+1.068889,Con((VelRas>1.6) & (VelRas<3.3),(-0.1585*VelRas)+0.64,Con((VelRas>3.3) & (VelRas<4.9),(-0.04267*VelRas)+0.26,Con((VelRas>4.9) & (VelRas<6.6),(-0.03048*VelRas)+0.2,Con(VelRas>6.6,0))))))
                            SetProgressorLabel("Calculating final HSI raster for juvenile sculpin...")
                            FinalRaster = Con(DepthRaster < VelocityRaster, DepthRaster, VelocityRaster)
                            FinalRaster.save(OutputWorkspace + r"\SculpinJuvenile" + depRas[3:] + "Hsi")
                            Delete_management(DepthRaster)
                            Delete_management(VelocityRaster)
                    
                    if (AdultCondition):
                        if (BrownTroutCondition):
                            SetProgressorLabel("Calculating depth HSI for adult brown trout...")
                            DepthRaster = Con((DepRas>0) & (DepRas<1.6),(0.54375*DepRas),Con((DepRas>1.6) & (DepRas<2),(0.2*DepRas)+0.55,Con((DepRas>2) & (DepRas<2.6),(0.083333*DepRas)+0.783333,Con((DepRas>2.6) & (DepRas<3.6),(-0.16*DepRas)+1.416,Con((DepRas>3.6) & (DepRas<4),(-0.975*DepRas)+4.35,Con((DepRas>4) & (DepRas<5),(-0.15*DepRas)+1.05,Con((DepRas>5) & (DepRas<7),(-0.045*DepRas)+0.525,Con(DepRas>7,0.21))))))))
                            SetProgressorLabel("Calculating velocity HSI for adult brown trout... ")
                            VelocityRaster = Con((VelRas>0) & (VelRas<0.1),(4.9*VelRas)+0.21,Con((VelRas>0.1) & (VelRas<0.5),(0.75*VelRas)+0.625,Con((VelRas>0.5) & (VelRas<1),(-0.62*VelRas)+1.31,Con((VelRas>1) & (VelRas<1.5),(-0.38*VelRas)+1.07,Con((VelRas>1.5) & (VelRas<2.4),(-0.33333*VelRas)+1,Con((VelRas>2.4) & (VelRas<3.1),(-0.24286*VelRas)+0.782857,Con((VelRas>3.1) & (VelRas<5),0.03,Con((VelRas>5) & (VelRas<6),(-0.03*VelRas)+0.18,Con(VelRas>6,0)))))))))
                            SetProgressorLabel("Calculating final HSI raster for adult brown trout...")
                            FinalRaster = Con(DepthRaster < VelocityRaster, DepthRaster, VelocityRaster)
                            FinalRaster.save(OutputWorkspace + r"\BrownTroutAdult" + depRas[3:] + "Hsi")
                            Delete_management(DepthRaster)
                            Delete_management(VelocityRaster)
                        if (MountainWhitefishCondition):
                            SetProgressorLabel("Calculating depth HSI for adult mountain whitefish...")
                            DepthRaster = Con((DepRas>0) & (DepRas<0.55),0,Con((DepRas>0.55) & (DepRas<1.55),(0.3*DepRas)-0.165,Con((DepRas>1.55) & (DepRas<2.25),(0.143*DepRas)+0.0785714,Con((DepRas>2.25) & (DepRas<3.25),(0.6*DepRas)-0.95,Con((DepRas>3.25) & (DepRas<3.45),(-0.95*DepRas)+4.0875,Con((DepRas>3.45) & (DepRas<3.95),0.81,Con((DepRas>3.95) & (DepRas<4.75),(-0.175*DepRas)+1.50125,Con((DepRas>4.75) & (DepRas<5),(-0.680*DepRas)+3.9,Con(DepRas>5,0.5)))))))))
                            SetProgressorLabel("Calculating velocity HSI for adult mountain whitefish...")
                            VelocityRaster = Con((VelRas>0) & (VelRas<1.45),(0.345*VelRas)+0.2,Con((VelRas>1.45) & (VelRas<1.75),(0.667*VelRas)-0.266667,Con((VelRas>1.75) & (VelRas<2.05),(0.333*VelRas)+0.3166667,Con((VelRas>2.05) & (VelRas<2.35),1,Con((VelRas>2.35) & (VelRas<3.05),(-0.229*VelRas)+1.5371429,Con((VelRas>3.05) & (VelRas<3.35),(-0.867*VelRas)+3.4833333,Con((VelRas>3.35) & (VelRas<5.5),(-0.27*VelRas)+1.4837209,Con(VelRas>5.5,0))))))))
                            SetProgressorLabel("Calculating final HSI raster for adult mountain whitefish...")
                            FinalRaster = Con(DepthRaster < VelocityRaster, DepthRaster, VelocityRaster)
                            FinalRaster.save(OutputWorkspace + r"\MountainWhitefishAdult" + depRas[3:] + "Hsi")
                            Delete_management(DepthRaster)
                            Delete_management(VelocityRaster)
                        if (RainbowTroutCondition):
                            SetProgressorLabel("Calculating depth HSI for adult rainbow trout...")
                            DepthRaster = Con((DepRas>0) & (DepRas<0.75),(0.04*DepRas),Con((DepRas>0.75) & (DepRas<3.25),(0.23*DepRas)-0.141,Con((DepRas>3.25) & (DepRas<3.45),(0.95*DepRas)-2.4875,Con((DepRas>3.45) & (DepRas<3.85),(0.525*DepRas)-1.02125,Con(DepRas>3.85,1)))))
                            SetProgressorLabel("Calculating velocity HSI for adult rainbow trout...")
                            VelocityRaster = Con((VelRas>0) & (VelRas<0.35),(1.03*VelRas)+0.3,Con((VelRas>0.35) & (VelRas<0.95),(0.57*VelRas)+0.461666667,Con((VelRas>0.95) & (VelRas<1.05),1,Con((VelRas>1.05) & (VelRas<1.15),(-0.4*VelRas)+1.42,Con((VelRas>1.15) & (VelRas<1.45),(-1.3*VelRas)+2.455,Con((VelRas>1.45) & (VelRas<1.55),(-0.5*VelRas)+1.295,Con((VelRas>1.55) & (VelRas<5),(-0.15*VelRas)+0.753623188,Con(VelRas>5,0))))))))
                            SetProgressorLabel("Calculating final HSI raster for adult rainbow trout...")
                            FinalRaster = Con(DepthRaster < VelocityRaster, DepthRaster, VelocityRaster)
                            FinalRaster.save(OutputWorkspace + r"\RainbowTroutJuvenile" + depRas[3:] + "Hsi")
                            Delete_management(DepthRaster)
                            Delete_management(VelocityRaster)
                        if (SculpinCondition):
                            SetProgressorLabel("Calculating depth HSI for adult sculpin ")
                            DepthRaster = Con((DepRas>0) & (DepRas<0.3281),(0.4572*DepRas)+0.85,Con((DepRas>0.3281) & (DepRas<1.6404),(-0.4953*DepRas)+1.1625,Con((DepRas>1.6404) & (DepRas<3.2808),(-0.1524*DepRas)+0.6,Con((DepRas>3.2808) & (DepRas<4.9213),(-0.03048*DepRas)+0.2,Con((DepRas>4.9213) & (DepRas<6.5617),(-0.03048*DepRas)+0.2,Con(DepRas>6.5617,0))))))
                            SetProgressorLabel("Calculating velocity HSI for adult sculpin ")
                            VelocityRaster = Con((VelRas>0) & (VelRas<0.2),(1.2192*VelRas)+0.8,Con((VelRas>0.2) & (VelRas<1.6),(-0.41995*VelRas)+1.068889,Con((VelRas>1.6) & (VelRas<3.3),(-0.1585*VelRas)+0.64,Con((VelRas>3.3) & (VelRas<4.9),(-0.04267*VelRas)+0.26,Con((VelRas>4.9) & (VelRas<6.6),(-0.03048*VelRas)+0.2,Con(VelRas>6.6,0))))))
                            SetProgressorLabel("Calculating final HSI raster for adult sculpin...")
                            FinalRaster = Con(DepthRaster < VelocityRaster, DepthRaster, VelocityRaster)
                            FinalRaster.save(OutputWorkspace + r"\SculpinAdult" + depRas[3:] + "Hsi")
                            Delete_management(DepthRaster)
                            Delete_management(VelocityRaster)
        return
