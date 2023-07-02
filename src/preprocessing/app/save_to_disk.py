# build-in
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# third-party
import geopandas as gpd
import numpy as np
import rasterio
import rasterio.features
import requests

# local modules
from aws_functions import delete_folder_on_aws, download_from_aws, upload_file_to_aws
from cloud_clients import aws_available
from constants import (
    HEADERS,
    IDENTIFIER_REGEX,
    IMAGE_INPUT_DIR,
    IMAGE_OUTPUT_DIR,
    IMAGES_WITH_SOLARPARK,
    KERNEL_SIZE,
    MASK_OUTPUT_DIR,
    MODEL_NAME,
    PADDING,
    REQUIRED_BANDS,
    UNDERSAMPLING_RATE,
    URL_API,
    URL_ML,
)
from geopandas import GeoDataFrame
from logging_config import get_logger

# from rasterio import DatasetReader
from rasterio.features import geometry_mask
from rasterio.warp import transform_geom
from rasterio.windows import Window
from settings import MAKE_TRAININGS_DATA, PRODUCTION
from shapely.geometry import Polygon

logger = get_logger("BaseConfig")

"""
ToDo: Add padding to the image/mask
ToDo: Needs better documentation
ToDo: handle memory consumption (but not so important)
"""


# extracts tile, date, band and resolution from filename
# ! Adjust to TCI band
FILENAME_REGEX = re.compile(
    r"""(?P<band>.{3})(?:_
        (?P<resolution>\d{2}m))?\..*$""",
    re.VERBOSE,
)


def preprocess_and_save_data(  # noqa: C901
    tile_folder_path: str,
    masks_gdf: GeoDataFrame,
) -> int:
    # remove trailing slash
    tile_folder_path = tile_folder_path.strip("/")

    # get tile and date from folder name
    tile, tile_date = get_tile_and_date(tile_folder_path)

    # get identifier from folder name
    identifier = tile_folder_path.split("/")[-1]

    if tile is None or tile_date is None:
        return 0

    if aws_available and PRODUCTION:
        result = download_from_aws(tile_folder_path)
        if not result:
            return 0

    # find paths to all REQUIRED_BANDS
    band_paths = find_band_paths(image_dir=IMAGE_INPUT_DIR / identifier)
    logger.debug(f"Found {len(band_paths)} bands for {identifier}")

    # Loop over the patches

    bands = open_dataset_readers(band_paths=band_paths)

    logger.debug(f"Opened {len(bands)} bands for {identifier}")

    first_band = list(bands.keys())[0]
    metadata = bands[first_band].meta
    height = metadata["height"]
    width = metadata["width"]

    file_counter = 0
    file_identifier = 0
    # Initialize the counter
    mask_counter = 0

    for row in range(-PADDING, height + PADDING, KERNEL_SIZE):
        for col in range(-PADDING, width + PADDING, KERNEL_SIZE):
            file_identifier += 1
            filename = f"{tile}_{file_identifier}_{tile_date}.tif"
            # open all bands from REQUIRED_BANDS
            window = rasterio.windows.Window(col, row, KERNEL_SIZE, KERNEL_SIZE)

            stacked_bands = preprocess_bands(bands, window)
            if stacked_bands.max() == 0:
                continue
            # ! probably not needed anymore
            stacked_bands = pad_array(stacked_bands)

            logger.debug(f"Preprocessed {len(bands)} bands for {identifier}")

            metadata.update(
                {
                    "width": window.width,
                    "height": window.height,
                    "transform": bands[first_band].window_transform(window),
                }
            )

            if MAKE_TRAININGS_DATA:
                masks = filter_mask_on_tile(masks_gdf, tile)

                # create a raster which matches the image shape
                rasterized_mask = rasterize_mask(masks, metadata)

                # checks if the image patch contains a solar park
                # if yes, save the image patch
                # if not, save the image patch without solarpark with a rate of 1/UNDERSAMPLING_RATE
                if not rasterized_mask.sum() >= 100:
                    mask_counter += 1
                    if mask_counter % (1 / UNDERSAMPLING_RATE) != 0:
                        continue

                data_saved = trainings_data_handler(
                    stacked_bands.transpose(2, 0, 1),
                    metadata,
                    filename,
                    rasterized_mask,
                    window,
                )
                file_counter += data_saved

            if PRODUCTION:
                prediction_handler(
                    stacked_bands.transpose(2, 0, 1), metadata, tile_date, filename
                )
                continue

    # delete the bigger image on aws
    if PRODUCTION:
        delete_folder_on_aws(folder_path=identifier)

    return file_counter


