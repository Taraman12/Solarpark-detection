# NOTE: Note used at the moment
# from sqlalchemy.orm import Session
# from fastapi.testclient import TestClient
# from datetime import date

# from app import crud
# from app.schemas.instance import InstanceCreate, InstanceUpdate
# from app.tests.utils.utils import random_lower_string


# def test_create_instance_started(db: Session) -> None:
#     status = "started"
#     service = random_lower_string()
#     ec2_instance_id = random_lower_string()
#     instance_in = InstanceCreate(
#         status=status,
#         service=service,
#         ec2_instance_id=ec2_instance_id,
#     )
#     instance = crud.instance.create(db, obj_in=instance_in)
#     assert instance.status == status
#     assert instance.service == service
#     assert instance.ec2_instance_id == ec2_instance_id

# def test_create_instance_error(db: Session) -> None:
#     status = "error"
#     service = random_lower_string()
#     ec2_instance_id = random_lower_string()
#     instance_in = InstanceCreate(
#         status=status,
#         service=service,
#         ec2_instance_id=ec2_instance_id,
#     )
#     instance = crud.instance.create(db, obj_in=instance_in)
#     assert instance.status == status
#     assert instance.service == service
#     assert instance.ec2_instance_id == ec2_instance_id


# def test_get_instance(db: Session) -> None:
#     status = "started"
#     service = random_lower_string()
#     ec2_instance_id = random_lower_string()
#     instance_in = InstanceCreate(
#         status=status,
#         service=service,
#         ec2_instance_id=ec2_instance_id,
#     )
#     instance = crud.instance.create(db, obj_in=instance_in)
#     stored_instance = crud.instance.get(db, id=instance.id)
#     assert stored_instance
#     assert instance.id == stored_instance.id
#     assert instance.status == stored_instance.status
#     assert instance.service == stored_instance.service
#     assert instance.ec2_instance_id == stored_instance.ec2_instance_id


# def test_get_instance_by_service(db: Session) -> None:
#     status = random_lower_string()
#     service = random_lower_string()
#     ec2_instance_id = random_lower_string()
#     instance_in = InstanceCreate(
#         status=status,
#         service=service,
#         ec2_instance_id=ec2_instance_id,
#     )
#     instance = crud.instance.create(db, obj_in=instance_in)
#     stored_instance = crud.instance.get_by_service(db, service=instance.service)
#     assert stored_instance
#     assert instance.id == stored_instance.id
#     assert instance.status == stored_instance.status
#     assert instance.service == stored_instance.service
#     assert instance.ec2_instance_id == stored_instance.ec2_instance_id


# def test_get_instance_by_ec2_instance_id(db: Session) -> None:
#     status = random_lower_string()
#     service = random_lower_string()
#     ec2_instance_id = random_lower_string()
#     instance_in = InstanceCreate(
#         status=status,
#         service=service,
#         ec2_instance_id=ec2_instance_id,
#     )
#     instance = crud.instance.create(db, obj_in=instance_in)
#     stored_instance = crud.instance.get_by_ec2_instance_id(
#         db, ec2_instance_id=instance.ec2_instance_id
#     )
#     assert stored_instance
#     assert instance.id == stored_instance.id
#     assert instance.status == stored_instance.status
#     assert instance.service == stored_instance.service
#     assert instance.ec2_instance_id == stored_instance.ec2_instance_id


# def test_update_instance(db: Session) -> None:
#     status = random_lower_string()
#     service = random_lower_string()
#     ec2_instance_id = random_lower_string()
#     instance_in = InstanceCreate(
#         status=status,
#         service=service,
#         ec2_instance_id=ec2_instance_id,
#     )
#     instance = crud.instance.create(db, obj_in=instance_in)
#     status2 = random_lower_string()
#     service2 = random_lower_string()
#     ec2_instance_id2 = random_lower_string()
#     instance_update = InstanceUpdate(
#         status=status2,
#         service=service2,
#         ec2_instance_id=ec2_instance_id2,
#     )
#     instance2 = crud.instance.update(db, db_obj=instance, obj_in=instance_update)
#     assert instance.id == instance2.id
#     assert instance.status == instance2.status
#     assert instance.service == instance2.service
#     assert instance.ec2_instance_id == instance2.ec2_instance_id


# def test_delete_instance(db: Session) -> None:
#     status = random_lower_string()
#     service = random_lower_string()
#     ec2_instance_id = random_lower_string()
#     instance_in = InstanceCreate(
#         status=status,
#         service=service,
#         ec2_instance_id=ec2_instance_id,
#     )
#     instance = crud.instance.create(db, obj_in=instance_in)
#     instance2 = crud.instance.remove(db, id=instance.id)
#     instance3 = crud.instance.get(db, id=instance.id)
#     assert instance3 is None
#     assert instance2.id == instance.id
#     assert instance2.status == status
#     assert instance2.service == service
#     assert instance2.ec2_instance_id == ec2_instance_id
