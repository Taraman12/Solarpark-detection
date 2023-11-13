from datetime import datetime
from typing import List, Tuple

import numpy as np
import rasterio
import rasterio.features
import requests
from constants import AREA_THRESHOLD, HEADERS, MODEL_NAME, URL_API
from jwt_functions import get_jwt
from logging_config import get_logger
from rasterio.crs import CRSError

# from rasterio.features import geometry_mask
from rasterio.warp import transform_geom
from shapely.geometry import Polygon

logger = get_logger("BaseConfig")


def write_to_db_handler(
    prediction: np.ndarray, metadata: dict, tile_date: str, filename: str
) -> None:
    """
    Sends the prediction to the API.

    Args:
        prediction (np.ndarray):
        metadata (dict): The metadata of the image.
        tile_date (str): The date of the image.
        filename (str): The filename of the image.
    """
    polygons, areas = prediction_to_polygons(prediction, metadata)
    for polygon, area in zip(polygons, areas):
        try:
            write_to_db(polygon, area=area, tile_date=tile_date, filename=filename)
            logger.info("Polygon written to DB")
        except Exception as e:
            logger.error(f"Could not write to DB: {e}")
            raise e
    return None


def write_to_db(polygon: Polygon, area, tile_date: str, filename: str) -> bool:
    if not isinstance(polygon, Polygon):
        raise TypeError("polygon must be a Polygon")

    if not isinstance(area, (int, float)) or area < 0:
        raise ValueError("area must be a number greater than or equal to zero")

    if not isinstance(tile_date, str):
        raise TypeError("tile_date must be a string")

    if not isinstance(filename, str):
        raise TypeError("filename must be a string")

    # tile_date = to_datetime_str(tile_date)
    lat, lon = extract_polygon_coordinates(polygon)
    # TODO: refactor into a dataclass or something (DataBuilder class)
    data = {
        "name_of_model": MODEL_NAME,
        "size_in_sq_m": area,
        "peak_power": calc_peak_power(area_in_sq_m=area),
        "date_of_data": tile_date,
        "avg_confidence": 0,
        "name_in_aws": filename,
        "is_valid": "None",
        "comment": "None",
        "lat": lat,
        "lon": lon,
        "geom": polygon.wkt,
    }
    token = get_jwt()
    HEADERS["Authorization"] = f"Bearer {token}"
    url = f"{URL_API}/solarpark_observation/"
    logger.debug(f"Writing to DB: {data}")
    try:
        response = requests.post(url, headers=HEADERS, json=data)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Could not write to DB: {e}")
        raise e


# def to_datetime_str(date_string: str) -> str:
#     """
#     Formats the date string to a real datetime string.
#     tile_date does not have a leading zeros due to previous constraints.
#     Therefore we need to add them, but the output must be a string again

#     Args:
#         date_string (str): The date string to format.

#     Returns:
#         str: The formatted date string.

#     Raises:
#         TypeError: If date_string is not a string.
#         ValueError: If date_string is not in the correct format.
#     """
#     if not isinstance(date_string, str):
#         raise TypeError("date_string must be a string")

#     try:
#         date_obj = datetime.strptime(date_string, "%Y-%m-%d").date()
#     except ValueError:
#         raise ValueError("date_string must be in the format 'YYYY-MM-DD'")

#     return date_obj.strftime("%Y-%m-%d")


def extract_polygon_coordinates(polygon: Polygon) -> Tuple[List[float], List[float]]:
    """
    Extracts the latitude and longitude coordinates of the exterior ring of a polygon.

    Args:
        polygon (Polygon): The polygon to extract coordinates from.

    Returns:
        Tuple[List[float], List[float]]: A tuple containing two lists: the latitude coordinates and the longitude coordinates.

    Raises:
        TypeError: If polygon is not a Polygon.
        ValueError: If polygon does not have an exterior ring.
    """
    if not isinstance(polygon, Polygon):
        raise TypeError("polygon must be a Polygon")
    if polygon.exterior is None or len(polygon.exterior.coords) == 0:
        raise ValueError("polygon must have an exterior ring")

    # Extract the coordinates of the exterior ring of the polygon
    coords = polygon.exterior.coords

    # Extract the latitude and longitude coordinates into separate lists
    latitudes = [coord[1] for coord in coords]
    longitudes = [coord[0] for coord in coords]

    return latitudes, longitudes


