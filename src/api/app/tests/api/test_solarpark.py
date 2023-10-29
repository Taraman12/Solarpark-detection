from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.tests.utils.solarpark import create_random_solarpark

# TODO: Fix the read_multi test
# TODO: Reduce boilerplate code (data)


def test_create_solarpark(client: TestClient, db: Session) -> None:
    data = {
        "name_of_model": ["Test"],
        "size_in_sq_m": 100.0,
        "peak_power": 100.0,
        "date_of_data": "2021-01-01",
        "first_detection": "2021-01-01",
        "last_detection": "2021-01-01",
        "avg_confidence_over_all_observations": 0.8,
        "name_in_aws": "Test",
        "is_valid": "None",
        "comment": "None",
        "lat": [599968.55, 599970.91, 599973.65, 599971.31, 599968.55],
        "lon": [5570202.63, 5570205.59, 5570203.42, 5570200.46, 5570202.63],
        "geom": "POLYGON ((599968.55 5570202.63, 599970.91 5570205.59, 599973.65 5570203.42, 599971.31 5570200.46, 599968.55 5570202.63))",
    }
    # solarpark = create_random_solarpark(db)
    # print(f"data: {type(data)}")
    # print(f"solarpark: {type(solarpark.__dict__)}")
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
    assert content["first_detection"] == data["first_detection"]
    assert content["last_detection"] == data["last_detection"]
    assert (
        content["avg_confidence_over_all_observations"]
        == data["avg_confidence_over_all_observations"]
    )
    assert content["name_in_aws"] == data["name_in_aws"]
    assert content["is_valid"] == data["is_valid"]
    assert content["comment"] == data["comment"]
    assert content["lat"] == data["lat"]
    assert content["lon"] == data["lon"]
    assert content["geom"] == data["geom"]


def test_read_solarpark(client: TestClient, db: Session) -> None:
    # NOTE: The date is returned as a string from the db
    solarpark = create_random_solarpark(db)
    response = client.get(f"{settings.API_V1_STR}/solarpark/{solarpark.id}")
    assert response.status_code == 200
    content = response.json()
    assert content["name_of_model"] == solarpark.name_of_model
    assert content["size_in_sq_m"] == solarpark.size_in_sq_m
    assert content["peak_power"] == solarpark.peak_power
    assert content["first_detection"] == solarpark.first_detection.strftime("%Y-%m-%d")
    assert content["last_detection"] == solarpark.last_detection.strftime("%Y-%m-%d")
    assert (
        content["avg_confidence_over_all_observations"]
        == solarpark.avg_confidence_over_all_observations
    )
    assert content["name_in_aws"] == solarpark.name_in_aws
    assert content["is_valid"] == solarpark.is_valid
    assert content["comment"] == solarpark.comment
    assert content["lat"] == solarpark.lat
    assert content["lon"] == solarpark.lon
    assert content["geom"] == solarpark.geom


