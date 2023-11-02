import pytest

from app.main_preprocessing import run_checks, run_setup


def test_run_checks_success(monkeypatch):
    # Mock the check_input_paths and check_ml_serve_online functions to always return True
    monkeypatch.setattr("app.main_preprocessing.check_input_paths", lambda x: True)
    monkeypatch.setattr("app.main_preprocessing.check_ml_serve_online", lambda: True)

    # Run the function
    run_checks()

    # Then
    # If the function completes without raising an exception, the test will pass


def test_run_setup(monkeypatch):
    # Mock the create_output_directories function to do nothing
    monkeypatch.setattr(
        "app.main_preprocessing.create_output_directories", lambda x: None
    )

    # Run the function
    run_setup()

    # Then
    # If the function completes without raising an exception, the test will pass


def test_get_identifier(date: str, tile: str) -> str:
    # get date
    ...
