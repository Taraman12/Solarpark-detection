# third-party
from pydantic import BaseModel, EmailStr


class MailListBase(BaseModel):
    email: EmailStr

    class Config:
        orm_mode = True


class MailList(MailListBase):
    id: int

    class Config:
        orm_mode = True


class MailListCreate(MailListBase):
    pass


class MailListUpdate(MailListBase):
    pass