def trainings_data_handler(
    small_image: np.ndarray,
    metadata: dict,
    filename: str,
    rasterized_mask: np.array,
    window: rasterio.windows.Window,
) -> int:
    # Extract the patch from the rasterized_mask
    # mask_patch = rasterized_mask[
    #     window.row_off : window.row_off + window.height,
    #     window.col_off : window.col_off + window.width,
    # ]
    # if not rasterized_mask.sum() >= 100:
    #     return 0

    metadata["count"] = 1
    metadata["dtype"] = rasterio.uint8

    mask_output_path = MASK_OUTPUT_DIR / filename
    # Assuming the metadata for the mask GeoTIFF is the same as the small_image GeoTIFF
    save_patch(
        mask_output_path,
        metadata,
        np.expand_dims(rasterized_mask, axis=0),
    )
    # store small images as GeoTIFF
    metadata["count"] = 4
    metadata["dtype"] = rasterio.float32
    output_path = IMAGE_OUTPUT_DIR / filename
    save_patch(output_path, metadata, small_image)
    save_for_upload(output_path,metadata, small_image)
    return 1


def prediction_handler(
    data: np.ndarray,
    metadata: dict,
    tile_date: str,
    filename: str,
) -> None:
    prediction = send_to_ml_model(data, metadata)

    if len(prediction) == 0:
        return None

    polygons, areas = masks_to_polygons(prediction, metadata)
    # got changed in masks_to_polygons
    # metadata["crs"] = "EPSG:4326"
    logger.info(f"Found {len(polygons)} polygons")

    for polygon, area in zip(polygons, areas):
        if write_to_db(polygon, area=area, tile_date=tile_date, filename=filename):
            logger.info("Polygon written to DB")

        if upload_geotiff_handler(data[1:4], metadata, filename):
            logger.info("Image uploaded to AWS")

    return None


def save_for_upload(output_path: Path, metadata: dict, data: np.ndarray) -> bool:
    data = np.round(data * 255).astype(np.uint8)
    metadata["driver"] = "GTiff"
    metadata["dtype"] = rasterio.uint8
    metadata["count"] = 3
    output_upload_path = output_path.parent.joinpath('upload', output_path.name)
    output_upload_path.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(fp=output_upload_path, mode="w", **metadata) as dst:
        dst.write(data[1:4])

    return True

def upload_geotiff_handler(data: np.ndarray, metadata: dict, filename: str) -> bool:
    # FIXME: upload to aws doesn't find the path in windows
    metadata["driver"] = "GTiff"
    metadata["dtype"] = rasterio.uint8
    metadata["count"] = 3
    data = np.round(data * 255).astype(np.uint8)
    with rasterio.open(fp=filename, mode="w", **metadata) as dst:
        dst.write(data)

    if upload_file_to_aws(filename, prefix=IMAGES_WITH_SOLARPARK, output_path=filename):
        logger.info("Image uploaded to AWS")
    # delete the file from local storage
    os.remove(filename)


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
    json_data = json.dumps(data_array.tolist())
    req = requests.post(
        f"{URL_ML}/predictions/{MODEL_NAME}",
        headers=HEADERS,
        data=json_data,
    )
    logger.debug(f"Got response from ml model: {req.status_code}")
    pred = np.array(req.json())
    mask = np.where(pred[0] < 0.5, 0, 1)
    if mask.sum() == 0:
        return {}
    else:
        logger.debug("Found prediction")
        return pred


def masks_to_polygons(
    masks: np.ndarray, metadata: dict
) -> Tuple[List[Polygon], List[float]]:
    masks = masks.astype(np.uint8)
    transform = metadata["transform"]
    crs = metadata["crs"]
    # extract shapes
    shapes = rasterio.features.shapes(masks, transform=transform)
    polygons = []
    areas = []
    for shape in shapes:
        if shape[1] == 1:
            polygon = Polygon(shape[0]["coordinates"][0])
            area = polygon.area
            # realistically, the smallest solar park should be bigger than 10.000 m²
            if area >= 5000:
                # Transform the polygon coordinates to EPSG:4326
                transformed_geom = transform_geom(
                    crs, "EPSG:4326", polygon.__geo_interface__
                )
                transformed_coords = transformed_geom["coordinates"][0]
                transformed_polygon = Polygon(transformed_coords)
                polygons.append(transformed_polygon)
                areas.append(area)
    return polygons, areas


