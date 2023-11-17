from unittest.mock import Mock, patch

import numpy as np
import pytest

# import requests
from constants import (
    IMAGE_OUTPUT_DIR,
    KERNEL_SIZE,
    MASK_OUTPUT_DIR,
    NOW_DICT,
    STEP_SIZE,
)
from main_preprocessing import (  # process_window,
    calc_rows_cols,
    get_identifier_and_band_info,
    get_prediction_and_filename,
    get_small_image,
    open_and_preprocess_data,
    run_setup,
)
from models.identifier import Identifier
from rasterio.windows import Window


@patch("main_preprocessing.get_jwt_from_api")
@patch("main_preprocessing.store_jwt")
@patch("main_preprocessing.create_output_directories")
def test_run_setup_success(
    mock_create_output_directories, mock_store_jwt, mock_get_jwt_from_api
):
    # Test with successful setup
    mock_get_jwt_from_api.return_value = "test_token"
    run_setup()
    mock_create_output_directories.assert_called_once_with(
        [IMAGE_OUTPUT_DIR, MASK_OUTPUT_DIR]
    )
    mock_get_jwt_from_api.assert_called_once_with(
        username="John@Doe.com", password="password"
    )
    mock_store_jwt.assert_called_once_with("test_token")


@patch("main_preprocessing.get_jwt_from_api")
@patch("main_preprocessing.store_jwt")
@patch("main_preprocessing.create_output_directories")
def test_run_setup_jwt_api_failure(
    mock_create_output_directories, mock_store_jwt, mock_get_jwt_from_api
):
    # Test with failure to get JWT from API
    mock_get_jwt_from_api.side_effect = Exception
    with pytest.raises(SystemExit) as e:
        run_setup()
    assert e.type == SystemExit
    assert e.value.code == 1
    mock_create_output_directories.assert_called_once_with(
        [IMAGE_OUTPUT_DIR, MASK_OUTPUT_DIR]
    )
    mock_get_jwt_from_api.assert_called_once_with(
        username="John@Doe.com", password="password"
    )
    mock_store_jwt.assert_not_called()


@patch("main_preprocessing.get_identifier_handler")
def test_get_identifier_and_band_info_no_identifier(mock_get_identifier_handler):
    # Test when get_identifier_handler returns None
    mock_get_identifier_handler.return_value = None
    result = get_identifier_and_band_info("test_tile")
    assert result == (None, None)
    mock_get_identifier_handler.assert_called_once_with(
        tile_id="test_tile", dates=NOW_DICT
    )


@patch("main_preprocessing.download_from_sentinel_aws_handler")
@patch("main_preprocessing.get_identifier_handler")
def test_get_identifier_and_band_info_success(
    mock_get_identifier_handler, mock_download_from_sentinel_aws_handler
):
    # Test when get_identifier_handler and download_from_sentinel_aws_handler return valid results
    mock_identifier = Mock()
    mock_identifier.to_string.return_value = "test_string"
    mock_get_identifier_handler.return_value = mock_identifier
    mock_download_from_sentinel_aws_handler.return_value = {"band_info": "test_info"}
    result = get_identifier_and_band_info("test_tile")
    assert result == (mock_identifier, {"band_info": "test_info"})
    mock_get_identifier_handler.assert_called_once_with(
        tile_id="test_tile", dates=NOW_DICT
    )
    mock_download_from_sentinel_aws_handler.assert_called_once_with(
        identifier=mock_identifier, target_folder=IMAGE_OUTPUT_DIR
    )


@patch("main_preprocessing.preprocess_handler")
@patch("main_preprocessing.open_data_handler")
def test_open_and_preprocess_data_no_stacked_bands(
    mock_open_data_handler, mock_preprocess_handler
):
    # Test when open_data_handler returns None for stacked_bands
    mock_open_data_handler.return_value = (
        None,
        "test_first_band_open",
        "test_original_metadata",
    )
    result = open_and_preprocess_data("test_band_file_info")
    assert result == (None, None, None)
    mock_open_data_handler.assert_called_once_with(band_file_info="test_band_file_info")
    mock_preprocess_handler.assert_not_called()


@patch("main_preprocessing.preprocess_handler")
@patch("main_preprocessing.open_data_handler")
def test_open_and_preprocess_data_success(
    mock_open_data_handler, mock_preprocess_handler
):
    # Test successful run of open_and_preprocess_data
    mock_open_data_handler.return_value = (
        "test_stacked_bands",
        "test_first_band_open",
        "test_original_metadata",
    )
    mock_preprocess_handler.return_value = "test_preprocessed_stacked_bands"
    result = open_and_preprocess_data("test_band_file_info")
    assert result == (
        "test_preprocessed_stacked_bands",
        "test_first_band_open",
        "test_original_metadata",
    )
    mock_open_data_handler.assert_called_once_with(band_file_info="test_band_file_info")
    mock_preprocess_handler.assert_called_once_with(
        array="test_stacked_bands", training=True
    )


