import json

import pytest
from jsonschema import ValidationError

from ..geo_helper.geojson import (NotSupportedGeometryType, get_geojson,
                                  validate_geojson, write_geojson)

VALID_GEOJSON_PATH = 'tests/assets/1sqkm_germany.geojson'

ALL_GEOMETRY_TYPES_PATH = "tests/assets/all_geometry_types.geojson"
SCHEMA_PATH = "tests/assets/geojson_schema.json"

@pytest.fixture
def schema():
    with open(SCHEMA_PATH, 'r') as f:
        schema = f.read()
    return json.loads(schema)

VALID_GEOJSON = json.loads(open(VALID_GEOJSON_PATH, 'r').read())
ALL_GEOMETRY_TYPES_GEOJSON = json.loads(open(ALL_GEOMETRY_TYPES_PATH, 'r').read())

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

def test_get_geojson_all_geometry_types():
    geojson = get_geojson(ALL_GEOMETRY_TYPES_PATH)
    assert geojson["type"] == "FeatureCollection"
    assert len(geojson["features"]) == 7

@pytest.mark.parametrize("geojson",
    [VALID_GEOJSON, ALL_GEOMETRY_TYPES_GEOJSON],
    ids=["valid_geojson", "all_geometry_types_geojson"])
def test_validate_geojson(geojson, schema):
    validate_geojson(geojson, schema)

def test_validate_geojson_not_allowed_geometry_type_not_in_all_geometry_types(schema):
    geojson = ALL_GEOMETRY_TYPES_GEOJSON
    with pytest.raises(NotSupportedGeometryType):
        validate_geojson(geojson, schema, ['NotSupportedGeometryType'])

def test_validate_geojson_not_allowed_geometry_types(schema):
    geojson = ALL_GEOMETRY_TYPES_GEOJSON
    with pytest.raises(ValueError):
        validate_geojson(geojson, schema, ['Point'])

def test_validate_geojson_no_features(schema):
    geojson = {"type": "FeatureCollection"}
    with pytest.raises(ValidationError):
        validate_geojson(geojson, schema)

def test_validate_geojson_empty_features(schema):
    geojson = {"type": "FeatureCollection", "features": []}
    with pytest.raises(ValidationError):
        validate_geojson(geojson, schema)

def test_validate_geojson_no_geometry(schema):
    geojson = {"type": "FeatureCollection", "features": [{"type": "Feature"}]}
    with pytest.raises(ValidationError):
        validate_geojson(geojson, schema)

def test_validate_geojson_no_type(schema):
    geojson = {"features": []}
    with pytest.raises(ValidationError):
        validate_geojson(geojson, schema)

def test_validate_geojson_wrong_type(schema):
    geojson = {"type": "Feature", "features": []}
    with pytest.raises(ValidationError):
        validate_geojson(geojson, schema)

def test_validate_geojson_wrong_feature_type(schema):
    geojson = {"type": "FeatureCollection", "features": [{"type": "FeatureCollection"}]}
    with pytest.raises(ValidationError):
        validate_geojson(geojson, schema)

def test_validate_geojson_wrong_geometry_type(schema):
    geojson = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "geometry": {"type": "Point"}}]}
    with pytest.raises(ValidationError):
        validate_geojson(geojson, schema)

def test_validate_geojson_wrong_point_coordinates(schema):
    geojson = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [1, 2, 3]}}]}
    with pytest.raises(ValidationError):
        validate_geojson(geojson, schema)

def test_validate_geojson_wrong_line_coordinates(schema):
    geojson = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "geometry": {"type": "LineString", "coordinates": [[1, 2], [3, 4, 5]]}}]}
    with pytest.raises(ValidationError):
        validate_geojson(geojson, schema)

def test_validate_geojson_wrong_polygon_coordinates(schema):
    geojson = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[1, 2], [3, 4, 5]]]}}]}
    with pytest.raises(ValidationError):
        validate_geojson(geojson, schema)

def test_validate_geojson_polygon_not_closed(schema):
    geojson = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "geometry": {"type": "Polygon", "coordinates": [[[1, 2], [3, 4], [5, 6]]]}}]}
    with pytest.raises(ValidationError):
        validate_geojson(geojson, schema)

def test_validate_geojson_wrong_multipoint_coordinates(schema):
    geojson = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "geometry": {"type": "MultiPoint", "coordinates": [[1, 2, 3]]}}]}
    with pytest.raises(ValidationError):
        validate_geojson(geojson, schema)

def test_validate_geojson_wrong_multiline_coordinates(schema):
    geojson = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "geometry": {"type": "MultiLineString", "coordinates": [[[1, 2], [3, 4, 5]]]}}]}
    with pytest.raises(ValidationError):
        validate_geojson(geojson, schema)

def test_validate_geojson_wrong_multipolygon_coordinates(schema):
    geojson = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "geometry": {"type": "MultiPolygon", "coordinates": [[[[1, 2], [3, 4, 5]]]]}}]}
    with pytest.raises(ValidationError):
        validate_geojson(geojson, schema)

def test_validate_geojson_multipolygon_not_closed(schema):
    geojson = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "geometry": {"type": "MultiPolygon", "coordinates": [[[[1, 2], [3, 4], [5, 6]]]]}}]}
    with pytest.raises(ValidationError):
        validate_geojson(geojson, schema)

def test_validate_geojson_wrong_geometrycollection_coordinates(schema):
    geojson = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "geometry": {"type": "GeometryCollection", "geometries": [
            {"type": "Point", "coordinates": [1, 2, 3]}]}}]}
    with pytest.raises(ValidationError):
        validate_geojson(geojson, schema)

def test_validate_geojson_wrong_feature_properties(schema):
    geojson = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [1, 2]}, "properties": 42}]}
    with pytest.raises(ValidationError):
        validate_geojson(geojson, schema)

def test_validate_geojson_wrong_feature_id(schema):
    geojson = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [1, 2]}, "id": 42}]}
    with pytest.raises(ValidationError):
        validate_geojson(geojson, schema)

def test_validate_geojson_wrong_feature_boundingbox(schema):
    geojson = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [1, 2]}, "bbox": 42}]}
    with pytest.raises(ValidationError):
        validate_geojson(geojson, schema)

def test_validate_geojson_wrong_feature_boundingbox_length(schema):
    geojson = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [1, 2]}, "bbox": [1, 2, 3]}]}
    with pytest.raises(ValidationError):
        validate_geojson(geojson, schema)

def test_validate_geojson_wrong_feature_boundingbox_type(schema):
    geojson = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [1, 2]}, "bbox": [1, 2, 3, "4"]}]}
    with pytest.raises(ValidationError):
        validate_geojson(geojson, schema)

def test_write_geojson(tmpdir):
    geojson = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": [1, 2]}, "properties": {"foo": "bar"}}]}
    path = tmpdir.join("test.geojson")
    write_geojson(geojson, path)
    with open(path) as f:
        assert f.read() == json.dumps(geojson, indent=4)
