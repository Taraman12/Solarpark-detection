from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.tests.utils.solarpark_observation import (  # create_random_solarpark_observation,
    random_solarpark_observation_data,
)


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


# TODO: Fix this test
# https://stackoverflow.com/questions/30763961/update-statement-on-table-xxx-expected-to-update-1-rows-0-were-matched-with
# def test_read_solarpark_observation(client: TestClient, db: Session) -> None:
#     # NOTE: The date is returned as a string from the db
#     solarpark_observation = create_random_solarpark_observation(db)
#     response = client.get(
#         f"{settings.API_V1_STR}/solarpark_observation/{solarpark_observation.id}"
#     )
#     assert response.status_code == 200
#     content = response.json()
#     assert content["name_of_model"] == solarpark_observation.name_of_model
#     assert content["date_of_data"] == solarpark_observation.date_of_data.strftime(
#         "%Y-%m-%d"
#     )
#     assert content["size_in_sq_m"] == solarpark_observation.size_in_sq_m
#     assert content["peak_power"] == solarpark_observation.peak_power
#     assert content["avg_confidence"] == solarpark_observation.avg_confidence
#     assert content["name_in_aws"] == solarpark_observation.name_in_aws
#     assert content["comment"] == solarpark_observation.comment
#     assert content["lat"] == solarpark_observation.lat
#     assert content["lon"] == solarpark_observation.lon
#     assert content["geom"] == solarpark_observation.geom


# # def test_read_multi_solarpark_observation(client: TestClient, db: Session) -> None:


# def test_update_solarpark_observation(client: TestClient, db: Session) -> None:
#     solarpark_observation = create_random_solarpark_observation(db)
#     solarpark_observation_update = random_solarpark_observation_data()
#     response = client.put(
#         f"{settings.API_V1_STR}/solarpark_observation/{solarpark_observation.id}",
#         json=solarpark_observation_update,
#     )
#     assert response.status_code == 200
#     content = response.json()
#     assert content["name_of_model"] == solarpark_observation_update["name_of_model"]
#     assert content["date_of_data"] == solarpark_observation_update["date_of_data"]
#     assert content["size_in_sq_m"] == solarpark_observation_update["size_in_sq_m"]
#     assert content["peak_power"] == solarpark_observation_update["peak_power"]
#     assert content["avg_confidence"] == solarpark_observation_update["avg_confidence"]
#     assert content["name_in_aws"] == solarpark_observation_update["name_in_aws"]
#     assert content["comment"] == solarpark_observation_update["comment"]
#     assert content["lat"] == solarpark_observation_update["lat"]
#     assert content["lon"] == solarpark_observation_update["lon"]
#     assert content["geom"] == solarpark_observation_update["geom"]


# def test_delete_solarpark_observation(client: TestClient, db: Session) -> None:
#     solarpark_observation = create_random_solarpark_observation(db)
#     response = client.delete(
#         f"{settings.API_V1_STR}/solarpark_observation/{solarpark_observation.id}",
#     )
#     assert response.status_code == 200
#     content = response.json()
#     assert content["name_of_model"] == solarpark_observation.name_of_model
#     assert content["date_of_data"] == solarpark_observation.date_of_data.strftime(
#         "%Y-%m-%d"
#     )
#     assert content["size_in_sq_m"] == solarpark_observation.size_in_sq_m
#     assert content["peak_power"] == solarpark_observation.peak_power
#     assert content["avg_confidence"] == solarpark_observation.avg_confidence
#     assert content["name_in_aws"] == solarpark_observation.name_in_aws
#     assert content["comment"] == solarpark_observation.comment
#     assert content["lat"] == solarpark_observation.lat
#     assert content["lon"] == solarpark_observation.lon
#     assert content["geom"] == solarpark_observation.geom
