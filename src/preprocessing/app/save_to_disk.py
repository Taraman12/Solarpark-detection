# build-in
import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

# third-party
import geopandas as gpd
import numpy as np
import rasterio
import rasterio.features
import requests

# local modules
from aws_functions import (
    aws_list_files,
    delete_folder_on_aws,
    download_from_aws,
    upload_file_to_aws,
)
from cloud_clients import aws_available
from constants import (
    IDENTIFIER_REGEX,
    IMAGE_INPUT_DIR,
    IMAGE_OUTPUT_DIR,
    KERNEL_SIZE,
    MASK_INPUT_DIR,
    MASK_OUTPUT_DIR,
    REQUIRED_BANDS,
)
from geopandas import GeoDataFrame
from logging_config import get_logger
from pyproj import Transformer
from rasterio import DatasetReader
from rasterio.features import geometry_mask
from settings import DOCKERIZED, MAKE_TRAININGS_DATA, PRODUCTION
from shapely.geometry import Polygon

# set up logging
logging.getLogger("rasterio").setLevel(logging.WARNING)
logging.getLogger("fiona").setLevel(logging.WARNING)
logger = get_logger(__name__)
# log_file_path = path.join(path.dirname(path.abspath(__file__)), "logging.conf")
# logging.config.fileConfig(log_file_path)
# logger = logging.getLogger(__name__)
"""
ToDo: Add padding to the image/mask
ToDo: Needs better documentation
ToDo: handle memory consumption (but not so important)
"""

# Defining constants

# extracts tile, date, band and resolution from filename
# ! Adjust to TCI band
FILENAME_REGEX = re.compile(
    r"""(?P<band>.{3})(?:_
        (?P<resolution>\d{2}m))?\..*$""",
    re.VERBOSE,
)


def preprocess_and_save_data(
    identifier: str,
    masks_gdf: GeoDataFrame,
) -> int:
    tile, tile_date = get_tile_and_date(identifier)

    if tile is None or tile_date is None:
        return 0

    PRODUCTION = False
    if aws_available and PRODUCTION:
        result = download_from_aws(identifier)
        if not result:
            return 0

    # find paths to all REQUIRED_BANDS
    band_paths = find_band_paths(image_dir=IMAGE_INPUT_DIR / identifier)

    # open all REQUIRED_BANDS
    bands = open_dataset_readers(band_paths=band_paths)

    stacked_bands = preprocess_bands(bands)

    # ! MASK #
    # masks_gdf = gpd.read_file(mask_input_dir)
    first_band = list(bands.keys())[0]
    # filter all masks to selected tile
    if MAKE_TRAININGS_DATA:
        masks = filter_mask_on_tile(masks_gdf, tile)

        if len(masks) == 0:
            return 0

        # create a raster which matches the image shape
        rasterized_mask = rasterize_mask(masks, bands[first_band])

    metadata = bands[first_band].meta

    num_rows = metadata["height"] // KERNEL_SIZE
    num_cols = metadata["width"] // KERNEL_SIZE

    # unused, but start for more
    # arr = transform_to_patched_array(stacked_bands, num_rows, num_cols)

    metadata["width"] = KERNEL_SIZE
    metadata["height"] = KERNEL_SIZE

    file_counter = 0
    file_identifier = 0

    # Iterate over the rows and columns to split the image into small images
    for row in range(num_rows):
        for col in range(num_cols):
            # Define the window coordinates for the snippet
            window = rasterio.windows.Window(
                col * KERNEL_SIZE, row * KERNEL_SIZE, KERNEL_SIZE, KERNEL_SIZE
            )

            # Cut out the snippet from the merged image
            small_image = stacked_bands[
                window.row_off : window.row_off + window.height,
                window.col_off : window.col_off + window.width,
            ]

            # check if the image patch is not empty (all black)
            # https://gis.stackexchange.com/questions/380038/reasons-for-partial-tiles-in-sentinel
            if small_image.max() == 0:
                continue

            file_identifier += 1
            file_counter += 1

            # update metadata for small image patch
            metadata["transform"] = rasterio.windows.transform(
                window, bands[list(bands.keys())[0]].transform
            )

            if PRODUCTION:
                prediction_handler(small_image.transpose(2, 0, 1), metadata)
                continue

            if MAKE_TRAININGS_DATA:
                filename = f"{tile}_{file_identifier}_{tile_date}.tif"
                trainings_data_handler(file_name, rasterize_mask, window)

    if PRODUCTION:
        # delete the bigger image on aws
        delete_folder_on_aws(folder_path=identifier)

    return file_counter


