# build-in
import os
import re
import shutil
from zipfile import ZipFile

# third-party
import geopandas as gpd
from dotenv import load_dotenv
from sentinelsat import SentinelAPI


class HTTPError(Exception):
    "Raised by sentinelsat"
    pass


def download_sentinel2_data(
    footprint: str, download_root: str
) -> tuple[gpd.GeoDataFrame, str]:
    """
    Download Sentinel-2 data for a given footprint and extract the RGB image.

    Args:
        footprint (str): WKT formatted string of the area of interest.
        download_root (str): Path to the directory where the data will be downloaded.

    Returns:
        tuple: A tuple containing the metadata of the downloaded product and the path to the extracted RGB image.
    """
    load_dotenv()
    api_user = os.getenv("API_USER")
    api_secret = os.getenv("API_SECRET")
    api_url = os.getenv("API_URL")
    # Connect to the Sentinel API
    api = SentinelAPI(api_user, api_secret, api_url)

    # Search for products that match the query criteria
    products = api.query(
        # tileid=tileid,
        footprint,
        # date=("20220101", date(2023, 3, 7)),
        date=("NOW-21DAYS", "NOW"),
        platformname="Sentinel-2",
        producttype="S2MSI2A",  # S2MSI1C is more data available but stream crashes
        cloudcoverpercentage=(0, 30),
        limit=1,
    )

    # check if a product is found
    if not products:
        # ToDo: Need better error handling
        return gpd.GeoDataFrame(), ""

    # Convert the products to a geopandas dataframe
    gdf = api.to_geodataframe(products)

    # create target folder
    target_folder = os.path.join(download_root, gdf.identifier[0])

    # checks if the folder already exists
    if os.path.isdir(target_folder):
        return gdf, target_folder

    # creates folder
    os.makedirs(target_folder, exist_ok=True)

    try:
        # Download the product using the UUID
        api.download(gdf.uuid[0], directory_path=download_root)
    except HTTPError:
        # ToDo: Need better error handling
        return gpd.GeoDataFrame(), ""

    # Extract the TCI_10m image from the downloaded ZIP file
    extract_image_bands(download_root, gdf.identifier[0], target_folder)

    # Remove the downloaded ZIP file
    os.remove(os.path.join(download_root, gdf.identifier[0] + ".zip"))

    return gdf, gdf.identifier[0]


def extract_image_bands(download_root: str, identifier: str, target_folder: str) -> str:
    """
    Extracts the TCI_10m image from the zip file in the given download path for the given Sentinel-2 image identifier.

    Args:
        download_root (str): The path to the directory where the zip file is downloaded.
        identifier (str): The Sentinel-2 image identifier.

    Returns:
        str: The path to the extracted TCI_10m image.
    """
    pattern = re.compile(r"_B0[2438]_10m\.jp2$")

    # Extract the TCI_10m image from the ZIP file
    with ZipFile(
        os.path.join(download_root, identifier + ".zip"), mode="r"
    ) as zipped_folder:
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