def test_calc_rows_cols():
    # Test with metadata where height and width are both greater than KERNEL_SIZE
    metadata = {"height": 1000, "width": 1000}
    result = calc_rows_cols(metadata)
    assert result == (
        (1000 - KERNEL_SIZE) // STEP_SIZE + 1,
        (1000 - KERNEL_SIZE) // STEP_SIZE + 1,
    )

    # Test with metadata where height and width are both equal to KERNEL_SIZE
    metadata = {"height": KERNEL_SIZE, "width": KERNEL_SIZE}
    result = calc_rows_cols(metadata)
    assert result == (1, 1)


def test_calc_rows_cols_not_dict():
    # Test with metadata that is not a dictionary
    with pytest.raises(ValueError) as e:
        calc_rows_cols("not a dict")
    assert str(e.value) == "Could not calculate rows and cols for not a dict"


def test_calc_rows_cols_none():
    # Test with None metadata
    with pytest.raises(ValueError) as e:
        calc_rows_cols(None)
    assert str(e.value) == "Could not calculate rows and cols for None"


def test_calc_rows_cols_height_not_int():
    # Test with metadata where height is not an integer
    with pytest.raises(ValueError) as e:
        calc_rows_cols({"height": "not an int", "width": 100})
    assert (
        str(e.value)
        == "Could not calculate rows and cols for {'height': 'not an int', 'width': 100}"
    )


def test_calc_rows_cols_width_not_int():
    # Test with metadata where width is not an integer
    with pytest.raises(ValueError) as e:
        calc_rows_cols({"height": 100, "width": "not an int"})
    assert (
        str(e.value)
        == "Could not calculate rows and cols for {'height': 100, 'width': 'not an int'}"
    )


@patch("main_preprocessing.moving_window")
def test_get_small_image_none(mock_moving_window):
    # Test when moving_window returns None
    mock_moving_window.return_value = None
    result = get_small_image(np.array([1, 2, 3, 4]), Window(0, 0, 2, 2))
    assert result is None
    mock_moving_window.assert_called_once()


@patch("main_preprocessing.moving_window")
def test_get_small_image_max_zero(mock_moving_window):
    # Test when the maximum value of the small image is 0
    mock_moving_window.return_value = np.zeros((KERNEL_SIZE, KERNEL_SIZE, 4))
    result = get_small_image(np.array([1, 2, 3, 4]), Window(0, 0, 2, 2))
    assert result is None
    mock_moving_window.assert_called_once()


# TODO: Fix this test
# @patch("main_preprocessing.moving_window")
# @patch("main_preprocessing.pad_image")
# def test_get_small_image_pad(mock_pad_image, mock_moving_window):
#     # Test when the shape of the small image is not (KERNEL_SIZE, KERNEL_SIZE, 4)
#     mock_moving_window.return_value = np.ones((KERNEL_SIZE - 1, KERNEL_SIZE - 1, 4))
#     mock_pad_image.return_value = np.ones((KERNEL_SIZE, KERNEL_SIZE, 4))
#     result = get_small_image(np.array([1, 2, 3, 4]), Window(0, 0, 2, 2))
#     np.testing.assert_array_equal(result, np.ones((KERNEL_SIZE, KERNEL_SIZE, 4)))
#     mock_moving_window.assert_called_once()
#     mock_pad_image.assert_called_once_with(
#         np.ones((KERNEL_SIZE - 1, KERNEL_SIZE - 1, 4)), KERNEL_SIZE
#     )


@patch("main_preprocessing.moving_window")
def test_get_small_image_success(mock_moving_window):
    # Test successful run of get_small_image
    mock_moving_window.return_value = np.ones((KERNEL_SIZE, KERNEL_SIZE, 4))
    result = get_small_image(np.array([1, 2, 3, 4]), Window(0, 0, 2, 2))
    np.testing.assert_array_equal(result, np.ones((KERNEL_SIZE, KERNEL_SIZE, 4)))
    mock_moving_window.assert_called_once()


