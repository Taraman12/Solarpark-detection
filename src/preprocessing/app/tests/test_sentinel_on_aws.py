import os
from pathlib import Path

import boto3
import pytest
from constants import USED_BANDS
from models.identifier import Identifier
from moto import mock_s3
from sentinel_on_aws import (
    download_from_sentinel_aws,
    download_from_sentinel_aws_handler,
    make_sentinel_aws_path,
)


@pytest.fixture(scope="function")
def aws_credentials():
    """Mocked AWS Credentials for moto."""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


def test_make_sentinel_aws_path():
    identifier = Identifier(
        "S2A_MSIL1C_20220101T123456_N0302_R123_T01ABC_20220101T123456"
    )
    sentinel_bucket, prefix = make_sentinel_aws_path(identifier)
    assert sentinel_bucket == "sentinel-s2-l1c"
    assert prefix == "tiles/01/A/BC/2022/1/1/0"


@mock_s3
@pytest.fixture(scope="function")
def test_download_from_sentinel_aws_happy_path():
    # Set up mock S3 bucket
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="sentinel-s2-l1c")
    s3.put_object(Bucket="sentinel-s2-l1c", Key="prefix/10m/B02.jp2", Body=b"test data")

    # Call function under test
    sentinel_bucket = "sentinel-s2-l1c"
    prefix = "prefix"
    band = "B02"
    resolution = "10m"
    target_folder = Path("/tmp")
    file_path = download_from_sentinel_aws(
        sentinel_bucket, prefix, band, resolution, target_folder
    )

    # Check result
    assert file_path == target_folder / f"{band}_{resolution}.jp2"
    with open(file_path, "rb") as file:
        assert file.read() == b"test data"


@mock_s3
@pytest.fixture(scope="function")
def test_download_from_sentinel_aws_unhappy_path_no_file():
    # Set up mock S3 bucket
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="test_bucket")

    # Call function under test
    sentinel_bucket = "test_bucket"
    prefix = "prefix"
    band = "B02"
    resolution = "10m"
    target_folder = Path("/tmp")

    with pytest.raises(FileNotFoundError):
        download_from_sentinel_aws(
            sentinel_bucket, prefix, band, resolution, target_folder
        )


@mock_s3
@pytest.fixture(scope="function")
def test_download_from_sentinel_aws_handler_happy_path():
    # Set up mock S3 bucket
    s3 = boto3.client("s3", region_name="us-east-1")
    identifier = Identifier(
        "S2A_MSIL1C_20220101T123456_N0302_R123_T01ABC_20220101T123456"
    )
    sentinel_bucket, prefix = make_sentinel_aws_path(identifier)
    s3.create_bucket(Bucket=sentinel_bucket)
    for band, resolution in USED_BANDS.items():
        s3.put_object(
            Bucket=sentinel_bucket,
            Key=f"{prefix}/{resolution}/{band}.jp2",
            Body=b"test data",
        )

    # Call function under test
    identifier = Identifier(
        "S2A_MSIL1C_20220101T123456_N0302_R123_T01ABC_20220101T123456"
    )
    target_folder = Path("/tmp")
    band_file_info = download_from_sentinel_aws_handler(identifier, Path("/tmp"))

    # Check result
    for band, resolution in USED_BANDS.items():
        assert band_file_info[band]["resolution"] == resolution
        assert (
            band_file_info[band]["file_path"]
            == target_folder / f"{band}_{resolution}.jp2"
        )
        with open(band_file_info[band]["file_path"], "rb") as file:
            assert file.read() == b"test data"


@mock_s3
@pytest.fixture(scope="function")
def test_download_from_sentinel_aws_handler_unhappy_path_no_file():
    # Set up mock S3 bucket
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="test_bucket")

    # Call function under test
    identifier = Identifier(
        "S2A_MSIL1C_20220101T123456_N0302_R123_T01ABC_20220101T123456"
    )
    band_file_info = download_from_sentinel_aws_handler(identifier, Path("/tmp"))

    # Check result
    assert band_file_info is None


@mock_s3
@pytest.fixture(scope="function")
def test_download_from_sentinel_aws_handler_unhappy_path():
    # Set up mock S3 bucket
    s3 = boto3.client("s3", region_name="us-east-1")
    s3.create_bucket(Bucket="test_bucket")

    # Call function under test
    identifier = Identifier(
        "S2A_MSIL1C_20220101T123456_N0302_R123_T01ABC_20220101T123456"
    )
    band_file_info = download_from_sentinel_aws_handler(
        identifier, Path("/invalid/path")
    )

    # Check result
    assert band_file_info is None
