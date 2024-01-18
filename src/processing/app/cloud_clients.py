# build-in
import os

# third-party
import boto3
from botocore.credentials import InstanceMetadataFetcher, InstanceMetadataProvider
from botocore.errorfactory import ClientError
from dotenv import load_dotenv

from app.logging_config import get_logger

logger = get_logger(__name__)

"""
ToDo: rework aws credentials
"""
# local file
if not os.environ.get("DOCKERIZED"):
    load_dotenv()


logger.info("aws_access_key_id: ", os.getenv("aws_access_key_id"))

# In local docker environment, the AWS credentials are stored in the .env file
if os.environ.get("aws_access_key_id") and os.environ.get("aws_secret_access_key"):
    session = boto3.Session(
        aws_access_key_id=os.environ.get("aws_access_key_id"),
        aws_secret_access_key=os.environ.get("aws_secret_access_key"),
        region_name=os.environ.get("region_name"),
    )

# if deployed on aws ec2 instance, the credentials are provided by the IAM role of the ec2 instance
else:
    logger.info("Using IAM role credentials")
    provider = InstanceMetadataProvider(
        iam_role_fetcher=InstanceMetadataFetcher(timeout=1000, num_attempts=2)
    )
    if provider.load() is None:
        raise ValueError("No IAM role found")
    try:
        credentials = provider.load().get_frozen_credentials()
        logger.info(f"Credentials:{credentials.access_key}")
        session = boto3.Session(
            aws_access_key_id=credentials.access_key,
            aws_secret_access_key=credentials.secret_key,
            aws_session_token=credentials.token,
            region_name="eu-central-1",
        )
    except AttributeError as e:
        logger.error(e)


# create s3 client
s3_client = session.client("s3")


def verify_aws_credentials() -> bool:
    try:
        s3_client.list_buckets()
        return True
    except ClientError:
        logger.error("Credentials are NOT valid.")
        return False


aws_available = verify_aws_credentials()
