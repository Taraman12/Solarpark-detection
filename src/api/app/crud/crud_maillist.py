# local modules
from .base import CRUDBase
from app.models.maillist import MailList
from app.schemas.maillist import MailListCreate, MailListUpdate


class CRUDMailList(CRUDBase[MailList, MailListCreate, MailListUpdate]):
    pass


maillist = CRUDMailList(MailList)
