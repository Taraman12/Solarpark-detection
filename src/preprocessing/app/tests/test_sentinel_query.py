from unittest.mock import MagicMock, patch

import pytest
import requests
from models.identifier import Identifier
from sentinel_query import (
    get_identifier_handler,
    identifier_from_title,
    make_query_string,
    query,
    title_from_query,
)


def test_make_query_string_valid_inputs():
    # Test case 1: Check the returned URL with specific parameters
    start_date = "2022-01-01"
    end_date = "2022-01-31"
    tile_id = "T32TPT"
    cloudcover = 10
    expected_url = "https://catalogue.dataspace.copernicus.eu/resto/api/collections/Sentinel2/search.json?startDate=2022-01-01&completionDate=2022-01-31&productType=S2MSI2A&cloudCover=[0,10]&tileId=T32TPT"
    assert (
        make_query_string(
            tile_id=tile_id,
            start_date=start_date,
            end_date=end_date,
            cloudcover=cloudcover,
        )
        == expected_url
    )

    # Test case 2: Check the returned URL with different parameters
    start_date = "2022-02-01"
    end_date = "2022-02-28"
    tile_id = "T32TPS"
    cloudcover = 20
    expected_url = "https://catalogue.dataspace.copernicus.eu/resto/api/collections/Sentinel2/search.json?startDate=2022-02-01&completionDate=2022-02-28&productType=S2MSI2A&cloudCover=[0,20]&tileId=T32TPS"
    assert (
        make_query_string(
            tile_id=tile_id,
            start_date=start_date,
            end_date=end_date,
            cloudcover=cloudcover,
        )
        == expected_url
    )


# def test_make_query_string_invalid_date():
#     # Test case 3: Check if ValueError is raised when date is not in correct format
#     start_date = "01-01-2022"
#     end_date = "31-01-2022"
#     with pytest.raises(ValueError, match="Dates must be in the format YYYY-MM-DD"):
#         make_query_string(start_date, end_date, tile_id, cloudcover)


def test_make_query_string_invalid_cloudcover():
    # Test case 4: Check if ValueError is raised when cloudcover is not between 0 and 100
    start_date = "2022-01-01"
    end_date = "2022-01-31"
    tile_id = "T32TPT"
    cloudcover = 110
    with pytest.raises(ValueError, match="Cloudcover must be between 0 and 100"):
        make_query_string(
            tile_id=tile_id,
            start_date=start_date,
            end_date=end_date,
            cloudcover=cloudcover,
        )


def test_make_query_string_invalid_tile_id():
    # Test case 5: Check if ValueError is raised when tile_id is not a string
    start_date = "2022-01-01"
    end_date = "2022-01-31"
    tile_id = 123
    cloudcover = 10
    with pytest.raises(ValueError, match="Tile ID must be a string"):
        make_query_string(
            tile_id=tile_id,
            start_date=start_date,
            end_date=end_date,
            cloudcover=cloudcover,
        )


@patch("requests.get")
def test_query_valid_url(mock_get):
    # Test case 1: Check if the function returns the expected response given a valid URL
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = {
        "key": "value"
    }  # Set the return value of .json() to the expected dictionary
    mock_get.return_value = mock_response
    query_string = "https://example.com"
    assert query(query_string) == {
        "key": "value"
    }  # Expect the function to return the dictionary


@patch("requests.get")
def test_query_invalid_url(mock_get):
    # Test case 2: Check if the function returns None when the request fails
    mock_get.side_effect = requests.exceptions.RequestException
    query_string = "https://example.com"
    with pytest.raises(ValueError, match="Request failed"):
        query(query_string)


def test_query_invalid_query_string():
    # Test case 3: Check if ValueError is raised when query_string is not a string
    query_string = 123
    with pytest.raises(ValueError, match="Query string must be a string"):
        query(query_string)


def test_title_from_query_valid_response():
    # Test case 1: Check if the function returns the expected title given a valid response
    query_response = {
        "features": [
            {"properties": {"title": "title1", "cloudCover": 10}},
            {"properties": {"title": "title2", "cloudCover": 5}},
        ]
    }
    assert title_from_query(query_response) == "title2"


