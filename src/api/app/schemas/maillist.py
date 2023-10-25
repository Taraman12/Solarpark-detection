# third-party
from pydantic import BaseModel, ConfigDict, EmailStr


class MailListBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: EmailStr


class MailList(MailListBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class MailListCreate(MailListBase):
    pass


class MailListUpdate(MailListBase):
    pass
