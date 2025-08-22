# -*- coding: utf-8 -*-

import arcpy
from pathlib import Path
from arcpy.management import (CreateRelationshipClass,
                              AddFields,
                              CalculateFields,
                              XYTableToPoint,
                              )
from arcpy.conversion import (FeatureClassToGeodatabase,
                              )
from arcpy.da import (FeatureClassToNumPyArray)
from arcpy import (
    Parameter,
    AddMessage,
    env,
    ListFeatureClasses,
)
import pandas as pd
from datetime import datetime, timezone


class Toolbox:
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Marketing Tools"
        self.alias = "marketing_tools"

        # List of tool classes associated with this toolbox
        self.tools = [Tool]


class Tool:
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Tool"
        self.description = ""
        self.state_fip = {
            "Alabama":"01",
            "Alaska":"02",
            "Arizona":"04",
            "Arkansas":"05",
            "California":"06",
            "Colorado":"08",
            "Connecticut":"09",
            "Delaware":"10",
            "District of Columbia":"11",
            "Florida":"12",
            "Georgia":"13",
            "Hawaii":"15",
            "Idaho":"16",
            "Illinois":"17",
            "Indiana":"18",
            "Iowa":"19",
            "Kansas":"20",
            "Kentucky":"21",
            "Louisiana":"22",
            "Maine":"23",
            "Maryland":"24",
            "Massachusetts":"25",
            "Michigan":"26",
            "Minnesota":"27",
            "Mississippi":"28",
            "Missouri":"29",
            "Montana":"30",
            "Nebraska":"31",
            "Nevada":"32",
            "New Hampshire":"33",
            "New Jersey":"34",
            "New Mexico":"35",
            "New York":"36",
            "North Carolina":"37",
            "North Dakota":"38",
            "Ohio":"39",
            "Oklahoma":"40",
            "Oregon":"41",
            "Pennsylvania":"42",
            "Rhode Island":"44",
            "South Carolina":"45",
            "South Dakota":"46",
            "Tennessee":"47",
            "Texas":"48",
            "Utah":"49",
            "Vermont":"50",
            "Virginia":"51",
            "Washington":"53",
            "West Virginia":"54",
            "Wisconsin":"55",
            "Wyoming":"56"
        }

    def getParameterInfo(self):
        """Define the tool parameters."""
        populations_csv = Parameter(
            displayName="Input population .csv downloaded from census website",
            name="population_csv",
            datatype="DEFile",
            parameterType="Required",
            direction="Input"
        )

        cities_shp = Parameter(
            displayName="Cities shapefile downloaded from TIGER/CENSUS site",
            name="cities_shp",
            datatype="DEShapeFile",
            parameterType="Required",
            direction="Input"
        )

        projects_csv = Parameter(
            displayName="CSV file containing project information",
            name="projects_csv",
            datatype="DEFile",
            parameterType="Required",
            direction="Input"
        )

        state_dropdown = Parameter(
            displayName="Select state",
            name="state_dropdown",
            datatype="String",
            parameterType="Required",
            direction="Input"
        )
        state_dropdown.filter.type = "ValueList"
        state_dropdown.filter.list = list(self.state_fip.keys())

        csv_save_location = Parameter(
            displayName="Save location for output .csv",
            name="csv_save_location",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input"
        )

        gdb_location = Parameter(
            displayName="GDB to save table",
            name="gdb_location",
            datatype="DEWorkspace",
            parameterType="Required",
            direction="Input"
        )

        relate_name = Parameter(
            displayName="Set name for relationship class",
            name="relate_name",
            datatype="GPString",
            parameterType="Required",
            direction="Input"
        )

        aprx_param = Parameter(
            displayName="Select ArcGIS Pro Project (.aprx)",
            name="aprx_path",
            datatype="DEFile",
            parameterType="Required",
            direction="Input"
        )
        aprx_param.filter.list = ["aprx"]

        map_param = Parameter(
            displayName="Select map",
            name="selected_map",
            datatype="String",
            parameterType="Required",
            direction="Input"
        )
        map_param.filter.type = "ValueList"

        sd_draft_param = Parameter(
            displayName="Specify save location and name for service definition draft",
            name="sd_draft_file",
            datatype="DEFile",
            parameterType="Required",
            direction="Output"
        )
        sd_draft_param.filter.list = ["sddraft"]

        sd_file_param = Parameter(
            displayName="Specify save location and name for service definition",
            name="sd_file",
            datatype="DEFile",
            parameterType="Required",
            direction="Output"
        )
        sd_file_param.filter.list = ["sd"]
        params = [
            populations_csv,
            cities_shp,
            projects_csv,
            state_dropdown,
            csv_save_location,
            gdb_location,
            relate_name,
            aprx_param,
            map_param,
            sd_draft_param,
            sd_file_param
        ]
        return params

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        if parameters[7].value:
            aprx_path = parameters[7].valueAsText
            try:
                aprx = arcpy.mp.ArcGISProject(aprx_path)
                map_names = [map.name for map in aprx.listMaps()]
                parameters[8].filter.list = map_names
            except Exception as e:
                parameters[8].filter.list = []
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        populations_csv = parameters[0].valueAsText
        cities_shp = parameters[1].valueAsText
        projects_csv = parameters[2].valueAsText
        state_dropdown = parameters[3].valueAsText
        csv_save_location = parameters[4].valueAsText
        gdb_location = parameters[5].valueAsText
        relate_name = parameters[6].valueAsText
        # aprx_path = parameters[7].valueAsText
        selected_map = parameters[8].valueAsText
        sd_draft_file = parameters[9].valueAsText
        sd_file = parameters[10].valueAsText
        env.workspace = gdb_location

        #* Export census places shapefile to geodatabase
        AddMessage(f"Converting shapefile to feature class")
        FeatureClassToGeodatabase(Input_Features=cities_shp, Output_Geodatabase=gdb_location)

        #* Add new latitude and longitude fields to feature class
        AddMessage(f"Converting latitude and longitude")
        cities_shp_file_path = Path(f"{cities_shp}")
        cities_shp_file_name = cities_shp_file_path.stem
        cities_fc = ListFeatureClasses(f"{cities_shp_file_name}")[0]
        AddFields(
            in_table=f"{cities_fc}",
            field_description="LAT_EDIT FLOAT Latitude # # #;LON_EDIT FLOAT Longitude # # #",
            template=None
        )

        #* Calculate latitude and longitude based on old lat/lon fields
        CalculateFields(
            in_table=f"{cities_fc}",
            expression_type="PYTHON3",
            fields="LAT_EDIT float(!INTPTLAT![1:]) #;LON_EDIT float(!INTPTLON!) #",
            code_block="",
            enforce_domains="NO_ENFORCE_DOMAINS"
        )

        #* Create point feature class using lat/lon in existing feature class
        AddMessage(f"Creating point feature class")
        spatial_ref = arcpy.Describe(cities_fc).spatialReference
        XYTableToPoint(
            in_table=f"{cities_fc}",
            out_feature_class=f"{gdb_location}\\{cities_fc}_point",
            x_field="LON_EDIT",
            y_field="LAT_EDIT",
            z_field=None,
            coordinate_system=spatial_ref
        )

        #* Get cities dataframe
        AddMessage(f"Modifying project data")
        point_fc = ListFeatureClasses("*_point")[0]
        point_fc_fields = [field.name for field in arcpy.ListFields(point_fc) if field.type not in ("Geometry", "OID")]
        point_fc_array = FeatureClassToNumPyArray(point_fc,point_fc_fields)
        cities_df = pd.DataFrame(point_fc_array)
        #* Get list of cities
        city_names_list = cities_df["NAME"].tolist()

        #* Clean up populations .csv
        populations_df = pd.read_csv(f"{populations_csv}")
        populations_df = populations_df.loc[~populations_df["City"].str.contains("Estimate") & ~populations_df["City"].str.contains("Margin of Error")]
        populations_df["City"] = populations_df["City"].str.replace(f" city, {state_dropdown}","",regex=False)
        populations_df["City"] = populations_df["City"].str.replace(f", {state_dropdown}","",regex=False)
        populations_df["City"] = populations_df["City"].str.replace(f" CDP","",regex=False)

        #* Include populations in point city feature class
        population_field = "Population"
        populations_dict = populations_df.set_index("City")["Total"].to_dict()
        if population_field not in point_fc_fields:
            arcpy.management.AddField(point_fc, population_field, "LONG")        
        with arcpy.da.UpdateCursor(point_fc, ["NAME", "Population"]) as cursor:
            for row in cursor:
                city_name = row[0]
                if city_name in populations_dict:
                    row[1] = populations_dict[city_name]
                    cursor.updateRow(row)

        #* Get dataframe from projects CSV and split locations into multiple columns 
        projects_df = pd.read_csv(f"{projects_csv}")
        projects_df["Location"] = projects_df["Location"].fillna("No location")
        locations_split_df = projects_df["Location"].str.split(",", expand=True)
        locations_split_df = locations_split_df.rename(columns={
            0:"Country",
            1:"State",
            2:"County",
            3:"City"
        })
        cols_to_drop = locations_split_df.columns[3+1:]
        locations_split_df = locations_split_df.drop(columns=cols_to_drop)
        projects_df = pd.concat([projects_df, locations_split_df], axis=1)

        #* Strip whitespace remaining after "split"
        projects_df["Country"] = projects_df["Country"].str.strip()
        projects_df["State"] = projects_df["State"].str.strip()
        projects_df["County"] = projects_df["County"].str.strip()
        projects_df["City"] = projects_df["City"].str.strip()
        projects_df["City"] = projects_df["City"].fillna("No city info provided")
        projects_df["Script edited"] = None

        #* Find projects that have "City of *city name*" in "Primary Account Name" column, populate location columns appropriately
        for city in city_names_list:
            projects_df.loc[(projects_df["Primary Account Name"].str.contains(f"City of {city}", case=False, na=False)), ["Country","State","City","Script edited"]] = ["United States","Idaho",f"{city}","Yes"]
        def replace_if_substring(val, full_list):
            for full_city in full_list:
                if val in full_city and val != full_city:
                    return full_city
            return val
        projects_df["City"] = projects_df["City"].apply(lambda x: replace_if_substring(x, city_names_list))
        
        #* Filter original dataframe by cities that are only in selected state
        projects_df = projects_df[(projects_df["State"] == f"{state_dropdown}") & (projects_df["City"].isin(city_names_list))]
        
        #* Save formatted .csv file
        projects_df.to_csv(f"{csv_save_location}\\{state_dropdown}ProjectsCitiesData.csv")

        #* Use table to geodatabase tool to save csv into geodatabase
        arcpy.conversion.TableToGeodatabase(
            Input_Table=f"{csv_save_location}\\{state_dropdown}ProjectsCitiesData.csv",
            Output_Geodatabase=gdb_location
        )

        # #* Get projects fees grouped by city and year
        # projects_df["Start Date"] = pd.to_datetime(projects_df["Start Date"])
        # projects_df["Year"] = projects_df["Start Date"].dt.year
        # city_fees_per_year = projects_df.groupby(["City", "Year"])["Net Fee"].sum().reset_index()
        # city_fees_per_year_dict = city_fees_per_year.set_index(["City", "Year"])["Net Fee"].to_dict()

        # #* Include project fees earned in the last 5 years by city to point feature class
        # current_year = datetime.now(timezone.utc).year
        # year_range_list = list(range(current_year - 5, current_year+1))
        # for list_item in year_range_list:
        #     arcpy.management.AddField(
        #         in_table=point_fc,
        #         field_name=f"Fees_{list_item}",
        #         field_type="FLOAT",
        #         field_alias=f"Fees_{list_item}"
        #     )
        # point_fc_fee_fields = [field.name for field in arcpy.ListFields(point_fc) if "Fees_" in field.name]
        # for year in point_fc_fee_fields:
        #     with arcpy.da.UpdateCursor(point_fc, ["NAME", year]) as cursor:
        #         for row in cursor:
        #             key = (row[0], float(year[5:]))
        #             if key in city_fees_per_year_dict:
        #                 row[1] = city_fees_per_year_dict[key]
        #                 cursor.updateRow(row)

        #* Add point feature class and project data table to map
        AddMessage(f"Adding needed layers to map")
        aprx = arcpy.mp.ArcGISProject("CURRENT")
        map_obj = aprx.listMaps(f"{selected_map}")[0]
        point_fc_path = f"{gdb_location}\\{point_fc}"
        project_data_table_path = f"{gdb_location}\\{state_dropdown}ProjectsCitiesData"
        map_obj.addDataFromPath(f"{point_fc_path}")
        map_obj.addDataFromPath(f"{project_data_table_path}")
        map_obj = aprx.listMaps(f"{selected_map}")[0]

        #* Create relationship class using point feature class and geodatabase table
        AddMessage(f"Creating relationship class")
        CreateRelationshipClass(
            origin_table=point_fc,
            destination_table=f"{state_dropdown}ProjectsCitiesData",
            out_relationship_class=f"{gdb_location}\\{relate_name}",
            relationship_type="SIMPLE",
            forward_label="IdahoProjectsCitiesData",
            backward_label="Idaho_Cities",
            message_direction="NONE",
            cardinality="ONE_TO_MANY",
            attributed="NONE",
            origin_primary_key="NAME",
            origin_foreign_key="City",
            destination_primary_key="",
            destination_foreign_key=""
        )
        #* Share feature layer with relationship to AGOL
        AddMessage(f"Starting upload to AGOL...")
        sharing_draft = map_obj.getWebLayerSharingDraft(
            server_type="HOSTING_SERVER",
            service_type="FEATURE",
            service_name="city_project_data_08052025",
            )
        sharing_draft.summary = "New feature layer"
        sharing_draft.tags = "relationship, arcpy, feature class"
        sharing_draft.description = "Uploaded via arcpy with relationship class"
        sharing_draft.exportToSDDraft(sd_draft_file)
        arcpy.StageService_server(sd_draft_file, sd_file)
        arcpy.UploadServiceDefinition_server(sd_file, "My Hosted Services")
        AddMessage(f"Finished upload")
        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return
