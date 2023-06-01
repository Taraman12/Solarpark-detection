# build-in
import os

# third-party
import boto3
from botocore.errorfactory import ClientError
from dotenv import load_dotenv

# local-modules
from logging_config import get_logger

# set up logger
logger = get_logger('BaseConfig')


load_dotenv()
# login to aws
session = boto3.Session(
    aws_access_key_id=os.getenv("aws_access_key_id"),
    aws_secret_access_key=os.getenv("aws_secret_access_key"),
    region_name=os.getenv("region_name"),
)

# create s3 client
s3_client = session.client("s3")

BUCKET_NAME = os.getenv("aws_s3_bucket")


def verify_aws_credentials() -> bool:
    try:
        s3_client.list_buckets()
        return True
    except ClientError:
        logger.warning("Credentials are NOT valid.")
        return False


aws_available = verify_aws_credentials()
