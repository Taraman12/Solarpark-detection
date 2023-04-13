# build-in
import asyncio
import os
import re
import shutil
import time
from datetime.datetime import date
from pathlib import Path
from zipfile import ZipFile

# local-modules
from sentinel_on_aws import download_from_aws
from sentinelsat import SentinelAPI
from sentinelsat.exceptions import LTATriggered


# ToDo: change os.path to pathlib
# ToDo: use sentinelsat get_stream() for streaming data to AWS S3
class HTTPError(Exception):
    "Raised by sentinelsat"
    pass


def download_sentinel2_data(
    api: SentinelAPI, footprint: str, download_root: Path, mode: str = "production"
) -> bool:
    """
    Download Sentinel-2 data for a given footprint and extract the RGB image.

    Args:
        footprint (str): WKT formatted string of the area of interest.
        download_root (str): Path to the directory where the data will be downloaded.

    Returns:
        tuple: A tuple of gdf product and the path to the extracted RGB image.

    """

    if mode == "production":
        start_date = "NOW-5DAYS"
        end_date = "NOW"

    elif mode == "training":
        start_date = date(2018, 6, 1)
        end_date = date(2023, 8, 1)

    # sentinelsat get_stream() for streaming data to AWS S3
    # Search for products that match the query criteria
    products = api.query(
        footprint,
        date=(start_date, end_date),
        platformname="Sentinel-2",
        producttype="S2MSI2A",  # S2MSI1C is more data available but stream crashes
        cloudcoverpercentage=(0, 20),
    )

    # check if a product is found
    if not products:
        # ToDo: Need better error handling
        return False

    # Convert the products to a geopandas dataframe
    products_gdf = api.to_geodataframe(products)

    # sort products by cloud cover percentage
    products_gdf_sorted = products_gdf.sort_values(
        ["cloudcoverpercentage"], ascending=True
    )

    # select first product
    product = products_gdf_sorted.iloc[0]

    # create target folder
    target_folder = download_root / product.identifier[0]

    # creates folder
    target_folder.mkdir(parents=True, exist_ok=True)

    # check if product is online
    is_online = api.is_online(product.uuid)

    if is_online:
        try:
            print("Product is online. Starting download.")
            # Download the product using the UUID
            api.download(product.uuid[0], directory_path=download_root)

            # Extract the TCI_10m image from the downloaded ZIP file
            extract_image_bands(download_root, product.identifier[0], target_folder)

            # Remove the downloaded ZIP file
            (download_root / (product.identifier[0] + ".zip")).unlink()

        except HTTPError:
            # ToDo: Need better error handling
            return False

    else:
        if download_from_aws(product.identifier[0], target_folder):
            return True

        else:
            # trigger LTA
            api.trigger_offline_retrieval(product.uuid[0])

            # download from LTA waiting for 10 minutes before trying again
            result = asyncio.run(download_from_lta(api, product.uuid[0], download_root))

            if result:
                return True
            else:
                return False

    return False


def get_product_from_footprint() -> None:
    pass


def extract_image_bands(
    download_root: Path, identifier: str, target_folder: str
) -> str:
    """
    Extracts the TCI_10m image from the zip file in the given download path for the
    given Sentinel-2 image identifier.

    Args:
        download_root (str): The path to the directory where the zip file is downloaded.
        identifier (str): The Sentinel-2 image identifier.

    Returns:
        str: The path to the extracted TCI_10m image.

    """
    pattern = re.compile(r"_B0[2438]_10m\.jp2$")

    # Extract the TCI_10m image from the ZIP file
    with ZipFile(download_root / (identifier + ".zip"), mode="r") as zipped_folder:
        for source_filename in zipped_folder.namelist():
            if source_filename.endswith("_TCI_10m.jp2") or pattern.search(
                source_filename
            ):
                target_filename = os.path.join(
                    target_folder, os.path.basename(source_filename)
                )
                with zipped_folder.open(source_filename) as zf, open(
                    target_filename, "wb"
                ) as f:
                    shutil.copyfileobj(zf, f)

    return identifier


async def download_from_lta(
    api: SentinelAPI, product_uuid: str, download_root: Path, timeout_hours: int = 24
) -> bool:
    """
    Downloads a product from the Long-Term Archive (LTA).

    :param api: SentinelAPI instance
    :param product_id: ID of the product to download
    :param timeout_hours: Maximal number of hours to keep retrying

    """
    timeout = timeout_hours * 3600  # Convert hours to seconds
    start_time = time.monotonic()
    while time.monotonic() - start_time < timeout:
        try:
            api.download(product_uuid, directory_path=download_root)
            print(f"Product {product_uuid} downloaded successfully.")
            return True
        except LTATriggered:
            # Wait for 10 minutes before trying again
            await asyncio.sleep(600)
    print(f"Download timed out after {timeout_hours} hours.")
    return False
