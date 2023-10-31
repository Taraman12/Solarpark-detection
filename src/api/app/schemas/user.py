from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = Field("example@mail.com")
    is_active: Optional[bool] = Field(True)
    is_superuser: bool = Field(False)
    full_name: Optional[str] = Field("John Doe")


# Properties to receive via API on creation
class UserCreate(UserBase):
    email: EmailStr
    password: str


# Properties to receive via API on update
class UserUpdate(UserBase):
    password: str


class UserInDBBase(UserBase):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)
    id: int


# Additional properties to return via API
class User(UserInDBBase):
    pass


# Additional properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str
