# third-party
import requests
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def root():
    return {"message": "Hello World!"}


@router.get("/ml-server")
def ml_server():
    response = requests.get("http://ml-serve:8081/models")
    # return json response
    return response.json()["models"][0]
