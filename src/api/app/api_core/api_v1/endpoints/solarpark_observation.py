# build-in
from typing import Any, List

# third-party
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# local modules
from app import crud, schemas
from app.api_core import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.SolarParkObservation])
def read_solarpark_observation(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 10000,  # 100 originally
    solarpark_id: int = None,
) -> Any:
    """Retrieve solarpark observation."""
    if solarpark_id is not None:
        solarpark_observation = crud.solarpark_observation.get_multi_by_solarpark_id(
            db, solarpark_id=solarpark_id, skip=skip, limit=limit
        )
        return solarpark_observation
    return crud.solarpark_observation.get_multi(db, skip=skip, limit=limit)


@router.get("/{id}", response_model=schemas.SolarParkObservation)
def read_solarpark_observation(  # noqa: F811
    *, db: Session = Depends(deps.get_db), id: int
) -> Any:
    """Get solarpark observation by ID."""
    solarpark_observation = crud.solarpark_observation.get(db=db, id=id)
    print(solarpark_observation.__dict__)
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
    solarpark = crud.solarpark.check_overlap(db=db, obj_in=solarpark_observation_in)
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
        # ToDo: check if solarpark is created
        print(f"solarpark created:{solarpark}")
        solarpark_observation = crud.solarpark_observation.create(
            db=db, obj_in=solarpark_observation_in, solarpark_id=solarpark.id
        )
    else:
        # ToDo: Add solarpark update
        solarpark_observation = crud.solarpark_observation.create(
            db=db, obj_in=solarpark_observation_in, solarpark_id=solarpark.id
        )
        # crud.solarpark.update(db=db, db_obj=solarpark, obj_in=solarpark_observation_in)
    return solarpark_observation
