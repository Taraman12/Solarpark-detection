from unittest.mock import patch

import pytest

# import requests
from constants import IMAGE_OUTPUT_DIR, MASK_OUTPUT_DIR
from main_preprocessing import run_setup  # run_checks,


@patch("main_preprocessing.get_jwt_from_api")
@patch("main_preprocessing.store_jwt")
@patch("main_preprocessing.create_output_directories")
def test_run_setup_success(
    mock_create_output_directories, mock_store_jwt, mock_get_jwt_from_api
):
    # Test with successful setup
    mock_get_jwt_from_api.return_value = "test_token"
    run_setup()
    mock_create_output_directories.assert_called_once_with(
        [IMAGE_OUTPUT_DIR, MASK_OUTPUT_DIR]
    )
    mock_get_jwt_from_api.assert_called_once_with(
        username="John@Doe.com", password="password"
    )
    mock_store_jwt.assert_called_once_with("test_token")


@patch("main_preprocessing.get_jwt_from_api")
@patch("main_preprocessing.store_jwt")
@patch("main_preprocessing.create_output_directories")
def test_run_setup_jwt_api_failure(
    mock_create_output_directories, mock_store_jwt, mock_get_jwt_from_api
):
    # Test with failure to get JWT from API
    mock_get_jwt_from_api.side_effect = Exception
    with pytest.raises(SystemExit) as e:
        run_setup()
    assert e.type == SystemExit
    assert e.value.code == 1
    mock_create_output_directories.assert_called_once_with(
        [IMAGE_OUTPUT_DIR, MASK_OUTPUT_DIR]
    )
    mock_get_jwt_from_api.assert_called_once_with(
        username="John@Doe.com", password="password"
    )
    mock_store_jwt.assert_not_called()


# def test_run_checks_success(monkeypatch):
#     # Mock the check_input_paths and check_ml_serve_online functions to always return True
#     monkeypatch.setattr("main_preprocessing.check_input_paths", lambda x: True)
#     monkeypatch.setattr("main_preprocessing.check_ml_serve_online", lambda: True)

#     # Run the function
#     run_checks()

#     # Then
#     # If the function completes without raising an exception, the test will pass


# def test_run_setup(monkeypatch):
#     # Mock the create_output_directories function to do nothing
#     monkeypatch.setattr("main_preprocessing.create_output_directories", lambda x: None)

#     # Run the function
#     run_setup()

#     # Then
#     # If the function completes without raising an exception, the test will pass


# def test_get_identifier(date: str, tile: str) -> str:
#     # get date
#     ...
