# built-in
from typing import Any, List

# third-party
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/")
def root():
    return {"message": "Hello World!"}