def calc_peak_power(area_in_sq_m: float) -> float:
    """
    Calculates the peak power of a solar park based on its area.

    Solar park in 2015
    https://www.bundesnetzagentur.de/SharedDocs/Downloads/DE/Sachgebiete/Energie/Unternehmen_Institutionen/ErneuerbareEnergien/PV-Freiflaechenanlagen/Bericht_Flaecheninanspruchnahme_2016.pdf?__blob=publicationFile&v=2#:~:text=Die%20bereits%20im%20Rahmen%20der,Ackerland%20in%20benachteiligten%20Gebieten%20errichtet. # noqa
    page 8 on the pdf (german)
    1,6 acre = 1 MWp

    Solar park in 2022
    https://www.ise.fraunhofer.de/content/dam/ise/de/documents/publications/studies/aktuelle-fakten-zur-photovoltaik-in-deutschland.pdf
    page 40 on the pdf (german)
    1 MWP/ha, 980 MWh/MWP
    => 1 acre = 10000 m² = 1 MWp

    Args:
        area_in_sq_m (float): The area of the solar park in square meters.

    Returns:
        float: The peak power of the solar park in MWp.

    Raises:
        TypeError: If area_in_sq_m is not a number.
        ValueError: If area_in_sq_m is less than zero.
    """
    if not isinstance(area_in_sq_m, (int, float)):
        raise TypeError("area_in_sq_m must be a number")
    if area_in_sq_m < 0:
        raise ValueError("area_in_sq_m must be greater than or equal to zero")

    return area_in_sq_m / 10000


def prediction_to_polygons(
    prediction: np.ndarray,
    metadata: dict,
) -> Tuple[List[Polygon], List[float]]:
    """
    Converts prediction to polygons.

    Args:
        prediction (np.ndarray): The prediction from the ML model.
        metadata (dict): The metadata of the prediction.

    Returns:
        Tuple[List[Polygon], List[float]]: A list of polygons and their corresponding areas.

    Raises:
        TypeError: If prediction is not a numpy array or if metadata is not a dictionary.
        KeyError: If metadata does not contain a 'transform' or 'crs' key.
    """
    if not isinstance(prediction, np.ndarray):
        raise TypeError("prediction must be a numpy array")
    if not isinstance(metadata, dict):
        raise TypeError("metadata must be a dictionary")
    if "transform" not in metadata:
        raise KeyError("metadata must contain a 'transform' key")
    if "crs" not in metadata:
        raise KeyError("metadata must contain a 'crs' key")

    polygons, areas = [], []
    mask = create_mask(prediction)

    transform = metadata["transform"]
    crs = metadata["crs"]

    for shape in extract_shapes(mask, transform):
        polygon, area = create_polygon_and_area(shape)
        if area >= AREA_THRESHOLD:
            transformed_polygon = transform_polygon(polygon, crs)
            polygons.append(transformed_polygon)
            areas.append(area)

    return polygons, areas