# def test_read_multi_solarpark(client: TestClient, db: Session) -> None:
#     # TODO: This test is failing
#     solarpark1 = create_random_solarpark(db)
#     solarpark2 = create_random_solarpark(db)
#     response = client.get(f"{settings.API_V1_STR}/solarpark/")
#     assert response.status_code == 200
#     content = response.json()
# assert content[0]["name_of_model"] == solarpark1.name_of_model
# assert content[0]["size_in_sq_m"] == solarpark1.size_in_sq_m
# assert content[0]["peak_power"] == solarpark1.peak_power
# assert content[0]["first_detection"] == solarpark1.first_detection.strftime("%Y-%m-%d")
# assert content[0]["last_detection"] == solarpark1.last_detection.strftime("%Y-%m-%d")
# assert content[0]["avg_confidence_over_all_observations"] == solarpark1.avg_confidence_over_all_observations
# assert content[0]["name_in_aws"] == solarpark1.name_in_aws
# assert content[0]["is_valid"] == solarpark1.is_valid
# assert content[0]["comment"] == solarpark1.comment
# assert content[0]["lat"] == solarpark1.lat
# assert content[0]["lon"] == solarpark1.lon
# assert content[0]["geom"] == solarpark1.geom
# assert content[1]["name_of_model"] == solarpark2.name_of_model
# assert content[1]["size_in_sq_m"] == solarpark2.size_in_sq_m
# assert content[1]["peak_power"] == solarpark2.peak_power
# assert content[1]["first_detection"] == solarpark2.first_detection.strftime("%Y-%m-%d")
# assert content[1]["last_detection"] == solarpark2.last_detection.strftime("%Y-%m-%d")
# assert content[1]["avg_confidence_over_all_observations"] == solarpark2.avg_confidence_over_all_observations
# assert content[1]["name_in_aws"] == solarpark2.name_in_aws
# assert content[1]["is_valid"] == solarpark2.is_valid
# assert content[1]["comment"] == solarpark2.comment
# assert content[1]["lat"] == solarpark2.lat
# assert content[1]["lon"] == solarpark2.lon
# assert content[1]["geom"] == solarpark2.geom


def test_update_solarpark(client: TestClient, db: Session) -> None:
    solarpark = create_random_solarpark(db)
    data = {
        "name_of_model": ["Test"],
        "size_in_sq_m": 100.0,
        "peak_power": 100.0,
        "date_of_data": "2021-01-01",
        "first_detection": "2021-01-01",
        "last_detection": "2021-01-01",
        "avg_confidence_over_all_observations": 0.8,
        "name_in_aws": "Test",
        "is_valid": "None",
        "comment": "None",
        "lat": [599968.55, 599970.91, 599973.65, 599971.31, 599968.55],
        "lon": [5570202.63, 5570205.59, 5570203.42, 5570200.46, 5570202.63],
        "geom": "POLYGON ((599968.55 5570202.63, 599970.91 5570205.59, 599973.65 5570203.42, 599971.31 5570200.46, 599968.55 5570202.63))",
    }
    response = client.put(
        f"{settings.API_V1_STR}/solarpark/{solarpark.id}",
        # headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name_of_model"] == data["name_of_model"]
    assert content["size_in_sq_m"] == data["size_in_sq_m"]
    assert content["peak_power"] == data["peak_power"]
    assert content["first_detection"] == data["first_detection"]
    assert content["last_detection"] == data["last_detection"]
    assert (
        content["avg_confidence_over_all_observations"]
        == data["avg_confidence_over_all_observations"]
    )
    assert content["name_in_aws"] == data["name_in_aws"]
    assert content["is_valid"] == data["is_valid"]
    assert content["comment"] == data["comment"]
    assert content["lat"] == data["lat"]
    assert content["lon"] == data["lon"]
    assert content["geom"] == data["geom"]


def test_delete_solarpark(client: TestClient, db: Session) -> None:
    solarpark = create_random_solarpark(db)
    response = client.delete(
        f"{settings.API_V1_STR}/solarpark/{solarpark.id}",
        # headers=superuser_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["name_of_model"] == solarpark.name_of_model
    assert content["size_in_sq_m"] == solarpark.size_in_sq_m
    assert content["peak_power"] == solarpark.peak_power
    assert content["first_detection"] == solarpark.first_detection.strftime("%Y-%m-%d")
    assert content["last_detection"] == solarpark.last_detection.strftime("%Y-%m-%d")
    assert (
        content["avg_confidence_over_all_observations"]
        == solarpark.avg_confidence_over_all_observations
    )
    assert content["name_in_aws"] == solarpark.name_in_aws
    assert content["is_valid"] == solarpark.is_valid
    assert content["comment"] == solarpark.comment
    assert content["lat"] == solarpark.lat
    assert content["lon"] == solarpark.lon
    assert content["geom"] == solarpark.geom
