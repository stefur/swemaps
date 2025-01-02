"""Simple test for the GeoParquet files"""

from pathlib import Path
from unittest.mock import patch

import geopandas as gpd
import pyarrow.parquet as pq
import pytest
from geopandas import GeoDataFrame
from pyarrow import Table

from swemaps.utils import MapNotFound, fetch_map, get_path, table_to_geojson

map_shapes = [("lan", (21, 3)), ("kommun", (290, 3)), ("fa", (60, 6))]


@pytest.mark.parametrize("map_type, shape", map_shapes)
def test_geopandas(map_type, shape):
    """All of the map types should be able to load in GeoPandas"""
    gdf = gpd.read_parquet(get_path(map_type))
    assert isinstance(gdf, GeoDataFrame)
    assert gdf.shape == shape


@pytest.mark.parametrize("map_type, shape", map_shapes)
def test_pyarrow(map_type, shape):
    """All of the map types should be able to be loaded as PyArrow Tables"""
    tbl = pq.read_table(get_path(map_type))
    assert isinstance(tbl, Table)
    assert tbl.shape == shape


@pytest.mark.parametrize("map_type", [item[0] for item in map_shapes])
def test_geojson(snapshot, map_type):
    """GeoJSON output should match expected"""
    tbl = pq.read_table(get_path(map_type))

    geojson = table_to_geojson(tbl)

    assert geojson == snapshot


@pytest.mark.parametrize("invalid_map_type", [None, True, "", 3.14, (1, 2, 3)])
def test_inputs(invalid_map_type):
    """Invalid map types should raise MapNotFound"""
    with pytest.raises(MapNotFound):
        _ = get_path(invalid_map_type)

    with pytest.raises(MapNotFound):
        _ = fetch_map(invalid_map_type)


@patch("pooch.Pooch.fetch")
def test_valid_fetch(mock_fetch, tmp_path):
    """A succesful fetch of a valid extra map type should return a Path"""
    mock_fetch.return_value = tmp_path / "valdistrikt_2022.parquet"

    result = fetch_map("valdistrikt_2022")

    assert isinstance(result, Path)
    assert result == tmp_path / "valdistrikt_2022.parquet"
