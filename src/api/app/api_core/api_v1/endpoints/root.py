# third-party
from fastapi import APIRouter

# local modules
from app.cloud.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter()


@router.get("/")
def root():
    return {"message": "API is running"}


@router.get("/health")
def health_check():
    return {"status": "Healthy"}


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


# @router.get("/docker-token")
# def docker_token():
#     return {"token": settings.DOCKER_SWARM_JOIN_TOKEN_MANAGER}


# @router.get("/env")
# def docker_env():
#     return {
#         "USER": settings.POSTGRES_USER,
#         "PASSWORD": settings.POSTGRES_PASSWORD,
#         "HOST": settings.POSTGRES_HOST,
#         "POSTGRES_PORT": settings.POSTGRES_PORT,
#         "FIRST_SUPERUSER": settings.FIRST_SUPERUSER,
#         "FIRST_SUPERUSER_PASSWORD": settings.FIRST_SUPERUSER_PASSWORD,
#         "SECRET_KEY": settings.SECRET_KEY,
#         "DOCKER_SWARM_MANAGER_IP": settings.DOCKER_SWARM_MANAGER_IP,
#         "DOCKER_SWARM_JOIN_TOKEN_MANAGER": settings.DOCKER_SWARM_JOIN_TOKEN_MANAGER,
#         "DOCKER_SWARM_JOIN_TOKEN_WORKER": settings.DOCKER_SWARM_JOIN_TOKEN_WORKER,
#     }


# @router.get("/docker-info")
# def docker_info():
#     client = docker.from_env()
#     info = client.info()
#     return {"info": info}
