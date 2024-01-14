from typing import Dict, List
import requests
from fastapi import FastAPI, BackgroundTasks
from app.health_checks import run_checks
from app.main_preprocessing import main, run_setup
from app.logging_config import get_logger

logger = get_logger(__name__)

app = FastAPI()
URL_ML = "http://ml-serve:8080"


@app.get("/")
def read_root():
    return {"Message": "Service is running"}


@app.get("/run-checks")
def health_check():
    run_setup()
    message = run_checks()
    return {"Message": message}


@app.post("/run-prediction")
def run_prediction(
    *,
    tiles_list: List[str] = ["32UQE"],
    start_date: str = "2020-05-01",
    end_date: str = "2020-07-02",
    background_tasks: BackgroundTasks,
):
    logger.info(f"Tiles list: {tiles_list}")
    if start_date and end_date:
        dates = {"start_date": start_date, "end_date": end_date}
    else:
        dates = None
    background_tasks.add_task(start_preprocessing, tiles_list=tiles_list, dates=dates)
    return {"status": "started"}


def start_preprocessing(tiles_list: list = None, dates: Dict[str, str] = None):
    main(tiles_list=tiles_list, dates=dates)
    return {"Message": "Preprocessing finished"}
