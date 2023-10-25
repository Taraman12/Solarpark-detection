# https://github.com/tiangolo/full-stack-fastapi-postgresql/blob/master/%7B%7Bcookiecutter.project_slug%7D%7D/backend/app/app/crud/__init__.py

from .crud_instance import instance  # noqa
from .crud_maillist import maillist  # noqa
from .crud_solarpark import solarpark  # noqa
from .crud_solarpark_observation import solarpark_observation  # noqa

# For a new basic set of CRUD operations you could just do

# from .base import CRUDBase
# from app.models.item import Item
# from app.schemas.item import ItemCreate, ItemUpdate

# item = CRUDBase[Item, ItemCreate, ItemUpdate](Item)
