# build-in
from statistics import mean
from typing import Any, List

# third-party
from fastapi import APIRouter, Depends, HTTPException
from geoalchemy2.shape import to_shape

# from sqlalchemy import event
from sqlalchemy.orm import Session

# local modules
from app import crud, models, schemas
from app.api_core import deps
from app.crud.utils import check_overlap

router = APIRouter()


@router.get("/", response_model=List[schemas.Prediction])
def read_prediction(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 10000,  # 100 originally
    solarpark_id: int = None,
) -> Any:
    """Retrieve solarpark observation."""
    prediction = crud.prediction.get_multi(
        db, skip=skip, limit=limit, solarpark_id=solarpark_id
    )
    if not prediction:
        raise HTTPException(status_code=404, detail="No solarpark observation in DB")
    return prediction


@router.get("/{id}", response_model=schemas.Prediction)
def read_prediction(  # noqa: F811
    *, db: Session = Depends(deps.get_db), id: int
) -> Any:
    """Get solarpark observation by ID."""

    prediction = crud.prediction.get(db=db, id=id)

    if not prediction:
        raise HTTPException(status_code=404, detail="solarpark observation not found")
    return prediction


# @router.get("/{solarpark_id}", response_model=List[schemas.Prediction])
# def read_prediction_by_solarpark_id(  # noqa: F811
#     *, db: Session = Depends(deps.get_db), solarpark_id: int
# ) -> Any:
#     """Get solarpark observation by solarpark ID."""
#     print("solarpark_id", solarpark_id)
#     prediction = crud.prediction.get_multi(
#         db=db, solarpark_id=solarpark_id
#     )


@router.post("/", response_model=schemas.Prediction)
def create_prediction(
    *,
    db: Session = Depends(deps.get_db),
    prediction_in: schemas.PredictionCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser)
) -> Any:
    """Create new solarpark observation."""
    # if polygon is in solarpark, than use solarpark_id as foreign key
    # else create new solarpark and use solarpark_id as foreign key

    solarpark = check_overlap(db=db, obj_in=prediction_in)

    if solarpark is None:
        # TODO: move to utils
        solarpark_in = vars(prediction_in).copy()
        unwanted_keys = ["name_of_model", "avg_confidence", "date_of_data"]
        for key in unwanted_keys:
            solarpark_in.pop(key, None)
        solarpark_in["name_of_model"] = [prediction_in.name_of_model]
        solarpark_in["first_detection"] = prediction_in.date_of_data
        solarpark_in["last_detection"] = prediction_in.date_of_data
        solarpark_in[
            "avg_confidence_over_all_observations"
        ] = prediction_in.avg_confidence

        solarpark = crud.solarpark.create(db=db, obj_in=solarpark_in)
        if not solarpark:
            raise HTTPException(
                status_code=404, detail="solarpark could not be created"
            )
        prediction = crud.prediction.create(
            db=db, obj_in=prediction_in, solarpark_id=solarpark.id
        )
        return prediction
    else:
        # ToDo: Add solarpark update
        # * shouldn't be updated if solarpark update fails
        # solve with event listener https://docs.sqlalchemy.org/en/20/orm/session_events.html
        prediction = crud.prediction.create(
            db=db, obj_in=prediction_in, solarpark_id=solarpark.id
        )

        solarpark = crud.solarpark.get(db=db, id=solarpark.id)

        solarpark_update = update_solarpark(db=db, solarpark=solarpark)
        solarpark = crud.solarpark.update(
            db=db, db_obj=solarpark, obj_in=solarpark_update
        )
        # shouldn't be necessary (crud returns solarpark with wkt)
        prediction.geom = to_shape(prediction.geom).wkt

    return prediction


@router.put("/{id}", response_model=schemas.Prediction)
def update_prediction(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    prediction_in: schemas.PredictionUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser)
) -> Any:
    """Update an solarpark observation."""
    prediction = crud.prediction.get(db=db, id=id)
    if not prediction:
        raise HTTPException(status_code=404, detail="solarpark observation not found")

    prediction = crud.prediction.update(db=db, db_obj=prediction, obj_in=prediction_in)
    # print(prediction.solarpark)
    # solarpark_update = update_solarpark(
    #     db=db, solarpark=prediction.solarpark
    # )
    # solarpark = crud.solarpark.update(
    #     db=db, db_obj=prediction.solarpark, obj_in=solarpark_update
    # )
    return prediction


