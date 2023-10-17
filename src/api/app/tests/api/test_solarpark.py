from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.tests.utils.solarpark import create_random_solarpark


def test_create_solarpark(client: TestClient, db: Session) -> None:
    data = {
        "name_of_model": "Test",
        "size_in_sq_m": 100.0,
        "peak_power": 100.0,
        "date_of_data": "2021-01-01",
        "first_detection": "2021-01-01",
        "last_detection": "2021-01-01",
        "avg_confidence": 100.0,
        "name_in_aws": "Test",
        "is_valid": "None",
        "comment": "None",
        "lat": [1.0, 2.0],
        "lon": [1.0, 2.0],
    }
    response = client.post(
        f"{settings.API_V1_STR}/solarpark/",
        # headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name_of_model"] == data["name_of_model"]
    assert content["size_in_sq_m"] == data["size_in_sq_m"]
    assert content["peak_power"] == data["peak_power"]
    assert content["date_of_data"] == data["date_of_data"]
    assert content["first_detection"] == data["first_detection"]
    assert content["last_detection"] == data["last_detection"]
    assert content["avg_confidence"] == data["avg_confidence"]
    assert content["name_in_aws"] == data["name_in_aws"]
    assert content["is_valid"] == data["is_valid"]
    assert content["comment"] == data["comment"]
    assert content["lat"] == data["lat"]
    assert content["lon"] == data["lon"]


def test_read_solarpark(client: TestClient, db: Session) -> None:
    # NOTE: The date is returned as a string from the db
    solarpark = create_random_solarpark(db)
    response = client.get(f"{settings.API_V1_STR}/solarpark/{solarpark.id}")
    assert response.status_code == 200
    content = response.json()
    assert content["name_of_model"] == solarpark.name_of_model
    assert content["size_in_sq_m"] == solarpark.size_in_sq_m
    assert content["peak_power"] == solarpark.peak_power
    assert content["date_of_data"] == solarpark.date_of_data.strftime("%Y-%m-%d")
    assert content["first_detection"] == solarpark.first_detection.strftime("%Y-%m-%d")
    assert content["last_detection"] == solarpark.last_detection.strftime("%Y-%m-%d")
    assert content["avg_confidence"] == solarpark.avg_confidence
    assert content["name_in_aws"] == solarpark.name_in_aws
    assert content["is_valid"] == solarpark.is_valid
    assert content["comment"] == solarpark.comment
    assert content["lat"] == solarpark.lat
    assert content["lon"] == solarpark.lon
