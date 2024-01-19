# build-in
from datetime import date
from enum import Enum
from typing import List  # Any, Sequence, Tuple, Union, TypeVar

# from geoalchemy2.types import Geometry
from geoalchemy2.types import WKBElement

# third-party
from pydantic import BaseModel, ConfigDict, Field

# from shapely.geometry import Polygon
from typing_extensions import Annotated  # , TypeAliasType

# from uuid import uuid4


# from geoalchemy2 import WKTElement


class Status(str, Enum):
    none = "None"
    valid = "valid"
    non_valid = "non-valid"
    unsure = "unsure"


class CustomStr(str):
    """Custom str."""

    pass


class SolarParkBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    name_of_model: List[str] = Field(["test-model"])
    size_in_sq_m: float = Field(100.0)
    peak_power: float = Field(10.0)
    first_detection: date = Field(date.today())
    last_detection: date = Field(date.today())
    avg_confidence_over_all_observations: float = Field(0.8)
    image_identifier: str = Field(
        "S2A_MSIL1C_20170105T013442_N0204_R031_T53NMJ_20170105T013443"
    )
    is_valid: Status = Field(Status.none)
    comment: str = "None"
    lat: List[float] = Field([599968.55, 599970.90, 599973.65, 599971.31, 599968.55])
    lon: List[float] = Field(
        [5570202.63, 5570205.59, 5570203.42, 5570200.46, 5570202.63]
    )
    geom: Annotated[str, WKBElement] = Field(
        "POLYGON ((599968.55 5570202.63, 599970.90 5570205.59, 599973.65 5570203.42, 599971.31 5570200.46, 599968.55 5570202.63))"
    )
    # WKTElement #Polygon


class SolarPark(SolarParkBase):
    id: int


class SolarParkCreate(SolarParkBase):
    pass


class SolarParkUpdate(SolarParkBase):
    pass