def test_title_from_query_invalid_response():
    # Test case 2: Check if ValueError is raised when query_response is not a dictionary
    query_response = "not a dictionary"
    with pytest.raises(ValueError, match="Query response must be a dictionary"):
        title_from_query(query_response)

    # Test case 4: Check if ValueError is raised when feature does not contain 'properties' key
    query_response = {"features": [{"not_properties": {}}]}
    with pytest.raises(ValueError, match="Feature does not contain 'properties' key"):
        title_from_query(query_response)

    # Test case 5: Check if ValueError is raised when properties do not contain 'title' or 'cloudCover' key
    query_response = {
        "features": [{"properties": {"not_title": "", "not_cloudCover": ""}}]
    }
    with pytest.raises(
        ValueError, match="Properties do not contain 'title' or 'cloudCover' key"
    ):
        title_from_query(query_response)


def test_title_from_query_no_product_found():
    # Test case 6: Check if ValueError is raised when there is no data to sort
    query_response = {"features": []}
    assert title_from_query(query_response) is None


def test_identifier_from_title_valid_title():
    # Test case 2: Check if the function returns the same title when title is already an identifier
    title = "S2A_MSIL1C_20220101T123456_N0302_R123_T01ABC_20220101T123456"
    identifier = identifier_from_title(title)
    assert isinstance(identifier, Identifier)
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
    assert identifier.product_time == "123456"
    assert identifier.tile == "01ABC"
    assert identifier.tile_date == "2022-01-01"


def test_identifier_from_title_valid_title_and_suffix():
    # Test case 1: Check if the function returns the expected identifier when title ends with ".SAFE"
    title = "S2A_MSIL1C_20220101T123456_N0302_R123_T01ABC_20220101T123456.SAFE"
    identifier = identifier_from_title(title)
    assert isinstance(identifier, Identifier)
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
    assert identifier.product_time == "123456"
    assert identifier.tile == "01ABC"
    assert identifier.tile_date == "2022-01-01"


def test_identifier_from_title_invalid_title():
    # Test case 3: Check if ValueError is raised when title is not a valid identifier
    invalid_identifier_string = "S2A_MSIL1C_20220101T123456_R123_T01ABC_20220101T123456"
    with pytest.raises(ValueError, match=f"Invalid title: {invalid_identifier_string}"):
        identifier_from_title(invalid_identifier_string)


@patch("sentinel_query.make_query_string")
@patch("sentinel_query.query")
@patch("sentinel_query.title_from_query")
@patch("sentinel_query.identifier_from_title")
def test_get_identifier_handler_valid_inputs(
    mock_identifier_from_title,
    mock_title_from_query,
    mock_query,
    mock_make_query_string,
):
    # Test case 1: Check if the function returns the expected identifier given valid inputs
    mock_make_query_string.return_value = "query_string"
    mock_query.return_value = "query_response"
    mock_title_from_query.return_value = "title"
    mock_identifier_from_title.return_value = "identifier"
    assert (
        get_identifier_handler(
            "T32TPT", {"start_date": "2022-01-01", "end_date": "2022-01-31"}, 10
        )
        == "identifier"
    )

    # Test case 2: Check if the functions returns the expected identifier when dates is None
    mock_make_query_string.return_value = "query_string"
    mock_query.return_value = "query_response"
    mock_title_from_query.return_value = "title"
    mock_identifier_from_title.return_value = "identifier"
    assert get_identifier_handler("T32TPT") == "identifier"


@patch("sentinel_query.make_query_string")
def test_get_identifier_handler_invalid_tile_id(mock_make_query_string):
    # Test case 2: Check if ValueError is raised when tile_id is not a string
    with pytest.raises(ValueError, match="Tile ID must be a string"):
        get_identifier_handler(
            123, {"start_date": "2022-01-01", "end_date": "2022-01-31"}, 10
        )


@patch("sentinel_query.make_query_string")
def test_get_identifier_handler_invalid_dates(mock_make_query_string):
    # Test case 3: Check if ValueError is raised when start_date or end_date is not a string
    with pytest.raises(ValueError, match="Start date and end date must be strings"):
        get_identifier_handler(
            "T32TPT", {"start_date": "2022-01-01", "end_date": 2020}, 10
        )
    with pytest.raises(ValueError, match="Start date and end date must be strings"):
        get_identifier_handler(
            "T32TPT", {"start_date": 2020, "end_date": "2022-01-31"}, 10
        )


