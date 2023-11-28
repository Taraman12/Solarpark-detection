from sqlalchemy.orm import Session

from app import crud

from app.schemas.solarpark import SolarParkUpdate
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
def test_get_multi_solarpark(db: Session) -> None:
    """
    needs to create two solarpark_observation objects to check if get_multi works
    """
    # solarpark_in1 = random_solarpark()
    # solarpark_in2 = random_solarpark()
    # solarpark1 = crud.solarpark.create(db, obj_in=solarpark_in1)
    # solarpark2 = crud.solarpark.create(db, obj_in=solarpark_in2)
    stored_solarparks = crud.solarpark.get_multi(db)
    assert len(stored_solarparks) > 1


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


def test_update_solarpark(db: Session) -> None:
    solarpark_in = random_solarpark()
    solarpark = crud.solarpark.create(db, obj_in=solarpark_in)
    solarpark_update = SolarParkUpdate(name_od_model=["Test-update"])
    solarpark2 = crud.solarpark.update(db, db_obj=solarpark, obj_in=solarpark_update)
    assert solarpark.id == solarpark2.id
    assert solarpark.name_of_model == solarpark2.name_of_model
    assert solarpark.size_in_sq_m == solarpark2.size_in_sq_m
    assert solarpark.peak_power == solarpark2.peak_power
    assert solarpark.first_detection == solarpark2.first_detection
    assert solarpark.last_detection == solarpark2.last_detection
    assert (
        solarpark.avg_confidence_over_all_observations
        == solarpark2.avg_confidence_over_all_observations
    )
    assert solarpark.name_in_aws == solarpark2.name_in_aws
    assert solarpark.is_valid == solarpark2.is_valid
    assert solarpark.comment == solarpark2.comment
    assert solarpark.lat == solarpark2.lat
    assert solarpark.lon == solarpark2.lon
    assert solarpark.geom == solarpark2.geom


# NOTE: solarparks should be deleted automatically when deleting all solarpark_observation with solarpark_id
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
