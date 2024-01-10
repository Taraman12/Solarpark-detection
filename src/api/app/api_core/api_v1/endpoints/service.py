from typing import Any

import docker
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import crud, models
from app.api_core import deps
from app.cloud.logging_config import get_logger
from app.core.config import settings

logger = get_logger(__name__)

router = APIRouter()

client = docker.from_env()


@router.get("/docker-swarm-info")
def docker_swarm_info():
    # client = docker.from_env()
    info = client.swarm.attrs
    return {"info": info}


@router.get("/manager-token")
def manager_token():
    info = client.swarm.attrs
    return {"Token": info["JoinTokens"]["Manager"]}


@router.get("/start-instance-and-join-swarm")
def start_instance_and_join_swarm(
    *,
    db: Session = Depends(deps.get_db),
    service: str,
    instance_type: str = "t3.micro",
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    logger.info(f"Starting instance for service: {service}")
    # 1. start instance
    response = crud.instance.start_instance(
        db=db, service=service, instance_type=instance_type
    )
    logger.info(f"Started instance with {response}")
    return response


# todo: move to crud, and docker secrets
@router.post("/add-service")
def add_service_to_swarm(
    image: str = "taraman12/api-preprocessing:latest",
    service_name: str = "main_preprocessing",
    network_name: str = "main_mynetwork",
) -> Any:
    # client = docker.from_env()
    try:
        response = client.services.create(
            image=image,
            name=service_name,
            networks=[network_name],
            env=[
                f"FIRST_SUPERUSER={settings.FIRST_SUPERUSER}",
                f"FIRST_SUPERUSER_PASSWORD={settings.FIRST_SUPERUSER_PASSWORD}",
            ],
        )
    except Exception as e:
        logger.error(e)
        return {"error": e}

    return {"serviceID": response.id}


@router.get("/get-service")
def get_service_from_swarm(
    serviceID: str,
) -> Any:
    # client = docker.from_env()
    try:
        response = client.services.get(serviceID)
        return
    except docker.errors.NotFound:
        logger.error(f"Service with ID: {serviceID} not found in swarm")
        return {"response": f"Service with ID: {serviceID} not found in swarm"}
    except Exception as e:
        logger.error(e)
        return {"response": e}
    return {"response": response}


@router.get("/update-service")
def update_service_from_swarm(
    serviceID: str,
    image: str,
) -> Any:
    # client = docker.from_env()
    try:
        service = client.services.get(serviceID)
        service.update(image=image)
    except docker.errors.NotFound:
        logger.error(f"Service with ID: {serviceID} not found in swarm")
        return {"response": f"Service with ID: {serviceID} not found in swarm"}
    except Exception as e:
        logger.error(e)
        return {"response": e}
    return {"response": service}


@router.delete("/remove-service")
def remove_service_from_swarm(
    name: str,
) -> Any:
    # client = docker.from_env()
    try:
        response = client.services.get(name).remove()
    except docker.errors.NotFound:
        logger.error(f"Service {name} not found in swarm")
        return {"response": f"Service {name} not found in swarm"}
    except Exception as e:
        logger.error(e)
        return {"response": e}
    return {"response": response}


@router.get("/list-services")
def list_services() -> Any:
    logger.info("Listing services")
    try:
        services = client.services.list()
        return {
            "response": [
                {"name": service.name, "id": service.id} for service in services
            ]
        }
    except docker.errors.APIError as e:
        logger.error("Docker API error: %s", str(e))
        return {"error": str(e)}
    except Exception as e:
        logger.error("Unexpected error: %s", str(e))
        return {"error": str(e)}


@router.get("/list-containers")
def list_containers():
    try:
        containers = client.containers.list()
        return {
            "response": [
                {"name": container.name, "id": container.id} for container in containers
            ]
        }
    except Exception as e:
        logger.error(str(e))
        return {"error": str(e)}


@router.get("/list-nodes")
def list_nodes():
    try:
        nodes = client.nodes.list()
        return {"response": [{"id": node.id} for node in nodes]}
    except Exception as e:
        logger.error(str(e))
        return {"error": str(e)}
