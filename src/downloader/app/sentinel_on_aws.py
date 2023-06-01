# build-in
import os
import pickle
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

# third-party
from botocore.errorfactory import ClientError
from cloud_clients import BUCKET_NAME, s3_client

# local-modules
from logging_config import get_logger
from constants import IDENTIFIER_REGEX, REQUIRED_BANDS, DATA_OUTPUT_PREFIX_AWS
from settings import PRODUCTION


# set up logger
logger = get_logger("BaseConfig")

# ToDo: add variable for resolution
# ToDo: replace hard-coded value with a constant


def download_from_aws_handler(
    identifier: str, target_folder: Path, deployed: bool = False
) -> bool:
    """Downloads Sentinel data from AWS S3.

    Args:
        identifier (str): The Sentinel identifier (folder name).
        target_folder (Path): The target folder to download the data to.
        deployed (bool, optional): Whether the code is deployed to AWS. Defaults to False.

    Returns:
        bool: True if the download was successful, False otherwise.
    """
    # if deployed in production on aws no transfer limit
    if not PRODUCTION and not check_aws_free_tier_available(target_folder.parents[0]):
        return False

    sentinel_bucket, prefix = make_aws_path(identifier)

    for band in REQUIRED_BANDS:
        band_file = f"{band}_10m.jp2"
        band_file_path = target_folder / band_file
        if PRODUCTION:
            # ! leads to
            # https://stackoverflow.com/questions/63323425/download-sentinel-file-from-s3-using-python-boto3
            if copy_from_aws(sentinel_bucket, identifier, prefix, band):
                continue

            return True

        if band_file_path.exists():
            continue

        download_from_aws(sentinel_bucket, prefix, band, target_folder)

        write_downloaded_size(target_folder)
    return True


def check_aws_free_tier_available(root_folder: Path) -> bool:
    # Get the current year and month
    now = datetime.now()
    year = now.year
    month = now.month

    if (root_folder / "downloaded_size_logs.pickle").exists():
        with open((root_folder / "downloaded_size_logs.pickle"), "rb") as f:
            size_logs = pickle.load(f)
    else:
        size_logs = {}

    # Calculate the sum of sizes for all days in the current month
    current_month_sum = sum(
        size_logs[date]
        for date in size_logs
        if date.year == year and date.month == month
    )
    # ToDo: replace hard-coded value with a constant
    if current_month_sum < 90 * (1024**3):
        logger.info(f"Current month sum is: {current_month_sum/(1024**3):.2f} GB.")
        return True
    else:
        logger.warning("Current month sum is 90 GB or above.")
        return False


def make_aws_path(identifier: str) -> Tuple[str, str]:
    """Returns sentinel_bucket and prefix."""
    regex_match = re.match(IDENTIFIER_REGEX, identifier)

    if regex_match:
        # mission = regex_match.group("mission")
        utm_code = regex_match.group("utm_code")
        product_level = regex_match.group("product_level").lower()
        latitude_band = regex_match.group("latitude_band")
        square = regex_match.group("square")
        year = regex_match.group("year")
        month = str(int(regex_match.group("month")))
        day = str(int(regex_match.group("day")))

    # https://roda.sentinel-hub.com/sentinel-s2-l2a/readme.html
    sentinel_bucket = f"sentinel-s2-{product_level}"
    prefix = f"tiles/{utm_code}/{latitude_band}/{square}/{year}/{month}/{day}/0/R10m"
    return sentinel_bucket, prefix


def copy_from_aws(
    sentinel_bucket: str, identifier: str, prefix: str, band: str
) -> bool:
    try:
        band_file_input = f"{band}.jp2"
        band_file_output = f"{band}_10m.jp2"
        response = s3_client.copy_object(
            Bucket=BUCKET_NAME,
            Key=f"{DATA_OUTPUT_PREFIX_AWS}/{identifier}/{band_file_output}",
            CopySource={
                "Bucket": sentinel_bucket,
                "Key": f"{prefix}/{band_file_input}",
            },
            RequestPayer="requester",
        )
        if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
            return True
        else:
            logger.warning("Copy object on AWS failed")
            return False
    except s3_client.exceptions.NoSuchKey:
        # ToDo: Need better error handling
        # should trigger LTA
        logger.warning("No such key in bucket")
        return False


def download_from_aws(
    sentinel_bucket: str, prefix: str, band: str, target_folder: Path
) -> bool:
    band_file_input = f"{band}.jp2"
    band_file_output = f"{band}_10m.jp2"
    try:
        response = s3_client.get_object(
            Bucket=sentinel_bucket,
            Key=f"{prefix}/{band_file_input}",
            RequestPayer="requester",
        )
    except s3_client.exceptions.NoSuchKey:
        # ToDo: Need better error handling
        # should trigger LTA
        logger.warning("No such key in bucket")
        return False

    response_content = response["Body"].read()
    # TODO: add variable for resolution
    with open(target_folder / band_file_output, "wb") as file:
        file.write(response_content)
    return True


def write_downloaded_size(target_folder: Path) -> None:
    # Get all files in folder
    files = list(target_folder.iterdir())

    # Calculate total size of files
    total_size = sum(f.stat().st_size for f in files if f.is_file())

    root_folder = target_folder.parents[0]

    # Load existing pickle file or create empty dictionary
    if (root_folder / "downloaded_size_logs.pickle").exists():
        # ? r+b is used due to an error with mypy
        with open((root_folder / "downloaded_size_logs.pickle"), "r+b") as f:
            size_logs = pickle.load(f)
    else:
        size_logs = {}

    # Add or update the size for the current date
    today = datetime.now().date()
    if today not in size_logs:
        size_logs[today] = total_size
    else:
        size_logs[today] += total_size

    # Save the updated size logs to the pickle file
    with open((root_folder / "downloaded_size_logs.pickle"), "w+b") as f:
        pickle.dump(size_logs, f)


def upload_to_aws(
    input_folder: Path,
    bucket: Optional[str] = None,
    output_path: Optional[str] = None,
) -> bool:
    """Uploads a Sentinel-2 image to AWS S3.

    Args:
        input_folder (Path): The path to the directory where the Sentinel-2 image is
            located.

    Returns:
        bool: True if the upload was successful, False otherwise.
    """
    # If S3 object_name was not specified, use file_name
    if output_path is None:
        output_path = os.path.basename(input_folder)

    for root, dirs, files in os.walk(input_folder):
        for file in files:
            local_file = os.path.join(root, file)

            # Upload the file
            try:
                s3_client.upload_file(local_file, BUCKET_NAME, f"{output_path}/{file}")
            except ClientError as e:
                logger.warning(e)
                return False
    return True
