import copy
import glob
import os
import time
from functools import partial
from multiprocessing import Pool
from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
import torch
from constants import KERNEL_SIZE, STEP_SIZE, UNDERSAMPLING_RATE, USED_BANDS
from models.identifier import Identifier
from open_data import open_data_handler
from preprocess import moving_window, pad_image, preprocess_handler
from rasterio.features import geometry_mask

# from rasterio.windows import Window
from utils import update_metadata

"""
Idea:
store just the raw bands and the masks in a folder
so the preprocessing can be done on the fly

ToDos:
- [ ] Add docstrings
- [ ] Add type hints
- [ ] Add logging
- [ ] Add tests

"""


def make_trainings_data_handler(
    path: Path, identifier: Identifier, masks_gdf: gpd.GeoDataFrame
):
    output_path = Path(
        r"C:\Users\Fabian\Documents\Github_Masterthesis\Solarpark-detection\data_local\refactored_undersampling_not_color\images"
    )
    MASK_OUTPUT_DIR = Path(
        r"C:\Users\Fabian\Documents\Github_Masterthesis\Solarpark-detection\data_local\refactored_undersampling_not_color\masks"
    )

    output_path.mkdir(parents=True, exist_ok=True)
    MASK_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # identifier_string = identifier.to_string()
    band_file_info = make_file_paths(path)  # / identifier_string
    stacked_bands, first_band_open, original_metadata = open_data_handler(
        band_file_info=band_file_info
    )
    metadata = copy.deepcopy(original_metadata)

    num_rows = (metadata["height"] - KERNEL_SIZE) // STEP_SIZE + 1
    num_cols = (metadata["width"] - KERNEL_SIZE) // STEP_SIZE + 1
    large_image = preprocess_handler(array=stacked_bands, training=True)
    file_identifier = 0
    mask_counter = 0

    large_image = large_image.transpose(1, 2, 0)

    masks = filter_mask_on_tile(masks_gdf, identifier.tile)

    for row in range(num_rows + 1):
        for col in range(num_cols + 1):
            window = rasterio.windows.Window(
                col * STEP_SIZE, row * STEP_SIZE, KERNEL_SIZE, KERNEL_SIZE
            )

            small_image = moving_window(large_image, window)

            if small_image.max() == 0:
                continue

            if small_image.shape != (KERNEL_SIZE, KERNEL_SIZE, 4):
                small_image = pad_image(small_image, KERNEL_SIZE)

            metadata_small_image = update_metadata(
                metadata=metadata, window=window, first_band_open=first_band_open
            )

            rasterized_mask = rasterize_mask(masks, metadata_small_image)

            if not rasterized_mask.sum() >= 100:
                mask_counter += 1
                if mask_counter % (1 / UNDERSAMPLING_RATE) != 0:
                    continue

            file_identifier += 1
            filename = f"{identifier.tile}_{file_identifier}_{identifier.tile_date}.tif"
            if not (output_path / filename).exists():
                save_patch_image(
                    small_image, metadata_small_image, output_path / filename
                )
            # save_as_tensor(small_image, filename, output_path)

            if rasterized_mask.dtype != np.uint8:
                rasterized_mask = rasterized_mask.astype(np.uint8)

            if not (MASK_OUTPUT_DIR / filename).exists():
                # save_as_tensor(
                #     np.expand_dims(rasterized_mask, axis=0), filename, MASK_OUTPUT_DIR
                # )
                save_patch_mask(
                    np.expand_dims(rasterized_mask, axis=0),
                    metadata_small_image,
                    MASK_OUTPUT_DIR / filename,
                )


def make_file_paths(path: Path):
    """
    Make file paths for the given identifier.
    :param path: Path to the directory.
    :param identifier: Identifier of the file.
    :return: File paths for the identifier.
    """
    band_file_info = {}
    for band, resolution in USED_BANDS.items():
        file_path = path / f"{band}_{resolution}.jp2"
        band_file_info[band] = {"resolution": resolution, "file_path": file_path}
    return band_file_info


