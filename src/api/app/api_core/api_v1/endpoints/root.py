# third-party
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import docker
from typing import Any, List
import requests

from app import crud, models, schemas
from app.core.config import settings
import logging

from app.cloud.logging_config import get_logger
from app.api_core import deps

import queue
import threading
import asyncio

logger = get_logger(__name__)

router = APIRouter()

URL_API = "http://preprocessing-w"


def log_stream():
    while True:
        message = log_queue.get()
        if message is None:
            break
        yield message


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


# --------- Start Up ------------ #
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
# instance/terminate/{service}
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