@router.delete("/{id}", response_model=schemas.Prediction)
def delete_prediction(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser)
) -> Any:
    """Delete an solarpark observation."""
    prediction = crud.prediction.get(db=db, id=id)
    if not prediction:
        raise HTTPException(status_code=404, detail="solarpark observation not found")
    prediction = crud.prediction.remove(db=db, id=id)
    return prediction


# ToDo: get as geojson

# ToDo:post as geojson


@router.delete("/", response_model=List[schemas.Prediction])
def delete_all_prediction(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser)
) -> Any:
    """Delete all solarpark observation."""
    prediction = crud.prediction.remove_all(db=db)
    return prediction


# @event.listens_for(models.Prediction, "after_insert")
# def receive_after_insert(mapper, connection, target, **kwargs):
#     # db = Session(bind=engine)
#     print("after_insert")
#     solarpark_id = target.solarpark_id
#     with Session(bind=engine) as db:
#         solarpark = update_solarpark(db=db, solarpark_id=solarpark_id)
#         db.add(solarpark)
#         db.commit()
#         db.refresh(solarpark)
#         db.close()
# solarpark_id = target.solarpark_id
# solarpark = update_solarpark(db=db, solarpark_id=solarpark_id)
# prediction = crud.prediction.get_multi(
#     db=db, solarpark_id=solarpark_id
# )
# solarpark = crud.solarpark.get(db=db, id=solarpark_id)

# # all unique solarpark names
# name_of_models = [item.name_of_model for item in prediction]
# solarpark.name_of_model = set(name_of_models)
# # ! maybe rename?
# # size_in_sq_m
# size_in_sq_m = [item.size_in_sq_m for item in prediction]
# solarpark.size_in_sq_m = mean(size_in_sq_m)

# # peak_power
# peak_power = [item.peak_power for item in prediction]
# solarpark.peak_power = mean(peak_power)

# # first detection
# first_detection = [item.date_of_data for item in prediction]
# solarpark.first_detection = min(first_detection)

# # last detection
# last_detection = [item.date_of_data for item in prediction]
# solarpark.last_detection = max(last_detection)

# # average confidence
# avg_confidence = [item.avg_confidence for item in prediction]
# solarpark.avg_confidence_over_all_observations = mean(avg_confidence)

# db.add(solarpark)
# db.commit()
# db.refresh(solarpark)
# db.close()


# @event.listens_for(models.Prediction, "after_update")
# def receive_after_update(mapper, connection, target, **kwargs):
#     print("after_update")
#     solarpark_id = target.solarpark_id
#     with Session(bind=engine) as db:
#         print("db", db)
#         solarpark = update_solarpark(db=db, solarpark_id=solarpark_id)
#         print("solarpark", solarpark)
#         db.add(solarpark)
#         db.commit()
#         db.refresh(solarpark)
#         # db.close()


def update_solarpark(
    db: Session,
    solarpark: schemas.SolarPark,
) -> schemas.SolarParkUpdate:
    prediction = crud.prediction.get_multi(db=db, solarpark_id=solarpark.id)
    # prediction = solarpark.observations
    # print("predictions", prediction)
    name_of_models = [item.name_of_model for item in prediction]
    # ! maybe rename?
    size_in_sq_m = [item.size_in_sq_m for item in prediction]

    peak_power = [item.peak_power for item in prediction]

    first_detection = [item.date_of_data for item in prediction]

    last_detection = [item.date_of_data for item in prediction]

    avg_confidence = [item.avg_confidence for item in prediction]

    solarpark_update = schemas.SolarParkUpdate(
        name_of_model=set(name_of_models),
        size_in_sq_m=mean(size_in_sq_m),
        peak_power=mean(peak_power),
        first_detection=min(first_detection),
        last_detection=max(last_detection),
        avg_confidence_over_all_observations=mean(avg_confidence),
    )
    return solarpark_update
