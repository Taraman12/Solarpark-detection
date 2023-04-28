# change constants here

# built-in
import re

# third-party
from datetime import date
from pathlib import Path

# NOTE file path can be created on the fly
DOWNLOAD_PATH = Path(r".\data_local\training_data_raw")

SEASONS_DICT = {
    "winter": {"start_date": date(2018, 1, 1), "end_date": date(2018, 3, 31)},
    "spring": {"start_date": date(2018, 4, 1), "end_date": date(2018, 6, 30)},
    "summer": {"start_date": date(2018, 7, 1), "end_date": date(2018, 9, 30)},
    "autumn": {"start_date": date(2018, 10, 1), "end_date": date(2018, 11, 30)},
}

IDENTIFIER_REGEX = re.compile(
    r"""^(?P<mission>S2[A-B])_MSI
                    (?P<product_level>L[1-2][A-C])_
                    (?P<sensing_time>\d{8}T\d{6})_
                    (?P<processing_baseline>N\d{4})_
                    (?P<relative_orbit>R\d{3})_T
                    (?P<utm_code>\d{2})
                    (?P<latitude_band>\w{1})
                    (?P<square>\w{2})_
                    (?P<year>\d{4})
                    (?P<month>\d{2})
                    (?P<day>\d{2})T
                    (?P<product_time>\d{6})""",
    re.VERBOSE,
)

BAND_FILE_MAP = {
    "B02": None,  # blue
    "B03": None,  # green
    "B04": None,  # red
    "B08": None,  # NIR
}
