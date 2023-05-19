# build-in
import re
from pathlib import Path

# from dataclasses import dataclass
# from typing import Union

IMAGE_INPUT_DIR = Path(r".\data_raw")

MASK_INPUT_DIR = Path(
    r".\src\preprocessing\app\data\trn_polygons_germany_tile_names.geojson"
)

# NOTE will be created if not existent
IMAGE_OUTPUT_DIR = Path(r".\data_local\test_images_geotiff")
# NOTE will be created if not existent
MASK_OUTPUT_DIR = Path(r".\data_local\test_mask_patches")

IDENTIFIER_REGEX = re.compile(
    r"""(?P<mission>S2[A-B])_MSI
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


# @dataclass
# class BandFileMap:
#     B02: Union[Path, None]
#     B03: Union[Path, None]
#     B04: Union[Path, None]
#     B08: Union[Path, None]


# BAND_FILE_MAP = {
#     "B02": None,  # blue
#     "B03": None,  # green
#     "B04": None,  # red
#     "B08": None,  # NIR
# }

REQUIRED_BANDS = ["B02", "B03", "B04", "B08"]
