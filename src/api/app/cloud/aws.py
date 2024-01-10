# build-in
import os

# third-party
import boto3

# import docker
from botocore.credentials import InstanceMetadataFetcher, InstanceMetadataProvider
from botocore.errorfactory import ClientError
from dotenv import load_dotenv

from app.core.config import settings

from .logging_config import get_logger

# import logging
"""

ToDo: Rework the login with boto3
"""
# local-modules

# load_dotenv()
# login to aws
aws_access_key_id = os.getenv("aws_access_key_id")
aws_secret_access_key = os.getenv("aws_secret_access_key")
region_name = os.getenv("region_name")
BUCKET_NAME = os.getenv("aws_s3_bucket")

COPERNICUS_API_USER = os.getenv("COPERNICUS_API_USER")
COPERNICUS_API_SECRET = os.getenv("COPERNICUS_API_SECRET")
COPERNICUS_API_URL = os.getenv("COPERNICUS_API_URL")

DOCKERHUB_USER = os.getenv("DOCKERHUB_USER")
DOCKERHUB_PASSWORD = os.getenv("DOCKERHUB_PASSWORD")

PROJECT_NAME = os.getenv("PROJECT_NAME")

session = boto3.Session(
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=region_name,
)

logger = get_logger(__name__)
# local file
# local file
if not os.environ.get("DOCKERIZED"):
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
    logger.info("Using IAM role credentials")
    provider = InstanceMetadataProvider(
        iam_role_fetcher=InstanceMetadataFetcher(timeout=1000, num_attempts=2)
    )
    try:
        credentials = provider.load().get_frozen_credentials()
        logger.info(f"Credentials:{credentials.access_key}")
        session = boto3.Session(
            aws_access_key_id=credentials.access_key,
            aws_secret_access_key=credentials.secret_key,
            aws_session_token=credentials.token,
            region_name="eu-central-1",
        )
    except Exception as e:
        logger.error(f"Error: {e}")


# create s3 client
s3_client = session.client("s3")
ec2_client = session.client("ec2", region_name="eu-central-1")
ec2_resource = session.resource("ec2", region_name="eu-central-1")


def verify_aws_credentials() -> bool:
    try:
        s3_client.list_buckets()
        logger.info("Credentials are valid.")
        return True
    except ClientError:
        logger.warning("Credentials are NOT valid.")
        return False


aws_available = verify_aws_credentials()


# client = docker.from_env()

EC2_KWARGS = {
    "ImageId": "ami-07151644aeb34558a",
    "InstanceType": "t3.small",
    "MinCount": 1,
    "MaxCount": 1,
    "KeyName": "Ec2-boto3",
    "SecurityGroupIds": ["sg-0b7b73b05e7577a3b"],
    "IamInstanceProfile": {
        "Arn": "arn:aws:iam::103976228435:instance-profile/EC2_S3_allowens"
    },
    "SubnetId": "subnet-0e19e3f6d404a4467",
    "UserData": f"""#!/bin/bash
                sudo yum update -y
                sudo yum install docker -y
                sudo service docker start
                sudo usermod -a -G docker ec2-user
                sudo docker pull taraman12/api-ml-serve:latest
                sudo docker pull taraman12/api-preprocessing:latest
                sudo docker swarm join --token {settings.DOCKER_SWARM_JOIN_TOKEN_WORKER} {settings.DOCKER_SWARM_MANAGER_IP}:2377

             """,
    "TagSpecifications": [
        {
            "ResourceType": "instance",
            "Tags": [
                {"Key": "Name", "Value": "worker-instance"},
            ],
        },
    ],
}
# echo 'sudo docker swarm leave --force' > /usr/local/bin/docker-swarm-leave.sh
# chmod +x /usr/local/bin/docker-swarm-leave.sh
# echo '[Unit]
# Description=Leave Docker Swarm before shutdown
# DefaultDependencies=no
# Before=shutdown.target reboot.target halt.target

# [Service]
# Type=oneshot
# ExecStart=/usr/local/bin/docker-swarm-leave.sh
# TimeoutStartSec=0

