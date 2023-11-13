import time

import requests
from cloud_clients import aws_available
from constants import URL_API, URL_ML
from jwt_functions import check_jwt_against_api
from logging_config import get_logger

logger = get_logger("BaseConfig")


def run_checks() -> None:
    """Runs all health checks."""
    logger.info("Running health checks")

    if not aws_available:
        logger.warning("AWS credentials not valid")

    if not check_ml_serve_online():
        logger.error("ml-serve not online. Exiting.")
        exit(2)

    if not check_api_online():
        logger.error("API not online. Exiting.")
        exit(2)

    if not check_jwt_against_api():
        logger.error("JWT not valid. Exiting.")
        exit(2)


# def check_input_paths(input_dirs: List[Path]) -> bool:
#     """Validates that the input directories exist.

#     Args:
#         input_dirs (List[Path]): A list of input directories to validate.
#         logger: A logger instance to use for logging.

#     Returns:
#         bool: True if all input directories exist, False otherwise.
#     """
#     all_dirs_exist = True
#     for input_dir in input_dirs:
#         if not input_dir.exists():
#             logger.error(f"Input path: {input_dir} does not exist")
#             all_dirs_exist = False
#     return all_dirs_exist


def check_ml_serve_online() -> bool:
    retries = 3
    while retries > 0:
        try:
            logger.info(f"Checking if TorchServe is running on {URL_ML}")
            response = requests.get(f"{URL_ML}/ping")
            if response.status_code == 200:
                logger.info("TorchServe is running")
                return True
            else:
                logger.info("TorchServe is not running. retry in 5 seconds.")
                time.sleep(5)
        except requests.exceptions.ConnectionError:
            logger.info("TorchServe is not running. Retry in 5 seconds.")
            time.sleep(5)
        retries -= 1
    return False


def check_ml_serve_online_localhost() -> bool:
    retries = 3
    while retries > 0:
        try:
            logger.info(f"Checking if TorchServe is running on {URL_ML}")
            response = requests.get("http://localhost:8080/ping")
            if response.status_code == 200:
                logger.info("TorchServe is running")
                return True
            else:
                logger.info("TorchServe is not running. retry in 5 seconds.")
                time.sleep(5)
        except requests.exceptions.ConnectionError:
            logger.info("TorchServe is not running. Retry in 5 seconds.")
            time.sleep(5)
        retries -= 1
    return False


def check_api_online() -> bool:
    retries = 3
    while retries > 0:
        try:
            logger.info(f"Checking if API is running on {URL_API}")
            response = requests.get(f"{URL_API}")
            if response.status_code == 200:
                logger.info("API is running")
                return True
            else:
                logger.info("API is not running. retry in 5 seconds.")
                time.sleep(5)
        except requests.exceptions.ConnectionError:
            logger.info("API is not running. Retry in 5 seconds.")
            time.sleep(5)
        retries -= 1
    return False
