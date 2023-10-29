# build-in
from typing import Any, List

# third-party
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# local modules
from app import crud, schemas
from app.api_core import deps
from app.crud.utils import check_overlap

router = APIRouter()


@router.get("/", response_model=List[schemas.SolarParkObservation])
def read_solarpark_observation(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 10000,  # 100 originally
    solarpark_id: int = None,
) -> Any:
    """Retrieve solarpark observation."""
    return crud.solarpark_observation.get_multi(
        db, skip=skip, limit=limit, solarpark_id=solarpark_id
    )


@router.get("/{id}", response_model=schemas.SolarParkObservation)
def read_solarpark_observation(  # noqa: F811
    *, db: Session = Depends(deps.get_db), id: int
) -> Any:
    """Get solarpark observation by ID."""

    solarpark_observation = crud.solarpark_observation.get(db=db, id=id)

    if not solarpark_observation:
        raise HTTPException(status_code=404, detail="solarpark observation not found")
    return solarpark_observation


@router.post("/", response_model=schemas.SolarParkObservation)
def create_solarpark_observation(
    *,
    db: Session = Depends(deps.get_db),
    solarpark_observation_in: schemas.SolarParkObservationCreate,
) -> Any:
    """Create new solarpark observation."""
    # if polygon is in solarpark, than use solarpark_id as foreign key
    # else create new solarpark and use solarpark_id as foreign key
    #
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
        # solve with event listener https://docs.sqlalchemy.org/en/20/orm/session_events.html
        solarpark_observation = crud.solarpark_observation.create(
            db=db, obj_in=solarpark_observation_in, solarpark_id=solarpark.id
        )
        # update solarpark

        # solarparks_in = crud.solarpark_observation.get_multi(db=db, skip=0, limit=10000, solarpark_id=solarpark.id)
    return solarpark_observation


@router.put("/{id}", response_model=schemas.SolarParkObservation)
def update_solarpark_observation(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    solarpark_observation_in: schemas.SolarParkObservationUpdate,
) -> Any:
    """Update an solarpark observation."""
    solarpark_observation = crud.solarpark_observation.get(db=db, id=id)
    if not solarpark_observation:
        raise HTTPException(status_code=404, detail="solarpark observation not found")

    solarpark_observation = crud.solarpark_observation.update(
        db=db, db_obj=solarpark_observation, obj_in=solarpark_observation_in
    )
    return solarpark_observation


@router.delete("/{id}", response_model=schemas.SolarParkObservation)
def delete_solarpark_observation(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
) -> Any:
    """Delete an solarpark observation."""
    solarpark_observation = crud.solarpark_observation.get(db=db, id=id)
    if not solarpark_observation:
        raise HTTPException(status_code=404, detail="solarpark observation not found")
    solarpark_observation = crud.solarpark_observation.remove(db=db, id=id)
    return solarpark_observation
