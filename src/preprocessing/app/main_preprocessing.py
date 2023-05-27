# build-in
import os
import re
import time
from os import path
from pathlib import Path
from typing import List

# third-party
import debugpy
import geopandas as gpd
import requests

# local-modules
from aws_functions import aws_list_files, aws_list_folders
from cloud_clients import aws_available
from constants import (
    IDENTIFIER_REGEX,
    IMAGE_INPUT_DIR,
    IMAGE_OUTPUT_DIR,
    MASK_INPUT_DIR,
    MASK_OUTPUT_DIR,
    URL,
)
from logging_config import get_logger
from save_to_disk import preprocess_and_save_data
from settings import DOCKERIZED, MAKE_TRAININGS_DATA, PRODUCTION

# set up logging
logger = get_logger(__name__)
debugpy.listen(("0.0.0.0", 5678))
"""
ToDo: Add counter for loop
ToDo: Add check if image and mask have the same length
ToDo: Log/Print the number of total files saved

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


def validate_input_paths(input_dirs: List[Path]) -> bool:
    """
    Validates that the input directories exist.

    Args:
        input_dirs (List[Path]): A list of input directories to validate.
        logger: A logger instance to use for logging.

    Returns:
        bool: True if all input directories exist, False otherwise.

    """
    all_dirs_exist = True
    for input_dir in input_dirs:
        if not input_dir.exists():
            logger.error(f"Input path: {input_dir} does not exist")
            all_dirs_exist = False
    return all_dirs_exist


def create_output_directories(output_dirs: List[Path]) -> None:
    """
    Creates the output directories if they do not exist.

    Args:
        output_dirs (List[Path]): A list of output directories to create.
        logger: A logger instance to use for logging.

    """
    for output_dir in output_dirs:
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=False)
            logger.info(
                f"Output path: {output_dir} does not exist \n" f"Directory created"
            )


def check_ml_serve_online() -> bool:
    retries = 5
    while retries > 0:
        try:
            response = requests.get(f"{URL}/ping")
            if response.status_code == 200:
                logger.info("TorchServe is running")
                return True
            else:
                logger.info("TorchServe is not running. retry in 5 seconds.")
                time.sleep(5)
        except requests.exceptions.ConnectionError:
            logger.info("TorchServe is not running. retry in 5 seconds.")
            time.sleep(5)
        retries -= 1
    return False


if __name__ == "__main__":
    logger.info("Preprocessing started, with the settings:")
    logger.info(f"Dockerized = {DOCKERIZED}")
    logger.info(f"Make_trainings_data = {MAKE_TRAININGS_DATA}")
    logger.info(f"Production = {PRODUCTION}")

    ##########################################
    # data = {
    #     "size_in_sq_m": 0,
    #     "peak_power": 0,
    #     "date_of_data": "2023-05-20",
    #     "first_detection": "2023-05-20",
    #     "last_detection": "2023-05-20",
    #     "geometry": "Test",  # lon_lat_polygon
    # }
    # url = "http://api:8000/api/v1/solarpark/"
    # headers = {"content-type": "application/json"}
    # logger.info(f"Writing to DB: {data}")
    # response = requests.get(url, headers=headers)
    # logger.info(f"Response get: {response.status_code}")
    # response = requests.post(url, headers=headers, json=data)
    # logger.info(f"Response post: {response.status_code}")

    # url = "http://localhost:8081/models"
    # req = requests.get(url)
    # logger.info(f"Response get model: {req.status_code}")
    # req.request.url
    # req.request.headers
    # req.request.body
    input_dirs = [IMAGE_INPUT_DIR, MASK_INPUT_DIR]
    output_dirs = [IMAGE_OUTPUT_DIR, MASK_OUTPUT_DIR]

    # mandatory if trainings data should be created
    if MAKE_TRAININGS_DATA and not validate_input_paths(input_dirs):
        exit()

    create_output_directories(output_dirs)

    # optional
    if not aws_available:
        logger.warning("AWS credentials not valid")

    PRODUCTION = False
    if PRODUCTION:
        if not check_ml_serve_online():
            logger.error("ml-serve not online. Exiting.")
            exit()

    masks_gdf = gpd.read_file(MASK_INPUT_DIR)

    if MAKE_TRAININGS_DATA:
        folder_list = os.listdir(IMAGE_INPUT_DIR)
    else:
        # ! change to raw_data
        # ToDo: import from constants
        folder_list = aws_list_folders(prefix=str(IMAGE_INPUT_DIR))
        IMAGE_INPUT_DIR = Path()

    saved_total = 0
    logger.info(f"Number of files to process: {len(folder_list)}")

    for i, tile_folder in enumerate(folder_list):
        logger.info(f"Processing file {i+1} of {len(folder_list)}")
        # print(f"Processing file {i+1} of {len(folder_list)}")
        try:
            saved_patches = preprocess_and_save_data(
                identifier=tile_folder, masks_gdf=masks_gdf
            )

        except Exception as e:
            logger.error(e)
            continue

        saved_total += saved_patches
        print(f"Number of files saved: {saved_patches}")
    print(f"program finished. Total images saved: {saved_total}")
