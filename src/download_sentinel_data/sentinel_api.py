# build-in
import os
from typing import Union

# third-party
from dotenv import load_dotenv
from sentinelsat import SentinelAPI


def connect_to_sentinel_api() -> Union[SentinelAPI, Exception]:
    load_dotenv()
    api_user = os.getenv("API_USER")
    api_secret = os.getenv("API_SECRET")
    api_url = os.getenv("API_URL")
    api = SentinelAPI(api_user, api_secret, api_url)
    # Connect to the Sentinel API
    try:
        api.query(date=("NOW-8HOURS", "NOW"), producttype="SLC")
        return api
    except Exception as e:
        return e
