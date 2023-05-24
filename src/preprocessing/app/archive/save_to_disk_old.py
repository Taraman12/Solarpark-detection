# build-in
import os
import re
from pathlib import Path
from typing import Any, Dict, Tuple, Union

# third-party
import geopandas as gpd
import numpy as np
import rasterio

# local modules
from constants import BAND_FILE_MAP
from geopandas import GeoDataFrame
from rasterio import DatasetReader
from rasterio.features import geometry_mask

"""
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
) -> int:
    bands = open_dataset_readers_as_dict(image_input_dir)

    stacked_bands = stack_bands(bands)

    # Color correction
    stacked_bands = color_correction(stacked_bands)

    stacked_bands = robust_normalize(stacked_bands)

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

    # filter all masks to selected tile
    masks = filter_mask_on_tile(masks_gdf, tile)

    if len(masks) == 0:
        return 0

    # create a raster which matches the image shape
    rasterized_mask = rasterize_mask(masks, bands[list(bands.keys())[0]])

    # convert to tensor to use efficient padding from torchvision
    # mask_tensor = torch.from_numpy(rasterized_mask)
    # image_tensor_patched = image_tensor_patched.swapaxes(-3, -2)
    metadata = bands[list(bands.keys())[0]].meta
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

            # Extract the patch from the rasterized_mask
            mask_patch = rasterized_mask[
                window.row_off : window.row_off + window.height,
                window.col_off : window.col_off + window.width,
            ]
            if not mask_patch[row, col].sum() >= 200:
                continue
            # check if the image patch is not empty (all black)
            # https://gis.stackexchange.com/questions/380038/reasons-for-partial-tiles-in-sentinel
            if small_image[:, row, col].max() == 0:
                continue

            file_identifier += 1
            file_counter += 1

            # Aktualisiere die Metadaten für das kleine Bild
            metadata["width"] = kernel_size
            metadata["height"] = kernel_size
            metadata["transform"] = rasterio.windows.transform(
                window, bands[list(bands.keys())[0]].transform
            )
            metadata["count"] = 4

            filename = f"{tile}_{file_identifier}_{tile_date}.tif"
            # Speichere das kleine Bild als GeoTIFF
            output_path = image_output_dir / filename
            # print(small_image.shape)
            with rasterio.open(fp=output_path, mode="w", **metadata) as dst:
                dst.write(small_image.transpose(2, 0, 1))

            metadata["count"] = 1
            # Save the mask patch as GeoTIFF (similar to saving small_image)

            mask_output_path = mask_output_dir / filename
            # Assuming the metadata for the mask GeoTIFF is the same as the small_image GeoTIFF
            with rasterio.open(fp=mask_output_path, mode="w", **metadata) as mask_dst:
                mask_dst.write(np.expand_dims(mask_patch, axis=0))

    return file_counter

    # # ToDo: create a index which contains only patches with mask
    # # loop over this index instead of the whole array
    # mask_patched = convert_tensor_into_patches(mask_tensor, kernel_size, fill=False)

    # file_counter = 0

    # file_identifier = 0
    # # ToDo: find a better way for iterating
    # for i in range(image_tensor_patched.shape[1] - 1):
    #     for j in range(image_tensor_patched.shape[2] - 1):
    #         if mask_patched[i, j].sum() >= 200:
    #             # check if the image patch is not empty (all black)
    #             # https://gis.stackexchange.com/questions/380038/reasons-for-partial-tiles-in-sentinel
    #             if not image_tensor_patched[:, i, j].float().max() == 0:
    #                 file_identifier += 1
    #                 file_counter += 1
    #                 filename = f"{tile}_{file_identifier}_{tile_date}.pt"
    #                 torch.save(
    #                     image_tensor_patched[:, i, j].clone().float(),
    #                     os.path.join(image_output_dir, filename),
    #                 )
    #                 torch.save(
    #                     mask_patched[i, j].clone(),
    #                     os.path.join(mask_output_dir, filename),
    #                 )
    # return file_counter


def open_dataset_readers_as_dict(image_dir: Path) -> Dict[str, rasterio.DatasetReader]:
    """
    Open dataset readers for each band in the specified image directory.

    Args:
        image_dir (Path): The directory containing the band image files.

    Returns:
        Tuple[Dict[str, rasterio.DatasetReader], Union[str, Any]]: A tuple containing a dictionary mapping band names to
            their corresponding dataset readers, and a placeholder value (None in this case).

    Raises:
        Exception: If any of the required band files are missing.
    """
    # fill dict with paths
    for filename in os.listdir(image_dir):
        regex_match = re.match(FILENAME_REGEX, filename)

        if not regex_match:
            continue
        # ToDo: loop over items in BAND_FILE_MAP instead of keys
        for band_name in BAND_FILE_MAP.keys():
            if filename.endswith(f"{band_name}_10m.jp2"):
                BAND_FILE_MAP[band_name] = image_dir / filename
                break
    # Verify that all required bands have been found
    missing_bands = [
        band_name for band_name, file_path in BAND_FILE_MAP.items() if file_path is None
    ]

    if missing_bands:
        raise Exception(f"Missing band files: {missing_bands}")
    # store open DatasetReaders in dict
    return {
        band_name: rasterio.open(file_path)
        for band_name, file_path in BAND_FILE_MAP.items()
    }


def stack_bands(bands: Dict[str, rasterio.DatasetReader]) -> np.ndarray:
    """
    Stack the specified bands and return the resulting stacked bands array.

    Args:
        bands (Dict[str, rasterio.DatasetReader]): A dictionary mapping band names to their corresponding dataset readers.

    Returns:
        np.ndarray: The stacked bands array, where each band is stacked along the third dimension.
    """
    blue = np.float32(bands["B02"].read(1))
    green = np.float32(bands["B03"].read(1))
    red = np.float32(bands["B04"].read(1))
    nir = np.float32(bands["B08"].read(1))

    return np.dstack((nir, red, green, blue))


def color_correction(stacked_bands: np.ndarray) -> np.ndarray:
    """
    Perform color correction on the stacked bands array.

    Args:
        stacked_bands (np.ndarray): The stacked bands array.

    Returns:
        np.ndarray: The color-corrected stacked bands array.
    """
    stacked_bands = stacked_bands / 8
    return stacked_bands.astype(int)


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


def rasterize_mask(masks: gpd.GeoDataFrame, band: DatasetReader) -> np.ndarray:
    # convert crs
    masks = masks.to_crs(band.crs)
    # create a raster which matches the image shape
    # invert=True masked pixels set to True (instead of the other way around)
    # all_touched=True all pixels within the mask set to True (instead of the bounds)
    return geometry_mask(
        masks,
        out_shape=band.shape,
        transform=band.transform,
        invert=True,
        all_touched=True,
    )


def filter_mask_on_tile(masks: gpd.GeoDataFrame, tile: str) -> gpd.GeoDataFrame:
    return masks[masks.tile_name == tile].geometry.reset_index(drop=True)


# def padding_tensor(tensor: Tensor, kernel_size: int, fill: int = 0) -> Tensor:
#     # computes the padding size
#     padding = padding_size(tensor.shape[1], kernel_size)
#     # Use PyTorch's Pad function to add padding with the fill value
#     return Pad(padding, fill=fill)(tensor)


# def convert_tensor_into_patches(
#     tensor: Tensor, kernel_size: int, fill: int = 0
# ) -> Tensor:
#     padding = padding_size(tensor.shape[1], kernel_size)
#     tensor_pad = Pad(padding, fill=fill)(tensor)
#     tensor_patched = tensor_pad.reshape(
#         tensor_pad.shape[1] // kernel_size,
#         kernel_size,
#         tensor_pad.shape[1] // kernel_size,
#         kernel_size,
#     )
#     return tensor_patched.swapaxes(-3, -2)


def padding_size(image_size: int, kernel_size: int) -> int:
    """Computes the padding size, which is needed so that the kernel fits the image."""
    return int(((image_size // kernel_size + 1) * kernel_size - image_size) / 2)
