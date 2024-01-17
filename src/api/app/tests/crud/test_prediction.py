from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app import crud
from app.schemas.prediction import SolarParkObservationUpdate
from app.tests.utils.prediction import random_prediction

solarpark_id = 22


# @pytest.mark.anyio
def test_get_prediction(db: Session) -> None:
    prediction_in = random_prediction()
    prediction = crud.prediction.create(
        db, obj_in=prediction_in, solarpark_id=solarpark_id
    )
    stored_prediction = crud.prediction.get(db, id=prediction.id)
    assert stored_prediction
    assert prediction.id == stored_prediction.id
    assert prediction.name_of_model == stored_prediction.name_of_model
    assert prediction.date_of_data == stored_prediction.date_of_data
    assert prediction.size_in_sq_m == stored_prediction.size_in_sq_m
    assert prediction.peak_power == stored_prediction.peak_power
    assert prediction.avg_confidence == stored_prediction.avg_confidence
    assert prediction.image_identifier == stored_prediction.image_identifier
    assert prediction.comment == stored_prediction.comment
    assert prediction.lat == stored_prediction.lat
    assert prediction.lon == stored_prediction.lon
    assert prediction.geom == stored_prediction.geom


def test_get_multi_without_solarpark_id(db: Session) -> None:
    # Create some SolarParkObservation objects
    prediction_in1 = random_prediction()
    prediction_in2 = random_prediction()
    crud.prediction.create(db, obj_in=prediction_in1, solarpark_id=solarpark_id)
    crud.prediction.create(db, obj_in=prediction_in2, solarpark_id=solarpark_id)

    # Get multiple SolarParkObservation objects
    db_obj = crud.prediction.get_multi(db, skip=0, limit=10000)

    # Check if the correct number of objects was retrieved
    assert len(db_obj) >= 2


def test_get_multi_with_solarpark_id(db: Session) -> None:
    # Create some SolarParkObservation objects
    prediction_in1 = random_prediction()
    prediction_in2 = random_prediction()
    crud.prediction.create(db, obj_in=prediction_in1, solarpark_id=solarpark_id)
    crud.prediction.create(db, obj_in=prediction_in2, solarpark_id=solarpark_id)

    # Get multiple SolarParkObservation objects
    db_obj = crud.prediction.get_multi(
        db, skip=0, limit=10000, solarpark_id=solarpark_id
    )

    # Check if the correct number of objects was retrieved
    assert len(db_obj) >= 1

    # Check if the correct objects were retrieved
    for obj in db_obj:
        assert obj.solarpark_id == solarpark_id
        print(obj.geom)
        print(type(obj.geom))
        assert isinstance(obj.geom, str)


def test_update_prediction(db: Session) -> None:
    prediction_in = random_prediction()
    prediction = crud.prediction.create(
        db, obj_in=prediction_in, solarpark_id=solarpark_id
    )

    prediction_in = SolarParkObservationUpdate(name_of_model="Test-update")
    prediction2 = crud.prediction.update(db, db_obj=prediction, obj_in=prediction_in)
    assert prediction.id == prediction2.id
    assert prediction.name_of_model == prediction2.name_of_model
    assert prediction.date_of_data == prediction2.date_of_data
    assert prediction.size_in_sq_m == prediction2.size_in_sq_m
    assert prediction.peak_power == prediction2.peak_power
    assert prediction.avg_confidence == prediction2.avg_confidence
    assert prediction.image_identifier == prediction2.image_identifier
    assert prediction.comment == prediction2.comment
    assert prediction.lat == prediction2.lat
    assert prediction.lon == prediction2.lon
    assert prediction.geom == prediction2.geom


def test_get_as_geojson(db: Session) -> None:
    response = crud.prediction.get_as_geojson(db)

    # Check if the response is a StreamingResponse
    assert isinstance(response, StreamingResponse)

    # Check if the response headers are correct

    assert (
        response.headers["Content-Disposition"]
        == "attachment; filename=solar-parks.geojson"
    )


# def test_delete_solarpark(db: Session) -> None:
#     prediction_in = random_prediction()
#     prediction = crud.prediction.create(
#         db, obj_in=prediction_in, solarpark_id=1
#     )
#     prediction2 = crud.prediction.remove(
#         db, id=prediction.id
#     )
#     prediction3 = crud.prediction.get(
#         db, id=prediction.id
#     )
#     assert prediction3 is None
#     assert prediction2.id == prediction.id
#     assert prediction2.name_of_model == prediction.name_of_model
#     assert prediction2.date_of_data == prediction.date_of_data
#     assert prediction2.size_in_sq_m == prediction.size_in_sq_m
#     assert prediction2.peak_power == prediction.peak_power
#     assert prediction2.avg_confidence == prediction.avg_confidence
#     assert prediction2.image_identifier == prediction.image_identifier
#     assert prediction2.comment == prediction.comment
#     assert prediction2.lat == prediction.lat
#     assert prediction2.lon == prediction.lon
#     assert prediction2.geom == prediction.geom


