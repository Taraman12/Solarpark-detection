from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.tests.utils.solarpark_observation import random_solarpark_observation_data


def test_create_solarpark_observation_overlapping(
    client: TestClient, db: Session
) -> None:
    solarpark_observation = random_solarpark_observation_data()
    response = client.post(
        f"{settings.API_V1_STR}/solarpark_observation/",
        json=solarpark_observation,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name_of_model"] == solarpark_observation["name_of_model"]
    assert content["date_of_data"] == solarpark_observation["date_of_data"]
    assert content["size_in_sq_m"] == solarpark_observation["size_in_sq_m"]
    assert content["peak_power"] == solarpark_observation["peak_power"]
    assert content["avg_confidence"] == solarpark_observation["avg_confidence"]
    assert content["name_in_aws"] == solarpark_observation["name_in_aws"]
    assert content["comment"] == solarpark_observation["comment"]
    assert content["lat"] == solarpark_observation["lat"]
    assert content["lon"] == solarpark_observation["lon"]
    assert content["geom"] == solarpark_observation["geom"]


def test_create_solarpark_observation_non_overlapping(
    client: TestClient, db: Session
) -> None:
    solarpark_observation = random_solarpark_observation_data()
    response = client.post(
        f"{settings.API_V1_STR}/solarpark_observation/",
        json=solarpark_observation,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name_of_model"] == solarpark_observation["name_of_model"]
    assert content["date_of_data"] == solarpark_observation["date_of_data"]
    assert content["size_in_sq_m"] == solarpark_observation["size_in_sq_m"]
    assert content["peak_power"] == solarpark_observation["peak_power"]
    assert content["avg_confidence"] == solarpark_observation["avg_confidence"]
    assert content["name_in_aws"] == solarpark_observation["name_in_aws"]
    assert content["comment"] == solarpark_observation["comment"]
    assert content["lat"] == solarpark_observation["lat"]
    assert content["lon"] == solarpark_observation["lon"]
    assert content["geom"] == solarpark_observation["geom"]
