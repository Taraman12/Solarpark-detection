# build-in
import os

# third-party
import boto3
from boto3 import client
from botocore.errorfactory import ClientError
from dotenv import load_dotenv


# login to aws
session = boto3.Session(
    aws_access_key_id=os.getenv("aws_access_key_id"),
    aws_secret_access_key=os.getenv("aws_secret_access_key"),
    region_name=os.getenv("region_name"),
)

# crreate s3 client
s3_client = session.client("s3")

bucket_name = os.getenv("aws_s3_bucket")

def verify_aws_credentials() -> bool:
    try:
        response = s3_client.list_buckets()
        return True
    except ClientError:
        print("Credentials are NOT valid.")
        return False

# aws_available = verify_aws_credentials()
aws_available = False