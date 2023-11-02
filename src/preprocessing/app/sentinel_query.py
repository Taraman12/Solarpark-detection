# from app.sentinel_query import get_api
import time
import geopandas as gpd
from pathlib import Path
from typing import Union
from distutils.util import strtobool

from sentinelsat import SentinelAPI
from sentinelsat.exceptions import ServerError, UnauthorizedError
from geopandas import GeoDataFrame, GeoSeries


from sentinel_api import connect_to_sentinel_api
from logging_config import get_logger
from constants import NOW_DICT


logger = get_logger("BaseConfig")


def get_identifier(tile: str, dates: Union[dict, None] = None) -> Union[str, None]:
    api = get_api()

    if dates is None:
        dates = NOW_DICT

    print(dates)
    start_date, end_date = dates["start_date"], dates["end_date"]

    product = get_product_from_footprint(
        api=api, footprint=tile, start_date=start_date, end_date=end_date
    )
    if product is None:
        logger.info(f"No product found for {tile}")
        return None
    return product["identifier"]


def get_api() -> SentinelAPI:
    while True:
        try:
            api = wait_for_api_connection()
            return api
        except Exception as e:
            logger.error(f"Error connecting to API: {e}")
            exit()


def wait_for_api_connection() -> Union[bool, SentinelAPI]:
    """Connects to sentinelAPI and checks if the connection works."""
    api = connect_to_sentinel_api()

    if isinstance(api, ServerError):
        # ToDo: send mail to admin once a day
        # ToDo: check if this works
        logger.warning(
            """Could not connect to Sentinel API. \n
                Probably ongoing maintenance. \n
                Retrying in 5 minutes."""
        )
        time.sleep(300)  # retry after 5 minutes
        return False

    elif isinstance(api, UnauthorizedError):
        # ToDo: send mail to admin once
        logger.error("Wrong credentials for Sentinel API. Please check .env file")
        exit()

    elif isinstance(api, ConnectionError):
        logger.warning(
            """Could not connect to Sentinel API. \n
                Check your internet connection.
            """
        )
        exit()

    elif isinstance(api, Exception):
        # ToDo: send mail to admin every time
        logger.error(f"Unknown error occurred: {api}")
        exit()

    else:
        return api


def get_product_from_footprint(
    api: SentinelAPI,
    footprint: str,
    start_date: str = "NOW-5DAYS",
    end_date: str = "NOW",
) -> Union[GeoSeries, None]:
    """Queries the Sentinel API for products that intersect with a given
    footprint. Returns the product with the lowest cloud cover percentage.

    Args:
        api (SentinelAPI): The SentinelAPI instance to use for the query.
        footprint (str): The footprint to use for the query.
        start_date (str, optional): The start date of the query.
        Defaults to "NOW-5DAYS".
        end_date (str, optional): The end date of the query.
        Defaults to "NOW".

    Returns:
        GeoSeries: A GeoSeries containing the product with the lowest cloud cover
        percentage.
    """
    # create empty GeoSeries to return
    products_gdf = gpd.GeoSeries()

    products = api.query(
        footprint,
        date=(start_date, end_date),
        platformname="Sentinel-2",
        producttype="S2MSI2A",  # S2MSI1C is more data available but stream crashes
        cloudcoverpercentage=(0, 30),
    )

    # check if no product is found
    if not products:
        return None

    # Convert the products to a geopandas dataframe
    products_gdf = api.to_geodataframe(products)

    # sort products by cloud cover percentage
    products_gdf_sorted = products_gdf.sort_values(
        ["cloudcoverpercentage"], ascending=True
    )

    # return first product
    return products_gdf_sorted.iloc[0]
