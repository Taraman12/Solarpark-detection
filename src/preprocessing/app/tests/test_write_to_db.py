import os
from unittest.mock import patch

import numpy as np
import pytest
import rasterio
import requests
from constants import KERNEL_SIZE
from shapely.geometry import Polygon
from write_to_db import (
    calc_peak_power,
    create_mask,
    create_polygon_and_area,
    extract_polygon_coordinates,
    extract_shapes,
    prediction_to_polygons,
    to_datetime_str,
    transform_polygon,
    write_to_db,
)


def test_create_mask_with_all_values_below_threshold():
    # Test with a prediction where all values are below the threshold
    prediction = np.random.rand(1, KERNEL_SIZE, KERNEL_SIZE) * 0.4
    expected = np.zeros((KERNEL_SIZE, KERNEL_SIZE), dtype=np.uint8)
    result = create_mask(prediction)
    assert result.shape == (KERNEL_SIZE, KERNEL_SIZE)
    np.testing.assert_array_equal(result, expected)


def test_create_mask_with_all_values_above_threshold():
    # Test with a prediction where all values are above the threshold
    prediction = np.random.rand(1, KERNEL_SIZE, KERNEL_SIZE) * 0.6 + 0.5
    expected = np.ones((KERNEL_SIZE, KERNEL_SIZE), dtype=np.uint8)
    result = create_mask(prediction)
    assert result.shape == (KERNEL_SIZE, KERNEL_SIZE)
    np.testing.assert_array_equal(result, expected)


