from typing import Any, List

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

client = docker.from_env()


@router.get("/get-service")
def get_service_from_swarm(
    serviceID: str,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
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


def add_service_to_swarm(
    image: str = "taraman12/solar-park-detection-processing:latest",
    service_name: str = "main_processing",
    network_name: str = "main_mynetwork",
    ports: dict = {7000: 7000},
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
    ports: dict = {8080: 8080, 8081: 8081},
) -> Any:
    client = docker.from_env()
    try:
        response = client.services.create(
            image=image,
            name=service_name,
            networks=[network_name],
            endpoint_spec=docker.types.EndpointSpec(ports=ports),
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


def start_instance_and_service(db: Session, instance_tag: str, instance_type: str):
    logger.info(f"Starting instance for {instance_tag}")
    client = docker.from_env()

    nodes_old = client.nodes.list()
    logger.info(f"Nodes before: {nodes_old}")
    instance = crud.instance.start_instance(
        db=db, instance_tag=instance_tag, instance_type=instance_type
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

    add_ml_serve_to_swarm()
    add_service_to_swarm()
    # could check if service is running
    return {"status": "finished"}


@router.post("/start-service")
def start_service(
    *,
    db: Session = Depends(deps.get_db),
    instance_tag: str,
    current_user: models.User = Depends(deps.get_current_active_superuser),
    instance_type: str = "t3.micro",
    background_tasks: BackgroundTasks,
) -> Any:
    """Start service."""
    background_tasks.add_task(
        start_instance_and_service, db, instance_tag, instance_type
    )
    return {"status": "started"}


@router.delete("/remove-service")
def remove_service_from_swarm(
    name: str, current_user: models.User = Depends(deps.get_current_active_superuser)
) -> Any:
    try:
        response = client.services.get(name).remove()
    except docker.errors.NotFound:
        logger.error(f"Service {name} not found in swarm")
        return {"response": f"Service {name} not found in swarm"}
    except Exception as e:
        logger.error(e)
        return {"response": e}
    return {"response": response}


@router.get("/test-connection-service")
def test_connection(service_name: str):
    try:
        response = requests.get(f"http://{service_name}/")
    except requests.exceptions.ConnectionError as e:
        return {"error": f"connection to {service_name}/ failed with error {e} "}
    if response.status_code == 200:
        return {"success": "connection established"}
    else:
        return {"error": "connection failed"}


@router.get("/run-service-checks")
def run_service_checks(
    service_name: str,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """Run service checks."""
    try:
        response = requests.get(f"http://{service_name}/run-checks")
    except requests.exceptions.ConnectionError as e:
        return {"error": f"connection to {service_name}/ failed with error {e} "}
    return response.json()


@router.post("/run-prediction")
def run_prediction(
    service_name: str = "processing:7000",
    tiles_list: List[str] = ["32UQE"],
    start_date: str = "2020-05-01",
    end_date: str = "2020-07-02",
    model: str = "solar-park-detection",
    # current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """Run predictions."""
    url = f"http://{service_name}/run-prediction"
    params = {"start_date": start_date, "end_date": end_date}
    # json = tiles_list
    try:
        response = requests.post(url=url, params=params, json=tiles_list)
    except requests.exceptions.ConnectionError as e:
        return {"error": f"connection to {service_name}/ failed with error {e} "}
    return response.json()


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


@router.get("/get-nodes-overview")
def get_nodes_info() -> Any:
    client = docker.from_env()
    nodes_info = {}
    try:
        nodes = client.nodes.list()
        for i, node in enumerate(nodes):
            node_attrs = node.attrs
            nodes_info[i] = {
                "Node ID": node_attrs["ID"],
                "Status": node_attrs["Status"]["State"],
                "Availability": node_attrs["Spec"]["Availability"],
                "Manager Status": node_attrs["ManagerStatus"]["Leader"]
                if "ManagerStatus" in node_attrs
                else "N/A",
                "Created At": node_attrs["CreatedAt"],
            }
    except Exception as e:
        logger.error(e)
        return {"error": str(e)}

    return nodes_info


@router.get("/get-google-maps-api-key")
def get_google_api_key() -> Any:
    return {"api_key": settings.GOOGLE_MAPS_API_KEY}


# ------------------------------------------------------------

# @router.get("/docker-swarm-info")
# def docker_swarm_info():
#     # client = docker.from_env()
#     info = client.swarm.attrs
#     return {"info": info}


# @router.get("/manager-token")
# def manager_token():
#     info = client.swarm.attrs
#     return {"Token": info["JoinTokens"]["Manager"]}


# @router.get("/start-instance-and-join-swarm")
# def start_instance_and_join_swarm(
#     *,
#     db: Session = Depends(deps.get_db),
#     service: str,
#     instance_type: str = "t3.micro",
#     current_user: models.User = Depends(deps.get_current_active_superuser),
# ) -> Any:
#     logger.info(f"Starting instance for service: {service}")
#     # 1. start instance
#     response = crud.instance.start_instance(
#         db=db, service=service, instance_type=instance_type
#     )
#     logger.info(f"Started instance with {response}")
#     return response


# todo: move to crud, and docker secrets
# @router.post("/add-service")
# def add_service_to_swarm(
#     image: str = "taraman12/api-processing:latest",
#     service_name: str = "main_processing",
#     network_name: str = "main_mynetwork",
# ) -> Any:
#     # client = docker.from_env()
#     try:
#         response = client.services.create(
#             image=image,
#             name=service_name,
#             networks=[network_name],
#             env=[
#                 f"FIRST_SUPERUSER={settings.FIRST_SUPERUSER}",
#                 f"FIRST_SUPERUSER_PASSWORD={settings.FIRST_SUPERUSER_PASSWORD}",
#             ],
#         )
#     except Exception as e:
#         logger.error(e)
#         return {"error": e}

#     return {"serviceID": response.id}

# @router.get("/list-containers")
# def list_containers():
#     try:
#         containers = client.containers.list()
#         return {
#             "response": [
#                 {"name": container.name, "id": container.id} for container in containers
#             ]
#         }
#     except Exception as e:
#         logger.error(str(e))
#         return {"error": str(e)}

# @router.get("/update-service")
# def update_service_from_swarm(
#     serviceID: str,
#     image: str,
# ) -> Any:
#     # client = docker.from_env()
#     try:
#         service = client.services.get(serviceID)
#         service.update(image=image)
#     except docker.errors.NotFound:
#         logger.error(f"Service with ID: {serviceID} not found in swarm")
#         return {"response": f"Service with ID: {serviceID} not found in swarm"}
#     except Exception as e:
#         logger.error(e)
#         return {"response": e}
#     return {"response": service}
