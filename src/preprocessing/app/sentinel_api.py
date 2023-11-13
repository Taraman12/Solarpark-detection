# build-in
import os
from typing import Union

# third-party
from dotenv import load_dotenv
from logging_config import get_logger
from sentinelsat import SentinelAPI

logger = get_logger("BaseConfig")


def connect_to_sentinel_api() -> Union[SentinelAPI, Exception]:
    load_dotenv()

    api_user = os.getenv("COPERNICUS_API_USER")
    api_secret = os.getenv("COPERNICUS_API_SECRET")
    api_url = os.getenv("COPERNICUS_API_URL")
    logger.info("Connecting to Sentinel API")
    api = SentinelAPI(api_user, api_secret, api_url)
    logger.info("Checking connection to Sentinel API")
    try:
        # example query to test connection
        api.query(date=("NOW-8HOURS", "NOW"), producttype="SLC")
        return api
    except Exception as e:
        return e
