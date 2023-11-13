from pathlib import Path
from typing import Dict, Tuple, Union

import numpy as np
import rasterio
from rasterio.io import DatasetReader
from rasterio.windows import Window


# ! Return changed
def open_data_handler(
    band_file_info: Dict[str, Dict[str, Union[str, Path]]]
) -> (
    Tuple[np.ndarray, Dict[str, DatasetReader], Dict[str, Union[str, int, float]]]
    | Tuple[None, None, Dict[str, Union[str, int, float]]]
):
    """
    Handles the opening of datasets and stacking of bands.

    Args:
    band_file_info (Dict[str, Dict[str, Union[str, Path]]]): A dictionary mapping each band to a dictionary containing:
        - 'resolution' (str): The resolution of the band.
        - 'file_path' (Path): The local file path to the band file.

    Returns:
    tuple: A tuple containing the stacked bands as a numpy array, first open Dataset Readers and the metadata of the first band.
    """
    bands = open_dataset_readers(band_file_info)

    first_band = list(bands.keys())[0]
    original_metadata = bands[first_band].meta
    stacked_bands = stack_bands(bands)
    # check if the dimensions of the stacked bands are valid
    if np.any(np.array(stacked_bands.shape) == 0):
        return None, None, original_metadata
    # check if all bands are empty
    if stacked_bands.max() == 0:
        return None, None, original_metadata
    return stacked_bands, bands[first_band], original_metadata


def open_dataset_readers(
    band_file_info: Dict[str, Dict[str, Union[str, Path]]]
) -> Dict[str, rasterio.DatasetReader]:
    """
    Open dataset readers for each band in the specified image directory.

    Args:
        band_file_info (Dict[str, Dict[str, Union[str, Path]]]): A dictionary mapping each band to a dictionary containing:
            - 'resolution' (str): The resolution of the band.
            - 'file_path' (Path): The local file path to the band file.

    Returns:
        Dict[str, rasterio.DatasetReader]: A dictionary mapping band names to their corresponding dataset readers.
    """
    # store open DatasetReaders in dict
    band_files: Dict[str, rasterio.DatasetReader] = {
        band_name: rasterio.open(file_info["file_path"])
        for band_name, file_info in band_file_info.items()
    }

    return band_files


def stack_bands(
    bands: Dict[str, rasterio.DatasetReader], window: Window | None = None
) -> np.ndarray:
    """
    Stack the specified bands and return the resulting stacked bands array.
    NOTE: The order of the bands is specified to use for analysis in the notebook. (nir, red, green, blue)

    Args:
        bands (Dict[str, rasterio.DatasetReader]): A dictionary mapping band names to their corresponding dataset readers.

    Returns:
        np.ndarray: The stacked bands array, where each band is stacked along the third dimension.
    """
    return np.dstack(
        [
            bands[b].read(1, window=window)
            for b in bands.keys()  # ["B08", "B04", "B03", "B02"]
        ]
    )
