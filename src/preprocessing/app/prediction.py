import json
from typing import Union

import numpy as np
import requests
from constants import HEADERS, KERNEL_SIZE, MODEL_NAME, URL_ML, USED_BANDS
from logging_config import get_logger

logger = get_logger("BaseConfig")


def prediction_handler(
    small_image: np.array, threshold: float = 0.5
) -> Union[np.array, None]:
    """
    Handles the prediction process for a given image.

    This function takes a small image, ensures it has the correct shape, and sends it to the ML model for prediction.
    If all values in the prediction are below 0.5, the function returns None. Otherwise, it returns the prediction.

    Args:
        small_image (np.array): The image to predict. The shape should be (len(USED_BANDS), KERNEL_SIZE, KERNEL_SIZE). Expects dtype np.float64.

    Returns:
        np.array | None: The prediction from the ML model, or None if all values in the prediction are above 0.5.
    """
    if small_image.dtype not in [np.float64, np.float32]:
        raise TypeError("Input image must be of type float64 or float32")

    if small_image.shape != (len(USED_BANDS), KERNEL_SIZE, KERNEL_SIZE):
        logger.info(f"Input image shape: {small_image.shape}")
        small_image = small_image.transpose(2, 0, 1)

    try:
        pred = send_to_ml_model(small_image)

    except Exception as e:
        logger.error(f"Failed to send data to ML model: {e}")
        return None

    if np.all(pred < threshold):
        logger.debug("No prediction above threshold")
        return None

    return pred


def send_request(data_array: np.ndarray) -> dict:
    """
    Sends a POST request to the ML model and returns the response.

    Args:
        data_array (np.ndarray): The data to send in the request.

    Returns:
        dict: The response from the ML model.
    """
    json_data = json.dumps(data_array.tolist())
    try:
        req = requests.post(
            f"{URL_ML}/predictions/{MODEL_NAME}",
            headers=HEADERS,
            data=json_data,
        )
        req.raise_for_status()
    except Exception as e:
        logger.error(e)
        raise Exception(f"Failed to send data to ML model: {e}")

    return req.json()


def validate_prediction_shape(prediction: np.ndarray) -> np.ndarray:
    """
    Validates the shape of the prediction.

    Args:
        prediction (np.ndarray): The prediction to validate.

    Returns:
        np.ndarray: The validated prediction.

    Raises:
        ValueError: If the prediction shape is not correct.
    """
    if prediction.shape != (1, KERNEL_SIZE, KERNEL_SIZE):
        logger.debug(f"Prediction shape: {prediction.shape}")
        raise ValueError(
            f"Prediction shape is not correct. Expected (1, {KERNEL_SIZE}, {KERNEL_SIZE}) got {prediction.shape}"
        )

    return prediction


def send_to_ml_model(data_array: np.ndarray) -> np.ndarray:
    """
    Sends data to the ML model and returns the prediction.

    Args:
        data_array (np.ndarray): The data to send to the ML model.

    Returns:
        np.ndarray: The prediction from the ML model.
    """
    response = send_request(data_array)
    if response is None:
        return np.zeros((1, KERNEL_SIZE, KERNEL_SIZE))

    prediction = np.array(response)
    return validate_prediction_shape(prediction)


# def send_to_ml_model(data_array: np.ndarray) -> np.ndarray:
#     json_data = json.dumps(data_array.tolist())
#     try:
#         req = requests.post(
#             f"{URL_ML}/predictions/{MODEL_NAME}",
#             headers=HEADERS,
#             data=json_data,
#         )
#     except Exception as e:
#         logger.error(e)
#         return np.zeros((1, KERNEL_SIZE, KERNEL_SIZE))

#     logger.debug(f"Got response from ml model: {req.status_code}")
#     pred = np.array(req.json())
#     if pred.shape != (1, KERNEL_SIZE, KERNEL_SIZE):
#         # pred = pred.squeeze()
#         logger.debug(f"Prediction shape: {pred.shape}")
#         raise ValueError(
#             f"Prediction shape is not correct. Expected (1, 256, 256) got {pred.shape}"
#         )
#     return pred

# mask = np.where(pred[0] < 0.5, 0, 1)
# if mask.sum() == 0:
#     return {}
# else:
#     logger.debug("Found prediction")
#     return pred


def calc_average_confidence(pred: np.ndarray, threshold: float = 0.5) -> float:
    """
    Calculates the average confidence of the prediction.

    Args:
    pred (np.array): The prediction array.

    Returns:
    float: The average confidence of the prediction.
    """
    # Get the values that are greater than or equal to 0.5
    values = pred[pred >= threshold]

    # If there are no such values, return 0.0
    if values.size == 0:
        return 0.0

    # Otherwise, return the average of the values
    return np.mean(values)


# old version
# def get_average_confidence(pred: np.ndarray) -> float:
#     mask = np.where(pred[0] < 0.5, 0, pred)
#     print(f"mask mean -> Confidence: {np.mean(mask, where=mask!=0)}")
#     # Find a solution for multiple solarparks in one image (hashmap or something)
