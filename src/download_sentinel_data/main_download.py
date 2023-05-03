# built-in
import logging
import time
from distutils.util import strtobool
from pathlib import Path
from typing import Union

# local-modules
import constants as c

# third-party
import geopandas as gpd
from API_call_handler import download_sentinel2_data
from geopandas import GeoDataFrame
from sentinel_api import connect_to_sentinel_api
from sentinelsat import SentinelAPI
from sentinelsat.exceptions import ServerError, UnauthorizedError

"""
ToDo: Add faster way to check if tile is already downloaded
ToDo: Needs better documentation
ToDo: handle memory consumption (but not so important)
"""

logging.basicConfig(
    filename="app.log",
    filemode="w",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


def load_tiles_germany(path: Path) -> GeoDataFrame:
    """
    Load a GeoDataFrame from a GeoJSON file.

    Parameters
    ----------
    path : Path
        The path to the GeoJSON file.

    Returns
    -------
    tiles_germany : GeoDataFrame
        The GeoDataFrame loaded from the GeoJSON file.

    Raises
    ------
    SystemExit
        If the GeoDataFrame loaded from the GeoJSON file is empty.

    """

    tiles_germany = gpd.read_file(path)

    if len(tiles_germany) == 0:
        logging.error("Could not read tiles_germany.geojson")
        print("Could not read tiles_germany.geojson")
        exit()

    return tiles_germany


def create_download_path(path: Path) -> bool:
    """
    Creates download path if it does not exist
    Args:
        path (pathlib.Path): path to download data to

    Returns:
        bool: True if path was created, False if not
    """
    if not Path(path).exists():
        print(
            f"The download path: {path} does not exist. \n"
            f" Do you want to create it? [Y/n] (no will exiting program)"
        )
        user_input = input()

        try:
            user_input_bool = bool(strtobool(user_input))
        except ValueError:
            print("Invalid input. Please use Y/n")
            return False

        if user_input_bool:
            path.mkdir(parents=True, exist_ok=False)
            print("path created")
            return True
        else:
            print("path not created, exiting program")
            exit()

    else:
        return True


def wait_for_api_connection() -> Union[bool, SentinelAPI]:
    api = connect_to_sentinel_api()

    if isinstance(api, ServerError):
        # ToDo: send mail to admin once a day
        # ToDo: check if this works
        logging.warning(
            """Could not connect to Sentinel API. \n
                Probably ongoing maintenance. \n
                Retrying in 5 minutes."""
        )
        time.sleep(300)  # retry after 5 minutes
        return False

    elif isinstance(api, UnauthorizedError):
        # ToDo: send mail to admin once
        logging.error("Wrong credentials for Sentinel API. Please check .env file")
        exit()

    elif isinstance(api, Exception):
        # ToDo: send mail to admin every time
        logging.error(f"Unknown error occurred: {api}")
        exit()
    else:
        return api


if __name__ == "__main__":
    logging.info("Program started")
    print("Program started")

    tiles_germany = load_tiles_germany(path=c.PATH_TO_TILES)

    while True:
        if create_download_path(path=c.DOWNLOAD_PATH):
            break

    while True:
        try:
            api = wait_for_api_connection()
            break
        except Exception as e:
            logging.error(f"Error connecting to API: {e}")
            exit()


for season_counter, (season, dates) in enumerate(c.SEASONS_DICT.items()):
    start_date, end_date = dates["start_date"], dates["end_date"]
    for centroid_counter, centroid in enumerate(set(tiles_germany.centroid_of_tile)):
        # ToDo: add faster way to check if data is already downloaded
        # see: make_trainings_data.ipynb
        try:
            result = download_sentinel2_data(
                api=api,
                footprint=centroid,
                start_date=start_date,
                end_date=end_date,
                download_root=c.DOWNLOAD_PATH,
                mode="training",
            )
            print(
                f"season {season} ({season_counter+1}/{len(c.SEASONS_DICT.keys())}) "
                f"for tile {centroid_counter+1}/"
                f"{len(set(tiles_germany.centroid_of_tile))} finished"
            )
            # ToDo: add tile_name to final dataframe
        # ! result is type bool not exception
        except Exception as e:
            print(f"Error occurred while downloading data for centroid {centroid}: {e}")
            logging.error(
                f"Error occurred while downloading data for centroid {centroid}: {e}"
            )
            # ToDo: send mail to admin

    logging.info("Program finished successfully")
