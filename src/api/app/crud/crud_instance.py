# local modules
# import boto3
from builtins import NotImplementedError
from typing import Any, Dict, Optional

from fastapi import BackgroundTasks
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.cloud.aws import EC2_KWARGS, ec2_client
from app.crud.base import CRUDBase
from app.models.instance import Instance
from app.schemas.instance import InstanceCreate, InstanceUpdate


class CRUDInstance(CRUDBase[Instance, InstanceCreate, InstanceUpdate]):
    def get_by_service(self, db: Session, *, service: str) -> Instance:
        return db.query(self.model).filter(self.model.service == service).first()

    def get_by_ec2_instance_id(self, db: Session, *, ec2_instance_id: str) -> Instance:
        return (
            db.query(self.model)
            .filter(self.model.ec2_instance_id == ec2_instance_id)
            .first()
        )

    def create(self, db: Session, *, obj_in=InstanceCreate) -> Instance:
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)  # type: ignore
        if db_obj.status == "started":
            print("Instance started")
            db_obj.status = "running"

        elif db_obj.status == "finished":
            print("Instance finished")
            # ! shut down instance
            db_obj.status = "stopped"

        elif db_obj.status == "error":
            print("Instance error")
            # ! handle error
            # end instance
            # and start next instance
            # return {"status": "error"}

        else:
            raise NotImplementedError("Instance status not implemented")

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def start_instance(
        self, db: Session, *, service: str, instance_type: str = "t3.micro"
    ) -> str:
        # EC2_KWARGS = self.replace_instance_str(service, instance_type)
        print(EC2_KWARGS)
        response = ec2_client.run_instances(**EC2_KWARGS)
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            obj_in = {
                "status": "started",
                "service": service,
                "ec2_instance_id": response["Instances"][0]["InstanceId"],
            }
            db_obj = self.create(db, obj_in=obj_in)
            return db_obj

    def replace_instance_str(self, service: str, instance_type: str):
        EC2_KWARGS["InstanceType"] = instance_type
        EC2_KWARGS["UserData"] = EC2_KWARGS["UserData"].replace(
            "SERVICE_PLACEHOLDER", service
        )
        EC2_KWARGS["TagSpecifications"][0]["Tags"][0]["Value"] = EC2_KWARGS[
            "TagSpecifications"
        ][0]["Tags"][0]["Value"].replace("SERVICE_PLACEHOLDER", service)
        return EC2_KWARGS

    def terminate_instance_by_ec2_instance_id(
        self, db: Session, *, ec2_instance_id: str
    ) -> Any:
        response = ec2_client.terminate_instances(InstanceIds=[ec2_instance_id])
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            response = self.remove(db=db, id=instance.id)
        else:
            logging.error("Instance not terminated")
        return response

    def wait_for_instance_termination(ec2, instance_id):
        """
        Wartet auf die Terminierung einer EC2-Instanz.

        Args:
            ec2: Ein Boto3 EC2-Client.
            instance_id: Die ID der EC2-Instanz.

        Returns:
            None.
        """
        while True:
            response = ec2.describe_instances(InstanceIds=[instance_id])
            instance_status = response["Reservations"][0]["Instances"][0]["State"][
                "Name"
            ]
            if instance_status == "terminated":
                print(f"Instance {instance_id} terminated successfully.")
                break
            else:
                print(f"Instance {instance_id} is still {instance_status}. Waiting...")
                time.sleep(5)


instance = CRUDInstance(Instance)
