# build-in
import os
from typing import Union

# third-party
from dotenv import load_dotenv
from sentinelsat import SentinelAPI


def connect_to_sentinel_api() -> Union[SentinelAPI, Exception]:
    load_dotenv()
    api_user = os.getenv("COPERNICUS_API_USER")
    api_secret = os.getenv("COPERNICUS_API_SECRET")
    api_url = os.getenv("COPERNICUS_API_URL")
    api = SentinelAPI(api_user, api_secret, api_url)
    # Connect to the Sentinel API
    try:
        # example query to test connection
        api.query(date=("NOW-8HOURS", "NOW"), producttype="SLC")
        return api
    except Exception as e:
        return e