def create_mask(prediction: np.ndarray, threshold: float = 0.5) -> np.ndarray:
    """
    Creates a binary mask from the prediction.

    The prediction is expected to be a 3D numpy array with shape (1, KERNEL_SIZE, KERNEL_SIZE).
    The values in the prediction should be floating point numbers between 0 and 1.
    The function returns a 2D binary mask with the same width and height as the prediction,
    where each pixel is 1 if the corresponding value in the prediction is greater than or equal to 0.5,
    and 0 otherwise. The returned mask is of type np.uint8.

    Args:
        prediction (np.ndarray): The prediction from the ML model.
        threshold (float): The threshold to use for the mask.

    Returns:
        np.ndarray: The binary mask. Returns dtype np.uint8.

    Raises:
        TypeError: If prediction is not a numpy array.
        ValueError: If prediction does not have the expected shape or type.
    """
    if not isinstance(prediction, np.ndarray):
        raise TypeError("Input prediction must be a numpy array")

    if prediction.ndim != 3 or prediction.shape[0] != 1:
        raise ValueError(
            "Input prediction must have shape (1, KERNEL_SIZE, KERNEL_SIZE)"
        )

    if prediction.dtype not in [np.float64, np.float32]:
        raise TypeError("Input prediction must be of type float64 or float32")

    mask = np.where(prediction[0] < threshold, 0, 1)
    return mask.astype(np.uint8)


def extract_shapes(mask: np.array, transform: rasterio.transform) -> List[dict]:
    """
    Extracts shapes from a binary mask using the provided transform.

    This function uses rasterio's features.shapes function to extract shapes from the mask.
    The shapes are returned as a list of GeoJSON-like dict objects.

    Parameters:
    mask (np.array): A 2D numpy array of dtype int16, int32, uint8, uint16, or float32 representing the binary mask.
    transform (rasterio.transform): A rasterio transform object to map pixel coordinates in mask to another coordinate system.

    Returns:
    List[dict]: A list of GeoJSON-like dict objects representing the extracted shapes.

    Raises:
    TypeError: If the dtype of mask is not int16, int32, uint8, uint16, or float32.
    ValueError: If mask is not a 2D array.
    """
    if mask.dtype not in [np.int16, np.int32, np.uint8, np.uint16, np.float32]:
        raise TypeError(
            "Input mask must be of type int16, int32, uint8, uint16 or float32"
        )

    if mask.ndim != 2:
        raise ValueError("Input mask must be 2-dimensional")

    # mask is used to times, because using float mask may not be precise and without mask=mask the 0 will be passed as features
    return list(rasterio.features.shapes(mask, mask=mask, transform=transform))


def create_polygon_and_area(shape: dict) -> Tuple[Polygon, float]:
    """
    Creates a shapely Polygon and calculates its area from a shape.

    Parameters:
    shape (dict): A dict where the first element is a dict representing a GeoJSON-like shape and the second element is the value associated with the shape.

    Returns:
    Tuple: A tuple where the first element is a shapely Polygon created from the shape and the second element is the area of the Polygon.

    Raises:
    TypeError: If shape is not a dict or if the first element of shape is not a dict.
    KeyError: If the first element of shape does not contain a "coordinates" key.
    ValueError: If the coordinates in the shape are not valid.
    """

    if not isinstance(shape[0], dict):
        raise TypeError("The first element of shape must be a dict")

    if "coordinates" not in shape[0]:
        raise KeyError("The first element of shape must contain a 'coordinates' key")

    try:
        polygon = Polygon(shape[0]["coordinates"][0])
    except ValueError:
        raise ValueError("The coordinates in the shape are not valid")

    area = polygon.area
    return polygon, area


def transform_polygon(polygon: Polygon, crs: str) -> Polygon:
    """
    Transforms a shapely Polygon to a different coordinate reference system (CRS).

    Parameters:
    polygon (shapely.geometry.Polygon): The Polygon to transform.
    crs (str): The CRS to transform the Polygon to.

    Returns:
    shapely.geometry.Polygon: The transformed Polygon.

    Raises:
    TypeError: If polygon is not a shapely Polygon or if crs is not a string.
    ValueError: If crs is not a valid CRS.
    """
    if not isinstance(polygon, Polygon):
        raise TypeError("polygon must be a shapely Polygon")
    if not isinstance(crs, str):
        raise TypeError("crs must be a string")
    try:
        transformed_geom = transform_geom(crs, "EPSG:4326", polygon.__geo_interface__)
    except CRSError:
        raise ValueError(f"{crs} is not a valid CRS")
    transformed_coords = transformed_geom["coordinates"][0]
    return Polygon(transformed_coords)
