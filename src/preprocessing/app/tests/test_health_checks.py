import pytest
from pathlib import Path
import requests_mock
import requests

from app.health_checks import check_input_paths, check_ml_serve_online, check_api_online

URL_ML: str = "http://localhost:8080"


def test_check_input_paths_true(monkeypatch):
    # Mock the Path.exists method to always return True
    monkeypatch.setattr(Path, "exists", lambda x: True)

    # Given
    input_dirs = [Path("/path/to/dir1"), Path("/path/to/dir2")]

    # When
    result = check_input_paths(input_dirs)

    # Then
    assert result == True


def test_check_input_paths_false(monkeypatch):
    # Mock the Path.exists method to always return True
    monkeypatch.setattr(Path, "exists", lambda x: False)

    # Given
    input_dirs = [Path("/path/to/dir1"), Path("/path/to/dir2")]

    # When
    result = check_input_paths(input_dirs)

    # Then
    assert result == False


def test_check_ml_serve_online_success(monkeypatch):
    # Mock time.sleep to do nothing
    monkeypatch.setattr("time.sleep", lambda x: None)

    with requests_mock.Mocker() as m:
        m.get(f"{URL_ML}/ping", status_code=200)
        assert check_ml_serve_online() == True


def test_check_ml_serve_online_failure(monkeypatch):
    # Mock time.sleep to do nothing
    monkeypatch.setattr("time.sleep", lambda x: None)

    with requests_mock.Mocker() as m:
        m.get(f"{URL_ML}/ping", status_code=400)
        assert check_ml_serve_online() == False


def test_check_ml_serve_online_exception(monkeypatch):
    # Mock time.sleep to do nothing
    monkeypatch.setattr("time.sleep", lambda x: None)

    with requests_mock.Mocker() as m:
        m.get(f"{URL_ML}/ping", exc=requests.exceptions.ConnectionError)
        assert check_ml_serve_online() == False


def test_check_api_online_success(monkeypatch):
    # Mock time.sleep to do nothing
    monkeypatch.setattr("time.sleep", lambda x: None)

    with requests_mock.Mocker() as m:
        m.get(f"{URL_ML}", status_code=200)
        assert check_api_online() == True


def test_check_api_online_failure(monkeypatch):
    # Mock time.sleep to do nothing
    monkeypatch.setattr("time.sleep", lambda x: None)

    with requests_mock.Mocker() as m:
        m.get(f"{URL_ML}", status_code=400)
        assert check_api_online() == False


def test_check_api_online_exception(monkeypatch):
    # Mock time.sleep to do nothing
    monkeypatch.setattr("time.sleep", lambda x: None)

    with requests_mock.Mocker() as m:
        m.get(f"{URL_ML}", exc=requests.exceptions.ConnectionError)
        assert check_api_online() == False
