# build-in
import asyncio
import os
import re
import shutil
import tempfile
import time
from datetime import date
from pathlib import Path
from zipfile import ZipFile
from typing import Union

# third-party
import geopandas as gpd

# local-modules
from logging_config import get_logger
from constants import IMAGE_REGEX, REQUIRED_BANDS
from geopandas import GeoSeries
from sentinel_on_aws import download_from_aws_handler, upload_to_aws
from sentinelsat import SentinelAPI
from sentinelsat.exceptions import LTATriggered
from settings import DOCKERIZED, PRODUCTION

# ToDo: change os.path to pathlib
# ToDo: use sentinelsat get_stream() for streaming data to AWS S3

# set up logger
logger = get_logger('BaseConfig')

class HTTPError(Exception):
    "Raised by sentinelsat"
    pass


def download_sentinel2_data(
    api: SentinelAPI,
    footprint: str,
    start_date: Union[date, str],
    end_date: Union[date, str],
    download_root: Path = Path("."),
) -> bool:
    """Download Sentinel-2 data for a given footprint and extract the RGB
    image.

    Args:
        footprint (str): WKT formatted string of the area of interest.
        download_root (str): Path to the directory where the data will be downloaded.

    Returns:
        tuple: A tuple of gdf product and the path to the extracted RGB image.
    """
    # Search for products that match the query criteria
    product = get_product_from_footprint(api, footprint, start_date, end_date)

    if len(product) == 0:
        """No product found."""
        return False

    # create target folder
    target_folder = download_root / product.identifier

    # checks if product is already downloaded
    if check_files_already_downloaded(target_folder):
        return True

    # creates folder
    target_folder.mkdir(parents=True, exist_ok=True)

    # if deployed to aws prefer download from there
    # if deployed and aws_available:
    #     if download_from_aws_handler(product.identifier, target_folder):
    #         return True

    # check if product is online
    is_online = api.is_online(product.uuid)

    if PRODUCTION:
        logger.info("Production=True, COPY from AWS S3.")
        if download_from_aws_handler(product.identifier, target_folder):
            return True

    if is_online:
        try:
            logger.info("Product is online. Starting download.")
            # Download the product using the UUID
            api.download(product.uuid, directory_path=download_root)
        except HTTPError:
            # ToDo: Need better error handling
            return False
        # Extract the REQUIRED_BANDS from the downloaded ZIP file
        extract_image_bands(download_root, product.identifier, target_folder)

        if DOCKERIZED:
            # Upload the extracted image to AWS S3
            upload_to_aws(
                target_folder,
                output_path=f"data_raw/{product.identifier}",
            )
            # Remove the downloaded file from docker container
            (download_root / (product.identifier)).unlink()

        # Remove the downloaded ZIP file
        (download_root / (product.identifier + ".zip")).unlink()
        return True

    logger.info("Product is not online. Download from AWS S3.")
    if download_from_aws_handler(product.identifier, target_folder):
        return True

    # trigger LTA
    api.trigger_offline_retrieval(product.uuid)
    logger.info("Product is not online. Triggering LTA.")
    # download from LTA waiting for 10 minutes before trying again
    # result = asyncio.run(download_from_lta(api, product.uuid, download_root))
    return False


def get_product_from_footprint(
    api: SentinelAPI,
    footprint: str,
    start_date: str = "NOW-5DAYS",
    end_date: str = "NOW",
) -> GeoSeries:
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
        return products_gdf

    # Convert the products to a geopandas dataframe
    products_gdf = api.to_geodataframe(products)

    # sort products by cloud cover percentage
    products_gdf_sorted = products_gdf.sort_values(
        ["cloudcoverpercentage"], ascending=True
    )

    # return first product
    return products_gdf_sorted.iloc[0]


def check_files_already_downloaded(target_folder: Path):
    """Checks if the all bands of the product are already downloaded."""
    if target_folder.exists():
        # check if product is complete
        if len(os.listdir(target_folder)) >= len(REQUIRED_BANDS):
            return True
    return False


def extract_image_bands(
    download_root: Path, identifier: str, target_folder: Path
) -> bool:
    """Extracts 10-meter resolution band images (B02, B03, B04, and B08) from a
    Sentinel-2 ZIP folder and saves them as separate files with the format
    <band>_10m.jp2.

    Args:
        download_root (Path): The path to the root directory where the Sentinel-2 image
            ZIP file is located.
        identifier (str): The identifier of the Sentinel-2 image ZIP file, without the
            `.zip` extension.
        target_folder (Path): The path to the directory where the extracted band images
            will be saved.

    Returns:
        str: A message indicating that the band images have been successfully extracted
            and saved to the `target_folder` directory.
    """
    with ZipFile(download_root / f"{identifier}.zip", mode="r") as zipped_folder:
        with tempfile.TemporaryDirectory() as tmp_dir:
            zipped_folder.extractall(tmp_dir)
            tmp_dir_path = Path(tmp_dir)
            files = tmp_dir_path.glob("**/*_10m.jp2")

            for source_path in files:
                regex_match = re.match(IMAGE_REGEX, source_path.name)
                if not regex_match:
                    continue
                band = regex_match.group("band")

                if band not in REQUIRED_BANDS:
                    continue

                file_name = f"{band}.jp2"

                target_filename = target_folder / file_name

                with source_path.open("rb") as zf, target_filename.open("wb") as f:
                    shutil.copyfileobj(zf, f)

    return True


async def download_from_lta(
    api: SentinelAPI, product_uuid: str, download_root: Path, timeout_hours: int = 24
) -> bool:
    """Downloads a product from the Long-Term Archive (LTA).

    :param api: SentinelAPI instance
    :param product_id: ID of the product to download
    :param timeout_hours: Maximal number of hours to keep retrying
    """
    timeout = timeout_hours * 3600  # Convert hours to seconds
    start_time = time.monotonic()
    while time.monotonic() - start_time < timeout:
        try:
            api.download(product_uuid, directory_path=download_root)
            logger.info(f"Product {product_uuid} downloaded successfully.")
            return True
        except LTATriggered:
            # Wait for 10 minutes before trying again
            await asyncio.sleep(600)
    logger.warning(f"Download timed out after {timeout_hours} hours.")
    return False
