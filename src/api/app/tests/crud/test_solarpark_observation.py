from sqlalchemy.orm import Session

from app import crud

# from app.schemas.solarpark_observation import (
#     SolarParkObservationCreate,
#     SolarParkObservationUpdate,
# )
from app.tests.utils.solarpark_observation import random_solarpark_observation


def test_get_solarpark_observation(db: Session) -> None:
    solarpark_observation_in = random_solarpark_observation()
    solarpark_observation = crud.solarpark_observation.create(
        db, obj_in=solarpark_observation_in, solarpark_id=1
    )
    stored_solarpark_observation = crud.solarpark_observation.get(
        db, id=solarpark_observation.id
    )
    assert stored_solarpark_observation
    assert solarpark_observation.id == stored_solarpark_observation.id
    assert (
        solarpark_observation.name_of_model
        == stored_solarpark_observation.name_of_model
    )
    assert (
        solarpark_observation.date_of_data == stored_solarpark_observation.date_of_data
    )
    assert (
        solarpark_observation.size_in_sq_m == stored_solarpark_observation.size_in_sq_m
    )
    assert solarpark_observation.peak_power == stored_solarpark_observation.peak_power
    assert (
        solarpark_observation.avg_confidence
        == stored_solarpark_observation.avg_confidence
    )
    assert solarpark_observation.name_in_aws == stored_solarpark_observation.name_in_aws
    assert solarpark_observation.comment == stored_solarpark_observation.comment
    assert solarpark_observation.lat == stored_solarpark_observation.lat
    assert solarpark_observation.lon == stored_solarpark_observation.lon
    assert solarpark_observation.geom == stored_solarpark_observation.geom


# TODO: Fix this test
# NOTE: It fails, because the db is not properly cleaned up after each test
# def test_get_multi_solarpark_observation(db: Session) -> None:
#     solarpark_observation_in1 = random_solarpark_observation()
#     solarpark_observation_in2 = random_solarpark_observation()
#     solarpark_observation1 = crud.solarpark_observation.create(db, obj_in=solarpark_observation_in1)
#     solarpark_observation2 = crud.solarpark_observation.create(db, obj_in=solarpark_observation_in2)
#     stored_solarpark_observations = crud.solarpark_observation.get_multi(db)
#     assert stored_solarpark_observations
#     assert solarpark_observation1.id == stored_solarpark_observations[0].id
#     assert solarpark_observation1.name_of_model == stored_solarpark_observations[0].name_of_model
#     assert solarpark_observation1.date_of_data == stored_solarpark_observations[0].date_of_data
#     assert solarpark_observation1.size_in_sq_m == stored_solarpark_observations[0].size_in_sq_m
#     assert solarpark_observation1.peak_power == stored_solarpark_observations[0].peak_power
#     assert solarpark_observation1.avg_confidence == stored_solarpark_observations[0].avg_confidence
#     assert solarpark_observation1.name_in_aws == stored_solarpark_observations[0].name_in_aws
#     assert solarpark_observation1.comment == stored_solarpark_observations[0].comment
#     assert solarpark_observation1.lat == stored_solarpark_observations[0].lat
#     assert solarpark_observation1.lon == stored_solarpark_observations[0].lon
#     assert solarpark_observation1.geom == stored_solarpark_observations[0].geom
#     assert solarpark_observation2.id == stored_solarpark_observations[1].id
#     assert solarpark_observation2.name_of_model == stored_solarpark_observations[1].name_of_model
#     assert solarpark_observation2.date_of_data == stored_solarpark_observations[1].date_of_data
#     assert solarpark_observation2.size_in_sq_m == stored_solarpark_observations[1].size_in_sq_m
#     assert solarpark_observation2.peak_power == stored_solarpark


def test_create_solarpark_observation(db: Session) -> None:
    solarpark_observation_in = random_solarpark_observation()
    solarpark_observation = crud.solarpark_observation.create(
        db, obj_in=solarpark_observation_in, solarpark_id=1
    )
    assert solarpark_observation.name_of_model == solarpark_observation_in.name_of_model
    assert solarpark_observation.date_of_data == solarpark_observation_in.date_of_data
    assert solarpark_observation.size_in_sq_m == solarpark_observation_in.size_in_sq_m
    assert solarpark_observation.peak_power == solarpark_observation_in.peak_power
    assert (
        solarpark_observation.avg_confidence == solarpark_observation_in.avg_confidence
    )
    assert solarpark_observation.name_in_aws == solarpark_observation_in.name_in_aws
    assert solarpark_observation.comment == solarpark_observation_in.comment
    assert solarpark_observation.lat == solarpark_observation_in.lat
    assert solarpark_observation.lon == solarpark_observation_in.lon
    assert solarpark_observation.geom == solarpark_observation_in.geom


# def test_update_solarpark_observation(db: Session) -> None:


# ToDo: Update this test
# 1. Check if solarpark is updated
# 2. Check if this was the last observation, that solarpark is deleted
def test_delete_solarpark_observation(db: Session) -> None:
    solarpark_observation_in = random_solarpark_observation()
    solarpark_observation = crud.solarpark_observation.create(
        db, obj_in=solarpark_observation_in, solarpark_id=1
    )
    solarpark_observation2 = crud.solarpark_observation.remove(
        db, id=solarpark_observation.id
    )
    solarpark_observation3 = crud.solarpark_observation.get(
        db, id=solarpark_observation.id
    )
    assert solarpark_observation3 is None
    assert solarpark_observation2.id == solarpark_observation.id
    assert solarpark_observation2.name_of_model == solarpark_observation.name_of_model
    assert solarpark_observation2.date_of_data == solarpark_observation.date_of_data
    assert solarpark_observation2.size_in_sq_m == solarpark_observation.size_in_sq_m
    assert solarpark_observation2.peak_power == solarpark_observation.peak_power
    assert solarpark_observation2.avg_confidence == solarpark_observation.avg_confidence
    assert solarpark_observation2.name_in_aws == solarpark_observation.name_in_aws
    assert solarpark_observation2.comment == solarpark_observation.comment
    assert solarpark_observation2.lat == solarpark_observation.lat
    assert solarpark_observation2.lon == solarpark_observation.lon
    assert solarpark_observation2.geom == solarpark_observation.geom
