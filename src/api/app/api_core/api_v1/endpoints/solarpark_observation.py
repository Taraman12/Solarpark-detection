# build-in
from typing import Any, List, Generator
from statistics import mean

# third-party
from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from sqlalchemy import event
from geoalchemy2.shape import to_shape

# local modules
from app import crud, models, schemas
from app.api_core import deps
from app.crud.utils import check_overlap
from app.db.session import SessionLocal, engine


router = APIRouter()


@router.get("/", response_model=List[schemas.SolarParkObservation])
def read_solarpark_observation(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 10000,  # 100 originally
    solarpark_id: int = None,
) -> Any:
    """Retrieve solarpark observation."""
    solarpark_observation = crud.solarpark_observation.get_multi(
        db, skip=skip, limit=limit, solarpark_id=solarpark_id
    )
    if not solarpark_observation:
        raise HTTPException(status_code=404, detail="No solarpark observation in DB")
    return solarpark_observation


@router.get("/{id}", response_model=schemas.SolarParkObservation)
def read_solarpark_observation(  # noqa: F811
    *, db: Session = Depends(deps.get_db), id: int
) -> Any:
    """Get solarpark observation by ID."""

    solarpark_observation = crud.solarpark_observation.get(db=db, id=id)

    if not solarpark_observation:
        raise HTTPException(status_code=404, detail="solarpark observation not found")
    return solarpark_observation


# @router.get("/{solarpark_id}", response_model=List[schemas.SolarParkObservation])
# def read_solarpark_observation_by_solarpark_id(  # noqa: F811
#     *, db: Session = Depends(deps.get_db), solarpark_id: int
# ) -> Any:
#     """Get solarpark observation by solarpark ID."""
#     print("solarpark_id", solarpark_id)
#     solarpark_observation = crud.solarpark_observation.get_multi(
#         db=db, solarpark_id=solarpark_id
#     )


@router.post("/", response_model=schemas.SolarParkObservation)
def create_solarpark_observation(
    *,
    db: Session = Depends(deps.get_db),
    solarpark_observation_in: schemas.SolarParkObservationCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser)
) -> Any:
    """Create new solarpark observation."""
    # if polygon is in solarpark, than use solarpark_id as foreign key
    # else create new solarpark and use solarpark_id as foreign key

    solarpark = check_overlap(db=db, obj_in=solarpark_observation_in)

    if solarpark is None:
        # TODO: move to utils
        solarpark_in = vars(solarpark_observation_in).copy()
        unwanted_keys = ["name_of_model", "avg_confidence", "date_of_data"]
        for key in unwanted_keys:
            solarpark_in.pop(key, None)
        solarpark_in["name_of_model"] = [solarpark_observation_in.name_of_model]
        solarpark_in["first_detection"] = solarpark_observation_in.date_of_data
        solarpark_in["last_detection"] = solarpark_observation_in.date_of_data
        solarpark_in[
            "avg_confidence_over_all_observations"
        ] = solarpark_observation_in.avg_confidence

        solarpark = crud.solarpark.create(db=db, obj_in=solarpark_in)
        if not solarpark:
            raise HTTPException(
                status_code=404, detail="solarpark could not be created"
            )
        solarpark_observation = crud.solarpark_observation.create(
            db=db, obj_in=solarpark_observation_in, solarpark_id=solarpark.id
        )
        return solarpark_observation
    else:
        # ToDo: Add solarpark update
        # * shouldn't be updated if solarpark update fails
        # solve with event listener https://docs.sqlalchemy.org/en/20/orm/session_events.html
        solarpark_observation = crud.solarpark_observation.create(
            db=db, obj_in=solarpark_observation_in, solarpark_id=solarpark.id
        )

        solarpark = crud.solarpark.get(db=db, id=solarpark.id)

        solarpark_update = update_solarpark(db=db, solarpark=solarpark)
        solarpark = crud.solarpark.update(
            db=db, db_obj=solarpark, obj_in=solarpark_update
        )
        # shouldn't be necessary (crud returns solarpark with wkt)
        solarpark_observation.geom = to_shape(solarpark_observation.geom).wkt

    return solarpark_observation


