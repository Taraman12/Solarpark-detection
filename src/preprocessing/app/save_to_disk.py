# build-in
import os
import re
from pathlib import Path
from typing import Any, Dict, Tuple, Union, Optional

# third-party
import geopandas as gpd
from geopandas import GeoDataFrame
import numpy as np
import rasterio
from rasterio import DatasetReader
from rasterio.features import geometry_mask
import boto3


# local modules
from constants import REQUIRED_BANDS
from aws_functions import aws_list_files, download_from_aws, upload_file_to_aws
from cloud_clients import aws_available

"""
ToDo: Add padding to the image/mask
ToDo: Needs better documentation
ToDo: handle memory consumption (but not so important)
"""

# Defining constants

# extracts tile, date, band and resolution from filename
FILENAME_REGEX = re.compile(
    r"""(?P<band>B0\d{1})(?:_
        (?P<resolution>\d{2}m))?\..*$""",
    re.VERBOSE,
)


def save_patched_data_to_disk(
    image_input_dir: Path,
    masks_gdf: GeoDataFrame,
    image_output_dir: Path,
    mask_output_dir: Path,
    tile: str,
    tile_date: str,
    kernel_size: int = 256,
    production: bool = True,
    deployed: bool = False,
) -> int:
    if aws_available:
        result = download_from_aws(image_input_dir, deployed=deployed)
        if not result:
            return 0

    # find paths to all REQUIRED_BANDS
    band_paths = find_band_paths(image_dir=image_input_dir)
    # open all REQUIRED_BANDS
    bands = open_dataset_readers(band_paths=band_paths)
    # bands = open_dataset_readers_as_dict(image_input_dir)

    stacked_bands = preprocess_bands(bands)

    # stacked_bands_tensor = torch.from_numpy(stacked_bands.transpose((2, 0, 1)))

    # image_tensor_pad = padding_tensor(stacked_bands_tensor, kernel_size)

    # image_tensor_patched = image_tensor_pad.reshape(
    #     image_tensor_pad.shape[0],
    #     image_tensor_pad.shape[1] // kernel_size,
    #     kernel_size,
    #     image_tensor_pad.shape[1] // kernel_size,
    #     kernel_size,
    # )
    # ! MASK #
    # masks_gdf = gpd.read_file(mask_input_dir)
    first_band = list(bands.keys())[0]
    # filter all masks to selected tile
    if production:
        masks = filter_mask_on_tile(masks_gdf, tile)

        if len(masks) == 0:
            return 0

        # create a raster which matches the image shape
        rasterized_mask = rasterize_mask(masks, bands[first_band])

    # convert to tensor to use efficient padding from torchvision
    # mask_tensor = torch.from_numpy(rasterized_mask)
    # image_tensor_patched = image_tensor_patched.swapaxes(-3, -2)

    metadata = bands[first_band].meta

    # Berechne die Anzahl der Reihen und Spalten für die Aufteilung
    num_rows = metadata["height"] // kernel_size
    num_cols = metadata["width"] // kernel_size

    # Berechne das Padding für die kleinen Bilder
    pad_rows = metadata["height"] % kernel_size
    pad_cols = metadata["width"] % kernel_size

    file_counter = 0
    file_identifier = 0
    # Iteriere über die Reihen und Spalten, um das Bild in kleine Bilder aufzuteilen
    for row in range(num_rows):
        for col in range(num_cols):
            # Definiere die Fensterkoordinaten für den Ausschnitt
            window = rasterio.windows.Window(
                col * kernel_size, row * kernel_size, kernel_size, kernel_size
            )

            # Schneide den Ausschnitt aus dem zusammengefügten Bild aus
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

            # Aktualisiere die Metadaten für das kleine Bild
            metadata["width"] = kernel_size
            metadata["height"] = kernel_size
            metadata["transform"] = rasterio.windows.transform(
                window, bands[list(bands.keys())[0]].transform
            )

            filename = f"{tile}_{file_identifier}_{tile_date}.tif"

            if production:
                # Extract the patch from the rasterized_mask
                mask_patch = rasterized_mask[
                    window.row_off : window.row_off + window.height,
                    window.col_off : window.col_off + window.width,
                ]
                if not mask_patch.sum() >= 200:
                    continue

                metadata["count"] = 1
                # Save the mask patch as GeoTIFF (similar to saving small_image)

                mask_output_path = mask_output_dir / filename
                # Assuming the metadata for the mask GeoTIFF is the same as the small_image GeoTIFF
                save_patch(
                    mask_output_path,
                    metadata,
                    np.expand_dims(mask_patch, axis=0),
                )
                # ToDo: delete the bigger image if production is false

            # Speichere das kleine Bild als GeoTIFF
            output_path = image_output_dir / filename
            metadata["count"] = 4
            metadata["driver"] = "GTiff"
            metadata["dtype"] = rasterio.float32
            if production:
                # send to ml-model
                pass
            save_patch(output_path, metadata, small_image.transpose(2, 0, 1))
    # add check if all images are saved

    return file_counter


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
    #     #
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

    return stacked_bands


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
    metadata: Dict[str, Any], kernel_size: int
) -> Tuple[int, int, int, int]:
    num_rows = metadata["height"] // kernel_size
    num_cols = metadata["width"] // kernel_size
    pad_rows = metadata["height"] % kernel_size
    pad_cols = metadata["width"] % kernel_size
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


def padding_size(image_size: int, kernel_size: int) -> int:
    """Computes the padding size, which is needed so that the kernel fits the image."""
    return int(((image_size // kernel_size + 1) * kernel_size - image_size) / 2)
