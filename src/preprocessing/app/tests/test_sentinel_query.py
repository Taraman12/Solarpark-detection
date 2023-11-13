from unittest.mock import MagicMock, patch

import pytest
from sentinel_query import get_api, wait_for_api_connection
from sentinelsat.exceptions import ServerError, UnauthorizedError


@patch("sentinel_query.connect_to_sentinel_api")
def test_wait_for_api_connection(mock_connect_to_sentinel_api, monkeypatch):
    monkeypatch.setattr("time.sleep", lambda x: None)

    # Test case 1: connection successful
    mock_connect_to_sentinel_api.return_value = MagicMock()
    assert wait_for_api_connection() is not False

    # Test case 2: server error
    mock_connect_to_sentinel_api.return_value = ServerError()
    assert wait_for_api_connection() is False

    # Test case 3: unauthorized error
    mock_connect_to_sentinel_api.return_value = UnauthorizedError()
    with pytest.raises(SystemExit):
        wait_for_api_connection()

    # Test case 4: connection error
    mock_connect_to_sentinel_api.return_value = ConnectionError()
    with pytest.raises(SystemExit):
        wait_for_api_connection()

    # Test case 5: unknown error
    mock_connect_to_sentinel_api.return_value = Exception()
    with pytest.raises(SystemExit):
        wait_for_api_connection()


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
# def test_get_identifier_success(mock_get_product_from_footprint):
#     mock_get_product_from_footprint.return_value = {
#         "identifier": "S2A_MSIL1C_20220101T123456_N0302_R123456789"
#     }
#     assert (
#         get_identifier("POLYGON((10 10, 10 20, 20 20, 20 10, 10 10))")
#         == "S2A_MSIL1C_20220101T123456_N0302_R123456789"
#     )


# @patch("sentinel_query.get_product_from_footprint")
# def test_get_identifier_failure(mock_get_product_from_footprint):
#     mock_get_product_from_footprint.return_value = None
#     assert get_identifier("POLYGON((10 10, 10 20, 20 20, 20 10, 10 10))") is None


# @patch("sentinel_query.wait_for_api_connection")
# def test_get_api_success(mock_wait_for_api_connection, monkeypatch):
#     monkeypatch.setattr("time.sleep", lambda x: None)
#     mock_wait_for_api_connection.return_value = MagicMock()
#     assert isinstance(get_api(), SentinelAPI)


@patch("sentinel_query.wait_for_api_connection")
def test_get_api_failure(mock_wait_for_api_connection, monkeypatch):
    monkeypatch.setattr("time.sleep", lambda x: None)
    mock_wait_for_api_connection.side_effect = Exception()
    with pytest.raises(SystemExit):
        get_api()