@router.put("/{id}", response_model=schemas.SolarParkObservation)
def update_solarpark_observation(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    solarpark_observation_in: schemas.SolarParkObservationUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser)
) -> Any:
    """Update an solarpark observation."""
    solarpark_observation = crud.solarpark_observation.get(db=db, id=id)
    if not solarpark_observation:
        raise HTTPException(status_code=404, detail="solarpark observation not found")

    solarpark_observation = crud.solarpark_observation.update(
        db=db, db_obj=solarpark_observation, obj_in=solarpark_observation_in
    )
    # print(solarpark_observation.solarpark)
    # solarpark_update = update_solarpark(
    #     db=db, solarpark=solarpark_observation.solarpark
    # )
    # solarpark = crud.solarpark.update(
    #     db=db, db_obj=solarpark_observation.solarpark, obj_in=solarpark_update
    # )
    return solarpark_observation


@router.delete("/{id}", response_model=schemas.SolarParkObservation)
def delete_solarpark_observation(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser)
) -> Any:
    """Delete an solarpark observation."""
    solarpark_observation = crud.solarpark_observation.get(db=db, id=id)
    if not solarpark_observation:
        raise HTTPException(status_code=404, detail="solarpark observation not found")
    solarpark_observation = crud.solarpark_observation.remove(db=db, id=id)
    return solarpark_observation


# ToDo: get as geojson

# ToDo:post as geojson


@router.delete("/", response_model=List[schemas.SolarParkObservation])
def delete_all_solarpark_observation(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser)
) -> Any:
    """Delete all solarpark observation."""
    solarpark_observation = crud.solarpark_observation.remove_all(db=db)
    return solarpark_observation


# @event.listens_for(models.SolarParkObservation, "after_insert")
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
# solarpark_observation = crud.solarpark_observation.get_multi(
#     db=db, solarpark_id=solarpark_id
# )
# solarpark = crud.solarpark.get(db=db, id=solarpark_id)

# # all unique solarpark names
# name_of_models = [item.name_of_model for item in solarpark_observation]
# solarpark.name_of_model = set(name_of_models)
# # ! maybe rename?
# # size_in_sq_m
# size_in_sq_m = [item.size_in_sq_m for item in solarpark_observation]
# solarpark.size_in_sq_m = mean(size_in_sq_m)

# # peak_power
# peak_power = [item.peak_power for item in solarpark_observation]
# solarpark.peak_power = mean(peak_power)

# # first detection
# first_detection = [item.date_of_data for item in solarpark_observation]
# solarpark.first_detection = min(first_detection)

# # last detection
# last_detection = [item.date_of_data for item in solarpark_observation]
# solarpark.last_detection = max(last_detection)

# # average confidence
# avg_confidence = [item.avg_confidence for item in solarpark_observation]
# solarpark.avg_confidence_over_all_observations = mean(avg_confidence)

# db.add(solarpark)
# db.commit()
# db.refresh(solarpark)
# db.close()


# @event.listens_for(models.SolarParkObservation, "after_update")
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
    solarpark_observation = crud.solarpark_observation.get_multi(
        db=db, solarpark_id=solarpark.id
    )
    # solarpark_observation = solarpark.observations
    # print("solarpark_observations", solarpark_observation)
    name_of_models = [item.name_of_model for item in solarpark_observation]
    # ! maybe rename?
    size_in_sq_m = [item.size_in_sq_m for item in solarpark_observation]

    peak_power = [item.peak_power for item in solarpark_observation]

    first_detection = [item.date_of_data for item in solarpark_observation]

    last_detection = [item.date_of_data for item in solarpark_observation]

    avg_confidence = [item.avg_confidence for item in solarpark_observation]

    solarpark_update = schemas.SolarParkUpdate(
        name_of_model=set(name_of_models),
        size_in_sq_m=mean(size_in_sq_m),
        peak_power=mean(peak_power),
        first_detection=min(first_detection),
        last_detection=max(last_detection),
        avg_confidence_over_all_observations=mean(avg_confidence),
    )
    return solarpark_update
