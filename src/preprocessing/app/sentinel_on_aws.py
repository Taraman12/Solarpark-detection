import os
from pathlib import Path
from typing import Dict, Union

from cloud_clients import s3_client
from constants import USED_BANDS
from logging_config import get_logger
from models.identifier import Identifier

logger = get_logger("BaseConfig")


def download_from_sentinel_aws_handler(
    identifier: Identifier, target_folder: Path
) -> Dict[str, Dict[str, Union[str, Path]]] | None:
    """
    Handles the download of files from AWS based on the given identifier and target folder.

    Args:
        identifier (Identifier): The identifier object containing the necessary information.
        target_folder (Path): The local directory to download the files to.

    Returns:
        Dict[str, Dict[str, Union[str, Path]]] | None: A dictionary mapping each band to a dictionary containing:
            - 'resolution' (str): The resolution of the band.
            - 'file_path' (Path): The local file path to the band file.
        Returns None if there was an error downloading the files.
    """
    if not isinstance(identifier, Identifier):
        raise ValueError("Identifier must be an Identifier object")
    if not isinstance(target_folder, Path):
        raise ValueError("Target folder must be a Path object")
    target_folder = target_folder / identifier.to_string()
    band_file_info = {}
    sentinel_bucket, prefix = make_sentinel_aws_path(identifier)
    for band, resolution in USED_BANDS.items():
        try:
            file_path = download_from_sentinel_aws(
                sentinel_bucket, prefix, band, resolution, target_folder
            )
            band_file_info[band] = {"resolution": resolution, "file_path": file_path}

        except FileNotFoundError as e:
            logger.error(f"Error downloading file: {e}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None

    return band_file_info


def make_sentinel_aws_path(identifier: Identifier) -> str:
    """
    Constructs the AWS S3 bucket name and prefix based on the given identifier.

    Args:
        identifier (Identifier): The identifier object containing the necessary information.

    Returns:
        str: The constructed S3 bucket name and prefix.
    """
    if not isinstance(identifier, Identifier):
        raise ValueError("Identifier must be an Identifier object")
    # https://roda.sentinel-hub.com/sentinel-s2-l2a/readme.html
    sentinel_bucket = f"sentinel-s2-{identifier.product_level.lower()}"
    prefix = f"tiles/{identifier.utm_code}/{identifier.latitude_band}/{identifier.square}/{identifier.year}/{identifier.month_no_leading_zeros}/{identifier.day_no_leading_zeros}/0"  # /R10m
    return sentinel_bucket, prefix


def download_from_sentinel_aws(
    sentinel_bucket: str, prefix: str, band: str, resolution: str, target_folder: Path
) -> Path:
    """
    Downloads a file from AWS S3 Sentinel on AWS bucket.

    Args:
        sentinel_bucket (str): The name of the S3 bucket.
        prefix (str): The prefix of the file in the S3 bucket, without the resolution.
        band (str): The band of the file.
        resolution (str): The resolution of the file.
        target_folder (Path): The local directory to download the file to.

    Returns:
        Path: The path to the downloaded file.

    Raises:
        FileNotFoundError: If the file does not exist in the S3 bucket.
        Exception: If any other error occurs during the download.
    """
    prefix_with_resolution = f"{prefix}/R{resolution}"
    band_file_input = f"{band}.jp2"
    band_file_output = f"{band}_{resolution}.jp2"
    try:
        response = s3_client.get_object(
            Bucket=sentinel_bucket,
            Key=f"{prefix_with_resolution}/{band_file_input}",
            RequestPayer="requester",
        )
        response_content = response["Body"].read()

        # Ensure the directory exists
        os.makedirs(target_folder, exist_ok=True)

        with open(target_folder / band_file_output, "wb") as file:
            file.write(response_content)
        return target_folder / band_file_output
    except s3_client.exceptions.NoSuchKey:
        logger.warning(
            f"No such key: {prefix_with_resolution}/{band_file_input} in bucket: {sentinel_bucket}"
        )
        raise FileNotFoundError(
            f"No such key: {prefix_with_resolution}/{band_file_input} in bucket: {sentinel_bucket}"
        )
    except Exception as e:
        logger.error(f"Error downloading from AWS: {e}")
        raise e
