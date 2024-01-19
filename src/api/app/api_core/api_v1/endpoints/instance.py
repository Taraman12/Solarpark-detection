# build-in
from typing import Any, List

# third-party
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# local modules
from app import crud, models, schemas
from app.api_core import deps

router = APIRouter()

# TODO: add endpoint list all instances


@router.get("/", response_model=List[schemas.Instance])
def read_instance(  # noqa: F811
    *,
    db: Session = Depends(deps.get_db),
) -> Any:
    """Get instance."""
    instance = crud.instance.get_multi(db=db)
    if not instance:
        raise HTTPException(status_code=404, detail="No instance found")
    return instance


@router.get("/running-instances")
def read_running_instances(
    *,
    db: Session = Depends(deps.get_db),
) -> Any:
    """Get running instances."""
    instance = crud.instance.get_running_instances(db=db)
    if not instance:
        raise HTTPException(status_code=404, detail="instance not found")
    return instance


@router.get("/{id}", response_model=schemas.Instance)
def read_instance(  # noqa: F811
    *,
    db: Session = Depends(deps.get_db),
    id: int,
) -> Any:
    """Get instance by ID."""
    instance = crud.instance.get(db=db, id=id)
    if not instance:
        raise HTTPException(status_code=404, detail="instance not found")
    return instance


@router.get("/{service}", response_model=schemas.Instance)
def read_instance_by_service(  # noqa: F811
    *,
    db: Session = Depends(deps.get_db),
    service: str,
) -> Any:
    """Get instance by service."""
    instance = crud.instance.get_by_service(db=db, service=service)
    if not instance:
        raise HTTPException(status_code=404, detail="instance not found")
    return instance


@router.get("/{ec2_instance_id}", response_model=schemas.Instance)
def read_instance_by_ec2_instance_id(  # noqa: F811
    *,
    db: Session = Depends(deps.get_db),
    ec2_instance_id: str,
) -> Any:
    """Get instance by ec2_instance_id."""
    instance = crud.instance.get_by_ec2_instance_id(
        db=db, ec2_instance_id=ec2_instance_id
    )
    if not instance:
        raise HTTPException(status_code=404, detail="instance not found")
    return instance


@router.post("/", response_model=schemas.InstanceCreate)
def create(
    *,
    db: Session = Depends(deps.get_db),
    instance_in: schemas.InstanceCreate = Depends(),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """Shut down instance and start next instance"""
    instance = crud.instance.create(db=db, instance_in=instance_in)
    return instance


@router.put("/{id}", response_model=schemas.Instance)
def update_instance(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    instance_in: schemas.InstanceUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """Update an instance."""
    instance = crud.instance.get(db=db, id=id)
    if not instance:
        raise HTTPException(status_code=404, detail="instance not found")
    instance = crud.instance.update(db=db, db_obj=instance, obj_in=instance_in)
    return instance


@router.delete("/{id}", response_model=schemas.Instance)
def delete_instance_from_db(
    *,
    db: Session = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """Delete an instance from DB."""
    instance = crud.instance.get(db=db, id=id)
    if not instance:
        raise HTTPException(status_code=404, detail="instance not found")
    instance = crud.instance.remove(db=db, id=id)
    return instance


# FIXME: Fails, due to wrong response model
@router.post("/start/{instance_tag}")  # , response_model=schemas.Instance
def start_instance(
    *,
    db: Session = Depends(deps.get_db),
    instance_tag: str,
    instance_type: str = "t3.micro",
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """Start an instance."""
    instance = crud.instance.start_instance(
        db=db, instance_tag=instance_tag, instance_type=instance_type
    )
    return instance


# FIXME: maybe doesn't work
@router.delete("/terminate/{instance_id}")  # response_model=schemas.Instance
def terminate_instance_by_service(
    *,
    db: Session = Depends(deps.get_db),
    # service: str = "still InstanceID",
    instance_id: str,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """Terminate an instance."""
    # instance = crud.instance.get_by_service(db=db, service=service)
    # if not instance:
    #     raise HTTPException(status_code=404, detail="instance not found")
    instance = crud.instance.terminate_instance(db=db, instance_id=instance_id)
    return instance