def save_patch_image(array: np.ndarray, metadata: dict, output_path: Path) -> None:
    metadata["driver"] = "GTiff"
    metadata["count"] = 4
    metadata["dtype"] = rasterio.float32

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if array.shape != (len(USED_BANDS), KERNEL_SIZE, KERNEL_SIZE):
        array = array.transpose(2, 0, 1)

    with rasterio.open(fp=output_path, mode="w", **metadata) as dst:
        dst.write(array)  # .astype(rasterio.float32)

    return None


def save_patch_mask(array: np.ndarray, metadata: dict, output_path: Path) -> None:
    metadata["driver"] = "GTiff"
    metadata["count"] = 1
    metadata["dtype"] = rasterio.uint8

    output_path.parent.mkdir(parents=True, exist_ok=True)
    if array.shape != (1, KERNEL_SIZE, KERNEL_SIZE):
        array = array.transpose(2, 0, 1)
    with rasterio.open(fp=output_path, mode="w", **metadata) as dst:
        dst.write(array)  # .astype(rasterio.float32)

    return None


def save_as_tensor(array: np.array, filename: str, output_path: Path):
    """
    Save the array as a tensor.
    :param array: Array to save.
    :param filename: Filename of the tensor.
    :param output_path: Path to the output directory.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if array.shape != (len(USED_BANDS), KERNEL_SIZE, KERNEL_SIZE):
        array = array.transpose(2, 0, 1)
    tensor = torch.from_numpy(array)
    torch.save(tensor.clone(), output_path / filename)


def filter_mask_on_tile(masks: gpd.GeoDataFrame, tile: str) -> gpd.GeoDataFrame:
    return masks[masks.tile_name == tile].geometry.reset_index(drop=True)


def rasterize_mask(masks: gpd.GeoDataFrame, metadata: dict) -> np.ndarray:
    # create a raster which matches the image shape
    # invert=True masked pixels set to True (instead of the other way around)
    # all_touched=True all pixels within the mask set to True (instead of the bounds)
    crs = metadata["crs"]
    shape = (metadata["height"], metadata["width"])
    transform = metadata["transform"]
    return geometry_mask(
        geometries=masks.to_crs(crs),
        out_shape=shape,
        transform=transform,
        all_touched=True,
        invert=True,
    )


def process_file(file_path: Path, masks_gdf: gpd.GeoDataFrame):
    try:
        identifier = Identifier(file_path.name)
    except ValueError:
        # not a valid file path
        return
    make_trainings_data_handler(file_path, identifier, masks_gdf)


def check_files_exist(path: Path):
    # Iterate over all subdirectories in the directory
    for subdir, dirs, files in os.walk(path):
        # Iterate over all bands
        for band in bands:
            # Use glob to find all files in the subdirectory that end with the band
            matching_files = glob.glob(os.path.join(subdir, "*" + band))

            for file in matching_files:
                # Get the base name of the file (without the directory)
                base_name = os.path.basename(file)

                # If the base name is not equal to the band, it has a prefix
                if base_name != band:
                    print(
                        f"File {file} for band {band} in directory {subdir} has a prefix"
                    )


if __name__ == "__main__":
    bands = ["B02_10m.jp2", "B03_10m.jp2", "B04_10m.jp2", "B08_10m.jp2"]
    start_time = time.time()
    path = Path(
        r"C:\Users\Fabian\Documents\Github_Masterthesis\Solarpark-detection\data_local\training_data_raw"
    )
    check_files_exist(path)
    masks_gdf = gpd.read_file(
        "./src/preprocessing/app/data/trn_polygons_germany_tile_names.geojson"
    )
    process_file_with_args = partial(process_file, masks_gdf=masks_gdf)
    with Pool(processes=4) as p:
        # Use the pool to process the files in parallel
        p.map(process_file_with_args, path.iterdir())

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"The function took {execution_time:.2f} seconds to run.")
