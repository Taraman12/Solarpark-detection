# local modules
from app.models.maillist import MailList
from app.schemas.maillist import MailListCreate, MailListUpdate

from .base import CRUDBase


class CRUDMailList(CRUDBase[MailList, MailListCreate, MailListUpdate]):
    pass


maillist = CRUDMailList(MailList)
