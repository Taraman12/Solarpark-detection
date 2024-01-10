import requests
from fastapi import FastAPI

app = FastAPI()
URL_ML = "http://ml-serve:8080"


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/test_connection")
def test_connection():
    try:
        response = requests.get(f"{URL_ML}/ping")
    except requests.exceptions.ConnectionError:
        return {"error": "connection failed"}
    if response.status_code == 200:
        return {"success": "connection established"}
    else:
        return {"error": "connection failed"}
