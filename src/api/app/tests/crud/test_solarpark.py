from sqlalchemy.orm import Session

from app import crud

# from app.schemas.solarpark import SolarParkCreate, SolarParkUpdate
from app.tests.utils.solarpark import random_solarpark


def test_get_solarpark(db: Session) -> None:
    solarpark_in = random_solarpark()
    solarpark = crud.solarpark.create(db, obj_in=solarpark_in)
    stored_solarpark = crud.solarpark.get(db, id=solarpark.id)
    assert stored_solarpark
    assert solarpark.id == stored_solarpark.id
    assert solarpark.name_of_model == stored_solarpark.name_of_model
    assert solarpark.size_in_sq_m == stored_solarpark.size_in_sq_m
    assert solarpark.peak_power == stored_solarpark.peak_power
    assert solarpark.date_of_data == stored_solarpark.date_of_data
    assert solarpark.first_detection == stored_solarpark.first_detection
    assert solarpark.last_detection == stored_solarpark.last_detection
    assert (
        solarpark.avg_confidence_over_all_observations
        == stored_solarpark.avg_confidence_over_all_observations
    )
    assert solarpark.name_in_aws == stored_solarpark.name_in_aws
    assert solarpark.is_valid == stored_solarpark.is_valid
    assert solarpark.comment == stored_solarpark.comment
    assert solarpark.lat == stored_solarpark.lat
    assert solarpark.lon == stored_solarpark.lon
    assert solarpark.geom == stored_solarpark.geom


# TODO: Fix this test
# NOTE: It fails, because the db is not properly cleaned up after each test
# def test_get_multi_solarpark(db: Session) -> None:
#     solarpark_in1 = random_solarpark()
#     solarpark_in2 = random_solarpark()
#     solarpark1 = crud.solarpark.create(db, obj_in=solarpark_in1)
#     solarpark2 = crud.solarpark.create(db, obj_in=solarpark_in2)
#     stored_solarparks = crud.solarpark.get_multi(db)
#     print(f"solarpark1: {solarpark1.id}")
#     print(f"solarpark2: {solarpark2.id}")
#     print(f"stored_solarparks[0]: {stored_solarparks[0].id}")
#     print(f"stored_solarparks[1]: {stored_solarparks[1].id}")
#     assert stored_solarparks
#     assert solarpark1.id == stored_solarparks[0].id
#     assert solarpark1.name_of_model == stored_solarparks[0].name_of_model
#     assert solarpark1.size_in_sq_m == stored_solarparks[0].size_in_sq_m
#     assert solarpark1.peak_power == stored_solarparks[0].peak_power
#     assert solarpark1.date_of_data == stored_solarparks[0].date_of_data
#     assert solarpark1.first_detection == stored_solarparks[0].first_detection
#     assert solarpark1.last_detection == stored_solarparks[0].last_detection
#     assert (
#         solarpark1.avg_confidence_over_all_observations
#         == stored_solarparks[0].avg_confidence_over_all_observations
#     )
#     assert solarpark1.name_in_aws == stored_solarparks[0].name_in_aws
#     assert solarpark1.is_valid == stored_solarparks[0].is_valid
#     assert solarpark1.comment == stored_solarparks[0].comment
#     assert solarpark1.lat == stored_solarparks[0].lat
#     assert solarpark1.lon == stored_solarparks[0].lon
#     assert solarpark1.geom == stored_solarparks[0].geom
#     assert solarpark2.id == stored_solarparks[1].id
#     assert solarpark2.name_of_model == stored_solarparks[1].name_of_model
#     assert solarpark2.size_in_sq_m == stored_solarparks[1].size_in_sq_m
#     assert solarpark2.peak_power == stored_solarparks[1].peak_power
#     assert solarpark2.date_of_data == stored_solarparks[1].date_of_data
#     assert solarpark2.first_detection == stored_solarparks[1].first_detection
#     assert solarpark2.last_detection == stored_solarparks[1].last_detection
#     assert (
#         solarpark2.avg_confidence_over_all_observations
#         == stored_solarparks[1].avg_confidence_over_all_observations
#     )
#     assert solarpark2.name_in_aws == stored_solarparks[1].name_in_aws
#     assert solarpark2.is_valid == stored_solarparks[1].is_valid
#     assert solarpark2.comment == stored_solarparks[1].comment
#     assert solarpark2.lat == stored_solarparks[1].lat
#     assert solarpark2.lon == stored_solarparks[1].lon
#     assert solarpark2.geom == stored_solarparks[1].geom


