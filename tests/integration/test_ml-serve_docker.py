import torch
import requests
import json
import numpy as np


def test_prediction_with_solarpark():
    image = torch.load("data/32UMA_213_2018-9-27_with_solarpark.pt")
    assert image.shape == (4, 256, 256)
    json_data = json.dumps(image.numpy().tolist())
    response = requests.post(
        f"http://localhost:8080/predictions/solar-park-detection",
        headers={"Content-Type": "application/json"},
        data=json_data,
    ).json()
    pred = np.array(response)
    assert not np.all(pred < 0.5)


def test_prediction_without_solarpark():
    image = torch.load("data/32UMA_319_2018-9-27.pt")
    assert image.shape == (4, 256, 256)
    json_data = json.dumps(image.numpy().tolist())
    response = requests.post(
        f"http://localhost:8080/predictions/solar-park-detection",
        headers={"Content-Type": "application/json"},
        data=json_data,
    ).json()
    pred = np.array(response)
    assert np.all(pred < 0.5)
