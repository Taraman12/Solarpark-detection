# built-in
import logging
import time
from pathlib import Path

# third-party
import geopandas as gpd
from API_call_handler import download_sentinel2_data

# local-modules
import constants as c
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
    tiles_germany = gpd.read_file(r"src/download_sentinel_data/data/tiles_germany.geojson")

    api = connect_to_sentinel_api()

    # if api is ServerError:
    #     print(f"""Could not connect to Sentinel API \n
    #             Probably ongoing maintenance \n
    #             retry after 5 minutes""")
    #     # ToDo: add error handling -> retry after 5 minutes
    #     # ToDo: send mail to admin
    #     exit()
    # elif api is UnauthorizedError:
    #     print("Wrong credentials for Sentinel API \n Please check .env file")
    #     exit()
    # elif isinstance(api, Exception):
    #     # ToDo: send mail to admin
    #     print("Unknown error occurred")
    #     exit()

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

    for centroid in set(tiles_germany.centroid_of_tile):
        try:
            result = download_sentinel2_data(api, centroid, c.DOWNLOAD_PATH, mode="production")
            # ToDo: add tile_name to final dataframe
        # ! result is type bool not exception
        except Exception as e:
            print(f"Error occurred while downloading data for centroid {centroid}: {e}")
            logging.error(
                f"Error occurred while downloading data for centroid {centroid}: {e}"
            )
            # ToDo: send mail to admin

    logging.info("Program finished successfully")
