from enum import Enum

from pydantic import BaseModel, ConfigDict


class Status(str, Enum):
    started = "started"
    running = "running"
    finished = "finished"
    error = "error"


class InstanceBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    status: Status = Status.started
    service: str = "None"
    ec2_instance_id: str = "None"

    # class Config:
    #     schema_extra = {
    #         "example": {
    #             "status": "finished",
    #             "service": "ml-serve",
    #             "ec2_instance_id": "i-0b22a22eec53b9321",
    #         }
    #     }
    # class Config:
    #     from_attributes = True


class Instance(InstanceBase):
    id: int


class InstanceCreate(InstanceBase):
    pass


class InstanceUpdate(InstanceBase):
    pass
