# build-in
from typing import Any, List

# third-party
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

# local modules
from app import crud, models, schemas
from app.api_core import deps

router = APIRouter()
# The Docstring are shown in the Swagger UI as the description of the endpoint.


@router.get("/", response_model=List[schemas.SolarPark])
def read_solarpark(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 10000,  # 100 originally
) -> Any:
    """Retrieve solarpark."""
    solarpark = crud.solarpark.get_multi(db, skip=skip, limit=limit)
    if not solarpark:
        raise HTTPException(status_code=404, detail="No solarpark in DB")
    return solarpark


@router.get("/{id}", response_model=schemas.SolarPark)
def read_solarpark(*, db: Session = Depends(deps.get_db), id: int) -> Any:  # noqa: F811
    """Get solarpark by ID."""
    solarpark = crud.solarpark.get(db=db, id=id)
    if not solarpark:
        raise HTTPException(status_code=404, detail="solarpark not found")
    return solarpark


@router.delete("/", response_model=List[schemas.SolarPark])
def delete_all_solarparks(
    *,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """Delete all solarparks."""
    solarpark = crud.solarpark.remove_all(db=db)
    return solarpark


# @router.post("/", response_model=schemas.SolarPark)
# def create_solarpark(
#     *, db: Session = Depends(deps.get_db), solarpark_in: schemas.SolarParkCreate
# ) -> Any:
#     """Create new solarpark."""
#     solarpark = crud.solarpark.create(db=db, obj_in=solarpark_in)
#     return solarpark


# @router.put("/{id}", response_model=schemas.SolarPark)
# def update_solarpark(
#     *,
#     db: Session = Depends(deps.get_db),
#     id: int,
#     solarpark_in: schemas.SolarParkUpdate,
# ) -> Any:
#     """Update an solarpark."""
#     solarpark = crud.solarpark.get(db=db, id=id)
#     if not solarpark:
#         raise HTTPException(status_code=404, detail="solarpark not found")

#     solarpark = crud.solarpark.update(db=db, db_obj=solarpark, obj_in=solarpark_in)
#     return solarpark


# @router.delete("/{id}", response_model=schemas.SolarPark)
# def delete_solarpark(
#     *,
#     db: Session = Depends(deps.get_db),
#     id: int,
# ) -> Any:
#     """Delete an solarpark."""
#     solarpark = crud.solarpark.get(db=db, id=id)
#     if not solarpark:
#         raise HTTPException(status_code=404, detail="solarpark not found")
#     solarpark = crud.solarpark.remove(db=db, id=id)
#     return solarpark


@router.get("/download/as-geojson", response_class=StreamingResponse)
async def get_as_geojson(
    *,
    db: Session = Depends(deps.get_db),
) -> Any:
    """Retrieve all solar parks as geojson."""
    # response = crud.solarpark.get_geojson(db)
    # response.headers["Content-Disposition"] = "attachment; filename=geodata.geojson"
    # print(response)
    return crud.solarpark.get_as_geojson(db)  # response #crud.solarpark.get_geojson(db)


@router.post("/upload/as-geojson")
async def upload_as_geojson(
    *,
    db: Session = Depends(deps.get_db),
    file: UploadFile = File(...),
) -> Any:
    print("upload_as_geojson")
    print(file)
    """Upload geojson file."""
    # response.headers["Content-Disposition"] = "attachment; filename=geodata.geojson"
    message = await crud.solarpark.create_upload_file(db, file)
    return message


# @router.post("/check-overlap", response_model=schemas.SolarPark)
# def create_solarpark_with_check_overlap(
#     *, db: Session = Depends(deps.get_db), solarpark_in: schemas.SolarParkCreate
# ) -> Any:
#     # ToDo: Refactor this function and move to a util function

#     solarpark_id = crud.solarpark.check_overlap(db=db, obj_in=solarpark_in)
#     if solarpark_id is None:
#         solarpark = crud.solarpark.create(db=db, obj_in=solarpark_in)
#         return solarpark

#     solarpark_in.solarpark_id = solarpark_id
#     solarpark = crud.solarpark.create(db=db, obj_in=solarpark_in)
#     return solarpark
#     # print("create_solarpark_with_check_overlap")
#     # print(solarpark_in)
#     # existing_solarpark = db.query(SolarPark).filter(func.ST_Overlaps(SolarPark.geom, solarpark_in.geom))
#     # print(existing_solarpark)
#     """Upload geojson file."""
#     # response.headers["Content-Disposition"] = "attachment; filename=geodata.geojson"
#     # message = crud.solarpark.create_upload_file(db, file)
#     # return message
