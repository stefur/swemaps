"""
Check some basics to ensure functionality.
"""

import pyarrow.parquet as pq

import swemaps

kommuner = pq.read_table(swemaps.get_path("kommun"))

geojson = swemaps.table_to_geojson(kommuner)

if not isinstance(geojson, dict) or not geojson:
    raise RuntimeError("Smoke test failed")
else:
    print("Smoke test passed")
