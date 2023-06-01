# build-in
import time
from datetime import date
from distutils.util import strtobool
from pathlib import Path
from typing import Union
import requests

# third-party
import geopandas as gpd

# local modules
from api_call_handler import download_sentinel2_data
from cloud_clients import aws_available
from constants import DOWNLOAD_PATH, NOW_DICT, PATH_TO_TILES, SEASONS_DICT
from geopandas import GeoDataFrame
from logging_config import get_logger
from sentinel_api import connect_to_sentinel_api
from sentinelsat import SentinelAPI
from sentinelsat.exceptions import ServerError, UnauthorizedError
from settings import DOCKERIZED, MAKE_TRAININGS_DATA, PRODUCTION

# set up logger
logger = get_logger('BaseConfig')
"""
ToDo: Check logger settings
ToDo: logger in submodules
ToDo: Needs better documentation

"""


def main():
    check_requirements()
    api = get_api()
    tiles_gdf = load_tiles_file(path=PATH_TO_TILES)

    if MAKE_TRAININGS_DATA:
        dates_dict = SEASONS_DICT
    else:
        dates_dict = NOW_DICT

    for season_counter, (season, dates) in enumerate(dates_dict.items()):
        start_date, end_date = dates["start_date"], dates["end_date"]
        for centroid_counter, centroid in enumerate(set(tiles_gdf.centroid_of_tile)):
            download_data(api, centroid, start_date, end_date)
            logger.info(
                f"season {season} ({season_counter+1}/{len(dates_dict.keys())}) "
                f"for tile {centroid_counter+1}/"
                f"{len(set(tiles_gdf.centroid_of_tile))} finished"
            )
    logger.info("Program finished successfully")


def download_data(
    api: SentinelAPI, footprint: str, start_date: date, end_date: date
) -> None:
    try:
        download_sentinel2_data(
            api=api,
            footprint=footprint,
            start_date=start_date,
            end_date=end_date,
            download_root=DOWNLOAD_PATH,
        )

    except Exception as e:
        logger.error(f"Error occurred while downloading data: {e}")


def check_requirements() -> None:
    logger.info("Downloader started, with the settings:")
    logger.info(f"Dockerized = {DOCKERIZED}")
    logger.info(f"Make_trainings_data = {MAKE_TRAININGS_DATA}")
    logger.info(f"Production = {PRODUCTION}")

    while True:
        if create_download_path(path=DOWNLOAD_PATH):
            break

    if not aws_available:
        logger.warning("AWS credentials not valid, running script anyway")


def get_api() -> SentinelAPI:
    while True:
        try:
            api = wait_for_api_connection()
            return api
        except Exception as e:
            logger.error(f"Error connecting to API: {e}")
            exit()


def load_tiles_file(path: Path) -> GeoDataFrame:
    """Load a GeoDataFrame from a GeoJSON file.

    Parameters
    ----------
    path : Path
        The path to the GeoJSON file.

    Returns
    -------
    tiles_file : GeoDataFrame
        The GeoDataFrame loaded from the GeoJSON file.

    Raises
    ------
    SystemExit
        If the GeoDataFrame loaded from the GeoJSON file is empty.
    """
    if not path.exists():
        logger.error(f"Could not find {path}")
        exit()

    tiles_file = gpd.read_file(path)

    if len(tiles_file) == 0:
        logger.error(f"Could not read {path.name} or empty file")
        exit()

    return tiles_file


def create_download_path(path: Path) -> bool:
    """
    Creates download path if it does not exist
    Args:
        path (pathlib.Path): path to download data to

    Returns:
        bool: True if path was created, False if not
    """
    if DOCKERIZED:
        logger.info("Dockerized, input paths will be auto created")
        return True

    if not path.exists():
        logger.warning(
            f"The download path: {path} does not exist. \n"
            f" Do you want to create it? [Y/n] (no will exiting program)"
        )
        user_input = input()

        try:
            user_input_bool = bool(strtobool(user_input))
        except ValueError:
            logger.info("Invalid input. Please use Y/n")
            return False

        if user_input_bool:
            path.mkdir(parents=True, exist_ok=False)
            logger.info("path created")
            return True
        else:
            logger.error("path not created, exiting program")
            exit()

    else:
        return True


def wait_for_api_connection() -> Union[bool, SentinelAPI]:
    """Connects to sentinelAPI and checks if the connection works."""
    api = connect_to_sentinel_api()

    if isinstance(api, ServerError):
        # ToDo: send mail to admin once a day
        # ToDo: check if this works
        logger.warning(
            """Could not connect to Sentinel API. \n
                Probably ongoing maintenance. \n
                Retrying in 5 minutes."""
        )
        time.sleep(300)  # retry after 5 minutes
        return False

    elif isinstance(api, UnauthorizedError):
        # ToDo: send mail to admin once
        logger.error("Wrong credentials for Sentinel API. Please check .env file")
        exit()

    elif isinstance(api, ConnectionError):
        logger.warning(
            """Could not connect to Sentinel API. \n
                Check your internet connection.
            """
        )
        exit()

    elif isinstance(api, Exception):
        # ToDo: send mail to admin every time
        logger.error(f"Unknown error occurred: {api}")
        exit()

    else:
        return api


if __name__ == "__main__":
    main()
