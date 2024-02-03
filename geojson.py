import os
import re

import geopandas as gpd

shape_files = [
    f for f in os.listdir("./scb-files") if re.search(f"""{re.escape(".shp")}$""", f)
]

for shp in shape_files:
    gdf = gpd.read_file("./scb-files/" + shp)

    # Set the original CRS (UTM zone 33N)
    gdf.crs = "EPSG:32633"

    # Reproject the geometry to WGS 84 (latitude and longitude)
    gdf = gdf.to_crs("EPSG:4326")

    output_name = shp.split("_", 1)[0].lower()

    gdf.to_file(f"swe-maps-{output_name}.geojson", driver="GeoJSON")
