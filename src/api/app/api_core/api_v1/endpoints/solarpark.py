# build-in
from typing import Any, List

# third-party
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# local modules
from app import crud, models, schemas
from app.api_core import deps

router = APIRouter()


@router.get("/", response_model=List[schemas.SolarPark])
def read_solarpark(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    polygon: bool = False,
) -> Any:
    """
    Retrieve solarpark.
    """
    solarpark = crud.solarpark.get_multi(db, skip=skip, limit=limit)
    return solarpark


@router.get("/{id}", response_model=schemas.SolarPark)
def read_solarpark(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    polygon: bool = False,
) -> Any:
    """
    Get solarpark by ID.
    """
    solarpark = crud.solarpark.get(db=db, id=id)
    if not solarpark:
        raise HTTPException(status_code=404, detail="solarpark not found")
    return solarpark


@router.post("/", response_model=schemas.SolarPark)
def create_solarpark(
    *, db: Session = Depends(deps.get_db), solarpark_in: schemas.SolarParkCreate
) -> Any:
    """
    Create new solarpark.
    """
    solarpark = crud.solarpark.create(db=db, obj_in=solarpark_in)
    return solarpark


@router.put("/{id}", response_model=schemas.SolarPark)
def update_solarpark(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    solarpark_in: schemas.SolarParkUpdate,
) -> Any:
    """
    Update an solarpark.
    """
    solarpark = crud.solarpark.get(db=db, id=id)
    if not solarpark:
        raise HTTPException(status_code=404, detail="solarpark not found")

    solarpark = crud.solarpark.update(db=db, db_obj=solarpark, obj_in=solarpark_in)
    return solarpark


@router.delete("/{id}", response_model=schemas.SolarPark)
def delete_solarpark(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
) -> Any:
    """
    Delete an solarpark.
    """
    solarpark = crud.solarpark.get(db=db, id=id)
    if not solarpark:
        raise HTTPException(status_code=404, detail="solarpark not found")
    solarpark = crud.solarpark.remove(db=db, id=id)
    return solarpark
