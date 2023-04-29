# build-in
import os
import re
from pathlib import Path
from typing import Any, Dict, Tuple, Union

# third-party
import geopandas as gpd
import numpy as np
import rasterio
from rasterio.features import geometry_mask
import torch
from rasterio import DatasetReader
from torch import Tensor
from torchvision.transforms import Pad

# local modules
import constants as c

"""
ToDo: Needs better documentation
ToDo: handle memory consumption (but not so important)
"""
# Defining constants

# dict to store filenames with bands as keys
BAND_FILE_MAP = dict(
    B02=None,  # blue
    B03=None,  # green
    B04=None,  # red
    B08=None,  # NIR
)

# extracts tile, date, band and resolution from filename
FILENAME_REGEX = re.compile(
    r"""(?P<band>B0\d{1})(?:_
                            (?P<resolution>\d{2}m))?\..*$""",
    re.VERBOSE,
)


def save_patched_data_to_disk(
    image_input_dir,
    masks_gdf,
    image_output_dir,
    mask_output_dir,
    kernel_size,
    tile,
    tile_date,
):
    bands = open_DatasetReaders_as_dict(image_input_dir)

    blue = np.float32(bands["B02"].read(1))
    green = np.float32(bands["B03"].read(1))
    red = np.float32(bands["B04"].read(1))
    nir = np.float32(bands["B08"].read(1))

    # consumes a lot of memory
    blue = robust_normalize(blue)
    green = robust_normalize(green)
    red = robust_normalize(red)
    nir = robust_normalize(nir)

    # consumes a lot of additional memory
    stacked_bands = np.dstack((nir, red, green, blue))

    stacked_bands_tensor = torch.from_numpy(stacked_bands.transpose((2, 0, 1)))

    image_tensor_pad = padding_tensor(stacked_bands_tensor, kernel_size)

    image_tensor_patched = image_tensor_pad.reshape(
        image_tensor_pad.shape[0],
        image_tensor_pad.shape[1] // kernel_size,
        kernel_size,
        image_tensor_pad.shape[1] // kernel_size,
        kernel_size,
    )

    image_tensor_patched = image_tensor_patched.swapaxes(-3, -2)

    # ! MASK #
    # masks_gdf = gpd.read_file(mask_input_dir)

    # filter all masks to selected tile
    masks = filter_mask_on_tile(masks_gdf, tile)

    if len(masks) == 0:
        return 0

    # create a raster which matches the image shape
    rasterized_mask = rasterize_mask(masks, bands[list(bands.keys())[0]])

    # convert to tensor to use efficient padding from torchvision
    mask_tensor = torch.from_numpy(rasterized_mask)

    # ToDo: create a index which contains only patches with mask
    # loop over this index instead of the whole array
    mask_patched = convert_tensor_into_patches(mask_tensor, kernel_size, fill=False)

    file_counter = 0

    file_identifier = 0
    # ToDo: find a better way for iterating
    for i in range(image_tensor_patched.shape[1] - 1):
        for j in range(image_tensor_patched.shape[2] - 1):
            if mask_patched[i, j].sum() != 0:
                file_counter += 1
                file_identifier += 1
                filename = f"{tile}_{file_identifier}_{tile_date}.pt"
                torch.save(
                    image_tensor_patched[:, i, j].clone().float(),
                    os.path.join(image_output_dir, filename),
                )
                torch.save(
                    mask_patched[i, j].clone(),
                    os.path.join(mask_output_dir, filename),
                )
    return file_counter


def open_DatasetReaders_as_dict(
    image_dir: str,
) -> Tuple[Dict[str, Any], Union[str, Any]]:
    # fill dict with paths
    for filename in os.listdir(image_dir):
        regex_match = re.match(FILENAME_REGEX, filename)
        if regex_match:
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
    # dataset_readers = {}
    # for band_name, file_path in BAND_FILE_MAP.items():
    #     dataset_readers[band_name] = rasterio.open(file_path)

    # return dataset_readers, tile


def robust_normalize(band, lower_bound=1, upper_bound=99):
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
    # all_touched=True all pixels within the mask set to True (instead the bounds)
    return geometry_mask(
        masks,
        out_shape=band.shape,
        transform=band.transform,
        invert=True,
        all_touched=True,
    )


def filter_mask_on_tile(masks: gpd.GeoDataFrame, tile: str) -> gpd.GeoDataFrame:
    return masks[masks.tile_name == tile].geometry.reset_index(drop=True)


def padding_tensor(tensor: Tensor, kernel_size: int, fill=0) -> Tensor:
    # computes the padding size
    padding = padding_size(tensor.shape[1], kernel_size)
    # Use PyTorch's Pad function to add padding with the fill value
    return Pad(padding, fill=fill)(tensor)


def convert_tensor_into_patches(tensor: Tensor, kernel_size: int, fill=0) -> Tensor:
    padding = padding_size(tensor.shape[1], kernel_size)
    tensor_pad = Pad(padding, fill=fill)(tensor)
    tensor_patched = tensor_pad.reshape(
        tensor_pad.shape[1] // kernel_size,
        kernel_size,
        tensor_pad.shape[1] // kernel_size,
        kernel_size,
    )
    return tensor_patched.swapaxes(-3, -2)


def padding_size(image_size: int, kernel_size: int) -> int:
    """Computes the padding size, which is needed so that the kernel fits the image."""
    return int(((image_size // kernel_size + 1) * kernel_size - image_size) / 2)


# if __name__ == "__main__":
#     print("Program started")
#     root_dir = Path(__file__).resolve().parent.parent
#     # os.chdir(Path(__file__).parent)
#     print(os.getcwd())
#     # rename
#     image_input_dir = c.IMAGE_INPUT_DIR
#     mask_input_dir = c.MASK_INPUT_DIR  # root_dir
#     image_output_dir = c.IMAGE_OUTPUT_DIR
#     mask_output_dir = c.MASK_OUTPUT_DIR

#     for input_directory in [image_input_dir, mask_input_dir]:
#         if not input_directory.exists():
#             print(f"Input path: {input_directory} does not exist")

#     for output_directory in [image_output_dir, mask_output_dir]:
#         if not output_directory.exists():
#             output_directory.mkdir(parents=True, exist_ok=False)
#             print(
#                 f"Output path: {output_directory} does not exist \n"
#                 f"Directory created"
#             )

#     kernel_size = 256
#     # ToDo: add loop over all folders in image_dir (it is only a single one)
#     # open mask_gdf outside the loop
#     for tile_folder in os.listdir(image_input_dir):
#         # ! changed to match instead of search
#         regex_match = re.match(c.IDENTIFIER_REGEX, tile_folder)

#         if not regex_match:
#             continue

#         else:
#             # mission = regex_match.group("mission")
#             utm_code = regex_match.group("utm_code")
#             product_level = regex_match.group("product_level").lower()
#             latitude_band = regex_match.group("latitude_band")
#             square = regex_match.group("square")
#             year = regex_match.group("year")
#             month = str(int(regex_match.group("month")))
#             day = str(int(regex_match.group("day")))
#             tile = f"{latitude_band}{square}"

#         image_input_dir = image_input_dir / tile_folder
#         result = save_patched_data_to_disk(
#             image_input_dir,
#             mask_input_dir,
#             image_output_dir,
#             mask_output_dir,
#             kernel_size,
#             tile=tile,
#             tile_date=f"{year}-{month}-{day}",
#         )
#         print(f"Number of files saved: {result}")
#     print("program finished")
