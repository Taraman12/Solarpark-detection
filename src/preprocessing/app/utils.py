from distutils.util import strtobool
from pathlib import Path
from typing import List

import geopandas as gpd
from geopandas import GeoDataFrame
from logging_config import get_logger
from settings import DOCKERIZED

logger = get_logger("BaseConfig")


def create_output_directories(output_dirs: List[Path]) -> None:
    """Creates the output directories if they do not exist.

    Args:
        output_dirs (List[Path]): A list of output directories to create.
        logger: A logger instance to use for logging.
    """
    for output_dir in output_dirs:
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=False)
            logger.info(
                f"Output path: {output_dir} does not exist \n" f"Directory created"
            )


def load_tiles_file(path: Path) -> GeoDataFrame:
    """Load a GeoDataFrame from a GeoJSON file.

    Parameters
    ----------
    path : Path
        The path to the GeoJSON file.

    Returns
    -------
    tiles_file : GeoDataFrame
        The GeoDataFrame loaded from the GeoJSON file.

    Raises
    ------
    SystemExit
        If the GeoDataFrame loaded from the GeoJSON file is empty.
    """
    if not path.exists():
        logger.error(f"Could not find {path}")
        exit()

    tiles_file = gpd.read_file(path)

    if len(tiles_file) == 0:
        logger.error(f"Could not read {path.name} or empty file")
        exit()

    return tiles_file


def create_download_path(path: Path) -> bool:
    """
    Creates download path if it does not exist
    Args:
        path (pathlib.Path): path to download data to

    Returns:
        bool: True if path was created, False if not
    """
    if DOCKERIZED:
        logger.info("Dockerized, input paths will be auto created")
        return True

    if not path.exists():
        logger.warning(
            f"The download path: {path} does not exist. \n"
            f" Do you want to create it? [Y/n] (no will exiting program)"
        )
        user_input = input()

        try:
            user_input_bool = bool(strtobool(user_input))
        except ValueError:
            logger.info("Invalid input. Please use Y/n")
            return False

        if user_input_bool:
            path.mkdir(parents=True, exist_ok=False)
            logger.info("path created")
            return True
        else:
            logger.error("path not created, exiting program")
            exit()

    else:
        return True


# def open_dataset_readers(
#     band_file_info: Dict[str, Dict[str, Union[str, Path]]]
# ) -> Dict[str, rasterio.DatasetReader]:
#     """Open dataset readers for each band in the specified image directory.

#     Args:
#         band_file_info (Dict[str, Dict[str, Union[str, Path]]]): A dictionary mapping each band to a dictionary containing:
#             - 'resolution' (str): The resolution of the band.
#             - 'file_path' (Path): The local file path to the band file.

#     Returns:
#         Dict[str, rasterio.DatasetReader]: A dictionary mapping band names to their corresponding dataset readers.
#     """
#     # store open DatasetReaders in dict
#     band_files: Dict[str, rasterio.DatasetReader] = {
#         band_name: rasterio.open(file_info["file_path"])
#         for band_name, file_info in band_file_info.items()
#     }

#     return band_files


# def stack_bands(
#     bands: Dict[str, rasterio.DatasetReader], window: Window | None = None
# ) -> np.ndarray:
#     """
#     Stack the specified bands and return the resulting stacked bands array.
#     NOTE: The order of the bands is specified to use for analysis in the notebook. (nir, red, green, blue)

#     Args:
#         bands (Dict[str, rasterio.DatasetReader]): A dictionary mapping band names to their corresponding dataset readers.

#     Returns:
#         np.ndarray: The stacked bands array, where each band is stacked along the third dimension.
#     """
#     return np.dstack(
#         # ToDo: try np.int16 instead of int
#         [
#             bands[b].read(1, window=window).astype(int)
#             for b in ["B08", "B04", "B03", "B02"]
#         ]
#     )