def test_create_mask_with_some_values_above_threshold():
    # Test with a prediction where some values are above and below the threshold
    prediction = np.zeros((1, KERNEL_SIZE, KERNEL_SIZE))
    prediction[
        0, : KERNEL_SIZE // 2, : KERNEL_SIZE // 2
    ] = 0.4  # values below the threshold
    prediction[
        0, KERNEL_SIZE // 2 :, KERNEL_SIZE // 2 :
    ] = 0.6  # values above the threshold
    expected = np.zeros((KERNEL_SIZE, KERNEL_SIZE), dtype=np.uint8)
    expected[KERNEL_SIZE // 2 :, KERNEL_SIZE // 2 :] = 1
    result = create_mask(prediction)
    assert result.shape == (KERNEL_SIZE, KERNEL_SIZE)
    np.testing.assert_array_equal(result, expected)


def test_create_mask_with_invalid_input():
    # Test with invalid input
    prediction = "not a numpy array"
    with pytest.raises(TypeError):
        create_mask(prediction)


def test_create_mask_with_invalid_shape():
    # Test with invalid shape
    prediction = np.random.rand(2, KERNEL_SIZE, KERNEL_SIZE)
    with pytest.raises(ValueError):
        create_mask(prediction)


def test_create_mask_with_invalid_dtype():
    # Test with invalid dtype
    prediction = np.random.randint(0, 2, (1, KERNEL_SIZE, KERNEL_SIZE))
    with pytest.raises(TypeError):
        create_mask(prediction)


def test_extract_shapes_with_invalid_dtype():
    # Test with invalid dtype
    mask = np.random.rand(5, 5)
    transform = rasterio.transform.from_origin(0, 5, 1, 1)
    with pytest.raises(TypeError):
        extract_shapes(mask, transform)


def test_extract_shapes_with_invalid_dimensions():
    # Test with invalid dimensions
    mask = np.random.randint(0, 2, (1, 5, 5), dtype=np.uint8)
    transform = rasterio.transform.from_origin(0, 5, 1, 1)
    with pytest.raises(ValueError):
        extract_shapes(mask, transform)


def test_extract_shapes_with_single_shape():
    # Test with a mask that contains a single shape
    mask = np.zeros((5, 5), dtype=np.uint8)
    mask[1:4, 1:4] = 1
    transform = rasterio.transform.from_origin(0, 5, 1, 1)
    expected = [
        (
            {
                "type": "Polygon",
                "coordinates": [
                    [(1.0, 4.0), (1.0, 1.0), (4.0, 1.0), (4.0, 4.0), (1.0, 4.0)]
                ],
            },
            1.0,
        )
    ]
    result = extract_shapes(mask, transform)
    assert len(result) == 1
    assert result == expected


def test_extract_shapes_with_multiple_shapes():
    # Test with a mask that contains multiple shapes
    mask = np.zeros((5, 5), dtype=np.uint8)
    mask[1:3, 1:3] = 1
    mask[3:5, 3:5] = 1
    transform = rasterio.transform.from_origin(0, 5, 1, 1)
    expected = [
        (
            {
                "type": "Polygon",
                "coordinates": [
                    [(1.0, 4.0), (1.0, 2.0), (3.0, 2.0), (3.0, 4.0), (1.0, 4.0)]
                ],
            },
            1.0,
        ),
        (
            {
                "type": "Polygon",
                "coordinates": [
                    [(3.0, 2.0), (3.0, 0.0), (5.0, 0.0), (5.0, 2.0), (3.0, 2.0)]
                ],
            },
            1.0,
        ),
    ]
    result = extract_shapes(mask, transform)
    assert len(result) == 2
    assert result == expected
    assert isinstance(result, list)


def test_extract_shapes_with_no_shapes():
    # Test with a mask that contains no shapes
    mask = np.zeros((5, 5), dtype=np.uint8)
    transform = rasterio.transform.from_origin(0, 5, 1, 1)
    result = extract_shapes(mask, transform)
    assert len(result) == 0


def test_create_polygon_and_area_with_valid_input():
    # Test with valid input
    shape = list(
        (
            {
                "type": "Polygon",
                "coordinates": [
                    [(1.0, 4.0), (1.0, 1.0), (4.0, 1.0), (4.0, 4.0), (1.0, 4.0)]
                ],
            },
            1.0,
        )
    )
    expected_polygon = Polygon(
        [(1.0, 4.0), (1.0, 1.0), (4.0, 1.0), (4.0, 4.0), (1.0, 4.0)]
    )
    expected_area = expected_polygon.area
    result_polygon, result_area = create_polygon_and_area(shape)
    assert result_polygon.equals(expected_polygon)
    assert result_area == expected_area


def test_create_polygon_and_area_with_invalid_input():
    # Test with invalid input
    shape = "not a valid shape"
    with pytest.raises(TypeError):
        create_polygon_and_area(shape)


def test_create_polygon_and_area_with_invalid_coordinates():
    # Test with invalid coordinates
    shape = list(
        (
            {
                "type": "Polygon",
                "coordinates": "not a valid coordinates",
            },
            1.0,
        )
    )
    with pytest.raises(ValueError):
        create_polygon_and_area(shape)


def test_transform_polygon_with_valid_input():
    # Test with valid input
    polygon = Polygon([(1.0, 4.0), (1.0, 1.0), (4.0, 1.0), (4.0, 4.0), (1.0, 4.0)])
    crs = "EPSG:3857"
    result = transform_polygon(polygon, crs)
    assert isinstance(result, Polygon)
    assert result.is_valid


def test_transform_polygon_with_invalid_polygon():
    # Test with invalid polygon
    polygon = "not a valid polygon"
    crs = "EPSG:3857"
    with pytest.raises(TypeError):
        transform_polygon(polygon, crs)


def test_transform_polygon_with_invalid_crs():
    # Test with invalid CRS
    polygon = Polygon([(1.0, 4.0), (1.0, 1.0), (4.0, 1.0), (4.0, 4.0), (1.0, 4.0)])
    crs = 1234
    with pytest.raises(TypeError):
        transform_polygon(polygon, crs)


def test_transform_polygon_with_nonexistent_crs():
    # Test with non-existent CRS
    polygon = Polygon([(1.0, 4.0), (1.0, 1.0), (4.0, 1.0), (4.0, 4.0), (1.0, 4.0)])
    crs = "EPSG:9999"
    with pytest.raises(ValueError):
        transform_polygon(polygon, crs)


def test_prediction_to_polygons_with_valid_input():
    # Test with valid input
    prediction = np.random.rand(1, KERNEL_SIZE, KERNEL_SIZE)
    metadata = {
        "transform": rasterio.transform.from_origin(0, 5, 1, 1),
        "crs": "EPSG:3857",
    }
    polygons, areas = prediction_to_polygons(prediction, metadata)
    assert isinstance(polygons, list)
    assert isinstance(areas, list)
    assert len(polygons) == len(areas)


def test_prediction_to_polygons_with_invalid_prediction():
    # Test with invalid prediction
    prediction = "not a numpy array"
    metadata = {
        "transform": rasterio.transform.from_origin(0, 5, 1, 1),
        "crs": "EPSG:3857",
    }
    with pytest.raises(TypeError):
        prediction_to_polygons(prediction, metadata)


def test_prediction_to_polygons_with_invalid_metadata():
    # Test with invalid metadata
    prediction = np.random.rand(1, KERNEL_SIZE, KERNEL_SIZE)
    metadata = "not a dictionary"
    with pytest.raises(TypeError):
        prediction_to_polygons(prediction, metadata)


def test_prediction_to_polygons_with_missing_transform_in_metadata():
    # Test with missing 'transform' key in metadata
    prediction = np.random.rand(1, KERNEL_SIZE, KERNEL_SIZE)
    metadata = {"crs": "EPSG:3857"}
    with pytest.raises(KeyError):
        prediction_to_polygons(prediction, metadata)


def test_prediction_to_polygons_with_missing_crs_in_metadata():
    # Test with missing 'crs' key in metadata
    prediction = np.random.rand(1, KERNEL_SIZE, KERNEL_SIZE)
    metadata = {"transform": rasterio.transform.from_origin(0, 5, 1, 1)}
    with pytest.raises(KeyError):
        prediction_to_polygons(prediction, metadata)


def test_to_datetime_str_with_valid_input():
    # Test with valid input
    date_string = "2022-01-01"
    expected = "2022-01-01"
    result = to_datetime_str(date_string)
    assert result == expected


def test_to_datetime_str_with_invalid_format():
    # Test with date string in invalid format
    date_string = "01-01-2022"
    with pytest.raises(ValueError):
        to_datetime_str(date_string)


def test_to_datetime_str_with_invalid_type():
    # Test with non-string input
    date_string = 20220101
    with pytest.raises(TypeError):
        to_datetime_str(date_string)


def test_to_datetime_str_with_empty_string():
    # Test with empty string
    date_string = ""
    with pytest.raises(ValueError):
        to_datetime_str(date_string)


def test_extract_polygon_coordinates_with_valid_input():
    # Test with valid input
    polygon = Polygon([(0, 0), (1, 1), (1, 0)])
    expected_latitudes = [0, 1, 0, 0]
    expected_longitudes = [0, 1, 1, 0]
    result_latitudes, result_longitudes = extract_polygon_coordinates(polygon)
    assert result_latitudes == expected_latitudes
    assert result_longitudes == expected_longitudes


def test_extract_polygon_coordinates_with_invalid_type():
    # Test with non-Polygon input
    polygon = "not a polygon"
    with pytest.raises(TypeError):
        extract_polygon_coordinates(polygon)


def test_extract_polygon_coordinates_with_no_exterior_ring():
    # Test with Polygon that has no exterior ring
    polygon = Polygon()
    with pytest.raises(ValueError):
        extract_polygon_coordinates(polygon)


def test_calc_peak_power_with_valid_input():
    # Test with valid input
    area_in_sq_m = 10000
    expected = 1.0
    result = calc_peak_power(area_in_sq_m)
    assert result == expected


def test_calc_peak_power_with_zero():
    # Test with zero area
    area_in_sq_m = 0
    expected = 0.0
    result = calc_peak_power(area_in_sq_m)
    assert result == expected


def test_calc_peak_power_with_negative_input():
    # Test with negative area
    area_in_sq_m = -1
    with pytest.raises(ValueError):
        calc_peak_power(area_in_sq_m)


def test_calc_peak_power_with_non_number_input():
    # Test with non-number input
    area_in_sq_m = "not a number"
    with pytest.raises(TypeError):
        calc_peak_power(area_in_sq_m)


@patch("requests.post")
@patch.dict(os.environ, {"JWT": "test_token"}, clear=True)
def test_write_to_db_with_valid_input(mock_post):
    # Test with valid input
    mock_post.return_value.raise_for_status.return_value = None
    polygon = Polygon([(0, 0), (1, 1), (1, 0)])
    area = 0.5
    tile_date = "2022-01-01"
    filename = "test.tif"
    assert write_to_db(polygon, area, tile_date, filename)


@patch("requests.post")
@patch.dict(os.environ, {"JWT": "test_token"}, clear=True)
def test_write_to_db_with_invalid_polygon(mock_post):
    # Test with invalid polygon
    polygon = "not a polygon"
    area = 0.5
    tile_date = "2022-01-01"
    filename = "test.tif"
    with pytest.raises(TypeError):
        write_to_db(polygon, area, tile_date, filename)


@patch("requests.post")
@patch.dict(os.environ, {"JWT": "test_token"}, clear=True)
def test_write_to_db_with_invalid_area(mock_post):
    # Test with invalid area
    polygon = Polygon([(0, 0), (1, 1), (1, 0)])
    area = -1
    tile_date = "2022-01-01"
    filename = "test.tif"
    with pytest.raises(ValueError):
        write_to_db(polygon, area, tile_date, filename)


@patch("requests.post")
@patch.dict(os.environ, {"JWT": "test_token"}, clear=True)
def test_write_to_db_with_invalid_tile_date(mock_post):
    # Test with invalid tile_date
    polygon = Polygon([(0, 0), (1, 1), (1, 0)])
    area = 0.5
    tile_date = 20220101
    filename = "test.tif"
    with pytest.raises(TypeError):
        write_to_db(polygon, area, tile_date, filename)


@patch("requests.post")
@patch.dict(os.environ, {"JWT": "test_token"}, clear=True)
def test_write_to_db_with_invalid_filename(mock_post):
    # Test with invalid filename
    polygon = Polygon([(0, 0), (1, 1), (1, 0)])
    area = 0.5
    tile_date = "2022-01-01"
    filename = 123
    with pytest.raises(TypeError):
        write_to_db(polygon, area, tile_date, filename)


@patch("requests.post")
@patch.dict(os.environ, {"JWT": "test_token"}, clear=True)
def test_write_to_db_with_request_exception(mock_post):
    # Test with a request exception
    mock_post.return_value.raise_for_status.side_effect = (
        requests.exceptions.RequestException
    )
    polygon = Polygon([(0, 0), (1, 1), (1, 0)])
    area = 0.5
    tile_date = "2022-01-01"
    filename = "test.tif"
    with pytest.raises(requests.exceptions.RequestException):
        write_to_db(polygon, area, tile_date, filename)
