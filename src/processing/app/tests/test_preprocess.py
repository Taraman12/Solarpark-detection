import numpy as np
import rasterio
from constants import KERNEL_SIZE
from preprocess import (
    color_correction,
    moving_window,
    pad_image,
    preprocess_handler,
    robust_normalize,
)
from rasterio.windows import Window


def test_moving_window():
    # Create a test array
    array = np.ones((10980, 10980, 4), dtype="uint16")

    for col in [0, 5, 43]:
        for row in [0, 5, 43]:
            # Define a test window
            window = rasterio.windows.Window(col, row, 256, 256)

            # Call the function with the test array and window
            result = moving_window(array, window)

            # Check that the result has the correct shape
            assert result.shape == (window.height, window.width, 4)

            # Check that the result contains the correct values
            expected = array[
                window.row_off : window.row_off + window.height,
                window.col_off : window.col_off + window.width,
            ]
            assert np.array_equal(result, expected)


def test_pad_image_correct_size():
    image = np.ones((256, 256, 4), dtype="uint16")
    padded_image = pad_image(image, KERNEL_SIZE)
    assert padded_image.shape == image.shape
    assert np.array_equal(image, padded_image)


def test_pad_image_correct_size_no_input():
    image = np.ones((256, 256, 4), dtype="uint16")
    padded_image = pad_image(image)
    assert padded_image.shape == image.shape
    assert np.array_equal(image, padded_image)


def test_pad_image_needs_padding():
    image = np.ones((204, 204, 4), dtype="uint16")

    padded_image = pad_image(image, 250)
    assert padded_image.shape == (250, 250, 4)


def test_pad_image_needs_padding_no_input():
    image = np.ones((204, 204, 4), dtype="uint16")
    padded_image = pad_image(image)
    assert padded_image.shape == (KERNEL_SIZE, KERNEL_SIZE, 4)


def test_pad_image_needs_padding_only_in_height():
    image = np.ones((204, 728, 4), dtype="uint16")
    padded_image = pad_image(image, 256)
    assert padded_image.shape == (256, 728, 4)


def test_pad_image_needs_padding_only_in_width():
    image = np.ones((728, 204, 4), dtype="uint16")
    padded_image = pad_image(image, 256)
    assert padded_image.shape == (728, 256, 4)


def test_color_correction():
    # Test with an array of higher values
    stacked_bands = np.full((10, 10, 4), 1000, dtype="uint16")
    corrected_bands = color_correction(stacked_bands)
    assert corrected_bands.shape == (10, 10, 4)
    assert np.array_equal(corrected_bands, np.full((10, 10, 4), 125, dtype="int"))

    # Test with an array of maximum uint16 values
    stacked_bands = np.full((10, 10, 4), np.iinfo(np.uint16).max, dtype="uint16")
    corrected_bands = color_correction(stacked_bands)
    assert corrected_bands.shape == (10, 10, 4)
    assert np.array_equal(corrected_bands, np.full((10, 10, 4), 8191, dtype="int"))


def test_robust_normalize_ones():
    # Test with an array of ones
    band = np.ones((10, 10), dtype="uint16")
    normalized_band = robust_normalize(band)
    assert normalized_band.shape == (10, 10)
    # assert np.array_equal(normalized_band, np.ones((10, 10), dtype="uint16"))


def test_robust_normalize_zeros():
    # Test with an array of zeros
    band = np.zeros((10, 10), dtype="uint16")
    normalized_band = robust_normalize(band)
    assert normalized_band.shape == (10, 10)
    # assert np.array_equal(normalized_band, np.zeros((10, 10)))


def test_robust_normalize_arbitrary():
    # Test with an array of arbitrary values
    band = np.full((10, 10), 16, dtype="uint16")
    normalized_band = robust_normalize(band)
    assert normalized_band.shape == (10, 10)
    # assert np.array_equal(normalized_band, np.zeros((10, 10)))


def test_robust_normalize_random():
    # Test with an array of random values
    np.random.seed(0)
    band = np.random.randint(0, 1000, (10, 10), dtype="uint16")
    normalized_band = robust_normalize(band)
    assert normalized_band.shape == (10, 10)
    assert normalized_band.min() >= 0
    assert normalized_band.max() <= 1
    assert normalized_band.dtype == "float32"


def test_preprocess_handler_empty_window():
    # Test with an empty window
    array = np.ones((10, 10, 4), dtype="uint16")
    window = Window(10, 10, 0, 0)
    result = preprocess_handler(array, window)
    assert result is None


def test_preprocess_handler_zero_max():
    # Test with an array of zeros
    array = np.zeros((10, 10, 4), dtype="uint16")
    window = Window(0, 0, 10, 10)
    result = preprocess_handler(array, window)
    assert result is None


def test_preprocess_handler_normal_case():
    # Test with a normal case
    array = np.full((10, 10, 4), 1000, dtype="uint16")
    window = Window(0, 0, 10, 10)
    result = preprocess_handler(array, window)
    assert result.shape == (4, 10, 10)
    assert result.dtype == "float32"
    assert np.all(result >= 0)
    assert np.all(result <= 1)


def test_preprocess_handler_random():
    # Test with a random array
    np.random.seed(0)
    array = np.random.randint(1, 1000, (10, 10, 4), dtype="uint16")
    window = Window(0, 0, 10, 10)
    result = preprocess_handler(array, window)
    assert result.shape == (4, 10, 10)
    assert result.dtype == "float32"
    assert np.all(result >= 0)
    assert np.all(result <= 1)


# def test_moving_window():
#     KERNEL_SIZE = 256
#     metadata = {"height": 10980, "width": 10980}
#     stacked_bands = np.ones((10980, 10980, 4), dtype="uint16")
#     height = metadata["height"]
#     width = metadata["width"]
#     PADDING = 25
#     for row in range(0, height + PADDING, KERNEL_SIZE):
#         for col in range(0, width + PADDING, KERNEL_SIZE):
#             # Define the window coordinates for the snippet
#             window = rasterio.windows.Window(col, row, KERNEL_SIZE, KERNEL_SIZE)

#             # Cut out the snippet from the merged image
#             small_image = stacked_bands[
#                 window.row_off : window.row_off + window.height,
#                 window.col_off : window.col_off + window.width,
#             ]
#             assert small_image.shape == (256, 256, 4)
