from pathlib import Path

from utils import create_output_directories


def test_create_output_directories(monkeypatch):
    # Mock the Path.exists method to always return False
    monkeypatch.setattr(Path, "exists", lambda x: False)

    # Mock the Path.mkdir method
    monkeypatch.setattr(Path, "mkdir", lambda x, parents=False, exist_ok=False: None)

    # Given
    output_dirs = [Path("/path/to/dir1"), Path("/path/to/dir2")]

    # When
    create_output_directories(output_dirs)

    # Then
    # If the function completes without raising an exception, the test will pass


# NOTE: This test is not working
# def test_open_dataset_readers():
#     # Create temporary test files
#     with tempfile.TemporaryDirectory() as tmpdir:
#         band_file_info = {}
#         for band_name in ['band1', 'band2']:
#             file_path = f'{tmpdir}\\{band_name}.tif'
#             # Create a test GeoTIFF file
#             with rasterio.open(file_path, 'w', driver='GTiff', height=10, width=10, count=1, dtype='uint8') as dst:
#                 dst.write(np.ones((10, 10), dtype='uint8'), 1)
#             band_file_info[band_name] = {'resolution': '10m', 'file_path': file_path}

#         # Call the function under test
#         result = open_dataset_readers(band_file_info)

#         # Check the result
#         assert set(result.keys()) == {'band1', 'band2'}
#         for band_name, dataset_reader in result.items():
#             assert isinstance(dataset_reader, rasterio.DatasetReader)
#             assert dataset_reader.name == file_path