@patch("sentinel_query.make_query_string")
def test_get_identifier_handler_invalid_cloudcover(mock_make_query_string):
    # Test case 4: Check if ValueError is raised when cloudcover is not an integer between 0 and 100
    with pytest.raises(
        ValueError, match="Cloud cover must be an integer between 0 and 100"
    ):
        get_identifier_handler(
            "T32TPT", {"start_date": "2022-01-01", "end_date": "2022-01-31"}, "10"
        )
    with pytest.raises(
        ValueError, match="Cloud cover must be an integer between 0 and 100"
    ):
        get_identifier_handler(
            "T32TPT", {"start_date": "2022-01-01", "end_date": "2022-01-31"}, 110
        )


# @patch("sentinel_query.connect_to_sentinel_api")
# def test_wait_for_api_connection(mock_connect_to_sentinel_api, monkeypatch):
#     monkeypatch.setattr("time.sleep", lambda x: None)

#     # Test case 1: connection successful
#     mock_connect_to_sentinel_api.return_value = MagicMock()
#     assert wait_for_api_connection() is not False

#     # Test case 2: server error
#     mock_connect_to_sentinel_api.return_value = ServerError()
#     assert wait_for_api_connection() is False

#     # Test case 3: unauthorized error
#     mock_connect_to_sentinel_api.return_value = UnauthorizedError()
#     with pytest.raises(SystemExit):
#         wait_for_api_connection()

#     # Test case 4: connection error
#     mock_connect_to_sentinel_api.return_value = ConnectionError()
#     with pytest.raises(SystemExit):
#         wait_for_api_connection()

#     # Test case 5: unknown error
#     mock_connect_to_sentinel_api.return_value = Exception()
#     with pytest.raises(SystemExit):
#         wait_for_api_connection()


# @patch("sentinel_query.SentinelAPI")
# def test_get_product_from_footprint(mock_sentinel_api):
#     # create a mock product
#     mock_product = MagicMock()
#     mock_product.cloudcoverpercentage = 10

#     # create a mock geodataframe
#     mock_gdf = MagicMock()
#     mock_gdf.sort_values.return_value = mock_gdf
#     mock_gdf.iloc.return_value = mock_product

#     # set up the mock API
#     mock_api = MagicMock()
#     mock_api.query.return_value = [1]
#     mock_api.to_geodataframe.return_value = mock_gdf

#     # test case 1: product found
#     mock_sentinel_api.return_value = mock_api
#     assert (
#         get_product_from_footprint(
#             mock_api, "POLYGON((10 10, 10 20, 20 20, 20 10, 10 10))"
#         )
#         == mock_product
#     )

#     # test case 2: no product found
#     mock_api.query.return_value = []
#     assert (
#         get_product_from_footprint(
#             mock_api, "POLYGON((10 10, 10 20, 20 20, 20 10, 10 10))"
#         )
#         is None
#     )


# @patch("sentinel_query.get_product_from_footprint")
# def test_get_identifier_handler_success(mock_get_product_from_footprint):
#     mock_get_product_from_footprint.return_value = {
#         "identifier": "S2A_MSIL1C_20220101T123456_N0302_R123456789"
#     }
#     assert (
#         get_identifier_handler("POLYGON((10 10, 10 20, 20 20, 20 10, 10 10))")
#         == "S2A_MSIL1C_20220101T123456_N0302_R123456789"
#     )


# @patch("sentinel_query.get_product_from_footprint")
# def test_get_identifier_handler_failure(mock_get_product_from_footprint):
#     mock_get_product_from_footprint.return_value = None
#     assert get_identifier_handler("POLYGON((10 10, 10 20, 20 20, 20 10, 10 10))") is None


# @patch("sentinel_query.wait_for_api_connection")
# def test_get_api_success(mock_wait_for_api_connection, monkeypatch):
#     monkeypatch.setattr("time.sleep", lambda x: None)
#     mock_wait_for_api_connection.return_value = MagicMock()
#     assert isinstance(get_api(), SentinelAPI)


# @patch("sentinel_query.wait_for_api_connection")
# def test_get_api_failure(mock_wait_for_api_connection, monkeypatch):
#     monkeypatch.setattr("time.sleep", lambda x: None)
#     mock_wait_for_api_connection.side_effect = Exception()
#     with pytest.raises(SystemExit):
#         get_api()
