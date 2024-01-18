# build-in
import copy
from pathlib import Path
from typing import Any, Dict, Tuple, Union

import numpy as np

# third-party
import rasterio
from rasterio.windows import Window

# local-modules
from app.constants import (
    IMAGE_OUTPUT_DIR,
    KERNEL_SIZE,
    MASK_OUTPUT_DIR,
    NOW_DICT,
    PATH_TO_TILES,
    STEP_SIZE,
    URL_API,
    URL_ML,
)
from app.health_checks import run_checks
from app.jwt_functions import get_jwt_from_api, store_jwt
from app.logging_config import get_logger
from app.models.identifier import Identifier
from app.open_data import open_data_handler
from app.prediction import prediction_handler
from app.preprocess import moving_window, pad_image, preprocess_handler
from app.sentinel_on_aws import download_from_sentinel_aws_handler
from app.sentinel_query import get_identifier_handler
from app.settings import DOCKERIZED  # , MAKE_TRAININGS_DATA, PRODUCTION
from app.utils import create_output_directories, load_tiles_file, update_metadata
from app.write_to_db import write_to_db_handler

# set up logging
logger = get_logger(__name__)

# Vscode remote debugging in docker
# debugpy.listen(("0.0.0.0", 5678))
"""
ToDo: Add check if image and mask have the same length
ToDo: Log/logger.info the number of total files saved
"""


def main(
    tiles_list: list = None,
    dates: Dict[str, str] = NOW_DICT,
):
    logger.info(f"Dockerized = {DOCKERIZED}")
    logger.info(f"URL_ML = {URL_ML}")
    logger.info(f"URL_API = {URL_API}")

    run_setup()
    run_checks()

    # tiles_list = ["32UQE"]
    # ! tests needed
    if tiles_list is None:
        tiles_gdf = load_tiles_file(path=PATH_TO_TILES)
        tiles_list = list(set(tiles_gdf.tile_name))

    for tile_counter, tile_name in enumerate(tiles_list):
        # logger.info(f"Processing tile {tile_counter+1} of {len(set(tiles_gdf.tile_name))}")
        try:
            process_tile(tile_name=tile_name, dates=dates)
        except Exception as e:
            logger.error(f"Could not process tile {tile_name}: {e}")
            continue
    logger.info("Finished processing all tiles")


def run_setup() -> None:
    """Runs all setups."""
    logger.info("Running setups")
    output_dirs = [IMAGE_OUTPUT_DIR, MASK_OUTPUT_DIR]
    create_output_directories(output_dirs)
    # ! username and password change later
    try:
        token = get_jwt_from_api()
        store_jwt(token)
    except Exception as e:
        logger.error(f"Could not get JWT from API: {e}")
        exit(1)


def process_tile(
    tile_name: str,
    dates: Dict[str, str],
):
    identifier, band_file_info = get_identifier_and_band_info(
        tile_name=tile_name, dates=dates
    )
    if identifier is None or band_file_info is None:
        return

    stacked_bands, first_band_open, metadata = open_and_preprocess_data(
        band_file_info=band_file_info
    )
    if stacked_bands is None:
        return

    num_rows, num_cols = calc_rows_cols(metadata)

    file_identifier = 0
    # use
    # from concurrent.futures import ThreadPoolExecutor
    # from itertools import product
    # to improve speed

    for row in range(num_rows + 1):
        for col in range(num_cols + 1):
            logger.info(f"Processing tile {tile_name} row {row} col {col}")
            # Define the window coordinates for the snippet
            window = rasterio.windows.Window(
                col * STEP_SIZE, row * STEP_SIZE, KERNEL_SIZE, KERNEL_SIZE
            )
            file_identifier += 1
            process_window(
                stacked_bands=stacked_bands,
                window=window,
                metadata=metadata,
                first_band_open=first_band_open,
                identifier=identifier,
                file_identifier=file_identifier,
            )
    logger.info(f"Finished processing tile {tile_name}")
    return


