# third-party
from typing import Any

import docker
import requests
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session
from tenacity import retry, stop_after_attempt, wait_fixed

from app import crud, models
from app.api_core import deps
from app.cloud.logging_config import get_logger
from app.core.config import settings

logger = get_logger(__name__)

router = APIRouter()


@router.get("/")
def root():
    return {"message": "API is running"}


@router.get("/health")
def health_check():
    return {"status": "Healthy"}


@router.get("/test_connection-API")
def test_connection(service_name: str):
    try:
        response = requests.get(f"http://{service_name}/")
    except requests.exceptions.ConnectionError as e:
        return {"error": f"connection to {service_name}/ failed with error {e} "}
    if response.status_code == 200:
        return {"success": "connection established"}
    else:
        return {"error": "connection failed"}


@router.get("/docker-token")
def docker_token():
    return {"token": settings.DOCKER_SWARM_JOIN_TOKEN_MANAGER}


@router.get("/env")
def docker_env():
    return {
        "USER": settings.POSTGRES_USER,
        "PASSWORD": settings.POSTGRES_PASSWORD,
        "HOST": settings.POSTGRES_HOST,
        "POSTGRES_PORT": settings.POSTGRES_PORT,
        "FIRST_SUPERUSER": settings.FIRST_SUPERUSER,
        "FIRST_SUPERUSER_PASSWORD": settings.FIRST_SUPERUSER_PASSWORD,
        "SECRET_KEY": settings.SECRET_KEY,
        "DOCKER_SWARM_MANAGER_IP": settings.DOCKER_SWARM_MANAGER_IP,
        "DOCKER_SWARM_JOIN_TOKEN_MANAGER": settings.DOCKER_SWARM_JOIN_TOKEN_MANAGER,
        "DOCKER_SWARM_JOIN_TOKEN_WORKER": settings.DOCKER_SWARM_JOIN_TOKEN_WORKER,
    }


@router.get("/docker-info")
def docker_info():
    client = docker.from_env()
    info = client.info()
    return {"info": info}


def add_service_to_swarm(
    image: str = "taraman12/api-preprocessing:latest",
    service_name: str = "main_preprocessing",
    network_name: str = "main_mynetwork",
    ports: dict = {8001: 8001},
) -> Any:
    client = docker.from_env()
    try:
        response = client.services.create(
            image=image,
            name=service_name,
            networks=[network_name],
            endpoint_spec=docker.types.EndpointSpec(ports=ports),
            env=[
                f"FIRST_SUPERUSER={settings.FIRST_SUPERUSER}",
                f"FIRST_SUPERUSER_PASSWORD={settings.FIRST_SUPERUSER_PASSWORD}",
            ],
        )
    except Exception as e:
        logger.error(e)
        return {"error": e}

    return {"serviceID": response.id}


def add_ml_serve_to_swarm(
    image: str = "taraman12/solar-park-detection-ml-serve:latest",
    service_name: str = "main_ml_serve",
    network_name: str = "main_mynetwork",
) -> Any:
    client = docker.from_env()
    try:
        response = client.services.create(
            image=image,
            name=service_name,
            networks=[network_name],
        )
    except Exception as e:
        logger.error(e)
        return {"error": e}

    return {"serviceID": response.id}


@retry(wait=wait_fixed(15), stop=stop_after_attempt(10))
def wait_for_node(nodes_old: list = []):
    client = docker.from_env()
    nodes_new = client.nodes.list()
    logger.info("Waiting for node to join swarm...")
    if len(nodes_new) < len(nodes_old):
        raise Exception("Node not joined swarm")


def start_instance_and_service(db: Session, service: str, instance_type: str):
    logger.info(f"Starting instance for {service}")
    client = docker.from_env()
    logger.info(f"Client: {client.info()}")

    nodes_old = client.nodes.list()
    logger.info(f"Nodes before: {nodes_old}")
    instance = crud.instance.start_instance(
        db=db, service=service, instance_type=instance_type
    )
    logger.info(
        f"Started instance with instance id: {instance['Instances'][0]['InstanceId']}"
    )
    if not instance:
        raise HTTPException(status_code=404, detail="instance not found")

    logger.info("Waiting for node to join swarm...")

    try:
        wait_for_node(nodes_old=nodes_old)
    except Exception as e:
        logger.error(e)
        return {"error": e}

    logger.info("Node joined swarm")

    # add_ml_serve_to_swarm()
    add_service_to_swarm()
    # could check if service is running


@router.post("/start-service")
def start_service(
    *,
    db: Session = Depends(deps.get_db),
    service: str,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    instance_type: str = "t3.micro",
    background_tasks: BackgroundTasks,
) -> Any:
    """Start service."""
    background_tasks.add_task(start_instance_and_service, db, service, instance_type)
    return {"status": "started"}


# --------- Start Up ------------ #
# The process works, however it is at least a t3.small instance needed to run the docker containers
# but it is not in the aws free tier (only t3.micro)

# 1. Start instance
#   instance/start/{service}
# 2. Check if instance is running by checking if two nodes exists
# problem is, that the nodes are still shown, even if the instance is shut down or the node left the swarm
#   service/list-nodes
# 3. Add service to swarm
#   service/add-service
# 4. Check if service is running
#    /test_connection-API

# --------- During running ------------ #
# 5. Get service logs
# use Prometheus and Grafana for monitoring
# TODO: add service logs

# --------- Shut Down ------------ #
# 6. Stop service
#  service/remove-service
# 7. Stop instance
# and not stored with id in db
# instance/terminate/{service} (needs to be tested)
#
# todo: move to preprocessing service
# @router.get("/leave-swarm")
# def leave_swarm():
#     client = docker.from_env()
#     try:
#         response = client.swarm.leave(force=True)
#     except Exception as e:
#         logger.error(e)
#         return {"error": e}
#     return {"response": response}
