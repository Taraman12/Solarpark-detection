import requests
import requests_mock
from constants import URL_API, URL_ML
from health_checks import (  # check_input_paths,; run_checks,
    check_api_online,
    check_ml_serve_online,
)

# URL_ML: str = "http://localhost:8080"
# URL_API: str = "http://localhost:8000/api/v1"


# def test_check_input_paths_true(monkeypatch):
#     # Mock the Path.exists method to always return True
#     monkeypatch.setattr(Path, "exists", lambda x: True)

#     # Given
#     input_dirs = [Path("/path/to/dir1"), Path("/path/to/dir2")]

#     # When
#     result = check_input_paths(input_dirs)

#     # Then
#     assert result == True


# def test_check_input_paths_false(monkeypatch):
#     # Mock the Path.exists method to always return True
#     monkeypatch.setattr(Path, "exists", lambda x: False)

#     # Given
#     input_dirs = [Path("/path/to/dir1"), Path("/path/to/dir2")]

#     # When
#     result = check_input_paths(input_dirs)

#     # Then
#     assert result == False


def test_check_ml_serve_online_success(monkeypatch):
    # Mock time.sleep to do nothing
    monkeypatch.setattr("time.sleep", lambda x: None)

    with requests_mock.Mocker() as m:
        m.get(f"{URL_ML}/ping", status_code=200)
        assert check_ml_serve_online()


def test_check_ml_serve_online_failure(monkeypatch):
    # Mock time.sleep to do nothing
    monkeypatch.setattr("time.sleep", lambda x: None)

    with requests_mock.Mocker() as m:
        m.get(f"{URL_ML}/ping", status_code=400)
        assert not check_ml_serve_online()


def test_check_ml_serve_online_exception(monkeypatch):
    # Mock time.sleep to do nothing
    monkeypatch.setattr("time.sleep", lambda x: None)

    with requests_mock.Mocker() as m:
        m.get(f"{URL_ML}/ping", exc=requests.exceptions.ConnectionError)
        assert not check_ml_serve_online()


def test_check_api_online_success(monkeypatch):
    # Mock time.sleep to do nothing
    monkeypatch.setattr("time.sleep", lambda x: None)

    with requests_mock.Mocker() as m:
        m.get(f"{URL_API}", status_code=200)
        assert check_api_online()


def test_check_api_online_failure(monkeypatch):
    # Mock time.sleep to do nothing
    monkeypatch.setattr("time.sleep", lambda x: None)

    with requests_mock.Mocker() as m:
        m.get(f"{URL_API}", status_code=400)
        assert not check_api_online()


def test_check_api_online_exception(monkeypatch):
    # Mock time.sleep to do nothing
    monkeypatch.setattr("time.sleep", lambda x: None)

    with requests_mock.Mocker() as m:
        m.get(f"{URL_API}", exc=requests.exceptions.ConnectionError)
        assert not check_api_online()


# def test_run_checks_success(
#     mock_check_jwt_against_api, mock_check_api_online, mock_check_ml_serve_online
# ):
#     # Test with successful checks
#     mock_check_ml_serve_online.return_value = True
#     mock_check_api_online.return_value = True
#     mock_check_jwt_against_api.return_value = True
#     run_checks()


# def test_run_checks_ml_serve_offline(mock_check_ml_serve_online):
#     # Test with ml-serve offline
#     mock_check_ml_serve_online.return_value = False
#     with pytest.raises(SystemExit) as e:
#         run_checks()
#     assert e.type == SystemExit
#     assert e.value.code == 2


# def test_run_checks_api_offline(mock_check_api_online, mock_check_ml_serve_online):
#     # Test with API offline
#     mock_check_ml_serve_online.return_value = True
#     mock_check_api_online.return_value = False
#     with pytest.raises(SystemExit) as e:
#         run_checks()
#     assert e.type == SystemExit
#     assert e.value.code == 2


# def test_run_checks_jwt_invalid(
#     mock_check_jwt_against_api, mock_check_api_online, mock_check_ml_serve_online
# ):
#     # Test with invalid JWT
#     mock_check_ml_serve_online.return_value = True
#     mock_check_api_online.return_value = True
#     mock_check_jwt_against_api.return_value = False
#     with pytest.raises(SystemExit) as e:
#         run_checks()
#     assert e.type == SystemExit
#     assert e.value.code == 2
