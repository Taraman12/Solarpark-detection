from typing import Tuple

import numpy as np
from rasterio.windows import Window


def preprocess_handler(array: np.ndarray, window: Window) -> np.ndarray:
    """Handles the preprocessing of the array.

    Args:
        array (np.ndarray): The array to preprocess (w, h, dim). Expected dtype is uint16.
        window (Window): The window to extract.

    Returns:
        np.ndarray: The preprocessed array. Returned dtype is float64.
    """
    small_image = moving_window(array, window)
    if np.any(np.array(small_image.shape) == 0):
        return None
    if small_image.max() == 0:
        return None
    small_image = color_correction(small_image)
    small_image = robust_normalize(small_image)
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
    # Cut out the snippet from the merged stacked_array
    return stacked_array[
        window.row_off : window.row_off + window.height,
        window.col_off : window.col_off + window.width,
    ]


def pad_image(image, kernel_size, step_size):
    """
    Pads an image so that windows of the given kernel size and step size cover the entire image.

    Args:
    image (np.array): The image to pad.
    kernel_size (int): The size of the kernel.
    step_size (int): The size of the step.

    Returns:
    np.array: The padded image.
    """
    height, width, _ = image.shape
    pad_height = (
        (kernel_size - height % step_size) % step_size if height < kernel_size else 0
    )
    pad_width = (
        (kernel_size - width % step_size) % step_size if width < kernel_size else 0
    )
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


def robust_normalize(array, lower_percentile=1, upper_percentile=99, epsilon=1e-7):
    """
    Normalizes a band using a robust method.
    Winsorization is used to clip the band values to the given percentiles.

    Args:
    band (np.array): The band to normalize. Expected dtype is uint16.
    lower_bound (float): The lower bound for normalization.
    upper_bound (float): The upper bound for normalization.

    Returns:
    np.array: The normalized band. Returned dtype is float64.
    """
    lower_value = np.percentile(array, lower_percentile)
    upper_value = np.percentile(array, upper_percentile)
    array = np.clip(array, lower_value, upper_value)
    return (array - lower_value) / (max(upper_value - lower_value, epsilon))
