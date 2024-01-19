# Import all the models, so that Base has them before being
# imported by Alembic
from app.db.base_class import Base  # noqa
from app.models.maillist import MailList  # noqa
from app.models.prediction import Prediction  # noqa
from app.models.solarpark import SolarPark  # noqa