def trainings_data_handler(
    file_name: str, rasterize_mask: np.array, window: rasterio.windows.Window
) -> None:
    # Extract the patch from the rasterized_mask
    mask_patch = rasterized_mask[
        window.row_off : window.row_off + window.height,
        window.col_off : window.col_off + window.width,
    ]
    if not mask_patch.sum() >= 200:
        return None

    metadata["count"] = 1
    # Save the mask patch as GeoTIFF (similar to saving small_image)

    mask_output_path = MASK_OUTPUT_DIR / filename
    # Assuming the metadata for the mask GeoTIFF is the same as the small_image GeoTIFF
    save_patch(
        mask_output_path,
        metadata,
        np.expand_dims(mask_patch, axis=0),
    )
    # ToDo: delete the bigger image if production is false

    # store small images as GeoTIFF
    metadata["count"] = 4
    metadata["driver"] = "GTiff"
    metadata["dtype"] = rasterio.float32
    output_path = IMAGE_OUTPUT_DIR / filename
    save_patch(output_path, metadata, small_image.transpose(2, 0, 1))


def prediction_handler(
    data: np.array,
    metadata: dict,
) -> None:
    prediction = send_to_ml_model(small_image.transpose(2, 0, 1), metadata)
    if not len(prediction) == 0:
        # mask = prediction_to_mask(pred)
        polygons = masks_to_polygons(prediction, metadata)
        logger.info(f"Found {len(polygons)} polygons")
        for polygon in polygons:
            write_to_db(polygon)


def get_tile_and_date(identifier: str) -> Tuple[Optional[str], Optional[str]]:
    regex_match = re.search(IDENTIFIER_REGEX, identifier)

    if not regex_match:
        return None, None

    utm_code = regex_match.group("utm_code")
    latitude_band = regex_match.group("latitude_band")
    square = regex_match.group("square")
    year = regex_match.group("year")
    # remove leading zeros
    month = str(int(regex_match.group("month")))
    day = str(int(regex_match.group("day")))

    tile = f"{utm_code}{latitude_band}{square}"
    tile_date = f"{year}-{month}-{day}"

    return tile, tile_date


def send_to_ml_model(data_array: np.ndarray, metadata: dict) -> dict:
    headers = {"Content-Type": "application/json"}
    json_data = json.dumps(data_array.tolist())
    req = requests.post(
        "http://ml-serve:8080/predictions/solar-park-detection",
        headers=headers,
        data=json_data,
    )
    logger.info(f"Got response from ml model: {req.status_code}")
    pred = np.array(req.json())
    mask = np.where(pred[0] < 0.5, 0, 1)
    if mask.sum() == 0:
        return {}
    else:
        print(f"Found prediction")
        return pred


def masks_to_polygons(masks: np.ndarray, metadata: dict) -> gpd.GeoDataFrame:
    masks = masks.astype(np.uint8)
    transform = metadata["transform"]
    crs = metadata["crs"]
    transformer = Transformer.from_crs(crs, "EPSG:4326", always_xy=True)
    # extract shapes
    shapes = rasterio.features.shapes(masks, transform=transform)
    # shapes = shapes.astype(np.uint8)
    polygons = []
    for shape in shapes:
        if shape[1] == 1:
            polygon = Polygon(shape[0]["coordinates"][0])
            area = polygon.area
            if area >= 5000:
                polygons.append(polygon)
    return polygons