def get_identifier_and_band_info(
    tile_name: str,
    dates: Dict[str, str] = NOW_DICT,
) -> Tuple[Identifier | None, Dict[str, Dict[str, Union[str, Path]]] | None]:
    identifier = get_identifier_handler(tile_id=tile_name, dates=dates)
    if identifier is None:
        return None, None

    logger.info(f"Starting download from sentinel aws for {identifier.to_string()}")
    band_file_info = download_from_sentinel_aws_handler(
        identifier=identifier, target_folder=IMAGE_OUTPUT_DIR
    )
    return identifier, band_file_info


def open_and_preprocess_data(
    band_file_info: Dict[str, Dict[str, Union[str, Path]]]
) -> Tuple[np.ndarray | None, dict, Dict[str, Any] | None]:
    stacked_bands, first_band_open, original_metadata = open_data_handler(
        band_file_info=band_file_info
    )
    if stacked_bands is None:
        return None, None, None

    metadata = copy.deepcopy(original_metadata)
    stacked_bands = preprocess_handler(array=stacked_bands, training=True)
    return stacked_bands, first_band_open, metadata


def calc_rows_cols(metadata: Dict[str, Any]) -> Tuple[int, int]:
    if not isinstance(metadata, dict):
        raise ValueError(f"Could not calculate rows and cols for {metadata}")
    if metadata is None:
        raise ValueError(f"Could not calculate rows and cols for {metadata}")
    if not isinstance(metadata["height"], int):
        raise ValueError(f"Could not calculate rows and cols for {metadata}")
    if not isinstance(metadata["width"], int):
        raise ValueError(f"Could not calculate rows and cols for {metadata}")
    if metadata["height"] < KERNEL_SIZE:
        raise ValueError(
            f"Kernel size {KERNEL_SIZE} is bigger than image height {metadata['height']}"
        )
    if metadata["width"] < KERNEL_SIZE:
        raise ValueError(
            f"Kernel size {KERNEL_SIZE} is bigger than image width {metadata['width']}"
        )

    num_rows = (metadata["height"] - KERNEL_SIZE) // STEP_SIZE + 1
    num_cols = (metadata["width"] - KERNEL_SIZE) // STEP_SIZE + 1
    return num_rows, num_cols


def get_small_image(stacked_bands: np.array, window: Window) -> np.ndarray | None:
    small_image = moving_window(stacked_bands, window)
    if small_image is None or small_image.max() == 0:
        return None
    if small_image.shape != (KERNEL_SIZE, KERNEL_SIZE, 4):
        small_image = pad_image(small_image, KERNEL_SIZE)
    return small_image


def get_prediction_and_filename(
    small_image: np.array, identifier: Identifier, file_identifier: int
) -> Tuple[np.ndarray | None, str | None]:
    prediction = prediction_handler(small_image=small_image)
    if prediction is None:
        return None, None

    filename = f"{identifier.tile}_{file_identifier}_{identifier.tile_date}.tif"
    return prediction, filename


def process_window(
    stacked_bands: np.array,
    window: Window,
    metadata: Dict[str, Any],
    first_band_open: dict,
    identifier: Identifier,
    file_identifier: int,
) -> int:
    small_image = get_small_image(stacked_bands, window)
    if small_image is None:
        return file_identifier

    prediction, filename = get_prediction_and_filename(
        small_image, identifier, file_identifier
    )
    if prediction is None:
        return file_identifier

    metadata_small_image = update_metadata(
        metadata=metadata, window=window, first_band_open=first_band_open
    )

    write_to_db_handler(
        prediction=prediction,
        metadata=metadata_small_image,
        tile_date=identifier.tile_date,
        filename=filename,
        identifier=identifier.to_string(),
    )
    logger.debug("written to db")

    return file_identifier


if __name__ == "__main__":
    main()
