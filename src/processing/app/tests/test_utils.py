from pathlib import Path
from unittest.mock import Mock

import pytest
from rasterio import DatasetReader
from rasterio.windows import Window
from utils import create_output_directories, update_metadata


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


def test_update_metadata():
    # Given
    metadata = {"existing_key": "existing_value"}
    window = Window(0, 0, 10, 10)
    first_band_open = Mock(spec=DatasetReader)
    first_band_open.window_transform.return_value = "mock_transform"

    # When
    updated_metadata = update_metadata(metadata, window, first_band_open)

    # Then
    assert updated_metadata["existing_key"] == "existing_value"
    assert updated_metadata["width"] == 10
    assert updated_metadata["height"] == 10
    assert updated_metadata["transform"] == "mock_transform"


def test_update_metadata_with_invalid_metadata():
    # Given
    metadata = "invalid_metadata"
    window = Window(0, 0, 10, 10)
    first_band_open = Mock(spec=DatasetReader)

    # Then
    with pytest.raises(ValueError) as e:
        update_metadata(metadata, window, first_band_open)
    assert str(e.value) == "Metadata must be a dictionary"


def test_update_metadata_with_empty_metadata():
    # Given
    metadata = {}
    window = Window(0, 0, 10, 10)
    first_band_open = Mock(spec=DatasetReader)

    # Then
    with pytest.raises(ValueError) as e:
        update_metadata(metadata, window, first_band_open)
    assert str(e.value) == "Metadata cannot be empty"


def test_update_metadata_with_invalid_window():
    # Given
    metadata = {"existing_key": "existing_value"}
    window = "invalid_window"
    first_band_open = Mock(spec=DatasetReader)

    # Then
    with pytest.raises(ValueError) as e:
        update_metadata(metadata, window, first_band_open)
    assert str(e.value) == "Window must be a rasterio.windows.Window"


def test_update_metadata_with_invalid_first_band():
    # Given
    metadata = {"existing_key": "existing_value"}
    window = Window(0, 0, 10, 10)
    first_band_open = "invalid_first_band"

    # Then
    with pytest.raises(ValueError) as e:
        update_metadata(metadata, window, first_band_open)
    assert str(e.value) == "First band must be a rasterio.DatasetReader"


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
