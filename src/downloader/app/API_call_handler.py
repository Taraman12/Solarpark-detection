# build-in
import asyncio
import os
import shutil
import tempfile
import time
from datetime import date
from pathlib import Path
from typing import Optional, TypedDict, Union
from zipfile import ZipFile

import boto3

# third-party
import geopandas as gpd
from boto3 import client
from botocore.errorfactory import ClientError

# local-modules
from constants import BAND_FILE_MAP
from dotenv import load_dotenv
from geopandas import GeoSeries
from sentinel_on_aws import download_from_aws
from sentinelsat import SentinelAPI
from sentinelsat.exceptions import LTATriggered
from typing_extensions import Unpack

# ToDo: change os.path to pathlib
# ToDo: use sentinelsat get_stream() for streaming data to AWS S3


class HTTPError(Exception):
    "Raised by sentinelsat"
    pass


# maybe not needed
class RequestParams(TypedDict):
    footprint: str
    start_date: str
    end_date: str
    mode: str


def download_sentinel2_data(
    api: SentinelAPI,
    footprint: str,
    start_date: date,
    end_date: date,
    download_root: Path = Path("."),
    mode: str = "production",
    deployed: bool = False,
) -> bool:
    """
    Download Sentinel-2 data for a given footprint and extract the RGB image.

    Args:
        footprint (str): WKT formatted string of the area of interest.
        download_root (str): Path to the directory where the data will be downloaded.

    Returns:
        tuple: A tuple of gdf product and the path to the extracted RGB image.

    """

    # if mode == "production":
    #     start_date = "NOW-5DAYS"
    #     end_date = "NOW"

    # elif mode == "training":
    #     start_date = date(2018, 6, 1)  # type: ignore
    #     end_date = date(2018, 8, 1)  # type: ignore

    # sentinelsat get_stream() for streaming data to AWS S3
    # Search for products that match the query criteria
    product = get_product_from_footprint(api, footprint)

    if len(product) == 0:
        return False

    # create target folder
    target_folder = download_root / product.identifier

    # check if product is already downloaded
    if target_folder.exists():
        # check if product is complete
        if len(os.listdir(target_folder)) >= len(BAND_FILE_MAP.keys()):
            return True

    # creates folder
    target_folder.mkdir(parents=True, exist_ok=True)

    if deployed:
        s3 = login_aws()
        if not s3:
            return False

        load_dotenv(os.getcwd())
        bucket_name = os.getenv("aws_s3_bucket")
        try:
            # Skip if file already exists
            response = s3.head_object(
                Bucket=bucket_name, Key=f"\data_raw\{product.identifier}"
            )

        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                print("The object does not exist.")

    # check if product is online
    is_online = api.is_online(product.uuid)

    if is_online:
        try:
            print("Product is online. Starting download.")
            # Download the product using the UUID
            api.download(product.uuid, directory_path=download_root)

            # Extract the TCI_10m image from the downloaded ZIP file
            extract_image_bands(download_root, product.identifier, target_folder)

            # Upload the extracted image to AWS S3
            upload_to_aws(
                s3,
                target_folder,
                bucket=bucket_name,
                output_path=f"data_raw/{product.identifier}",
            )
            # Remove the downloaded ZIP file
            (download_root / (product.identifier + ".zip")).unlink()
            if deployed:
                # Remove the downloaded ZIP file
                (download_root / (product.identifier)).unlink()
            return True
        except HTTPError:
            # ToDo: Need better error handling
            return False

    print("Product is not online. Download from AWS S3.")
    if download_from_aws(product.identifier, target_folder):
        return True

    # trigger LTA
    api.trigger_offline_retrieval(product.uuid)
    print("Product is not online. Triggering LTA.")
    # download from LTA waiting for 10 minutes before trying again
    # result = asyncio.run(download_from_lta(api, product.uuid, download_root))

    # if result:
    #     return True
    # else:
    #     return False

    return False


def get_product_from_footprint(
    api: SentinelAPI,
    footprint: str,
    start_date: str = "NOW-5DAYS",
    end_date: str = "NOW",
    mode: str = "production",
    **kwargs: Unpack[RequestParams],  # type: ignore
) -> GeoSeries:
    products_gdf = gpd.GeoSeries()
    products = api.query(
        footprint,
        date=(start_date, end_date),
        platformname="Sentinel-2",
        producttype="S2MSI2A",  # S2MSI1C is more data available but stream crashes
        cloudcoverpercentage=(0, 30),
    )
    # check if a product is found
    if not products:
        if mode == "production":
            return products_gdf
        # ToDo: Need better error handling

    # Convert the products to a geopandas dataframe
    products_gdf = api.to_geodataframe(products)

    # sort products by cloud cover percentage
    products_gdf_sorted = products_gdf.sort_values(
        ["cloudcoverpercentage"], ascending=True
    )

    # return first product
    return products_gdf_sorted.iloc[0]


def login_aws() -> boto3.client:
    load_dotenv(os.getcwd())
    aws_access_key_id = os.getenv("aws_access_key_id")
    aws_secret_access_key = os.getenv("aws_secret_access_key")

    # move somewhere else to avoid multiple calls
    # add test if credentials are valid
    # https://stackoverflow.com/questions/53548737/verify-aws-credentials-with-boto3
    s3 = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
    )
    try:
        response = s3.list_buckets()
        return s3
    except boto3.exceptions.ClientError:
        print("Credentials are NOT valid.")
        return False


def upload_to_aws(
    s3: boto3.client,
    input_folder: Path,
    bucket: Optional[str],
    output_path: Union[str, None] = None,
) -> bool:
    """
    Uploads a Sentinel-2 image to AWS S3.

    Args:
        input_folder (Path): The path to the directory where the Sentinel-2 image is
            located.

    Returns:
        bool: True if the upload was successful, False otherwise.

    """
    # If S3 object_name was not specified, use file_name
    if output_path is None:
        output_path = os.path.basename(input_folder)

    for root, dirs, files in os.walk(input_folder):
        for file in files:
            local_file = os.path.join(root, file)

            # Upload the file
            try:
                response = s3.upload_file(local_file, bucket, f"{output_path}/{file}")
            except ClientError as e:
                # logging.error(e)
                return False
    return True


def extract_image_bands(
    download_root: Path, identifier: str, target_folder: Path
) -> bool:
    """
    Extracts 10-meter resolution band images (B02, B03, B04, and B08) from a Sentinel-2
    ZIP folder and saves them as separate files with the format <band>_10m.jp2.

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
            p = tmp_dir_path.glob("**/*B0[2438]_10m.jp2")
            files = [x for x in p if x.is_file()]

            for source_path in files:
                band_res = source_path.stem.split("_")[2] + "_10m.jp2"
                target_filename = target_folder / band_res

                with source_path.open("rb") as zf, target_filename.open("wb") as f:
                    shutil.copyfileobj(zf, f)

    # pattern = re.compile(r"_B0[2438]_10m\.jp2$")

    # # Extract the TCI_10m image from the ZIP file
    # with ZipFile(download_root / f"{identifier}.zip", mode="r") as zipped_folder:
    #     for source_filename in zipped_folder.namelist():
    #         if source_filename.endswith("_TCI_10m.jp2") or pattern.search(
    #             source_filename
    #         ):
    #             target_filename = os.path.join(
    #                 target_folder, os.path.basename(source_filename)
    #             )
    #             with zipped_folder.open(source_filename) as zf, open(
    #                 target_filename, "wb"
    #             ) as f:
    #                 shutil.copyfileobj(zf, f)

    return True


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
