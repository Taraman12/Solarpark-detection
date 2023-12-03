from typing import Union
import requests
from fastapi import FastAPI

app = FastAPI()
# URL_ML = "http://ml-serve:8080"


@app.get("/")
def read_root():
    return {"Hello": "api-ml-serve is running"}


@app.get("/prediction")
def test_connection():
    return {"Hello": "World"}
