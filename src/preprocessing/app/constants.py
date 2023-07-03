# build-in
import re
from pathlib import Path

from settings import API_HOST, ML_HOST

# where will the images be stored/ name of the folder in s3 bucket
IMAGE_INPUT_DIR = Path(r"data_raw")
# IMAGE_INPUT_DIR = Path(r".\data_local\training_data_raw")

# prefix of the images in the s3 bucket
# FIXME: used, but doesn't have an impact
IMAGES_WITH_SOLARPARK = Path(r"images_with_solarpark")

SCRIPT_DIR = Path(__file__).resolve().parent
MASK_INPUT_DIR = SCRIPT_DIR / "data" / "trn_polygons_germany_tile_names.geojson"

# NOTE will be created if not existent
IMAGE_OUTPUT_DIR = Path(r".\data_local\images_undersampling")

# NOTE will be created if not existent
MASK_OUTPUT_DIR = Path(r".\data_local\mask_undersampling")

KERNEL_SIZE = 256
PADDING = 25
UNDERSAMPLING_RATE = 0.05


URL_ML = f"http://{ML_HOST}:8080"  # ml-serve
URL_API = f"http://{API_HOST}:8000/api/v1"  # api


MODEL_NAME = "solar-park-detection"
HEADERS = {"Content-Type": "application/json"}

BUCKET_NAME = "solar-detection-697553-eu-central-1"

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


# NOTE if you change this, you have to change in save_to_disk.py -> stack_bands() as well (due to the order of the bands)
REQUIRED_BANDS = ["B02", "B03", "B04", "B08"]
