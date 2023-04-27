# built-in
import logging
import time
from pathlib import Path

# local-modules
import constants as c

# third-party
import geopandas as gpd
from API_call_handler import download_sentinel2_data
from sentinel_api import connect_to_sentinel_api
from sentinelsat.exceptions import ServerError, UnauthorizedError

logging.basicConfig(
    filename="app.log",
    filemode="w",
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

if __name__ == "__main__":
    logging.info("Program started")
    print(Path.cwd())
    tiles_germany = gpd.read_file(
        r"src/download_sentinel_data/data/tiles_germany.geojson"
    )

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
                f"season {season_counter} of {len(c.SEASONS_DICT.keys())}"
                f"for tile {centroid_counter}/"
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
