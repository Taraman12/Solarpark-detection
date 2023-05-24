# build-in
import os
import re
from pathlib import Path

# third-party
import geopandas as gpd
from aws_functions import aws_list_files, aws_list_folders
from cloud_clients import aws_available, s3_client, verify_aws_credentials

# local-modules
from constants import (
    IDENTIFIER_REGEX,
    IMAGE_INPUT_DIR,
    IMAGE_OUTPUT_DIR,
    MASK_INPUT_DIR,
    MASK_OUTPUT_DIR,
)

# from preprocessing_dataset_to_disk import save_patched_data_to_disk
from save_to_disk import save_patched_data_to_disk

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
    print("Program started")
    root_dir = Path(__file__).resolve().parent.parent
    # os.chdir(Path(__file__).parent)
    print(os.getcwd())

    if os.environ.get("DOCKERIZED") == "true":
        print("Running in docker container")
        exit()

    # if os.environ.get("Training") == "false":
    training = False
    # rename
    image_input_dir = IMAGE_INPUT_DIR
    mask_input_dir = MASK_INPUT_DIR  # root_dir
    image_output_dir = IMAGE_OUTPUT_DIR
    mask_output_dir = MASK_OUTPUT_DIR

    # mandatory
    for input_directory in [image_input_dir, mask_input_dir]:
        if not input_directory.exists():
            print(f"Input path: {input_directory} does not exist")
            exit()

    # optional
    for output_directory in [image_output_dir, mask_output_dir]:
        if not output_directory.exists():
            output_directory.mkdir(parents=True, exist_ok=False)
            print(
                f"Output path: {output_directory} does not exist \n"
                f"Directory created"
            )

    # optional

    if not aws_available:
        # ToDo: set up logging
        # ToDo: make it possible to run without aws credentials
        print("AWS credentials not valid")

    masks_gdf = gpd.read_file(mask_input_dir)

    kernel_size = 256

    training = True
    aws_available = False
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

    for i, tile_folder in enumerate(folder_list):
        print(f"Processing file {i+1} of {len(folder_list)}")

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

        result = save_patched_data_to_disk(
            image_input_dir / tile_folder,
            masks_gdf,
            image_output_dir,
            mask_output_dir,
            tile=tile,
            tile_date=f"{year}-{month}-{day}",
            kernel_size=kernel_size,
            production=False,
        )
        result_total += result
        print(f"Number of files saved: {result}")
    print(f"Number of total files saved: {result_total}")
    print("program finished")
