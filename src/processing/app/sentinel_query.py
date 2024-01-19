from typing import Optional

import pandas as pd
import requests

from app.constants import NOW_DICT
from app.logging_config import get_logger
from app.models.identifier import Identifier

logger = get_logger(__name__)


def get_identifier_handler(
    tile_id: str,
    dates: Optional[dict] = None,
    cloudcover: int = 30,
) -> Identifier | None:
    """Queries the OpenSearch API and returns the identifier of the product with the
    least cloud cover.

    Args:
        tile_id (str): The tile ID.
        dates (Optional[dict], optional): The start and end date of the query.
            - Example fixed dates: {"start_date": "2021-01-01", "end_date": "2021-01-31"}
            - Example relative dates: {"start_date": "NOW-30DAYS", "end_date": "NOW"}
            Defaults to None.
        cloudcover (int, optional): The maximum cloud cover of the product. Defaults to
            30.

    Returns:
        Identifier | None: The identifier of the product with the least cloud cover.
    """
    if not isinstance(dates, dict) and dates is not None:
        raise ValueError("Dates must be a dictionary")

    if dates is None:
        dates = NOW_DICT

    start_date, end_date = dates["start_date"], dates["end_date"]

    # could also be validated with regex
    if not isinstance(tile_id, str):
        raise ValueError("Tile ID must be a string")

    if not isinstance(start_date, str) or not isinstance(end_date, str):
        raise ValueError("Start date and end date must be strings")

    if not isinstance(cloudcover, int) or not 0 <= cloudcover <= 100:
        raise ValueError("Cloud cover must be an integer between 0 and 100")
    try:
        query_string = make_query_string(
            tile_id=tile_id,
            start_date=start_date,
            end_date=end_date,
            cloudcover=cloudcover,
        )

    except ValueError as e:
        logger.error(f"Error: {e}")
        return None

    query_response = query(query_string)

    title = title_from_query(query_response)

    if title is None:
        # no products found
        return None

    return identifier_from_title(title)


def make_query_string(
    tile_id: str, start_date: str, end_date: str, cloudcover: int
) -> str:
    """Creates a query string for the OpenSearch API.

    docs: https://documentation.dataspace.copernicus.eu/APIs/OpenSearch.html

    Returns:
        str: The query string.
    """
    # Validate dates
    # try:
    #     datetime.datetime.strptime(start_date, "%Y-%m-%d")
    #     datetime.datetime.strptime(end_date, "%Y-%m-%d")
    # except ValueError:
    #     regex
    #     raise ValueError("Dates must be in the format YYYY-MM-DD")

    # Validate cloudcover
    if not 0 <= cloudcover <= 100:
        raise ValueError("Cloudcover must be between 0 and 100")

    # Validate tile_id
    if not isinstance(tile_id, str):
        raise ValueError("Tile ID must be a string")

    collection = "Sentinel2"
    processing_level = "S2MSI2A"
    return f"https://catalogue.dataspace.copernicus.eu/resto/api/collections/{collection}/search.json?startDate={start_date}&completionDate={end_date}&productType={processing_level}&cloudCover=[0,{cloudcover}]&tileId={tile_id}"


def query(query_string: str) -> dict:
    """Queries the OpenSearch API.

    Returns:
        requests.Response: The response of the query.
    """
    # Validate query_string
    if not isinstance(query_string, str):
        raise ValueError("Query string must be a string")

    try:
        response = requests.get(query_string)
        # Raise an exception if the request was unsuccessful
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        raise ValueError("Request failed")

    return response.json()


def title_from_query(query_response: dict) -> str | None:
    """Extracts the identifier from the query response.

    Returns:
        str: The identifier.
    """
    # Validate query_response
    if not isinstance(query_response, dict):
        raise ValueError("Query response must be a dictionary")

    # Check if 'features' key exists in query_response
    if "features" not in query_response:
        raise ValueError("Query response does not contain 'features' key")

    data = query_response["features"]

    # Check if each feature has 'properties' key
    for feature in data:
        if "properties" not in feature:
            raise ValueError("Feature does not contain 'properties' key")

    properties_list = [feature["properties"] for feature in data]
    df = pd.DataFrame(properties_list)

    if df.empty:
        logger.info("No products found for given arguments")
        return None

    # Check if 'title' and 'cloudCover' keys exist in properties
    if "title" not in df.columns or "cloudCover" not in df.columns:
        raise ValueError("Properties do not contain 'title' or 'cloudCover' key")

    df_sorted = df[["title", "cloudCover"]].sort_values("cloudCover")

    return df_sorted.iloc[0]["title"]


def identifier_from_title(title: str) -> Identifier:
    """Extracts the identifier from the title.

    Returns:
        Identifier: The identifier.
    """
    if not isinstance(title, str):
        raise ValueError("Title must be a string")

    if title.endswith(".SAFE"):
        title[:-5]
    # check if title is already an identifier
    try:
        return Identifier(title)

    except ValueError:
        raise ValueError(f"Invalid title: {title}")