# def masks_to_polygons(masks: np.ndarray, metadata: dict) -> gpd.GeoDataFrame:
#     masks = masks.astype(np.uint8)
#     transform = metadata["transform"]
#     crs = metadata["crs"]
#     transformer = Transformer.from_crs(crs, "EPSG:4326", always_xy=True)
#     # extract shapes
#     shapes = rasterio.features.shapes(masks, transform=transform)
#     #shapes = shapes.astype(np.uint8)
#     return [Polygon(shape[0]["coordinates"][0]) for shape in shapes if shape[1] == 1]


def write_to_db(polygon: Polygon, area, tile_date: str, filename: str) -> bool:
    tile_date = to_datetime_str(tile_date)
    lat, lon = extract_polygon_coordinates(polygon)
    # tile_date = datetime.strptime(tile_date, "%Y-%m-%d").date()
    data = {
        "name_of_model": MODEL_NAME,
        "size_in_sq_m": area,
        "peak_power": calc_peak_power(area_in_sq_m=area),
        "date_of_data": tile_date,
        "first_detection": tile_date,  # will be handled on api level
        "last_detection": tile_date,  # will be handled on api level
        "avg_confidence": 0,
        "name_in_aws": filename,
        "is_valid": "None",
        "comment": "None",
        "lat": lat,
        "lon": lon,
    }
    url = f"{URL_API}/solarpark/"
    logger.debug(f"Writing to DB: {data}")
    try:
        response = requests.post(url, headers=HEADERS, json=data)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Could not write to DB: {e}")
        raise e


def to_datetime_str(date_string: str) -> str:
    # formats the date string to a real datetime string
    # tile_date does not have a leading zeros due to previous constraints
    # therefore we need to add them
    # but the output must be a string again
    date_obj = datetime.strptime(date_string, "%Y-%m-%d").date()
    return date_obj.strftime("%Y-%m-%d")


# def calculate_polygon_area(polygon: Polygon) -> float:
#     # Transform the polygon to a local projection (e.g. UTM) to get a more accurate area calculation
#     transformer = Transformer.from_crs("EPSG:4326", "EPSG:32632")
#     projected_polygon = Polygon(transformer.transform(*polygon.exterior.xy))
#     # Calculate the area of the projected polygon in square meters
#     area = projected_polygon.area
#     return area


def calc_peak_power(area_in_sq_m: float) -> float:
    # https://www.bundesnetzagentur.de/SharedDocs/Downloads/DE/Sachgebiete/Energie/Unternehmen_Institutionen/ErneuerbareEnergien/PV-Freiflaechenanlagen/Bericht_Flaecheninanspruchnahme_2016.pdf?__blob=publicationFile&v=2#:~:text=Die%20bereits%20im%20Rahmen%20der,Ackerland%20in%20benachteiligten%20Gebieten%20errichtet. # noqa
    # page 8 on the pdf (german)
    # 1,6 acre = 1 MWp
    # area in sq m / 10000 = area in acr * 1.6 = peak power in MWp
    return area_in_sq_m / 10000 * 1.6


def extract_polygon_coordinates(polygon: Polygon) -> Tuple[List[float], List[float]]:
    """
    Extracts the latitude and longitude coordinates of the exterior ring of a polygon.

    Args:
        polygon (Polygon): The polygon to extract coordinates from.

    Returns:
        Tuple[List[float], List[float]]: A tuple containing two lists: the latitude coordinates and the longitude coordinates.
    """
    # Extract the coordinates of the exterior ring of the polygon
    coords = polygon.exterior.coords

    # Extract the latitude and longitude coordinates into separate lists
    latitudes = [coord[1] for coord in coords]
    longitudes = [coord[0] for coord in coords]

    return latitudes, longitudes


