"""Simple test for the GeoParquet files"""

import json

import geopandas as gpd  # type: ignore[import-untyped]
import pyarrow.compute as pc  # type: ignore[import-untyped]
import pyarrow.parquet as pq  # type: ignore[import-untyped]
from geopandas import GeoDataFrame
from pyarrow import Table

import swemaps

# Map types along with expected shapes
MAP_TYPES = {
    "lan": {"shape": (21, 3)},
    "kommun": {"shape": (290, 3)},
    "fa": {"shape": (60, 6)},
}


def test_geopandas():
    """All of the map types should be able to load in GeoPandas"""
    for map_type in MAP_TYPES:
        shape = MAP_TYPES[map_type]["shape"]
        path = swemaps.get_path(map_type)
        gdf = gpd.read_parquet(path)
        assert isinstance(gdf, GeoDataFrame)
        assert gdf.shape == shape


def test_pyarrow():
    """All of the map types should be able to be loaded as PyArrow Tables and be converted to GeoJSON"""
    for map_type in MAP_TYPES:
        shape = MAP_TYPES[map_type]["shape"]
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


def test_geojson():
    """GeoJSON output should match expected"""
    tbl = pq.read_table(swemaps.get_path("lan")).filter(pc.field("lan_kod") == "01")

    geojson = swemaps.table_to_geojson(tbl)

    with open("tests/sthlm.geojson", mode="r", encoding="utf-8") as file:
        expected = json.load(file)

    assert geojson == expected
