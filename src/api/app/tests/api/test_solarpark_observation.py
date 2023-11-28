from statistics import mean

# import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# from app.main import app
from app.core.config import settings
from app.main import app
from app.tests.utils.solarpark_observation import (
    create_random_solarpark_observation,
    random_solarpark_observation_data,
)

client = TestClient(app)
# from httpx import AsyncClient


def test_create_solarpark_observation_overlapping(
    client: client, superuser_token_headers: dict, db: Session
) -> None:
    solarpark_observation = random_solarpark_observation_data()
    response = client.post(
        f"{settings.API_V1_STR}/solarpark_observation/",
        headers=superuser_token_headers,
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
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    solarpark_observation = random_solarpark_observation_data()
    response = client.post(
        f"{settings.API_V1_STR}/solarpark_observation/",
        headers=superuser_token_headers,
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


# # TODO: Fix this test
# # https://stackoverflow.com/questions/30763961/update-statement-on-table-xxx-expected-to-update-1-rows-0-were-matched-with
# @pytest.mark.anyio
# async def test_read_solarpark_observation(client: TestClient, db: Session) -> None:
#     # NOTE: The date is returned as a string from the db
#     solarpark_observation = create_random_solarpark_observation(db)
#     # response = client.get(
#     #     f"{settings.API_V1_STR}/solarpark_observation/{solarpark_observation.id}"
#     # )
#     async with AsyncClient(app=app, base_url=base_url) as ac:
#         response = await ac.get(f"/solarpark_observation/{solarpark_observation.id}")
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


# def test_read_multi_solarpark_observation(client: TestClient, db: Session) -> None:


def test_update_solarpark_observation(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    solarpark_observation = create_random_solarpark_observation(db)
    solarpark_observation_update = random_solarpark_observation_data()
    response = client.put(
        f"{settings.API_V1_STR}/solarpark_observation/{solarpark_observation.id}",
        headers=superuser_token_headers,
        json=solarpark_observation_update,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name_of_model"] == solarpark_observation_update["name_of_model"]
    assert content["date_of_data"] == solarpark_observation_update["date_of_data"]
    assert content["size_in_sq_m"] == solarpark_observation_update["size_in_sq_m"]
    assert content["peak_power"] == solarpark_observation_update["peak_power"]
    assert content["avg_confidence"] == solarpark_observation_update["avg_confidence"]
    assert content["name_in_aws"] == solarpark_observation_update["name_in_aws"]
    assert content["comment"] == solarpark_observation_update["comment"]
    assert content["lat"] == solarpark_observation_update["lat"]
    assert content["lon"] == solarpark_observation_update["lon"]
    assert content["geom"] == solarpark_observation_update["geom"]
    solarpark_id = content["solarpark_id"]
    response2 = client.get(f"{settings.API_V1_STR}/solarpark/{solarpark_id}")
    solarpark_after_update = response2.json()
    response3 = client.get(
        f"{settings.API_V1_STR}/solarpark_observation/",
        params={"solarpark_id": solarpark_id},
    )
    all_observations = response3.json()
    print(all_observations)
    # name_of_models = [item["name_of_model"] for item in all_observations]
    # assert solarpark_after_update["name_of_model"] == list(set(name_of_models))
    size_in_sq_m = [item["size_in_sq_m"] for item in all_observations]
    assert solarpark_after_update["size_in_sq_m"] == mean(size_in_sq_m)
    peak_power = [item["peak_power"] for item in all_observations]
    assert solarpark_after_update["peak_power"] == mean(peak_power)
    first_detection = [item["date_of_data"] for item in all_observations]
    assert solarpark_after_update["first_detection"] == min(first_detection)
    last_detection = [item["date_of_data"] for item in all_observations]
    assert solarpark_after_update["last_detection"] == max(last_detection)
    avg_confidence = [item["avg_confidence"] for item in all_observations]
    assert solarpark_after_update["avg_confidence_over_all_observations"] == mean(
        avg_confidence
    )


# * works
def test_delete_solarpark_observation(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    solarpark_observation = create_random_solarpark_observation(db)
    response = client.delete(
        f"{settings.API_V1_STR}/solarpark_observation/{solarpark_observation.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name_of_model"] == solarpark_observation.name_of_model
    assert content["date_of_data"] == solarpark_observation.date_of_data.strftime(
        "%Y-%m-%d"
    )
    assert content["size_in_sq_m"] == solarpark_observation.size_in_sq_m
    assert content["peak_power"] == solarpark_observation.peak_power
    assert content["avg_confidence"] == solarpark_observation.avg_confidence
    assert content["name_in_aws"] == solarpark_observation.name_in_aws
    assert content["comment"] == solarpark_observation.comment
    assert content["lat"] == solarpark_observation.lat
    assert content["lon"] == solarpark_observation.lon
    assert content["geom"] == solarpark_observation.geom
