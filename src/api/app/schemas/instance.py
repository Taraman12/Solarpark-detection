from enum import Enum
from typing import Literal

from pydantic import BaseModel


class Status(str, Enum):
    started = "started"
    running = "running"
    finished = "finished"
    error = "error"


class InstanceBase(BaseModel):
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
    class Config:
        orm_mode = True


class Instance(InstanceBase):
    id: int


class InstanceCreate(InstanceBase):
    pass


class InstanceUpdate(InstanceBase):
    pass
