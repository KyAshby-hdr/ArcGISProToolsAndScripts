# -*- coding: utf-8 -*-

# import arcpy
from arcpy import (Parameter,
                   env,
                   ListRasters,
                   AddMessage,
                   SetProgressorLabel)

from arcpy.sa import Raster, Con, RasterCalculator


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Toolbox"
        self.alias = "toolbox"
        
        # List of tool classes associated with this toolbox
        self.tools = [CalculatePeriphyton]


class CalculatePeriphyton(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Calculate Periphyton"
        self.description = "Use depth and velocity rasters, along with user defined variables, to calculate rasters showing optimal and non-optimal areas for periphyton growth"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        InputGdb = Parameter(
            displayName="Input velocity and depth rasters gdb",
            name="InputGdb",
            datatype="Workspace",
            parameterType="Required",
            direction="Input"
        )
        InputGdb.filter.list = ["Local Database"]
        InMetersBoolean = Parameter(
            displayName="Check if input rasters are in units of meters",
            name="InMetersBoolean",
            datatype="Boolean",
            parameterType="Required",
            direction="Input"
        )
        BiomassValue = Parameter(
            displayName="Biomass value (g/m^2)",
            name="BiomassValue",
            datatype="Double",
            parameterType="Required",
            direction="Input"
        )
        RhoValue = Parameter(
            displayName="Rho (kg/m^3)",
            name="Rho",
            datatype="Double",
            parameterType="Required",
            direction="Input"
        )
        RhoValue.value = "1000"
        DragCoeffValue = Parameter(
            displayName="Drag coefficient",
            name="DragCoeff",
            datatype="Double",
            parameterType="Required",
            direction="Input"
        )
        DragCoeffValue.value = "0.000253"
        UnitAreaValue = Parameter(
            displayName="Unit area",
            name="UnitArea",
            datatype="Double",
            parameterType="Required",
            direction="Input"
        )
        UnitAreaValue.value = "1"
        FCritValue = Parameter(
            displayName="Critical force (FCrit)",
            name="FCrit",
            datatype="Double",
            parameterType="Required",
            direction="Input"
        )
        OutputGdb = Parameter(
            displayName="Output raster location",
            name="OutputGdb",
            datatype="Workspace",
            parameterType="Required",
            direction="Input"
        )
        params = [InputGdb,
                  InMetersBoolean,
                  BiomassValue,
                  RhoValue,
                  DragCoeffValue,
                  UnitAreaValue,
                  FCritValue,
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

        # The parameters here are defined by the user.
        InputGdb = parameters[0].valueAsText
        InMetersBoolean = parameters[1].valueAsText
        BiomassValue = parameters[2].valueAsText
        RhoValue = parameters[3].valueAsText
        DragCoeffValue = parameters[4].valueAsText
        UnitAreaValue = parameters[5].valueAsText
        FCritValue = parameters[6].valueAsText
        OutputGdb = parameters[7].valueAsText

        env.workspace = OutputGdb
        MeterRasterList = ListRasters("Meter*")
        env.workspace = InputGdb
        InputRasterList = ListRasters("*")

        
        # This part of the code determines if the input rasters are in units of meters.
        # It does so by checking if there is a "Meters" suffix.
        # If there isn't a "Meters" suffix, it assumes that the rasters are in units of feet.
        # The code then converts the rasters from feet to meters and saves the meter rasters in the specified output geodatabase.
        # This calculation only needs to be done once, unless the created "Meters" rasters are removed or the suffix removed.
        if InMetersBoolean == "false":
            for ras in InputRasterList:
                if f"Meter{ras}" in MeterRasterList:
                    AddMessage(f"{ras}Meter already exists in output geodatabase")
                else:
                    SetProgressorLabel(f"Converting {ras} units from feet to meters...")
                    Ras = Raster(ras)
                    ConvertMeterRas = RasterCalculator([Ras], ["Ras"], 'Ras * 0.3048')
                    ConvertMeterRas.save(f"{OutputGdb}\\Meter{ras}")
        elif InMetersBoolean == "true":
            for ras in InputRasterList:
                if f"Meter{ras}" in MeterRasterList:
                    AddMessage(f"{ras}Meter already exists in output geodatabase")
                else:
                    SetProgressorLabel(f"Renaming {ras} to include meters...")
                    Ras = Raster(ras)
                    Ras.save(f"{OutputGdb}\\Meter{ras}")

        # The code here sorts the depth and velocity rasters
        # It also displays a message in the popup dialog box in ArcGIS Pro, showing a list of the depth and velocity rasters.
        env.workspace = OutputGdb
        rasterList = ListRasters("*")
        DepthRasters = []
        VelocityRasters = []
        for raster in rasterList:
            if "Dep" in raster:
                DepthRasters.append(raster)
            elif "Vel" in raster:
                VelocityRasters.append(raster)
        AddMessage(f"Depth rasters: {DepthRasters}")
        AddMessage(f"Velocity rasters: {VelocityRasters}")

        # Here the Biovolume is calculated using the equation found in the AQUATOX documentation.
        # The variables needed to calculate the Biovolume is depth, from the depth raster, and biomass, which is defined by the user.
        BioVolRasterList = ListRasters("*Biovol")
        for depRas in DepthRasters:
            if f"{depRas[8:]}Biovol" in BioVolRasterList:
                AddMessage(f"{depRas[8:]}Biovol already exists in output geodatabase")
            else:
                SetProgressorLabel(f"Calculating {depRas[8:]}Biovol raster...")
                DepRas = Raster(depRas)
                Biomass = BiomassValue
                BiovolRas = RasterCalculator([DepRas],["DepRas"],f"({Biomass}/0.00000000857) * DepRas")
                BiovolRas.save(f"{OutputGdb}\\{depRas[8:]}Biovol")
        
        # Here the adaptation factor is calculated.
        # To calculate the adaptation factor, a velocity value is needed, which is provided by the velocity rasters.
        AdaptFactorRasterList = ListRasters("*Adapt")
        for velRas in VelocityRasters:
            if f"{velRas[8:]}Adapt" in AdaptFactorRasterList:
                AddMessage(f"{velRas[8:]}Adapt already exists in output geodatabase")
            else:
                SetProgressorLabel(f"Calculating {velRas[8:]}Adapt factor raster...")
                VelRas = Raster(velRas)
                AdaptRas = RasterCalculator([VelRas], ["VelRas"], "(VelRas**2) / 0.006634")
                AdaptRas.save(f"{OutputGdb}\\{velRas[8:]}Adapt")
        
        # After calculating the biovolume and adaptation factor, the drag force is calculated.
        # The drag force is calculated using the velocity raster, the biovolume raster calculated previously, and other values that are specified by the user
        # These user specified values include a drag coeff, rho value, and unit area
        BioVolRasterList = ListRasters("*Biovol")
        for bioRas in BioVolRasterList:
            for velRas in VelocityRasters:
                if bioRas[:-6] == velRas[8:]:
                    SetProgressorLabel(f"Calculating {velRas[8:]}DragForce raster...")
                    VelRas = Raster(velRas)
                    BioRas = Raster(bioRas)
                    DragForceRas = RasterCalculator([VelRas,BioRas],["VelRas","BioRas"],f"{RhoValue}*{DragCoeffValue}*(VelRas**2)*((BioRas*{UnitAreaValue})**(2/3))*0.000001")
                    DragForceRas.save(f"{OutputGdb}\\{velRas[8:]}DragForce")
        
        # The code here calculates the optimal area for periphyton by multiplying the specified FCritValue by the Adaptation factor raster.
        # See equation 75 in the following PDF for a bit more context: https://www.epa.gov/sites/default/files/2014-03/documents/technical-documentation-3-1.pdf
        AdaptFactorRasterList = ListRasters("*Adapt")
        for adaptRas in AdaptFactorRasterList:
            SetProgressorLabel(f"Calculating {adaptRas[:-5]}OptimalArea raster...")
            AdaptRas = Raster(adaptRas)
            OptimalAreaRas = RasterCalculator([AdaptRas], ["AdaptRas"], f"{FCritValue} * AdaptRas")
            OptimalAreaRas.save(f"{OutputGdb}\\{adaptRas[:-5]}OptimalArea")
        
        # Initially, the results given specified areas as either optimal or not optimal.
        # This binary method of distinguishing periphyton growth areas was not useful, so a new method was devised.
        # This involved taking the drag force raster and dividing it by the optimal area raster calculated previously.
        # This results in a raster that shows a relative scale for how optimal an area is for periphyton growth.
        OptimalAreaRasterList = ListRasters("*OptimalArea")
        DragForceRasterList = ListRasters("*DragForce")
        for dragRas in DragForceRasterList:
            for optRas in OptimalAreaRasterList:
                SetProgressorLabel(f"Calculating {dragRas[:-9]}Comparison raster...")
                if dragRas[:-9] == optRas[:-11]:
                    OptRas = Raster(optRas)
                    DragRas = Raster(dragRas)
                    DragForceOptimalRelativeRaster = RasterCalculator([OptRas,DragRas],["OptRas","DragRas"],f"DragRas/OptRas")
                    DragForceOptimalRelativeRaster.save(f"{OutputGdb}\\{dragRas[:-9]}Relative") 
        return