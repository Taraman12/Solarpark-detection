# build-in
import copy

# third-party
import debugpy
import rasterio

# local-modules
from constants import (
    IMAGE_OUTPUT_DIR,
    KERNEL_SIZE,
    MASK_OUTPUT_DIR,
    PATH_TO_TILES,
    STEP_SIZE,
    URL_API,
    URL_ML,
)
from health_checks import run_checks
from jwt_functions import get_jwt_from_api, store_jwt
from logging_config import get_logger
from models.identifier import Identifier
from open_data import open_data_handler
from prediction import prediction_handler
from preprocess import pad_image, preprocess_handler
from sentinel_on_aws import download_from_sentinel_aws_handler
from sentinel_query import get_identifier
from settings import DOCKERIZED, MAKE_TRAININGS_DATA, PRODUCTION
from utils import create_output_directories, load_tiles_file
from write_to_db import write_to_db_handler

# set up logging
logger = get_logger("BaseConfig")
# Vscode remote debugging in docker
debugpy.listen(("0.0.0.0", 5678))
"""
ToDo: Add online downloader for Sentinel-2 images
ToDo: Add counter for loop
ToDo: Add check if image and mask have the same length
ToDo: Log/logger.info the number of total files saved

ToDo: Needs better documentation
ToDo: Needs better variable names
ToDo: Needs better function names
ToDo: Needs better type hints
ToDo: Needs better comments
ToDo: Needs better logging
ToDo: Needs better error handling
ToDo: Needs better testing
ToDo: Needs better refactoring
ToDo: Needs better structure
ToDo: Needs better everything
"""


# ! don't delete yet
# def check_ml_serve_online_localhost() -> bool:
#     retries = 3
#     while retries > 0:
#         try:
#             logger.info(f"Checking if TorchServe is running on {URL_ML}")
#             response = requests.get("http://localhost:8080/ping")
#             if response.status_code == 200:
#                 logger.info("TorchServe is running")
#                 return True
#             else:
#                 logger.info("TorchServe is not running. retry in 5 seconds.")
#                 time.sleep(5)
#         except requests.exceptions.ConnectionError:
#             logger.info("TorchServe is not running. Retry in 5 seconds.")
#             time.sleep(5)
#         retries -= 1
#     return False


def run_setup() -> None:
    """Runs all setups."""
    logger.info("Running setups")
    output_dirs = [IMAGE_OUTPUT_DIR, MASK_OUTPUT_DIR]
    create_output_directories(output_dirs)
    # ! Change later
    try:
        token = get_jwt_from_api(username="John@Doe.com", password="password")
        store_jwt(token)
    except Exception as e:
        logger.error(f"Could not get JWT from API: {e}")
        exit(1)


if __name__ == "__main__":
    logger.info("Preprocessing started, with the settings:")
    logger.info(f"Dockerized = {DOCKERIZED}")
    logger.info(f"Make_trainings_data = {MAKE_TRAININGS_DATA}")
    logger.info(f"Production = {PRODUCTION}")
    logger.info(f"URL_ML = {URL_ML}")
    logger.info(f"URL_API = {URL_API}")

    run_setup()
    run_checks()

    tiles_gdf = load_tiles_file(path=PATH_TO_TILES)
    # TODO: Include Case
    # if MAKE_TRAININGS_DATA:
    #     folder_list = os.listdir(IMAGE_INPUT_DIR)

    for centroid_counter, centroid in enumerate(set(tiles_gdf.centroid_of_tile)):
        # 1. get identifier from centroid
        identifier_string = get_identifier(centroid)
        if identifier_string is None:
            continue
        identifier = Identifier(identifier_string)
        exit()
        # If Production else use downloader to read from disk
        band_file_info = download_from_sentinel_aws_handler(identifier_string)
        if band_file_info is None:
            continue

        # 3. open dataset readers
        stacked_bands, first_band_open, original_metadata = open_data_handler(
            band_file_info
        )
        if stacked_bands is None:
            continue
        metadata = copy.deepcopy(original_metadata)

        stacked_bands = pad_image(stacked_bands, KERNEL_SIZE, STEP_SIZE)
        num_rows = (metadata["height"] - KERNEL_SIZE) // STEP_SIZE + 1
        num_cols = (metadata["width"] - KERNEL_SIZE) // STEP_SIZE + 1
        file_identifier = 0
        for row in range(num_rows + 1):
            for col in range(num_cols + 1):
                # Define the window coordinates for the snippet
                window = rasterio.windows.Window(
                    col * STEP_SIZE, row * STEP_SIZE, KERNEL_SIZE, KERNEL_SIZE
                )
                small_image = preprocess_handler(stacked_bands, window)
                if small_image is None:
                    continue

                # 5. send to ml-serve
                prediction = prediction_handler(small_image, metadata)
                if prediction is None:
                    continue

                file_identifier += 1
                filename = (
                    f"{identifier.tile}_{file_identifier}_{identifier.tile_date}.tif"
                )
                # 6. update metadata
                # ! IMPLEMENTATION NEEDED
                metadata.update(
                    {
                        "width": window.width,
                        "height": window.height,
                        "transform": first_band_open.window_transform(window),
                    }
                )

                # 7. send to api
                write_to_db_handler(
                    prediction, metadata, identifier.tile_date, filename
                )
                print("writen to db")
                # 8. send to aws
                # ! IMPLEMENTATION NEEDED

        # 4. if MAKE_TRAININGS_DATA: save to disk

        # ! Here the identifier from the API should be used
        # ! change to raw_data
        # ToDo: import from constants
        # folder_list = aws_list_folders(prefix=str(IMAGE_INPUT_DIR))
        # IMAGE_INPUT_DIR = Path()

    #     saved_total = 0

    #     # for i, tile_folder_path in enumerate(folder_list):
    #     #     logger.info(f"Processing file {i+1} of {len(folder_list)}")
    #     try:
    #         # saved_patches = preprocess_and_save_data(
    #         #     tile_folder_path=tile_folder_path, masks_gdf=masks_gdf
    #         # )
    #         saved_patches = preprocess_and_save_data(
    #             tile_folder_path=identifier, masks_gdf=masks_gdf
    #         )
    #     except Exception as e:
    #         logger.error(e)
    #         continue

    #     saved_total += saved_patches
    #     logger.info(f"Number of files saved: {saved_patches}")
    # logger.info(f"program finished. Total images saved: {saved_total}")
