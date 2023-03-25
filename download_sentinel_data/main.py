# third-party
import geopandas as gpd

# local-modules
from API_call_handler import download_sentinel2_data

# print('Program started')
# trn_polygons_path = r'C:\Users\Fabian\OneDrive - Universität Würzburg\Uni Würzburg\Master\Masterthesis\Code\Einarbeitung\trn_polygons.geojson'
# trn_polygons = gpd.read_file(trn_polygons_path)

# germany_borders_path = r'C:\Users\Fabian\Documents\Masterarbeit_Daten\DEU_adm\DEU_adm3.shp'
# germany_borders = gpd.read_file(germany_borders_path)

# wuerzburg_borders = germany_borders[germany_borders.NAME_3 =='Würzburg']

# polygons_wuerzburg= gpd.clip(trn_polygons, wuerzburg_borders)

# polygons_giebelstadt = polygons_wuerzburg[polygons_wuerzburg.name == 'Solarpark Giebelstadt'].reset_index()

# download_path = r'C:\Users\Fabian\Documents\Masterarbeit_Daten\API_test2'
# footprint = polygons_giebelstadt.loc[0, 'geometry'].wkt
# gdf, file_name = download_sentinel2_data(footprint, download_path)
# print('Program finished')
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
polygons_bavaria.dropna(subset=['image_path'], inplace=True)

polygons_bavaria.to_file("polygons_bavaria_image_path.geojson", driver="GeoJSON")
