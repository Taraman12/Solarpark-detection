from typing import Union
import requests
from fastapi import FastAPI
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import docker

app = FastAPI()
URL_ML = "http://ml-serve:8080"
URL_MASTER = "http://preprocessing-ma:8000"
URL_WORKER = "http://preprocessing-w:8000"
# client = docker.from_env()


class Settings(BaseSettings):
    USERNAME: str = Field("postgres")
    PASSWORD: str = Field("postgres")
    JOIN_TOKEN: str = Field("SWMTKN-1-token")
    MANAGER_IP: str = Field("10.0.1.10")


settings = Settings()


@app.get("/")
def read_root():
    return {"Hello": f"api-preprocessing is running. URL_ML: {URL_ML}"}


@app.get("/env")
def read_env():
    return {
        "Message": f"URL_ML: {URL_ML}, USERNAME: {settings.USERNAME}, PASSWORD: {settings.PASSWORD}, JOIN_TOKEN: {settings.JOIN_TOKEN}, MANAGER_IP: {settings.MANAGER_IP}"
    }


@app.get("/test_connection-ML")
def test_connection():
    try:
        response = requests.get(f"{URL_ML}/ping")
    except requests.exceptions.ConnectionError as e:
        return {"error": f"connection to {URL_ML}/prediction failed with error {e} "}
    if response.status_code == 200:
        return {"success": "connection established"}
    else:
        return {"error": "connection failed"}


@app.get("/test_connection-master")
def test_connection():
    try:
        response = requests.get(f"{URL_MASTER}/")
    except requests.exceptions.ConnectionError as e:
        return {"error": f"connection to {URL_MASTER}/ failed with error {e} "}
    if response.status_code == 200:
        return {"success": "connection established"}
    else:
        return {"error": "connection failed"}


@app.get("/test_connection-worker")
def test_connection():
    try:
        response = requests.get(f"{URL_WORKER}/")
    except requests.exceptions.ConnectionError as e:
        return {"error": f"connection to {URL_WORKER}/ failed with error {e} "}
    if response.status_code == 200:
        return {"success": "connection established"}
    else:
        return {"error": "connection failed"}


@app.get("/start-swarm-env")
def docker_token():
    try:
        client = docker.from_env()
        response = client.swarm.init()
        return {"response": response}
    except Exception as e:
        return {"error": e}


@app.get("/join-swarm-env")
def docker_token():
    try:
        client = docker.from_env()
        response = client.swarm.join(
            remote_addrs=[settings.MANAGER_IP],
            join_token=settings.JOIN_TOKEN,
        )
        return {"response": response}
    except Exception as e:
        return {"error": e}


# @app.get("/start-swarm-base")
# def docker_token():
#     try:
#         client = docker.DockerClient(base_url="unix://var/run/docker.sock")
#         response = client.swarm.init()
#         return {"response": response}
#     except Exception as e:
#         return {"error": e}


# @app.get("/docker-info")
# def docker_info():
#     try:
#         client = docker.DockerClient(base_url="unix://var/run/docker.sock")
#         info = client.info()
#         return {"token": info}
#     except Exception as e:
#         return {"error": e}


# @app.get("/token-from-env")
# def docker_token():
#     try:
#         client = docker.from_env()
#         token = client.swarm.get_unlock_key()
#     except Exception as e:
#         return {"error": e}
#     print("token", token)
#     print(info["Swarm"])
#     return {"token": token}


# @app.get("/token-base")
# def docker_token():
#     try:
#         client = docker.DockerClient(base_url="unix://var/run/docker.sock")
#         token = client.swarm.get_unlock_key()
#     except Exception as e:
#         return {"error": e}
#     print("token", token)
#     print(info["Swarm"])
#     return {"token": token}
