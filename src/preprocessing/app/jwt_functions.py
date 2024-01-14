import os
import time

import requests
from app.constants import URL_API
from app.logging_config import get_logger
from app.settings import FIRST_SUPERUSER, FIRST_SUPERUSER_PASSWORD

logger = get_logger(__name__)


def get_jwt() -> str:
    """
    Get JWT from environment variable or API.

    Returns:
        str: The JWT.

    Raises:
        Exception: If the JWT cannot be obtained from the environment variable or the API.
    """
    try:
        return get_jwt_from_environ()
    except KeyError:
        try:
            token = get_jwt_from_api()
            store_jwt(token)
            return token
        except Exception as e:
            logger.error(f"Could not get JWT: {e}")
            raise Exception("Could not get JWT") from e


def get_jwt_from_api(username: str | None = None, password: str | None = None) -> str:
    """
    Get JWT from API.

    Args:
        username (str, optional): The username to use for authentication. If not provided, the default username from settings will be used.
        password (str, optional): The password to use for authentication. If not provided, the default password from settings will be used.

    Returns:
        str: The JWT.

    Raises:
        Exception: If the request fails with a status code other than 401, or if the status code is 401 and the error message is "Not authenticated".
    """

    username = username or FIRST_SUPERUSER
    password = password or FIRST_SUPERUSER_PASSWORD

    if not username:
        logger.error("Username not provided")
        raise Exception("Username not provided")
    if not password:
        logger.error("Password not provided")
        raise Exception("Password not provided")
    if not URL_API:
        logger.error("URL_API not stored in environment variable")
        raise ValueError("URL_API not stored in constants.py")

    url = f"{URL_API}/login/access-token"
    data = {"username": username, "password": password}
    logger.info(f"Sending request to API: {url}")
    logger.info(f"Request data: {data}")
    for i in range(3):
        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            break
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed with exception: {e}")
            if i < 2:
                time.sleep(5)
    logger.info(f"Got response from API: {response}")
    if response.ok:
        return response.json()["access_token"]

    if (
        response.status_code == 401
        and response.json().get("detail") == "Not authenticated"
    ):
        logger.error("Invalid credentials")
        raise Exception("Invalid credentials")

    logger.error(f"Could not get JWT token: {response.status_code}")
    response.raise_for_status()
    raise requests.HTTPError(f"Request failed with status code {response.status_code}")


def store_jwt(token: str):
    """
    Store JWT in an environment variable.

    Args:
        token (str): The JWT to be stored. The token should not start or end with "Bearer ".

    Raises:
        TypeError: If the token is not a string.
        ValueError: If the token is empty.
    """
    if not isinstance(token, str):
        raise TypeError("Token must be a string")

    if not token:
        raise ValueError("Token must not be empty")

    if token.startswith("Bearer "):
        token = token[7:]
        logger.warning("Token should not start with 'Bearer '")

    if token.endswith("Bearer "):
        token = token[:-7]
        logger.warning("Token should not end with 'Bearer '")
    os.environ["JWT"] = token


def check_jwt_against_api(token: str | None = None) -> bool:
    """
    Check JWT against API.

    Args:
        token (str, optional): The JWT to be checked. If not provided, the function will try to get the token from the environment variable "JWT_TOKEN".

    Returns:
        bool: True if the token is valid, False otherwise.

    Raises:
        ValueError: If the token or the URL_API is not stored in the environment variables.
        requests.HTTPError: If the request to the API fails.
    """
    if not token:
        token = os.environ.get("JWT")
    if not token:
        logger.error("JWT token not stored in environment variable")
        raise ValueError("JWT token not stored in environment variable")
    if not URL_API:
        logger.error("URL_API not stored in environment variable")
        raise ValueError("URL_API not stored in constants.py")

    url = f"{URL_API}/login/test-token"
    try:
        response = requests.post(url, headers={"Authorization": f"Bearer {token}"})
        response.raise_for_status()
    except Exception as e:
        logger.error(f"JWT token not valid: {e}")
        raise e
    return True


def get_jwt_from_environ() -> str:
    """
    Get JWT from environment variable.

    Returns:
        str: The JWT.

    Raises:
        Exception: If the JWT is not stored in an environment variable.
    """
    try:
        token = os.environ["JWT"]
    except KeyError:
        logger.error("JWT not stored in environment variable")
        raise Exception("JWT not stored in environment variable")
    if not token:
        logger.error("JWT token is empty")
        raise Exception("JWT token is empty")
    return token
