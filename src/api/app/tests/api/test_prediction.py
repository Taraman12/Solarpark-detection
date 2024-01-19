from statistics import mean

# import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# from app.main import app
from app.core.config import settings
from app.main import app
from app.tests.utils.prediction import create_random_prediction, random_prediction_data

client = TestClient(app)
# from httpx import AsyncClient


def test_create_prediction_overlapping(
    client: client, superuser_token_headers: dict, db: Session
) -> None:
    prediction = random_prediction_data()
    response = client.post(
        f"{settings.API_V1_STR}/prediction/",
        headers=superuser_token_headers,
        json=prediction,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name_of_model"] == prediction["name_of_model"]
    assert content["date_of_data"] == prediction["date_of_data"]
    assert content["size_in_sq_m"] == prediction["size_in_sq_m"]
    assert content["peak_power"] == prediction["peak_power"]
    assert content["avg_confidence"] == prediction["avg_confidence"]
    assert content["image_identifier"] == prediction["image_identifier"]
    assert content["comment"] == prediction["comment"]
    assert content["lat"] == prediction["lat"]
    assert content["lon"] == prediction["lon"]
    assert content["geom"] == prediction["geom"]


def test_create_prediction_non_overlapping(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    prediction = random_prediction_data()
    response = client.post(
        f"{settings.API_V1_STR}/prediction/",
        headers=superuser_token_headers,
        json=prediction,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name_of_model"] == prediction["name_of_model"]
    assert content["date_of_data"] == prediction["date_of_data"]
    assert content["size_in_sq_m"] == prediction["size_in_sq_m"]
    assert content["peak_power"] == prediction["peak_power"]
    assert content["avg_confidence"] == prediction["avg_confidence"]
    assert content["image_identifier"] == prediction["image_identifier"]
    assert content["comment"] == prediction["comment"]
    assert content["lat"] == prediction["lat"]
    assert content["lon"] == prediction["lon"]
    assert content["geom"] == prediction["geom"]


# # TODO: Fix this test
# # https://stackoverflow.com/questions/30763961/update-statement-on-table-xxx-expected-to-update-1-rows-0-were-matched-with
# @pytest.mark.anyio
# async def test_read_prediction(client: TestClient, db: Session) -> None:
#     # NOTE: The date is returned as a string from the db
#     prediction = create_random_prediction(db)
#     # response = client.get(
#     #     f"{settings.API_V1_STR}/prediction/{prediction.id}"
#     # )
#     async with AsyncClient(app=app, base_url=base_url) as ac:
#         response = await ac.get(f"/prediction/{prediction.id}")
#     assert response.status_code == 200
#     content = response.json()
#     assert content["name_of_model"] == prediction.name_of_model
#     assert content["date_of_data"] == prediction.date_of_data.strftime(
#         "%Y-%m-%d"
#     )
#     assert content["size_in_sq_m"] == prediction.size_in_sq_m
#     assert content["peak_power"] == prediction.peak_power
#     assert content["avg_confidence"] == prediction.avg_confidence
#     assert content["image_identifier"] == prediction.image_identifier
#     assert content["comment"] == prediction.comment
#     assert content["lat"] == prediction.lat
#     assert content["lon"] == prediction.lon
#     assert content["geom"] == prediction.geom


# def test_read_multi_prediction(client: TestClient, db: Session) -> None:


def test_update_prediction(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    prediction = create_random_prediction(db)
    prediction_update = random_prediction_data()
    response = client.put(
        f"{settings.API_V1_STR}/prediction/{prediction.id}",
        headers=superuser_token_headers,
        json=prediction_update,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name_of_model"] == prediction_update["name_of_model"]
    assert content["date_of_data"] == prediction_update["date_of_data"]
    assert content["size_in_sq_m"] == prediction_update["size_in_sq_m"]
    assert content["peak_power"] == prediction_update["peak_power"]
    assert content["avg_confidence"] == prediction_update["avg_confidence"]
    assert content["image_identifier"] == prediction_update["image_identifier"]
    assert content["comment"] == prediction_update["comment"]
    assert content["lat"] == prediction_update["lat"]
    assert content["lon"] == prediction_update["lon"]
    assert content["geom"] == prediction_update["geom"]
    solarpark_id = content["solarpark_id"]
    response2 = client.get(f"{settings.API_V1_STR}/solarpark/{solarpark_id}")
    solarpark_after_update = response2.json()
    response3 = client.get(
        f"{settings.API_V1_STR}/prediction/",
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
def test_delete_prediction(
    client: TestClient, superuser_token_headers: dict, db: Session
) -> None:
    prediction = create_random_prediction(db)
    response = client.delete(
        f"{settings.API_V1_STR}/prediction/{prediction.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name_of_model"] == prediction.name_of_model
    assert content["date_of_data"] == prediction.date_of_data.strftime("%Y-%m-%d")
    assert content["size_in_sq_m"] == prediction.size_in_sq_m
    assert content["peak_power"] == prediction.peak_power
    assert content["avg_confidence"] == prediction.avg_confidence
    assert content["image_identifier"] == prediction.image_identifier
    assert content["comment"] == prediction.comment
    assert content["lat"] == prediction.lat
    assert content["lon"] == prediction.lon
    assert content["geom"] == prediction.geom
