from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from datetime import date

from app import crud
from app.schemas.solarpark import SolarParkCreate, SolarParkUpdate
from app.tests.utils.utils import random_lower_string


def test_create_solarpark(db: Session) -> None:
    name_of_model = random_lower_string()
    size_in_sq_m = 100.0
    peak_power = 100.0
    date_of_data = date(2021, 1, 1)
    first_detection = date(2021, 1, 1)
    last_detection = date(2021, 1, 1)
    avg_confidence = 100.0
    name_in_aws = random_lower_string()
    is_valid = "None"
    comment = "None"
    lat = [1.0, 2.0]
    lon = [1.0, 2.0]
    solarpark_in = SolarParkCreate(
        name_of_model=name_of_model,
        size_in_sq_m=size_in_sq_m,
        peak_power=peak_power,
        date_of_data=date_of_data,
        first_detection=first_detection,
        last_detection=last_detection,
        avg_confidence=avg_confidence,
        name_in_aws=name_in_aws,
        is_valid=is_valid,
        comment=comment,
        lat=lat,
        lon=lon,
    )
    solarpark = crud.solarpark.create(db, obj_in=solarpark_in)
    assert solarpark.name_of_model == name_of_model
    assert solarpark.size_in_sq_m == size_in_sq_m
    assert solarpark.peak_power == peak_power
    assert solarpark.date_of_data == date_of_data
    assert solarpark.first_detection == first_detection
    assert solarpark.last_detection == last_detection
    assert solarpark.avg_confidence == avg_confidence
    assert solarpark.name_in_aws == name_in_aws
    assert solarpark.is_valid == is_valid
    assert solarpark.comment == comment
    assert solarpark.lat == lat
    assert solarpark.lon == lon

def test_get_solarpark(db: Session) -> None:
    name_of_model = random_lower_string()
    size_in_sq_m = 100.0
    peak_power = 100.0
    date_of_data = date(2021, 1, 1)
    first_detection = date(2021, 1, 1)
    last_detection = date(2021, 1, 1)
    avg_confidence = 100.0
    name_in_aws = random_lower_string()
    is_valid = "None"
    comment = "None"
    lat = [1.0, 2.0]
    lon = [1.0, 2.0]
    solarpark_in = SolarParkCreate(
        name_of_model=name_of_model,
        size_in_sq_m=size_in_sq_m,
        peak_power=peak_power,
        date_of_data=date_of_data,
        first_detection=first_detection,
        last_detection=last_detection,
        avg_confidence=avg_confidence,
        name_in_aws=name_in_aws,
        is_valid=is_valid,
        comment=comment,
        lat=lat,
        lon=lon,
    )
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
    assert solarpark.avg_confidence == stored_solarpark.avg_confidence
    assert solarpark.name_in_aws == stored_solarpark.name_in_aws
    assert solarpark.is_valid == stored_solarpark.is_valid
    assert solarpark.comment == stored_solarpark.comment
    assert solarpark.lat == stored_solarpark.lat
    assert solarpark.lon == stored_solarpark.lon

