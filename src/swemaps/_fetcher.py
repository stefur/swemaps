import pooch

from ._version import __version__

registry = {
    "valdistrikt_2022.parquet": "32a37e434b7ddc571f5722f16b8237d5420a32a7f97d59fbd77969489245e59b",
    "deso.parquet": "138fb4e4ad1fadcf7cf688b59c5e019b0e5b802cc40df3e78d4b1fedf29a831f",
    "regso.parquet": "43831fe65e73d1899603cdbef1d59f221661adf6b53ab17e1f92bbf0a287affd",
}

_map_fetcher = pooch.create(
    path=pooch.os_cache("swemaps-data"),
    version=__version__,
    version_dev="main",
    base_url="https://raw.githubusercontent.com/stefur/swemaps-data/main/files/",
    registry=registry,
)