# TODO: Fix this test
# NOTE: It fails, because the db is not properly cleaned up after each test
# def test_get_multi_prediction_by_solarpark_id(db: Session) -> None:
#     prediction_in1 = random_prediction()
#     prediction_in2 = random_prediction()
#     prediction1 = crud.prediction.create(
#         db, obj_in=prediction_in1, solarpark_id=1
#     )
#     prediction2 = crud.prediction.create(
#         db, obj_in=prediction_in2, solarpark_id=1
#     )

#     stored_predictions = crud.prediction.get_multi(db, solarpark_id=1)
#     assert stored_predictions
# assert stored_predictions
# assert prediction1.id == stored_predictions[0].id
# assert (
#     prediction1.name_of_model
#     == stored_predictions[0].name_of_model
# )
# assert (
#     prediction1.date_of_data
#     == stored_predictions[0].date_of_data
# )
# assert (
#     prediction1.size_in_sq_m
#     == stored_predictions[0].size_in_sq_m
# )
# assert (
#     prediction1.peak_power == stored_predictions[0].peak_power
# )
# assert (
#     prediction1.avg_confidence
#     == stored_predictions[0].avg_confidence
# )
# assert (
#     prediction1.image_identifier
#     == stored_predictions[0].image_identifier
# )
# assert prediction1.comment == stored_predictions[0].comment
# assert prediction1.lat == stored_predictions[0].lat
# assert prediction1.lon == stored_predictions[0].lon
# assert prediction1.geom == stored_predictions[0].geom
# assert prediction2.id == stored_predictions[1].id
# assert (
#     prediction2.name_of_model
#     == stored_predictions[1].name_of_model
# )
# assert (
#     prediction2.date_of_data
#     == stored_predictions[1].date_of_data
# )
# assert (
#     prediction2.size_in_sq_m
#     == stored_predictions[1].size_in_sq_m
# )
# assert prediction2.peak_power == stored_solarpark[1].peak_power
# assert (
#     prediction2.avg_confidence
#     == stored_predictions[1].avg_confidence
# )


# def test_create_prediction(db: Session) -> None:
#     prediction_in = random_prediction()
#     prediction = crud.prediction.create(
#         db, obj_in=prediction_in, solarpark_id=1
#     )
#     assert prediction.name_of_model == prediction_in.name_of_model
#     assert prediction.date_of_data == prediction_in.date_of_data
#     assert prediction.size_in_sq_m == prediction_in.size_in_sq_m
#     assert prediction.peak_power == prediction_in.peak_power
#     assert (
#         prediction.avg_confidence == prediction_in.avg_confidence
#     )
#     assert prediction.image_identifier == prediction_in.image_identifier
#     assert prediction.comment == prediction_in.comment
#     assert prediction.lat == prediction_in.lat
#     assert prediction.lon == prediction_in.lon
#     assert prediction.geom == prediction_in.geom


# def test_update_prediction(db: Session) -> None:


# ToDo: Update this test
# 1. Check if solarpark is updated
# 2. Check if this was the last observation, that solarpark is deleted
# def test_delete_prediction(db: Session) -> None:
#     prediction_in = random_prediction()
#     prediction = crud.prediction.create(
#         db, obj_in=prediction_in, solarpark_id=1
#     )
#     prediction2 = crud.prediction.remove(
#         db, id=prediction.id
#     )
#     prediction3 = crud.prediction.get(
#         db, id=prediction.id
#     )
#     assert prediction3 is None
#     assert prediction2.id == prediction.id
#     assert prediction2.name_of_model == prediction.name_of_model
#     assert prediction2.date_of_data == prediction.date_of_data
#     assert prediction2.size_in_sq_m == prediction.size_in_sq_m
#     assert prediction2.peak_power == prediction.peak_power
#     assert prediction2.avg_confidence == prediction.avg_confidence
#     assert prediction2.image_identifier == prediction.image_identifier
#     assert prediction2.comment == prediction.comment
#     assert prediction2.lat == prediction.lat
#     assert prediction2.lon == prediction.lon
#     assert prediction2.geom == prediction.geom
