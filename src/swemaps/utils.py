from importlib import resources
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from arro3.core.types import ArrowStreamExportable


def get_path(map_type: str) -> Path:
    """
    Get the path for a specific map.

    Parameters
    ----------
    map_type : str
        A string defining which map type to get.
        Possible values are "kommun", "lan", "fa".

    Example
    --------
    Loading municipality map data from Dalarna county and plotting some random values with PyArrow:

    >>> import swemaps
    >>> import pyarrow.parquet as pq
    >>> import pyarrow.compute as pc

    >>> kommuner = pq.read_table(swemaps.get_path("kommun"))
    >>> kommuner.schema

        kommun_kod: string
        kommun: string
        geometry: extension<geoarrow.wkb<WkbType>>
        -- schema metadata --
        geo: '{"version":"1.1.0","primary_column":"geometry","columns":{"geometry' + 1631

    You can filter the PyArrow table.

    >>> kommuner = kommuner.filter(pc.starts_with(pc.field("kommun_kod"), "20"))

    To use with Plotly the included convenience function can help convert the PyArrow table to GeoJSON.

    >>> geojson = swemaps.table_to_geojson(kommuner)

    And with a dataset containing some values and municipalities (used as keys) we can get a nice map.

    >>> import plotly.express as px
    >>> fig = px.choropleth(
    df,
    geojson=geojson,
    color="Value",
    locations="Kommun",
    featureidkey="properties.kommun",
    projection="mercator",
    color_continuous_scale="Viridis",
    fitbounds="locations",
    basemap_visible=False,
    )
    """
    if map_type not in ("kommun", "lan", "fa"):
        raise ValueError(
            f"Invalid map type: {map_type}. Expected one of 'kommun', 'lan', 'fa'."
        )

    with resources.as_file(
        resources.files(__package__).joinpath(f"data/{map_type}.parquet")
    ) as path:
        return path


def table_to_geojson(table: "ArrowStreamExportable") -> dict:
    """
    Convert an Arrow tabular object to GeoJSON format using `geoarrow.rust.io`.

    This convenience function wraps `geoarrow.rust.io.write_geojson` to perform the conversion.
    For details on supported object types, see:
    https://geoarrow.org/geoarrow-rs/python/latest/api/io/functions/#geoarrow.rust.io.write_geojson

    Parameters
    ----------
    table : ArrowStreamExportable
        An Arrow tabular object containing geospatial data.
    """
    import io
    import json

    try:
        from geoarrow.rust.io import write_geojson

    except ModuleNotFoundError:
        raise ModuleNotFoundError(
            "geoarrow.rust.io is required to use this function."
        ) from None

    with io.BytesIO() as buffer:
        write_geojson(table, buffer)
        buffer.seek(0)
        geojson = buffer.read().decode("utf-8")

    return json.loads(geojson)