def test_create_solarpark(db: Session) -> None:
    solarpark_in = random_solarpark()
    solarpark = crud.solarpark.create(db, obj_in=solarpark_in)
    assert solarpark.name_of_model == solarpark_in.name_of_model
    assert solarpark.size_in_sq_m == solarpark_in.size_in_sq_m
    assert solarpark.peak_power == solarpark_in.peak_power
    assert solarpark.first_detection == solarpark_in.first_detection
    assert solarpark.last_detection == solarpark_in.last_detection
    assert (
        solarpark.avg_confidence_over_all_observations
        == solarpark_in.avg_confidence_over_all_observations
    )
    assert solarpark.name_in_aws == solarpark_in.name_in_aws
    assert solarpark.is_valid == solarpark_in.is_valid
    assert solarpark.comment == solarpark_in.comment
    assert solarpark.lat == solarpark_in.lat
    assert solarpark.lon == solarpark_in.lon
    assert solarpark.geom == solarpark_in.geom


# TODO: Fix this test -> obj_in is not the correct type
# def test_update_solarpark(db: Session) -> None:
#     # name_of_model = random_lower_string()
#     # size_in_sq_m = 100.0
#     # peak_power = 100.0
#     # date_of_data = date(2021, 1, 1)
#     # first_detection = date(2021, 1, 1)
#     # last_detection = date(2021, 1, 1)
#     # avg_confidence = 100.0
#     # name_in_aws = random_lower_string()
#     # is_valid = "None"
#     # comment = "None"
#     # lat = [1.0, 2.0]
#     # lon = [1.0, 2.0]
#     # solarpark_in = SolarParkCreate(
#     #     name_of_model=name_of_model,
#     #     size_in_sq_m=size_in_sq_m,
#     #     peak_power=peak_power,
#     #     date_of_data=date_of_data,
#     #     first_detection=first_detection,
#     #     last_detection=last_detection,
#     #     avg_confidence=avg_confidence,
#     #     name_in_aws=name_in_aws,
#     #     is_valid=is_valid,
#     #     comment=comment,
#     #     lat=lat,
#     #     lon=lon,
#     # )
#     solarpark_in1 = random_solarpark()
#     solarpark = crud.solarpark.create(db, obj_in=solarpark_in1)
#     solarpark_in2 = random_solarpark()
#     solarpark2 = crud.solarpark.update(db, db_obj=solarpark, obj_in=solarpark_in2)
#     assert solarpark.id == solarpark2.id
#     assert solarpark.name_of_model == solarpark2.name_of_model
#     assert solarpark.size_in_sq_m == solarpark2.size_in_sq_m
#     assert solarpark.peak_power == solarpark2.peak_power
#     assert solarpark.first_detection == solarpark2.first_detection
#     assert solarpark.last_detection == solarpark2.last_detection
#     assert (
#         solarpark.avg_confidence_over_all_observations
#         == solarpark2.avg_confidence_over_all_observations
#     )
#     assert solarpark.name_in_aws == solarpark2.name_in_aws
#     assert solarpark.is_valid == solarpark2.is_valid
#     assert solarpark.comment == solarpark2.comment
#     assert solarpark.lat == solarpark2.lat
#     assert solarpark.lon == solarpark2.lon
#     assert solarpark.geom == solarpark2.geom


def test_delete_solarpark(db: Session) -> None:
    solarpark_in = random_solarpark()
    solarpark = crud.solarpark.create(db, obj_in=solarpark_in)
    solarpark2 = crud.solarpark.remove(db, id=solarpark.id)
    solarpark3 = crud.solarpark.get(db, id=solarpark.id)
    assert solarpark3 is None
    assert solarpark2.id == solarpark.id
    assert solarpark2.name_of_model == solarpark.name_of_model
    assert solarpark2.size_in_sq_m == solarpark.size_in_sq_m
    assert solarpark2.peak_power == solarpark.peak_power
    assert solarpark2.first_detection == solarpark.first_detection
    assert solarpark2.last_detection == solarpark.last_detection
    assert (
        solarpark2.avg_confidence_over_all_observations
        == solarpark.avg_confidence_over_all_observations
    )
    assert solarpark2.name_in_aws == solarpark.name_in_aws
    assert solarpark2.is_valid == solarpark.is_valid
    assert solarpark2.comment == solarpark.comment
    assert solarpark2.lat == solarpark.lat
    assert solarpark2.lon == solarpark.lon
    assert solarpark2.geom == solarpark.geom
