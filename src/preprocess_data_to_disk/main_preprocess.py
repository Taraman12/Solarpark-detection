# build-in
import os
import re
from pathlib import Path
from typing import Any, Dict, Tuple, Union

# third-party
import geopandas as gpd
import numpy as np
import rasterio
import torch
from rasterio import DatasetReader
from torch import Tensor
from torchvision.transforms import Pad

# local modules
import constants as c
from preprocessing_dataset_to_disk import save_patched_data_to_disk 

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



"""

if __name__ == "__main__":
    print("Program started")
    root_dir = Path(__file__).resolve().parent.parent
    # os.chdir(Path(__file__).parent)
    print(os.getcwd())
    # rename
    image_input_dir = c.IMAGE_INPUT_DIR
    mask_input_dir = c.MASK_INPUT_DIR  # root_dir
    image_output_dir = c.IMAGE_OUTPUT_DIR
    mask_output_dir = c.MASK_OUTPUT_DIR

    for input_directory in [image_input_dir, mask_input_dir]:
        if not input_directory.exists():
            print(f"Input path: {input_directory} does not exist")

    for output_directory in [image_output_dir, mask_output_dir]:
        if not output_directory.exists():
            output_directory.mkdir(parents=True, exist_ok=False)
            print(
                f"Output path: {output_directory} does not exist \n"
                f"Directory created"
            )
    
    masks_gdf = gpd.read_file(mask_input_dir)

    kernel_size = 256
    # ToDo: add loop over all folders in image_dir (it is only a single one)
    # open mask_gdf outside the loop
    for tile_folder in os.listdir(image_input_dir):
        # ! changed to match instead of search
        regex_match = re.match(c.IDENTIFIER_REGEX, tile_folder)

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
            kernel_size,
            tile=tile,
            tile_date=f"{year}-{month}-{day}",
        )
        print(f"Number of files saved: {result}")
    print("program finished")