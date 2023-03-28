# third-party
import geopandas as gpd

# local-modules
from API_call_handler import download_sentinel2_data

print("Program started")
download_path = r"C:\Users\Fabian\Documents\Masterarbeit_Daten\API_test3"

# NOTE polygons_bavaria.geojson contains unused column 'image_path' (sic!)
polygons_bavaria = gpd.read_file("polygons_bavaria.geojson")

# ToDo: add tile_name to final dataframe
for centroid in set(polygons_bavaria.centroid_of_tile):
    gdf, target_folder = download_sentinel2_data(centroid, download_path)
    polygons_bavaria.loc[
        polygons_bavaria["centroid_of_tile"] == centroid, "image_path"
    ] = target_folder

# new line of code
polygons_bavaria.dropna(subset=["image_path"], inplace=True)

polygons_bavaria.to_file("polygons_bavaria_image_path.geojson", driver="GeoJSON")