def save_patch(output_path: Path, metadata: dict, data: np.ndarray) -> bool:
    metadata["driver"] = "GTiff"
    # ! add folder for masks and images
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # looks like the metadata is not correct or dytpe is not correct
    with rasterio.open(fp=output_path, mode="w", **metadata) as dst:
        dst.write(data)  # .astype(rasterio.float32)

    return True


def find_band_paths(image_dir: Path) -> Dict[str, Path]:
    """Find band files in the specified image directory.

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
    """Open dataset readers for each band in the specified image directory.

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


def preprocess_bands(bands: Dict[str, np.ndarray], window: Window) -> np.ndarray:
    """Preprocess a dictionary of bands.

    Args:
        bands: A dictionary of bands, where the keys are band names and the values are numpy arrays.

    Returns:
        A numpy array of preprocessed bands.
    """
    # ToDo: add padding
    stacked_bands = stack_bands(bands, window)
    if np.any(np.array(stacked_bands.shape) == 0):
        return np.zeros(1)
    if stacked_bands.max() == 0:
        return np.zeros(1)
    logger.debug(f"Stacked bands shape: {stacked_bands.shape}")
    stacked_bands = color_correction(stacked_bands)
    logger.debug(f"Color corrected bands shape: {stacked_bands.shape}")
    stacked_bands = robust_normalize(stacked_bands)
    # ToDo: check data type
    logger.debug(f"Normalized bands shape: {stacked_bands.shape}")
    return stacked_bands


def stack_bands(bands: Dict[str, rasterio.DatasetReader], window: Window) -> np.ndarray:
    """
    Stack the specified bands and return the resulting stacked bands array.
    NOTE: The order of the bands is specified to use for analysis in the notebook. (nir, red, green, blue)

    Args:
        bands (Dict[str, rasterio.DatasetReader]): A dictionary mapping band names to their corresponding dataset readers.

    Returns:
        np.ndarray: The stacked bands array, where each band is stacked along the third dimension.
    """
    return np.dstack(
        # ToDo: try np.int16 instead of int
        [
            bands[b].read(1, window=window).astype(int)
            for b in ["B08", "B04", "B03", "B02"]
        ]
    )


def color_correction(stacked_bands: np.ndarray) -> np.ndarray:
    """Perform color correction on the stacked bands array.

    Args:
        stacked_bands (np.ndarray): The stacked bands array.

    Returns:
        np.ndarray: The color-corrected stacked bands array.
    """
    # ToDo: try np.int16 instead of int
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
    # avoid division by zero
    if (percentile_upper_bound - percentile_lower_bound) == 0:
        return band
    # normalize
    return (band - percentile_lower_bound) / (
        percentile_upper_bound - percentile_lower_bound
    )


def pad_array(array: np.ndarray) -> np.ndarray:
    # Define the desired size of the array
    desired_size = (KERNEL_SIZE, KERNEL_SIZE)
    # Get the current size of the array
    current_size = array.shape[:2]
    # Calculate the amount of padding needed
    padding = (
        (0, desired_size[0] - current_size[0]),
        (0, desired_size[1] - current_size[1]),
        (0, 0),
    )
    # Pad the array with zeros
    return np.pad(array, padding, mode="constant")


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


def filter_mask_on_tile(masks: gpd.GeoDataFrame, tile: str) -> gpd.GeoDataFrame:
    return masks[masks.tile_name == tile].geometry.reset_index(drop=True)


# ------------ OLD CODE BELOW ------------
def padding_size(image_size: int, KERNEL_SIZE: int) -> int:
    """Computes the padding size, which is needed so that the kernel fits the
    image."""
    return int(((image_size // KERNEL_SIZE + 1) * KERNEL_SIZE - image_size) / 2)


def transform_to_patched_array(stacked_bands, num_rows, num_cols):
    stacked_bands = stacked_bands.transpose(2, 0, 1)
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


def get_num_rows_cols_and_padding(
    metadata: Dict[str, Any], KERNEL_SIZE: int
) -> Tuple[int, int, int, int]:
    num_rows = metadata["height"] // KERNEL_SIZE
    num_cols = metadata["width"] // KERNEL_SIZE
    pad_rows = metadata["height"] % KERNEL_SIZE
    pad_cols = metadata["width"] % KERNEL_SIZE
    return num_rows, num_cols, pad_rows, pad_cols
