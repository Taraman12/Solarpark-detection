from typing import Optional, Tuple

import numpy as np
from rasterio.windows import Window

from app.constants import KERNEL_SIZE  # , STEP_SIZE, USED_BANDS


def preprocess_handler(
    array: np.ndarray, window: Optional[Window] = None, training: bool = False
) -> np.ndarray | None:
    """Handles the preprocessing of the array.

    Args:
        array (np.ndarray): The array to preprocess (w, h, dim). Expected dtype is uint16 and shape is (w, h, dim).
        window (Window): The window to extract.

    Returns:
        np.ndarray: The preprocessed array. Returned dtype is float64 and shape is (w, h, dim).
    """
    if not isinstance(array, np.ndarray):
        raise ValueError("Array must be a numpy array")

    if not training:
        if not isinstance(window, Window):
            raise ValueError("Window must be a rasterio window")

    if not training:
        small_image = moving_window(array, window)
    else:
        small_image = array

    if np.any(np.array(small_image.shape) == 0):
        return None

    if small_image.max() == 0:
        return None

    # small_image = color_correction(small_image)
    small_image = robust_normalize(small_image)

    # if small_image.shape[0] != len(USED_BANDS):
    #     small_image = small_image.transpose(2, 0, 1)

    return small_image


def moving_window(
    stacked_array: np.ndarray,
    window: Window,
) -> Tuple[np.ndarray, Window]:
    """Extracts moving windows from an stacked_array.

    Args:
        stacked_array (np.ndarray): The stacked_array to extract windows from.
        window (Window): The window to extract.

    Returns:
        np.ndarray: The extracted windows.
    """
    if not isinstance(stacked_array, np.ndarray):
        raise ValueError("Stacked array must be a numpy array")
    if not isinstance(window, Window):
        raise ValueError("Window must be a rasterio window")

    # Cut out the snippet from the merged stacked_array
    return stacked_array[
        window.row_off : window.row_off + window.height,
        window.col_off : window.col_off + window.width,
    ]


# ! Doesn't work correctly
def pad_image(image: np.array, kernel_size: int = KERNEL_SIZE) -> np.array:
    """
    Pads an image so that windows of the given kernel size and step size cover the entire image.

    Args:
    image (np.array): The image to pad. (h, w, dim)
    kernel_size (int): The size of the kernel.
    step_size (int): The size of the step.

    Returns:
    np.array: The padded image.
    """
    if not isinstance(image, np.ndarray):
        raise ValueError("Image must be a numpy array")
    if not isinstance(kernel_size, int):
        raise ValueError("Kernel size must be an integer")
    if not kernel_size > 0:
        raise ValueError("Kernel size must be greater than 0")

    height, width, _ = image.shape

    pad_height = kernel_size - height if height < kernel_size else 0
    pad_width = kernel_size - width if width < kernel_size else 0

    return np.pad(
        image,
        ((0, pad_height), (0, pad_width), (0, 0)),
        mode="constant",
        constant_values=0,
    )


# def preprocess_bands(bands: Dict[str, np.ndarray], window: Window) -> np.ndarray:
#     """Preprocess a dictionary of bands.

#     Args:
#         bands: A dictionary of bands, where the keys are band names and the values are numpy arrays.

#     Returns:
#         A numpy array of preprocessed bands.
#     """
#     # ToDo: add padding
#     stacked_bands = stack_bands(bands, window)
#     if np.any(np.array(stacked_bands.shape) == 0):
#         return np.zeros(1)
#     if stacked_bands.max() == 0:
#         return np.zeros(1)
#     logger.debug(f"Stacked bands shape: {stacked_bands.shape}")
#     stacked_bands = color_correction(stacked_bands)
#     logger.debug(f"Color corrected bands shape: {stacked_bands.shape}")
#     stacked_bands = robust_normalize(stacked_bands)
#     # ToDo: check data type
#     logger.debug(f"Normalized bands shape: {stacked_bands.shape}")
#     return stacked_bands


def color_correction(array: np.ndarray) -> np.ndarray:
    """Perform color correction on the stacked bands array.

    Args:
        array (np.ndarray): The stacked bands array.

    Returns:
        np.ndarray: The color-corrected stacked bands array. The dtype is int16.
    """
    if not isinstance(array, np.ndarray):
        raise ValueError("Array must be a numpy array")

    # ToDo: try np.int16 instead of int
    return (array / 8).astype(np.uint16)


# def robust_normalize(
#     band: np.ndarray, lower_bound: int = 1, upper_bound: int = 99
# ) -> np.ndarray:
#     # get lower bound percentile
#     percentile_lower_bound = np.percentile(band, lower_bound)
#     # set all lower bound outliers to percentile_lower_bound value
#     band[band < percentile_lower_bound] = percentile_lower_bound
#     # get upper bound percentile
#     percentile_upper_bound = np.percentile(band, upper_bound)
#     # set all upper bound outliers to percentile_upper_bound value
#     band[band > percentile_upper_bound] = percentile_upper_bound
#     # avoid division by zero
#     if (percentile_upper_bound - percentile_lower_bound) == 0:
#         return band
#     # normalize
#     return (band - percentile_lower_bound) / (
#         percentile_upper_bound - percentile_lower_bound
#     )


def robust_normalize(
    array: np.array,
    lower_percentile: int = 1,
    upper_percentile: int = 99,
    epsilon: float = 1e-7,
) -> np.array:
    """
    Normalizes a band using a robust method.
    Winsorization is used to clip the band values to the given percentiles.

    Args:
    band (np.array): The band to normalize. Expected dtype is uint16.
    lower_bound (float): The lower bound for normalization.
    upper_bound (float): The upper bound for normalization.

    Returns:
    np.array: The normalized band. Returned dtype is float32.
    """
    if not isinstance(array, np.ndarray):
        raise ValueError("Array must be a numpy array")
    if not isinstance(lower_percentile, int):
        raise ValueError("Lower percentile must be an integer")
    if not isinstance(upper_percentile, int):
        raise ValueError("Upper percentile must be an integer")
    if not isinstance(epsilon, float):
        raise ValueError("Epsilon must be a float")
    if not lower_percentile < upper_percentile:
        raise ValueError("Lower percentile must be smaller than upper percentile")

    lower_value = np.percentile(array, lower_percentile)
    upper_value = np.percentile(array, upper_percentile)
    array = np.clip(array, lower_value, upper_value)
    # ! change of dtype
    array = array.astype(np.float32)
    return (array - lower_value) / (max(upper_value - lower_value, epsilon))