@patch("main_preprocessing.prediction_handler")
def test_get_prediction_and_filename_none(mock_prediction_handler):
    # Test when prediction_handler returns None
    mock_prediction_handler.return_value = None
    result = get_prediction_and_filename(
        np.array([1, 2, 3, 4]),
        Identifier("S2A_MSIL2A_20181013T100021_N0209_R122_T33UVP_20181013T114121"),
        1,
    )
    assert result == (None, None)
    # mock_prediction_handler.assert_called_once_with(small_image=np.array([1, 2, 3, 4]))


@patch("main_preprocessing.prediction_handler")
def test_get_prediction_and_filename_success(mock_prediction_handler):
    # Test successful run of get_prediction_and_filename
    mock_prediction_handler.return_value = np.array([5, 6, 7, 8])
    prediction, filename = get_prediction_and_filename(
        np.array([1, 2, 3, 4]),
        Identifier("S2A_MSIL2A_20181013T100021_N0209_R122_T33UVP_20181013T114121"),
        1,
    )
    assert np.array_equal(prediction, np.array([5, 6, 7, 8]))
    assert filename == "33UVP_1_2018-10-13.tif"
    # mock_prediction_handler.assert_called_once_with(small_image=np.array([1, 2, 3, 4]))


# @patch("main_preprocessing.get_small_image")
# def test_process_window_no_small_image(mock_get_small_image):
#     # Test when get_small_image returns None
#     mock_get_small_image.return_value = None
#     result = process_window(
#         np.array([1, 2, 3, 4]),
#         Window(0, 0, 2, 2),
#         {},
#         {},
#         Identifier("S2A_MSIL2A_20181013T100021_N0209_R122_T33UVP_20181013T114121"),
#         1,
#     )
#     assert result == 1
#     mock_get_small_image.assert_called_once_with(
#         np.array([1, 2, 3, 4]), Window(0, 0, 2, 2)
#     )


# @patch("main_preprocessing.get_prediction_and_filename")
# @patch("main_preprocessing.get_small_image")
# def test_process_window_no_prediction(
#     mock_get_small_image, mock_get_prediction_and_filename
# ):
#     # Test when get_prediction_and_filename returns None for prediction
#     mock_get_small_image.return_value = np.array([5, 6, 7, 8])
#     mock_get_prediction_and_filename.return_value = (None, "test_filename")
#     result = process_window(
#         np.array([1, 2, 3, 4]),
#         Window(0, 0, 2, 2),
#         {},
#         {},
#         Identifier("S2A_MSIL2A_20181013T100021_N0209_R122_T33UVP_20181013T114121"),
#         1,
#     )
#     assert result == 1
#     mock_get_small_image.assert_called_once_with(
#         np.array([1, 2, 3, 4]), Window(0, 0, 2, 2)
#     )
#     mock_get_prediction_and_filename.assert_called_once_with(
#         np.array([5, 6, 7, 8]), Identifier("S2A_MSIL2A_20181013T100021_N0209_R122_T33UVP_20181013T114121"), 1
#     )


# @patch("main_preprocessing.write_to_db_handler")
# @patch("main_preprocessing.update_metadata")
# @patch("main_preprocessing.get_prediction_and_filename")
# @patch("main_preprocessing.get_small_image")
# def test_process_window_success(
#     mock_get_small_image,
#     mock_get_prediction_and_filename,
#     mock_update_metadata,
#     mock_write_to_db_handler,
# ):
#     # Test successful run of process_window
#     mock_get_small_image.return_value = np.array([5, 6, 7, 8])
#     mock_get_prediction_and_filename.return_value = (
#         np.array([9, 10, 11, 12]),
#         "test_filename",
#     )
#     mock_update_metadata.return_value = {"updated": "metadata"}
#     result = process_window(
#         np.array([1, 2, 3, 4]),
#         Window(0, 0, 2, 2),
#         {},
#         {},
#         Identifier("S2A_MSIL2A_20181013T100021_N0209_R122_T33UVP_20181013T114121"),
#         1,
#     )
#     assert result == 1
#     mock_get_small_image.assert_called_once_with(
#         np.array([1, 2, 3, 4]), Window(0, 0, 2, 2)
#     )
#     mock_get_prediction_and_filename.assert_called_once_with(
#         np.array([5, 6, 7, 8]), Identifier("S2A_MSIL2A_20181013T100021_N0209_R122_T33UVP_20181013T114121"), 1
#     )
#     mock_update_metadata.assert_called_once_with(
#         metadata={}, window=Window(0, 0, 2, 2), first_band_open={}
#     )
#     mock_write_to_db_handler.assert_called_once_with(
#         prediction=np.array([9, 10, 11, 12]),
#         metadata={"updated": "metadata"},
#         tile_date="test_date",
#         filename="test_filename",
#     )
