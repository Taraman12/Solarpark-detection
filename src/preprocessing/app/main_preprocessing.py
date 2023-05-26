# build-in
import os
from os import path
import re
from pathlib import Path
import time
import requests

# import logging
# import logging.config

# third-party
import debugpy
import geopandas as gpd

# local-modules
from aws_functions import aws_list_files, aws_list_folders
from cloud_clients import aws_available, s3_client, verify_aws_credentials
from constants import (
    IDENTIFIER_REGEX,
    IMAGE_INPUT_DIR,
    IMAGE_OUTPUT_DIR,
    MASK_INPUT_DIR,
    MASK_OUTPUT_DIR,
)
from save_to_disk import save_patched_data_to_disk
from logging_config import get_logger

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


if __name__ == "__main__":
    # logger.info("Waiting for client to attach...")
    # debugpy.wait_for_client()
    # time.sleep(15)
    logger.info("Program started")
    # debugpy.breakpoint()
    # print("Program started")
    # root_dir = Path(__file__).resolve().parent.parent
    # os.chdir(Path(__file__).parent)

    if os.environ.get("DOCKERIZED") == "true":
        logger.info("Running in docker container")
        # print("Running in docker container")
        # exit()

    # if os.environ.get("Training") == "false":
    training = False
    logger.info("Running in production mode")

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

    # rename
    image_input_dir = IMAGE_INPUT_DIR
    mask_input_dir = MASK_INPUT_DIR  # root_dir
    image_output_dir = IMAGE_OUTPUT_DIR
    mask_output_dir = MASK_OUTPUT_DIR

    # mandatory if trainings data should be created
    if training:
        for input_directory in [image_input_dir, mask_input_dir]:
            if not input_directory.exists():
                logger.error(f"Input path: {input_directory} does not exist")
                # print(f"Input path: {input_directory} does not exist")
                exit()

    # optional
    for output_directory in [image_output_dir, mask_output_dir]:
        if not output_directory.exists():
            output_directory.mkdir(parents=True, exist_ok=False)
            logger.info(
                f"Output path: {output_directory} does not exist \n"
                f"Directory created"
            )
            # print(
            #     f"Output path: {output_directory} does not exist \n"
            #     f"Directory created"
            # )

    # optional

    if not aws_available:
        # ToDo: set up logging
        # ToDo: make it possible to run without aws credentials
        logger.warning("AWS credentials not valid")
        # print("AWS credentials not valid")

    masks_gdf = gpd.read_file(mask_input_dir)

    kernel_size = 256

    # aws_available = False
    if training:
        folder_list = os.listdir(image_input_dir)
    else:
        # ! change to raw_data
        # ToDo: import from constants
        folder_list = aws_list_folders(prefix=str(image_input_dir))
        image_input_dir = Path()

        # folder_list_raw = [
        #     folder.replace("data_raw/", "") for folder in folder_list_raw
        # ]
        # folder_list = [folder.strip("/") for folder in folder_list_raw]
    # ToDo: add loop over all folders in image_dir (it is only a single one)
    # open mask_gdf outside the loop
    result_total = 0
    logger.info(f"Number of files to process: {len(folder_list)}")
    # print(folder_list)
    for i, tile_folder in enumerate(folder_list):
        logger.info(f"Processing file {i+1} of {len(folder_list)}")
        # print(f"Processing file {i+1} of {len(folder_list)}")

        regex_match = re.search(IDENTIFIER_REGEX, tile_folder)

        if not regex_match:
            continue

        else:
            utm_code = regex_match.group("utm_code")
            latitude_band = regex_match.group("latitude_band")
            square = regex_match.group("square")
            year = regex_match.group("year")
            month = str(int(regex_match.group("month")))
            day = str(int(regex_match.group("day")))
            tile = f"{utm_code}{latitude_band}{square}"

        try:
            result = save_patched_data_to_disk(
                image_input_dir / tile_folder,
                masks_gdf,
                image_output_dir,
                mask_output_dir,
                tile=tile,
                tile_date=f"{year}-{month}-{day}",
                kernel_size=kernel_size,
                production=True,
            )
        except Exception as e:
            logger.error(e)
            continue
        #! Remove
        # exit()
        result_total += result
        print(f"Number of files saved: {result}")
    print(f"Number of total files saved: {result_total}")
    print("program finished")
