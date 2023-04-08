import json

import pytest

from ..geo_helper.geojson.geojson import (InvalidGeojsonError,
                                          NotSupportedGeometryType,
                                          get_geojson, get_geojson_geometry,
                                          validate_geojson)

VALID_GEOJSON_PATH = 'tests/assets/1sqkm_germany.geojson'

@pytest.fixture
def valid_geojson():
    with open(VALID_GEOJSON_PATH, 'r') as f:
        geojson = f.read()
    return json.loads(geojson)

def test_get_geojson():
    geojson = get_geojson(VALID_GEOJSON_PATH)
    assert geojson["type"] == "FeatureCollection"
    assert len(geojson["features"]) == 1
    assert geojson["features"][0]["type"] == "Feature"
    assert geojson["features"][0]["geometry"]["type"] == "Polygon"
    assert geojson["features"][0]["geometry"]["coordinates"][0][0] == [11.540825, 50.12874500000001]
    assert geojson["features"][0]["geometry"]["coordinates"][0][1] == [11.56041, 50.12874500000001]
    assert geojson["features"][0]["geometry"]["coordinates"][0][2] == [11.56041, 50.13516599999997]
    assert geojson["features"][0]["geometry"]["coordinates"][0][3] == [11.540825, 50.13516599999997]
    assert geojson["features"][0]["geometry"]["coordinates"][0][4] == [11.540825, 50.12874500000001]


def test_get_geojson_geometry():
    geometry = get_geojson_geometry(VALID_GEOJSON_PATH)
    assert geometry["type"] == "Polygon"
    assert geometry["coordinates"][0][0] == [11.540825, 50.12874500000001]
    assert geometry["coordinates"][0][1] == [11.56041, 50.12874500000001]
    assert geometry["coordinates"][0][2] == [11.56041, 50.13516599999997]
    assert geometry["coordinates"][0][3] == [11.540825, 50.13516599999997]
    assert geometry["coordinates"][0][4] == [11.540825, 50.12874500000001]

def test_validate_geojson(valid_geojson):
    geojson = validate_geojson(valid_geojson)
    assert geojson["type"] == "FeatureCollection"
    assert len(geojson["features"]) == 1
    assert geojson["features"][0]["type"] == "Feature"
    assert geojson["features"][0]["geometry"]["type"] == "Polygon"
    assert geojson["features"][0]["geometry"]["coordinates"][0][0] == [11.540825, 50.12874500000001]
    assert geojson["features"][0]["geometry"]["coordinates"][0][1] == [11.56041, 50.12874500000001]
    assert geojson["features"][0]["geometry"]["coordinates"][0][2] == [11.56041, 50.13516599999997]
    assert geojson["features"][0]["geometry"]["coordinates"][0][3] == [11.540825, 50.13516599999997]
    assert geojson["features"][0]["geometry"]["coordinates"][0][4] == [11.540825, 50.12874500000001]

def test_validate_geojson_no_featurecollection():
    with pytest.raises(InvalidGeojsonError):
        validate_geojson({"type": "Feature"})

def test_validate_geojson_no_features():
    with pytest.raises(InvalidGeojsonError):
        validate_geojson({"type": "FeatureCollection"})

def test_validate_geojson_no_feature():
    with pytest.raises(InvalidGeojsonError):
        validate_geojson({"type": "FeatureCollection", "features": [{"type": "NOT_FEATURE"}]})

def test_validate_geojson_no_geometry():
    with pytest.raises(InvalidGeojsonError):
        validate_geojson({"type": "FeatureCollection", "features": [{"type": "Feature"}]})

def test_validate_geojson_no_geometry_type():
    with pytest.raises(InvalidGeojsonError):
        validate_geojson({"type": "FeatureCollection", "features": [{"type": "Feature", "geometry": {}}]})

def test_validate_geojson_no_geometry_coordinates():
    with pytest.raises(InvalidGeojsonError):
        validate_geojson(
            {"type": "FeatureCollection", "features": [
            {"type": "Feature", "geometry": {"type": "Polygon"}}]})
