import os
from unittest.mock import patch

import pytest
import requests
from jwt_functions import (
    check_jwt_against_api,
    get_jwt,
    get_jwt_from_api,
    get_jwt_from_environ,
    store_jwt,
)


@patch("requests.post")
def test_get_jwt_from_api_with_valid_credentials(mock_post):
    # Test with valid credentials
    mock_post.return_value.json.return_value = {"access_token": "test_token"}
    mock_post.return_value.raise_for_status.return_value = None
    token = get_jwt_from_api("username", "password")
    assert token == "test_token"


def test_get_jwt_from_api_with_no_username():
    # Test with no username
    with pytest.raises(Exception, match="Username not provided"):
        get_jwt_from_api(password="password")


def test_get_jwt_from_api_with_no_password():
    # Test with no password
    with pytest.raises(Exception, match="Password not provided"):
        get_jwt_from_api(username="John@doe.com")


@patch("requests.post")
def test_get_jwt_from_api_with_401_and_not_authenticated(mock_post):
    # Test with 401 status code and "Not authenticated" error message
    mock_post.return_value.ok = False
    mock_post.return_value.status_code = 401
    mock_post.return_value.json.return_value = {"detail": "Not authenticated"}
    with pytest.raises(Exception, match="Invalid credentials"):
        get_jwt_from_api("username", "password")


@patch("requests.post")
def test_get_jwt_from_api_with_401_and_other_error(mock_post):
    # Test with 401 status code and an error message other than "Not authenticated"
    mock_post.return_value.ok = False
    mock_post.return_value.status_code = 401
    mock_post.return_value.json.return_value = {"detail": "Other error"}
    with pytest.raises(requests.HTTPError):
        get_jwt_from_api("username", "password")


@patch("requests.post")
def test_get_jwt_from_api_with_other_status_code(mock_post):
    # Test with a status code other than 401
    mock_post.return_value.ok = False
    mock_post.return_value.status_code = 500
    with pytest.raises(requests.HTTPError):
        get_jwt_from_api("username", "password")


@patch.dict(os.environ, {"JWT": ""}, clear=True)
def test_store_jwt_with_valid_token():
    # Test with valid token
    token = "test_token"
    store_jwt(token)
    assert os.environ["JWT"] == token


@patch.dict(os.environ, {"JWT": ""}, clear=True)
def test_store_jwt_with_empty_token():
    # Test with empty token
    token = ""
    with pytest.raises(ValueError):
        store_jwt(token)


@patch.dict(os.environ, {"JWT": ""}, clear=True)
def test_store_jwt_with_none_token():
    # Test with None token
    token = None
    with pytest.raises(TypeError):
        store_jwt(token)


@patch("requests.post")
def test_check_jwt_against_api_with_valid_token(mock_post):
    # Test with valid token
    mock_post.return_value.raise_for_status.return_value = None
    assert check_jwt_against_api("test_token") is True


@patch("requests.post")
def test_check_jwt_against_api_with_invalid_token(mock_post):
    # Test with invalid token
    mock_post.return_value.raise_for_status.side_effect = requests.HTTPError()
    with pytest.raises(requests.HTTPError):
        check_jwt_against_api("invalid_token")


@patch.dict(os.environ, {"JWT": "test_token"}, clear=True)
@patch("requests.post")
def test_check_jwt_against_api_with_token_in_environment_variable(mock_post):
    # Test with token in environment variable
    mock_post.return_value.raise_for_status.return_value = None
    assert check_jwt_against_api() is True


@patch.dict(os.environ, {"JWT": ""}, clear=True)
def test_check_jwt_against_api_with_no_token():
    # Test with no token
    with pytest.raises(Exception, match="JWT token not stored in environment variable"):
        check_jwt_against_api()


@patch.dict(os.environ, {"JWT": "test_token"}, clear=True)
@patch("requests.post")
def test_check_jwt_against_api_with_server_error(mock_post):
    # Test with server error
    mock_post.return_value.raise_for_status.side_effect = requests.HTTPError()
    with pytest.raises(requests.HTTPError):
        check_jwt_against_api()


@patch.dict(os.environ, {"JWT": "test_token"}, clear=True)
def test_get_jwt_from_environ_with_token_in_environment_variable():
    # Test with token in environment variable
    assert get_jwt_from_environ() == "test_token"


@patch.dict(os.environ, {"JWT": ""}, clear=True)
def test_get_jwt_from_environ_with_empty_token_in_environment_variable():
    # Test with empty token in environment variable
    with pytest.raises(Exception):
        get_jwt_from_environ()


@patch.dict(os.environ, {}, clear=True)
def test_get_jwt_from_environ_with_no_token_in_environment_variable():
    # Test with no token in environment variable
    with pytest.raises(Exception):
        get_jwt_from_environ()


@patch("jwt_functions.get_jwt_from_environ")
def test_get_jwt_with_token_in_environment_variable(mock_get_jwt_from_environ):
    # Test with token in environment variable
    mock_get_jwt_from_environ.return_value = "test_token"
    assert get_jwt() == "test_token"


@patch("jwt_functions.get_jwt_from_environ")
@patch("jwt_functions.get_jwt_from_api")
@patch("jwt_functions.store_jwt")
def test_get_jwt_with_token_from_api(
    mock_store_jwt, mock_get_jwt_from_api, mock_get_jwt_from_environ
):
    # Test with token from API
    mock_get_jwt_from_environ.side_effect = KeyError
    mock_get_jwt_from_api.return_value = "test_token"
    assert get_jwt() == "test_token"
    mock_store_jwt.assert_called_once_with("test_token")


@patch("jwt_functions.get_jwt_from_environ")
@patch("jwt_functions.get_jwt_from_api")
def test_get_jwt_with_no_token(mock_get_jwt_from_api, mock_get_jwt_from_environ):
    # Test with no token
    mock_get_jwt_from_environ.side_effect = KeyError
    mock_get_jwt_from_api.side_effect = Exception
    with pytest.raises(Exception, match="Could not get JWT"):
        get_jwt()
