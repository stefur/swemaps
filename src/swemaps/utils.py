import json
from importlib import resources
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pyarrow  # type: ignore[import-untyped]


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
        geometry: binary
        -- schema metadata --
        geo: '{"version":"1.0.0","primary_column":"geometry","columns":{"geometry' + 1478

    You can filter the PyArrow table.

    >>> kommuner = kommuner.filter(pc.starts_with(pc.field("kommun_kod"), "20"))

    To use with Plotly the included helper function can convert the PyArrow to GeoJSON.

    >>> geojson = swemaps.pyarrow_to_geojson(kommuner)

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


def pyarrow_to_geojson(
    table: "pyarrow.Table", geometry_column: str | None = None
) -> dict:
    """
    Converts a PyArrow table loaded from a GeoParquet to a GeoJSON structure.
    This function will use the defined primary column or a specific geometry column.
    All other columns will be treated as a property.

    Parameters
    ----------
    table : Table
        A PyArrow table containing GeoParquet data.
    geometry_column : str | None, default None
        Name of a specific column containing geometry.
    """
    try:
        import pyarrow  # type: ignore[import-untyped]
        from geomet import wkb  # type: ignore[import-untyped]
    except ModuleNotFoundError as err:
        err.add_note("PyArrow and GeoMet are required to use this function.")
        raise

    if not isinstance(table, pyarrow.Table):
        raise TypeError("The table must be a PyArrow Table object.")

    try:
        table_metadata: dict = json.loads(table.schema.metadata[b"geo"].decode())
        version: str = table_metadata["version"]
        if version != "1.0.0":
            raise ValueError(
                f"Invalid version: {version}. The GeoParquet specification must be version 1.0.0."
            )

        primary_column: str = table_metadata["primary_column"]
        all_geometry_columns: list = list(table_metadata["columns"].keys())

    except (json.JSONDecodeError, KeyError) as err:
        err.add_note("Invalid metadata.")
        raise

    features = []

    geometry_column = geometry_column or primary_column

    for row in table.to_pylist():
        properties: dict = {
            k: v for k, v in row.items() if k not in all_geometry_columns
        }
        geometry: dict = wkb.loads(row.get(geometry_column, None))
        feature = {
            "type": "Feature",
            "properties": properties,
            "geometry": geometry,
        }
        features.append(feature)

    return {
        "type": "FeatureCollection",
        "features": features,
    }
