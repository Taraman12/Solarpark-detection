# build-in
import os
import re
from pathlib import Path
from typing import Optional, Union, List

# third-party
import boto3
from boto3 import client
from botocore.errorfactory import ClientError
from dotenv import load_dotenv

# local-modules
from constants import IDENTIFIER_REGEX
from cloud_clients import s3_client, bucket_name


def download_from_aws(image_input_dir: Path, deployed: bool = False) -> bool:
    prefix = image_input_dir.parent.name
    identifier = image_input_dir.name

    regex_match = re.search(IDENTIFIER_REGEX, identifier)

    if not regex_match:
        return False
    # download all files in the aws folder

    files_list = aws_list_files(f"{prefix}/{identifier}")
    for band_file in files_list:
        # Skip if file already exists
        if os.path.exists(band_file):
            continue
        # add try except block
        # https://stackoverflow.com/questions/63323425/download-sentinel-file-from-s3-using-python-boto3
        try:
            response = s3_client.get_object(
                Bucket=bucket_name,
                Key=band_file,  # f"{prefix}/{identifier}/{band_file}"
            )
        except s3_client.exceptions.NoSuchKey:
            # ToDo: Need better error handling
            # should trigger LTA
            print("No such key in bucket")
            return False

        response_content = response["Body"].read()
        # ! add variable for resolution
        Path(band_file).parent.mkdir(parents=True, exist_ok=True)
        with open(band_file, "wb") as file:
            file.write(response_content)

    return True


def aws_list_folders(prefix: str) -> list:
    """List folders in specific S3 URL"""
    s3_folders = s3_client.list_objects_v2(
        Bucket=bucket_name, Prefix=f"{prefix}/", Delimiter="/"
    )
    folder_list: List[str] = []
    if s3_folders["KeyCount"] == 0:
        return folder_list
    return [item["Prefix"] for item in s3_folders["CommonPrefixes"]]


def aws_list_files(prefix: str) -> list:
    """List files in specific S3 URL"""
    s3_files = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    file_list: List[str] = []
    if s3_files["KeyCount"] == 0:
        return file_list
    for file in s3_files["Contents"]:
        file_list.append(file["Key"])
    return file_list


def upload_file_to_aws(
    input_file_path: Path,
    output_path: Optional[str] = None,
) -> bool:
    """
    Uploads a Sentinel-2 image to AWS S3.

    Args:
        input_file_path (Path): The path to the directory where the Sentinel-2 image is
            located.

    Returns:
        bool: True if the upload was successful, False otherwise.

    """
    # If S3 object_name was not specified, use file_name
    if output_path is None:
        output_path = os.path.basename(input_file_path)

    prefix = "data_preprocessed"
    # Upload the file
    try:
        response = s3_client.upload_file(input_file_path, bucket_name, f"{prefix}/{output_path}")
        return True
    except ClientError as e:
        # logging.error(e)
        return False


def upload_folder_to_aws(
    input_folder: Path,
    output_path: Optional[str] = None,
) -> bool:
    """
    Uploads a Sentinel-2 image to AWS S3.

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
                response = s3_client.upload_file(
                    local_file, bucket_name, f"{output_path}/{file}"
                )
            except ClientError as e:
                # logging.error(e)
                return False
    return True