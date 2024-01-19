from unittest import mock

import numpy as np
import pytest
import requests_mock
from constants import KERNEL_SIZE, MODEL_NAME, URL_ML, USED_BANDS
from prediction import (
    calc_average_confidence,
    prediction_handler,
    send_request,
    send_to_ml_model,
    validate_prediction_shape,
)


def test_calc_average_confidence_all_zeros():
    # Test with an array of zeros
    pred = np.zeros((1, 10, 10), dtype=np.float64)
    result = calc_average_confidence(pred)
    assert result == 0.0


def test_calc_average_confidence_all_ones():
    # Test with an array of ones
    pred = np.ones((1, 10, 10), dtype=np.float64)
    result = calc_average_confidence(pred)
    assert result == 1.0


def test_calc_average_confidence_mixed_values():
    # Test with an array of mixed values
    pred = np.array([[[0.1, 0.6], [0.4, 0.8]]])
    result = calc_average_confidence(pred)
    assert result == 0.7


def test_calc_average_confidence_random():
    # Test with a random array
    np.random.seed(0)
    pred = np.random.rand(1, 10, 10)
    result = calc_average_confidence(pred)
    assert result == np.mean(pred[pred >= 0.5])


def test_send_request_success():
    # Test when the request is successful
    with requests_mock.Mocker() as m:
        m.post(
            f"{URL_ML}/predictions/{MODEL_NAME}",
            json=np.ones((1, KERNEL_SIZE, KERNEL_SIZE)).tolist(),
        )
        data_array = np.ones((1, KERNEL_SIZE, KERNEL_SIZE))
        result = send_request(data_array)
        assert np.array_equal(result, np.ones((1, KERNEL_SIZE, KERNEL_SIZE)))


def test_send_request_exception():
    # Test when an exception is raised
    with requests_mock.Mocker() as m:
        m.post(f"{URL_ML}/predictions/{MODEL_NAME}", exc=Exception)
        data_array = np.ones((1, KERNEL_SIZE, KERNEL_SIZE))
        with pytest.raises(Exception):
            send_request(data_array)


def test_send_request_incorrect_shape():
    # Test when the response has an incorrect shape
    with requests_mock.Mocker() as m:
        m.post(
            f"{URL_ML}/predictions/{MODEL_NAME}",
            json=np.ones((2, KERNEL_SIZE, KERNEL_SIZE)).tolist(),
        )
        data_array = np.ones((1, KERNEL_SIZE, KERNEL_SIZE))
        result = send_request(data_array)
        assert (
            len(result) == 2
            and len(result[0]) == KERNEL_SIZE
            and len(result[1]) == KERNEL_SIZE
        )


def test_validate_prediction_shape_correct_shape():
    # Test with a prediction of correct shape
    pred = np.ones((1, KERNEL_SIZE, KERNEL_SIZE))
    result = validate_prediction_shape(pred)
    assert np.array_equal(result, pred)


def test_validate_prediction_shape_incorrect_shape():
    # Test with a prediction of incorrect shape
    pred = np.ones((2, KERNEL_SIZE, KERNEL_SIZE))
    with pytest.raises(ValueError):
        validate_prediction_shape(pred)


def test_validate_prediction_shape_incorrect_dimensions():
    # Test with a prediction of incorrect dimensions
    pred = np.ones((1, KERNEL_SIZE))
    with pytest.raises(ValueError):
        validate_prediction_shape(pred)


def test_send_to_ml_model_success():
    # Test when the request is successful and the prediction has the correct shape
    with requests_mock.Mocker() as m:
        m.post(
            f"{URL_ML}/predictions/{MODEL_NAME}",
            json=np.ones((1, KERNEL_SIZE, KERNEL_SIZE)).tolist(),
        )
        data_array = np.ones((1, KERNEL_SIZE, KERNEL_SIZE))
        result = send_to_ml_model(data_array)
        assert np.array_equal(result, np.ones((1, KERNEL_SIZE, KERNEL_SIZE)))