# def masks_to_polygons(masks: np.ndarray, metadata: dict) -> gpd.GeoDataFrame:
#     masks = masks.astype(np.uint8)
#     transform = metadata["transform"]
#     crs = metadata["crs"]
#     transformer = Transformer.from_crs(crs, "EPSG:4326", always_xy=True)
#     # extract shapes
#     shapes = rasterio.features.shapes(masks, transform=transform)
#     #shapes = shapes.astype(np.uint8)
#     return [Polygon(shape[0]["coordinates"][0]) for shape in shapes if shape[1] == 1]


def write_to_db(polygon: str) -> bool:
    data = {
        "size_in_sq_m": polygon.area,
        "peak_power": 0,
        "date_of_data": "2023-05-20",
        "first_detection": "2023-05-20",
        "last_detection": "2023-05-20",
        "geometry": polygon.wkt,
    }
    url = "http://api:8000/api/v1/solarpark/"
    headers = {"Content-type": "application/json"}
    logger.info(f"Writing to DB: {data}")
    response = requests.post(url, headers=headers, json=data)
    return response.status_code


def save_patch(output_path: Path, metadata: dict, data_array: np.ndarray) -> bool:
    # ! add folder for masks and images
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # looks like the metadata is not correct or dytpe is not correct
    with rasterio.open(fp=output_path, mode="w", **metadata) as dst:
        dst.write(data_array.astype(rasterio.float32))

    # Optional: Upload to AWS
    # NOTE: Each upload is a request to AWS and only 2000 requests per month are free
    # therefore, this is commented out by default
    #
    # if aws_available:
    #
    #     result = upload_file_to_aws(
    #         input_file_path=output_path, output_path=output_path.name
    #     )
    #     if result:
    #         return True
    #     else:
    #         raise Exception("Upload to AWS failed")

    return True


def find_band_paths(image_dir: Path) -> Dict[str, Path]:
    """
    Find band files in the specified image directory.

    Args:
        image_dir (Path): The directory containing the band image files.

    Returns:
        Dict[str, Path]: A dictionary mapping band names to their corresponding file paths.

    Raises:
        Exception: If any of the required band files are missing.

    """
    band_paths: Dict[str, Path] = {band: Path() for band in REQUIRED_BANDS}

    # fill dict with paths
    for filename in os.listdir(image_dir):
        regex_match = re.match(FILENAME_REGEX, filename)

        if not regex_match:
            continue

        band_name = regex_match.group(1)
        if band_name in band_paths:
            band_paths[band_name] = image_dir / filename

    # Verify that all required bands have been found
    missing_bands = [
        band_name for band_name, file_path in band_paths.items() if file_path.is_dir()
    ]

    if missing_bands:
        raise Exception(f"Missing band files: {missing_bands}")

    return band_paths


def open_dataset_readers(
    band_paths: Dict[str, Path]
) -> Dict[str, rasterio.DatasetReader]:
    """
    Open dataset readers for each band in the specified image directory.

    Args:
        band_paths (Dict[str, Path]): A dictionary mapping band names to their corresponding file paths.

    Returns:
        Dict[str, rasterio.DatasetReader]: A dictionary mapping band names to their corresponding dataset readers.

    """
    # store open DatasetReaders in dict
    band_files: Dict[str, rasterio.DatasetReader] = {
        band_name: rasterio.open(file_path)
        for band_name, file_path in band_paths.items()
    }

    return band_files


def preprocess_bands(bands: Dict[str, np.ndarray]) -> np.ndarray:
    """
    Preprocess a dictionary of bands.

    Args:
        bands: A dictionary of bands, where the keys are band names and the values are numpy arrays.

    Returns:
        A numpy array of preprocessed bands.

    """
    # ToDo: add padding
    stacked_bands = stack_bands(bands)
    stacked_bands = color_correction(stacked_bands)
    stacked_bands = robust_normalize(stacked_bands)

    return stacked_bands.transpose(2, 0, 1)


