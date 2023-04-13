# build-in
import os
import pickle
import re
from datetime import datetime
from pathlib import Path

# third-party
import boto3
from dotenv import load_dotenv

# local-modules
import constants as c


def download_from_aws(identifier: str, target_folder: Path) -> bool:
    if not check_aws_free_tier_available(target_folder.parents[0]):
        return False

    load_dotenv()
    aws_access_key_id = os.getenv("aws_access_key_id")
    aws_secret_access_key = os.getenv("aws_secret_access_key")

    # Let's use Amazon S3
    s3 = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )

    regex_match = re.search(c.IDENTIFIER_REGEX, identifier)

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
    bucket = f"sentinel-s2-{product_level}"
    prefix = f"tiles/{utm_code}/{latitude_band}/{square}/{year}/{month}/{day}/0"

    for band in c.BAND_FILE_MAP:
        band_file = f"{band}.jp2"
        band_file_path = target_folder / band_file

        if band_file_path.exists():
            continue

        # https://stackoverflow.com/questions/63323425/download-sentinel-file-from-s3-using-python-boto3
        response = s3.get_object(
            Bucket=bucket, Key=f"{prefix}/{band_file}", RequestPayer="requester"
        )
        response_content = response["Body"].read()
        with open(band_file_path, "wb") as file:
            file.write(response_content)

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
        if datetime.strptime(date, "%Y-%m-%d").year == year
        and datetime.strptime(date, "%Y-%m-%d").month == month
    )
    # ToDo: replace hard-coded value with a constant
    if current_month_sum < 90 * (1024**3):
        print(f"Current month sum is: {current_month_sum/(1024**3)} GB.")
        return True
    else:
        print("Current month sum is 90 GB or above.")
        return False


def write_downloaded_size(target_folder: Path) -> None:
    # Get all files in folder
    files = list(target_folder.iterdir())

    # Calculate total size of files
    total_size = sum(f.stat().st_size for f in files if f.is_file())

    root_folder = target_folder.parents[0]

    # Load existing pickle file or create empty dictionary
    if (root_folder / "downloaded_size_logs.pickle").exists():
        # ? wrb is used due to an error with mypy
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
