import re
from pathlib import Path

IMAGE_INPUT_DIR = Path(r".\data_local\training_data_raw")

MASK_INPUT_DIR = Path(
    r".\src\preprocess_data_to_disk\data\trn_polygons_germany_tile_names.geojson"
)

# NOTE will be created if not existent
IMAGE_OUTPUT_DIR = Path(r".\data_local\images_only_AOI_test_color_corr_2")
# NOTE will be created if not existent
MASK_OUTPUT_DIR = Path(r".\data_local\masks_only_AOI_test_color_corr_2")

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
