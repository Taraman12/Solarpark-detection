import numpy as np
import numpy.testing as npt
import rasterio
from open_data import open_dataset_readers, stack_bands


def test_open_dataset_readers(tmp_path):
    band_file_info = {}
    for band_name in ["band1", "band2"]:
        tmp_path.mkdir(parents=True, exist_ok=True)
        file_path = tmp_path / f"{band_name}.jp2"
        with rasterio.open(
            file_path, "w", driver="GTiff", height=10, width=10, count=1, dtype="uint8"
        ) as dst:
            dst.write(np.ones((10, 10), dtype="uint8"), 1)
        band_file_info[band_name] = {"resolution": "10m", "file_path": file_path}

    # Call the function under test
    bands = open_dataset_readers(band_file_info)

    # Check the result
    assert set(bands.keys()) == {"band1", "band2"}
    for band_name, dataset_reader in bands.items():
        assert isinstance(dataset_reader, rasterio.DatasetReader)


def test_stack_bands(tmp_path):
    band_file_info = {}
    for band_name in ["band1", "band2"]:
        tmp_path.mkdir(parents=True, exist_ok=True)
        file_path = tmp_path / f"{band_name}.jp2"
        with rasterio.open(
            file_path, "w", driver="GTiff", height=10, width=10, count=1, dtype="uint16"
        ) as dst:
            dst.write(
                np.random.randint(0, 9001, size=(10, 10)), 1
            )  # np.ones((10, 10), dtype="uint16")
        band_file_info[band_name] = {"resolution": "10m", "file_path": file_path}

    # Call the function under test
    bands = open_dataset_readers(band_file_info)
    stacked_bands = stack_bands(bands)

    # Check the result
    assert stacked_bands.shape == (10, 10, 2)
    assert stacked_bands.dtype == np.uint16


def test_open_data_handler(tmp_path):
    band_file_info = {}
    for band_name in ["band1", "band2"]:
        tmp_path.mkdir(parents=True, exist_ok=True)
        file_path = tmp_path / f"{band_name}.jp2"
        with rasterio.open(
            file_path, "w", driver="GTiff", height=10, width=10, count=1, dtype="uint16"
        ) as dst:
            dst.write(np.ones((10, 10), dtype="uint16"), 1)
        band_file_info[band_name] = {"resolution": "10m", "file_path": file_path}

    # Call the function under test
    bands = open_dataset_readers(band_file_info)
    stacked_bands = stack_bands(bands)
    first_band = list(bands.keys())[0]
    original_metadata = bands[first_band].meta

    expected_result = np.ones((10, 10, 2), dtype=int)
    npt.assert_array_equal(stacked_bands, expected_result)

    assert first_band == "band1"
    assert original_metadata["driver"] == "GTiff"
    assert original_metadata["dtype"] == "uint16"
    assert original_metadata["width"] == 10
    assert original_metadata["height"] == 10
    assert original_metadata["count"] == 1
