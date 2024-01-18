import pytest
from models.identifier import Identifier


def test_identifier_happy_path():
    identifier_string = "S2A_MSIL1C_20220101T123456_N0302_R123_T01ABC_20220101T123456"
    identifier = Identifier(identifier_string)
    assert identifier.mission == "S2A"
    assert identifier.product_level == "L1C"
    assert identifier.sensing_time == "20220101T123456"
    assert identifier.processing_baseline == "N0302"
    assert identifier.relative_orbit == "R123"
    assert identifier.utm_code == "01"
    assert identifier.latitude_band == "A"
    assert identifier.square == "BC"
    assert identifier.year == "2022"
    assert identifier.month == "01"
    assert identifier.day == "01"
    assert identifier.month_no_leading_zeros == "1"
    assert identifier.day_no_leading_zeros == "1"
    assert identifier.product_time == "123456"
    assert identifier.tile == "01ABC"
    assert identifier.tile_date == "2022-01-01"
    assert identifier.tile_date_no_leading_zeros == "2022-1-1"


def test_identifier_unhappy_path():
    # string is missing processing baseline
    identifier_string = "S2A_MSIL1C_20220101T123456_R123_T01ABC_20220101T123456"
    with pytest.raises(ValueError):
        Identifier(identifier_string)


def test_identifier_to_string():
    identifier_string = "S2A_MSIL1C_20220101T123456_N0302_R123_T01ABC_20220101T123456"
    identifier = Identifier(identifier_string)
    print(identifier.to_string())
    assert identifier.to_string() == identifier_string