def test_send_to_ml_model_request_exception():
    # Test when an exception is raised during the request
    with requests_mock.Mocker() as m:
        m.post(f"{URL_ML}/predictions/{MODEL_NAME}", exc=Exception)
        data_array = np.ones((1, KERNEL_SIZE, KERNEL_SIZE))
        with pytest.raises(Exception):
            result = send_to_ml_model(data_array)
            assert np.array_equal(result, np.zeros((1, KERNEL_SIZE, KERNEL_SIZE)))


def test_send_to_ml_model_incorrect_shape():
    # Test when the prediction has an incorrect shape
    with requests_mock.Mocker() as m:
        m.post(
            f"{URL_ML}/predictions/{MODEL_NAME}",
            json=np.ones((2, KERNEL_SIZE, KERNEL_SIZE)).tolist(),
        )
        data_array = np.ones((1, KERNEL_SIZE, KERNEL_SIZE))
        with pytest.raises(ValueError):
            send_to_ml_model(data_array)


def test_prediction_handler_correct_dtype_and_shape():
    # Test with a small image of correct shape and type
    small_image = np.random.rand(len(USED_BANDS), KERNEL_SIZE, KERNEL_SIZE).astype(
        np.float64
    )
    result = prediction_handler(small_image)
    assert isinstance(result, (np.ndarray, type(None)))


def test_prediction_handler_incorrect_dtype():
    # Test with a small image of correct shape but incorrect type
    small_image = np.random.rand(len(USED_BANDS), KERNEL_SIZE, KERNEL_SIZE).astype(
        np.int32
    )
    with pytest.raises(TypeError):
        prediction_handler(small_image)


def test_prediction_handler_incorrect_shape():
    # Test with a small image of correct type but incorrect shape
    small_image = np.random.rand(len(USED_BANDS), KERNEL_SIZE).astype(np.float64)
    with pytest.raises(ValueError):
        prediction_handler(small_image)


def test_prediction_handler_exception_in_send_to_ml_model():
    # Test when send_to_ml_model raises an exception
    small_image = np.random.rand(len(USED_BANDS), KERNEL_SIZE, KERNEL_SIZE).astype(
        np.float64
    )
    with mock.patch("prediction.send_to_ml_model", side_effect=Exception):
        result = prediction_handler(small_image)
        assert result is None


def test_prediction_handler_all_values_below_threshold():
    # Test when all values in the prediction are above the threshold
    small_image = np.random.rand(len(USED_BANDS), KERNEL_SIZE, KERNEL_SIZE).astype(
        np.float64
    )
    with mock.patch(
        "prediction.send_to_ml_model",
        return_value=np.full((1, KERNEL_SIZE, KERNEL_SIZE), 0.4),
    ):
        result = prediction_handler(small_image)
        assert result is None


# def test_send_to_ml_model_success():
#     # Test when the request is successful
#     with requests_mock.Mocker() as m:
#         m.post(
#             f"{URL_ML}/predictions/{MODEL_NAME}",
#             json=np.ones((1, KERNEL_SIZE, KERNEL_SIZE)).tolist(),
#         )
#         data_array = np.ones((1, KERNEL_SIZE, KERNEL_SIZE))
#         result = send_to_ml_model(data_array)
#         assert np.array_equal(result, np.ones((1, KERNEL_SIZE, KERNEL_SIZE)))


# def test_send_to_ml_model_exception():
#     # Test when an exception is raised
#     with requests_mock.Mocker() as m:
#         m.post(f"{URL_ML}/predictions/{MODEL_NAME}", exc=Exception)
#         data_array = np.ones((1, KERNEL_SIZE, KERNEL_SIZE))
#         result = send_to_ml_model(data_array)
#         assert np.array_equal(result, np.zeros((1, KERNEL_SIZE, KERNEL_SIZE)))


# def test_send_to_ml_model_incorrect_shape():
#     # Test when the response has an incorrect shape
#     with requests_mock.Mocker() as m:
#         m.post(
#             f"{URL_ML}/predictions/{MODEL_NAME}",
#             json=np.ones((2, KERNEL_SIZE, KERNEL_SIZE)).tolist(),
#         )
#         data_array = np.ones((1, KERNEL_SIZE, KERNEL_SIZE))
#         with pytest.raises(ValueError):
#             send_to_ml_model(data_array)
