from pathlib import Path

# from constants import USED_BANDS
from make_trainings_data import make_trainings_data_handler  # make_file_paths,
from models.identifier import Identifier

# def test_make_file_paths():
#     path = Path(
#         r"C:\Users\Fabian\Documents\Github_Masterthesis\Solarpark-detection\data_local\training_data_raw"
#     )
#     identifier = "S2A_MSIL2A_20181013T100021_N0209_R122_T33UVP_20181013T114121"
#     band_file_info = make_file_paths(path / identifier)
# assert band_file_info == {
#     "B02": {
#         "resolution": "10m",
#         "file_path": Path(
#             "/temp/S2B_MSIL2A_20210111T102309_N0214_R065_T32UQE_20210111T123455/B02_10m.jp2"
#         ),
#     },
#     "B03": {
#         "resolution": "10m",
#         "file_path": Path(
#             "/temp/S2B_MSIL2A_20210111T102309_N0214_R065_T32UQE_20210111T123455/B03_10m.jp2"
#         ),
#     },
#     "B04": {
#         "resolution": "10m",
#         "file_path": Path(
#             "/temp/S2B_MSIL2A_20210111T102309_N0214_R065_T32UQE_20210111T123455/B04_10m.jp2"
#         ),
#     },
#     "B08": {
#         "resolution": "10m",
#         "file_path": Path(
#             "/temp/S2B_MSIL2A_20210111T102309_N0214_R065_T32UQE_20210111T123455/B08_10m.jp2"
#         ),
#     },
# }


def test_make_trainings_data_handler():
    path = Path(
        r"C:\Users\Fabian\Documents\Github_Masterthesis\Solarpark-detection\data_local\training_data_raw"
    )
    identifier = Identifier(
        "S2A_MSIL2A_20181013T100021_N0209_R122_T33UVP_20181013T114121"
    )
    make_trainings_data_handler(path, identifier)