# [Install]
# WantedBy=halt.target reboot.target shutdown.target' > /etc/systemd/system/docker-swarm-leave.service
# systemctl enable docker-swarm-leave
# sudo docker service create -d \
#     -p 8080:8080 \
#     --network mynetwork \
#     --name ml-serve \
#     taraman12/api-ml-serve:latest
# sudo docker service create -d \
#     -v /var/run/docker.sock:/var/run/docker.sock \
#     -p 8000:8000 \
#     --network mynetwork \
#     --name preprocessing-w \
#     -e FIRST_SUPERUSER={settings.FIRST_SUPERUSER} \
#     -e FIRST_SUPERUSER_PASSWORD={settings.FIRST_SUPERUSER_PASSWORD} \
#     -e DOCKER_SWARM_JOIN_TOKEN_MANAGER={settings.DOCKER_SWARM_JOIN_TOKEN_MANAGER} \
#     -e DOCKER_SWARM_MANAGER_IP={settings.DOCKER_SWARM_MANAGER_IP} \
#     taraman12/api-preprocessing:latest

# EC2_KWARGS = {
#     "ImageId": "ami-07151644aeb34558a",  # ID des Amazon Linux 2 AMI
#     "InstanceType": "t2.micro",  # Instanztyp t3.medium
#     "MinCount": 1,  # Mindestanzahl von Instanzen
#     "MaxCount": 1,  # Maximale Anzahl von Instanzen
#     "KeyName": "Ec2-boto3",  # Name des Schlüsselpaars
#     "SubnetId": "subnet-054aaab26d7a9f96f",
#     "SecurityGroupIds": ["sg-0b7b73b05e7577a3b"],  # ID der Sicherheitsgruppe
#     "BlockDeviceMappings": [
#         {
#             "DeviceName": "/dev/xvda",
#             "Ebs": {
#                 "VolumeSize": 20,  # Größe des Root-Volumes in GB
#                 "DeleteOnTermination": True,
#                 "VolumeType": "gp3",
#             },
#         },
#     ],
#     "UserData": """#!/bin/bash
#                 sudo yum update -y
#                 sudo yum install docker -y
#                 sudo service docker start
#                 sudo usermod -a -G docker ec2-user
#                 sudo curl \
#                     -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) \
#                     -o /usr/local/bin/docker-compose
#                 sleep 3
#                 sudo chmod +x /usr/local/bin/docker-compose
#              """,  # Skript, das beim Start der Instanz ausgeführt wird
#     "TagSpecifications": [
#         {
#             "ResourceType": "instance",
#             "Tags": [
#                 {"Key": "Name", "Value": "solar-park-detection-ml-serve"},
#             ],
#         },
#     ],
# }

# EC2_KWARGS = {
#     "ImageId": "ami-07151644aeb34558a",  # ID des Amazon Linux 2 AMI
#     "InstanceType": "t3.micro",  # Instanztyp t3.medium
#     "MinCount": 1,  # Mindestanzahl von Instanzen
#     "MaxCount": 1,  # Maximale Anzahl von Instanzen
#     "KeyName": "Ec2-boto3",  # Name des Schlüsselpaars
#     "SecurityGroupIds": ["sg-0b7b73b05e7577a3b"],  # ID der Sicherheitsgruppe
#     "BlockDeviceMappings": [
#         {
#             "DeviceName": "/dev/xvda",
#             "Ebs": {
#                 "VolumeSize": 20,  # Größe des Root-Volumes in GB
#                 "DeleteOnTermination": True,
#                 "VolumeType": "gp3",
#             },
#         },
#     ],
#     "UserData": f"""#!/bin/bash
#                 sudo yum update -y
#                 sudo yum install docker -y
#                 sudo service docker start
#                 sudo usermod -a -G docker ec2-user
#                 sudo docker pull {DOCKERHUB_USER}/{PROJECT_NAME}-downloader:latest
#                 sudo docker run \
#                 -e DOCKERIZED=True \
#                 -e aws_access_key_id={aws_access_key_id} \
#                 -e aws_secret_access_key={aws_secret_access_key} \
#                 -e region_name={region_name} \
#                 -e aws_s3_bucket={BUCKET_NAME} \
#                 -e COPERNICUS_API_USER={COPERNICUS_API_USER} \
#                 -e COPERNICUS_API_SECRET={COPERNICUS_API_SECRET} \
#                 -e COPERNICUS_API_URL={COPERNICUS_API_URL} \
#                 {DOCKERHUB_USER}/{PROJECT_NAME}-downloader:latest
#              """,  # Skript, das beim Start der Instanz ausgeführt wird
#     "TagSpecifications": [
#         {
#             "ResourceType": "instance",
#             "Tags": [
#                 {"Key": "Name", "Value": f"{PROJECT_NAME}-downloader"},
#             ],
#         },
#     ],
# }

# echo {DOCKERHUB_PASSWORD} | sudo docker login --username {DOCKERHUB_USER} --password-stdin