def stack_bands(bands: Dict[str, rasterio.DatasetReader]) -> np.ndarray:
    """
    Stack the specified bands and return the resulting stacked bands array.
    NOTE: The order of the bands is specified to use for analysis in the notebook. (nir, red, green, blue)

    Args:
        bands (Dict[str, rasterio.DatasetReader]): A dictionary mapping band names to their corresponding dataset readers.

    Returns:
        np.ndarray: The stacked bands array, where each band is stacked along the third dimension.
    """
    return np.dstack(
        [np.float32(bands[b].read(1)) for b in ["B08", "B04", "B03", "B02"]]
    )


def color_correction(stacked_bands: np.ndarray) -> np.ndarray:
    """
    Perform color correction on the stacked bands array.

    Args:
        stacked_bands (np.ndarray): The stacked bands array.

    Returns:
        np.ndarray: The color-corrected stacked bands array.

    """
    return (stacked_bands / 8).astype(int)


def robust_normalize(
    band: np.ndarray, lower_bound: int = 1, upper_bound: int = 99
) -> np.ndarray:
    # get lower bound percentile
    percentile_lower_bound = np.percentile(band, lower_bound)
    # set all lower bound outliers to percentile_lower_bound value
    band[band < percentile_lower_bound] = percentile_lower_bound
    # get upper bound percentile
    percentile_upper_bound = np.percentile(band, upper_bound)
    # set all upper bound outliers to percentile_upper_bound value
    band[band > percentile_upper_bound] = percentile_upper_bound
    # normalize
    return (band - percentile_lower_bound) / (
        percentile_upper_bound - percentile_lower_bound
    )


def get_num_rows_cols_and_padding(
    metadata: Dict[str, Any], KERNEL_SIZE: int
) -> Tuple[int, int, int, int]:
    num_rows = metadata["height"] // KERNEL_SIZE
    num_cols = metadata["width"] // KERNEL_SIZE
    pad_rows = metadata["height"] % KERNEL_SIZE
    pad_cols = metadata["width"] % KERNEL_SIZE
    return num_rows, num_cols, pad_rows, pad_cols


def rasterize_mask(masks: gpd.GeoDataFrame, band: DatasetReader) -> np.ndarray:
    # create a raster which matches the image shape
    # invert=True masked pixels set to True (instead of the other way around)
    # all_touched=True all pixels within the mask set to True (instead of the bounds)
    return geometry_mask(
        geometries=masks.to_crs(band.crs),
        out_shape=band.shape,
        transform=band.transform,
        all_touched=True,
        invert=True,
    )


def filter_mask_on_tile(masks: gpd.GeoDataFrame, tile: str) -> gpd.GeoDataFrame:
    return masks[masks.tile_name == tile].geometry.reset_index(drop=True)


def padding_size(image_size: int, KERNEL_SIZE: int) -> int:
    """Computes the padding size, which is needed so that the kernel fits the
    image."""
    return int(((image_size // KERNEL_SIZE + 1) * KERNEL_SIZE - image_size) / 2)


def transform_to_patched_array(stacked_bands, num_rows, num_cols):
    # Calculate the shape of the padded array
    padded_shape = (
        stacked_bands.shape[0],
        (num_rows + 1) * KERNEL_SIZE,
        (num_cols + 1) * KERNEL_SIZE,
    )

    # Create a padded array
    padded_image = np.zeros(padded_shape, dtype=stacked_bands.dtype)
    padded_image[:, : stacked_bands.shape[1], : stacked_bands.shape[2]] = stacked_bands

    image_patched = padded_image.reshape(
        padded_image.shape[0],
        padded_image.shape[1] // KERNEL_SIZE,
        KERNEL_SIZE,
        padded_image.shape[1] // KERNEL_SIZE,
        KERNEL_SIZE,
    )

    return image_patched.transpose(1, 3, 0, 2, -1)