def test_update_solarpark(db: Session) -> None:
    name_of_model = random_lower_string()
    size_in_sq_m = 100.0
    peak_power = 100.0
    date_of_data = date(2021, 1, 1)
    first_detection = date(2021, 1, 1)
    last_detection = date(2021, 1, 1)
    avg_confidence = 100.0
    name_in_aws = random_lower_string()
    is_valid = "None"
    comment = "None"
    lat = [1.0, 2.0]
    lon = [1.0, 2.0]
    solarpark_in = SolarParkCreate(
        name_of_model=name_of_model,
        size_in_sq_m=size_in_sq_m,
        peak_power=peak_power,
        date_of_data=date_of_data,
        first_detection=first_detection,
        last_detection=last_detection,
        avg_confidence=avg_confidence,
        name_in_aws=name_in_aws,
        is_valid=is_valid,
        comment=comment,
        lat=lat,
        lon=lon,
    )
    solarpark = crud.solarpark.create(db, obj_in=solarpark_in)
    name_of_model2 = random_lower_string()
    size_in_sq_m2 = 200.0
    peak_power2 = 200.0
    date_of_data2 = date(2022, 2, 2)
    first_detection2 = date(2022, 2, 2)
    last_detection2 = date(2022, 2, 2)
    avg_confidence2 = 200.0
    name_in_aws2 = random_lower_string()
    is_valid2 = "None"
    comment2 = "None"
    lat2 = [3.0, 4.0]
    lon2 = [3.0, 4.0]
    solarpark_update = SolarParkUpdate(
        name_of_model=name_of_model2,
        size_in_sq_m=size_in_sq_m2,
        peak_power=peak_power2,
        date_of_data=date_of_data2,
        first_detection=first_detection2,
        last_detection=last_detection2,
        avg_confidence=avg_confidence2,
        name_in_aws=name_in_aws2,
        is_valid=is_valid2,
        comment=comment2,
        lat=lat2,
        lon=lon2,
    )
    solarpark2 = crud.solarpark.update(db, db_obj=solarpark, obj_in=solarpark_update)
    assert solarpark.id == solarpark2.id
    assert solarpark.name_of_model == solarpark2.name_of_model
    assert solarpark.size_in_sq_m == solarpark2.size_in_sq_m
    assert solarpark.peak_power == solarpark2.peak_power
    assert solarpark.date_of_data == solarpark2.date_of_data
    assert solarpark.first_detection == solarpark2.first_detection
    assert solarpark.last_detection == solarpark2.last_detection
    assert solarpark.avg_confidence == solarpark2.avg_confidence
    assert solarpark.name_in_aws == solarpark2.name_in_aws
    assert solarpark.is_valid == solarpark2.is_valid
    assert solarpark.comment == solarpark2.comment
    assert solarpark.lat == solarpark2.lat
    assert solarpark.lon == solarpark2.lon

def test_delete_solarpark(db: Session) -> None:
    name_of_model = random_lower_string()
    size_in_sq_m = 100.0
    peak_power = 100.0
    date_of_data = date(2021, 1, 1)
    first_detection = date(2021, 1, 1)
    last_detection = date(2021, 1, 1)
    avg_confidence = 100.0
    name_in_aws = random_lower_string()
    is_valid = "None"
    comment = "None"
    lat = [1.0, 2.0]
    lon = [1.0, 2.0]
    solarpark_in = SolarParkCreate(
        name_of_model=name_of_model,
        size_in_sq_m=size_in_sq_m,
        peak_power=peak_power,
        date_of_data=date_of_data,
        first_detection=first_detection,
        last_detection=last_detection,
        avg_confidence=avg_confidence,
        name_in_aws=name_in_aws,
        is_valid=is_valid,
        comment=comment,
        lat=lat,
        lon=lon,
    )
    solarpark = crud.solarpark.create(db, obj_in=solarpark_in)
    solarpark2 = crud.solarpark.remove(db, id=solarpark.id)
    solarpark3 = crud.solarpark.get(db, id=solarpark.id)
    assert solarpark3 is None
    assert solarpark2.id == solarpark.id
    assert solarpark2.name_of_model == solarpark.name_of_model
    assert solarpark2.size_in_sq_m == solarpark.size_in_sq_m
    assert solarpark2.peak_power == solarpark.peak_power
    assert solarpark2.date_of_data == solarpark.date_of_data
    assert solarpark2.first_detection == solarpark.first_detection
    assert solarpark2.last_detection == solarpark.last_detection
    assert solarpark2.avg_confidence == solarpark.avg_confidence
    assert solarpark2.name_in_aws == solarpark.name_in_aws
    assert solarpark2.is_valid == solarpark.is_valid
    assert solarpark2.comment == solarpark.comment
    assert solarpark2.lat == solarpark.lat
    assert solarpark2.lon == solarpark.lon
    