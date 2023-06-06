# build-in
import os
import logging

# third-party
import boto3
from botocore.errorfactory import ClientError

# from dotenv import load_dotenv

# import os
import boto3
from dotenv import load_dotenv

# local file
if os.environ.get("LOCAL"):
    load_dotenv()

# In local docker environment, the AWS credentials are stored in the .env file
if os.environ.get("AWS_ACCESS_KEY_ID") and os.environ.get("AWS_SECRET_ACCESS_KEY"):
    session = boto3.Session(
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        region_name=os.environ.get("AWS_REGION"),
    )

# if deployed on aws ec2 instance, the credentials are provided by the IAM role of the ec2 instance
else:
    logging.info("Using IAM role credentials")
    session = boto3.Session(region_name="eu-central-1")
    credentials = session.get_credentials()
    credentials = credentials.get_frozen_credentials()
    session = boto3.Session(
        aws_access_key_id=credentials.access_key,
        aws_secret_access_key=credentials.secret_key,
        region_name="eu-central-1",
    )


# create s3 client
s3_client = session.client("s3")


def verify_aws_credentials() -> bool:
    try:
        s3_client.list_buckets()
        return True
    except ClientError:
        print("Credentials are NOT valid.")
        return False


aws_available = verify_aws_credentials()
