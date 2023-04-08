import json
from enum import Enum

import jsonschema
from jsonschema import ValidationError
from shapely.geometry import MultiPolygon, Polygon, shape
from shapely.geometry.base import BaseGeometry


class NotSupportedGeometryType(Exception):
    """Exception for not supported geometry type"""

class GeometryType(Enum):
    POINT = 'Point'
    LINESTRING = 'LineString'
    LINEARRING = 'LinearRing'
    POLYGON = 'Polygon'
    MULTIPOINT = 'MultiPoint'
    MULTILINESTRING = 'MultiLineString'
    MULTIPOLYGON = 'MultiPolygon'
    GEOMETRYCOLLECTION = 'GeometryCollection'

def _read_geojson(geojson_path: str) -> str:
    try:
        with open(geojson_path, encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError as err:
        raise FileNotFoundError(f"Geojson file not found: {geojson_path}") from err

def _load_geojson(geojson_str: str) -> dict:
    return json.loads(geojson_str)

SCHEMA = _load_geojson(_read_geojson("assets/geojson_schema.json"))

def get_geojson(geojson_path: str, schema: dict = SCHEMA) -> dict:
    """Reads geojson file and returns a geojson dictionary.

    :param geojson_path: Path to geojson file
    :param schema: Geojson schema.
        Default is schema from 'https://geojson.org/schema/FeatureCollection.json'

    :return: Geojson dictionary

    :raises FileNotFoundError: If geojson file not found.
    :raises JSONDecodeError: If geojson file is not valid json.
    :raises jsonschema.exceptions.ValidationError: If geojson is not valid.
    :raises jsonschema.exceptions.SchemaError: If schema is not valid.

    """
    geojson = _load_geojson(_read_geojson(geojson_path))
    validate_geojson(geojson, schema)

    return geojson

def validate_geojson(geojson:dict, schema: dict) -> None:
    jsonschema.validate(geojson, schema)
    if not geojson["features"]:
        raise ValidationError("No features in geojson")

def get_geojson_geometry(geojson_path: str) -> dict:
    """Returns the geometry of the first feature in a geojson file.

    :param geojson_path: Path to geojson file

    :return: Geojson geometry

    :raises FileNotFoundError: If geojson file is not found
    :raises JSONDecodeError: If geojson file is not valid json.
    :raises jsonschema.exceptions.ValidationError: If geojson is not valid.
    :raises jsonschema.exceptions.SchemaError: If schema is not valid.
    """
    val_geojson = get_geojson(geojson_path)
    return val_geojson["features"][0]["geometry"]


def get_shape_from_geojson(geojson_path: str) -> BaseGeometry:
    """returns shapely shape from geojson file"""
    return shape(get_geojson_geometry(geojson_path))

def get_bbox_from_geojson(geojson_path: str):
    """returns bbox from geojson file"""
    return get_shape_from_geojson(geojson_path).bounds

def get_simple_polygon_from_geojson(geojson_path: str) -> dict:
    """returns polygon geojson from geojson file"""
    bbox = get_bbox_from_geojson(geojson_path)
    return {
        "type": "Polygon",
        "coordinates": [[
            [bbox[0], bbox[1]],
            [bbox[2], bbox[1]],
            [bbox[2], bbox[3]],
            [bbox[0], bbox[3]],
            [bbox[0], bbox[1]]
        ]]
    }
