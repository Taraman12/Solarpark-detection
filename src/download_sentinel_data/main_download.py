# built-in
import logging
import time
from distutils.util import strtobool
from pathlib import Path

# local-modules
import constants as c

# third-party
import geopandas as gpd
from API_call_handler import download_sentinel2_data
from sentinel_api import connect_to_sentinel_api
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

if __name__ == "__main__":
    logging.info("Program started")
    print("Program started")

    # ToDo: Check if tiles_germany.geojson exists
    tiles_germany = gpd.read_file(
        r"src/download_sentinel_data/data/tiles_germany.geojson"
    )

    if len(tiles_germany) == 0:
        logging.error("Could not read tiles_germany.geojson")
        print("Could not read tiles_germany.geojson")
        exit()

    while True:
        if not Path(c.DOWNLOAD_PATH).exists():
            print(
                f"The download path: {c.DOWNLOAD_PATH} does not exist. \n"
                f" Do you want to create it? [y/n] (no will exiting program)"
            )
            user_input = input()

            try:
                user_input_bool = bool(strtobool(user_input))
            except ValueError:
                print("Invalid input. Please use y/n")
                continue

            if user_input_bool:
                c.DOWNLOAD_PATH.mkdir(parents=True, exist_ok=False)
                print("path created")
            else:
                print("path not created, exiting program")
                exit()

        break

    api = connect_to_sentinel_api()

    while True:
        if isinstance(api, ServerError):
            # ToDo: send mail to admin once a day
            logging.warning(
                """Could not connect to Sentinel API. \n
                    Probably ongoing maintenance. \n
                    Retrying in 5 minutes."""
            )
            time.sleep(300)  # retry after 5 minutes
            api = connect_to_sentinel_api()

        elif isinstance(api, UnauthorizedError):
            # ToDo: send mail to admin once
            logging.error("Wrong credentials for Sentinel API. Please check .env file")
            exit()

        elif isinstance(api, Exception):
            # ToDo: send mail to admin every time
            logging.error(f"Unknown error occurred: {api}")
            exit()

        else:
            break


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
