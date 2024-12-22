"""Simple test for the GeoParquet files"""

import geopandas as gpd
import pyarrow.parquet as pq
import pytest
from geopandas import GeoDataFrame
from pyarrow import Table

import swemaps

map_shapes = [("lan", (21, 3)), ("kommun", (290, 3)), ("fa", (60, 6))]


@pytest.mark.parametrize("map_type, shape", map_shapes)
def test_geopandas(map_type, shape):
    """All of the map types should be able to load in GeoPandas"""
    path = swemaps.get_path(map_type)
    gdf = gpd.read_parquet(path)
    assert isinstance(gdf, GeoDataFrame)
    assert gdf.shape == shape


@pytest.mark.parametrize("map_type, shape", map_shapes)
def test_pyarrow(map_type, shape):
    """All of the map types should be able to be loaded as PyArrow Tables and be converted to GeoJSON"""

    tbl = pq.read_table(swemaps.get_path(map_type))
    assert isinstance(tbl, Table)
    assert tbl.shape == shape
    geojson = swemaps.table_to_geojson(tbl)
    features_length = len(geojson["features"])
    unpacked_properties = [
        list(prop["properties"].keys()) for prop in geojson["features"]
    ]
    # Unpack inner lists and keep only distinct values
    properties_length = len(
        list(set(item for sublist in unpacked_properties for item in sublist))
    )

    # +1 for geometries
    assert (features_length, properties_length + 1) == shape


@pytest.mark.parametrize("map_type", ["lan", "kommun", "fa"])
def test_geojson(snapshot, map_type):
    """GeoJSON output should match expected"""
    tbl = pq.read_table(swemaps.get_path(map_type))

    geojson = swemaps.table_to_geojson(tbl)

    assert geojson == snapshot
