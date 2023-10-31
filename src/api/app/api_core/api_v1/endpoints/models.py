# build-in
from typing import Any

# third-party
import requests
from fastapi import APIRouter, Depends

from app import models
from app.api_core import deps

router = APIRouter()

# * See for possible solution: https://github.com/pytorch/serve/issues/2085
"""
Due to torchserve not supporting S3 presigned URLs or boto3 compatible S3 Paths, we need to put a tiny python
webserver in front of the torchserve management API.

Relevant torchserve issues:
- https://github.com/pytorch/serve/issues/2085
- https://github.com/pytorch/serve/issues/1293

This only handles / forwards requests to the torchserve management API, and does not handle inference requests.

"""


@router.get("/")
def get_model() -> Any:
    """Returns registered models from ml server"""
    response = requests.get("http://ml-serve:8081/models")

    return response.json()["models"]


@router.get("/{model}")
def get_model(model: str) -> Any:  # noqa: F811
    """Get model by name from ml server"""
    response = requests.get(f"http://ml-serve:8081/models/{model}/all")

    return response.json()


@router.post("/")
def register_example_model(
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """Register squeezenet1_1 model as example"""
    response = requests.post(
        "http://ml-serve:8081/models?url=https://torchserve.pytorch.org/mar_files/squeezenet1_1.mar"
    )

    return response.json()


@router.post("/{model}")
async def register_model(
    model: str = "solar-park-detection",
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """register model by name from ml server"""
    response = requests.post(
        f"http://ml-serve:8081/models?url=https://solar-detection-697553-eu-central-1.s3.eu-central-1.amazonaws.com/model-store/{model}.mar"
    )

    return response.json()


@router.post("/as-url/{url}")
def register_model(  # noqa: F811
    url: str,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """register model by url from ml server"""
    response = requests.post(f"http://ml-serve:8081/models?url={url}")

    return response.json()


@router.delete("/{model}")
def delete_model(
    model: str,
    version: int = 1,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """Delete model by name from ml server"""
    response = requests.delete(f"http://ml-serve:8081/models/{model}/{version}.0")

    return response.json()
