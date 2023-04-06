from __future__ import annotations

import json
from enum import Enum
from typing import Union

from shapely.geometry import (LineString, MultiLineString, MultiPoint,
                              MultiPolygon, Point, Polygon, shape)


class InvalidGeojsonError(Exception):
    """Exception for invalid geojson"""

class InvalidGeojsonFeatureError(Exception):
    """Exception for invalid geojson feature"""

class InvalidGeojsonGeometryError(Exception):
    """Exception for invalid geojson geometry"""

class NotSupportedGeometryTypeError(Exception):
    """Exception for not supported geometry type"""

class GeometryType(Enum):
    """Supported geometry types for Planet API"""
    POINT = Point
    MULTIPOINT = MultiPoint
    LINESTRING = LineString
    MULTILINESTRING = MultiLineString
    POLYGON = Polygon
    MULTIPOLYGON = MultiPolygon

    @property
    def geom_type(self) -> str:
        """Returns geometry type string.

        :return: Geometry type string
        """
        return self.value.geom_type

    @staticmethod
    def get_geometry_type(geometry_type: str) -> Union[GeometryType, None]:
        """Returns GeometryType enum for given geometry type string.

        :param geometry_type: Geometry type string

        :return: GeometryType enum
        """
        try:
            return GeometryType[geometry_type.upper()]
        except KeyError:
            return None

def _read_geojson(geojson_path: str) -> str:
    try:
        with open(geojson_path, encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError as err:
        raise FileNotFoundError(f"Geojson file not found: {geojson_path}") from err

def _load_geojson(geojson_str: str) -> dict:
    try:
        return json.loads(geojson_str)
    except json.JSONDecodeError as err:
        raise InvalidGeojsonError("Invalid geojson format.") from err

def get_geojson(geojson_path: str) -> dict:
    """Reads geojson file and returns a geojson dictionary.

    :param geojson_path: Path to geojson file

    :return: Geojson dictionary

    :raises FileNotFoundError: If geojson file is not found
    :raises InvalidGeojsonError: If geojson file is invalid format
    :raises InvalidGeojsonFeatureError: If geojson file has invalid feature
    :raises InvalidGeojsonGeometryError: If geojson file has invalid geometry
    """
    geojson = _load_geojson(_read_geojson(geojson_path))
    validate_geojson(geojson)

    return geojson

def get_geojson_geometry(geojson_path: str) -> dict:
    """Returns the geometry of the first feature in a geojson file.

    :param geojson_path: Path to geojson file

    :return: Geojson geometry

    :raises FileNotFoundError: If geojson file is not found
    :raises InvalidGeojsonError: If geojson file is invalid format
    :raises InvalidGeojsonFeatureError: If geojson file has invalid feature
    :raises InvalidGeojsonGeometryError: If geojson file has invalid geometry
    """
    val_geojson = get_geojson(geojson_path)
    return val_geojson["features"][0]["geometry"]


def validate_geojson(geojson:dict) -> dict:
    """Validate geojson dictionary.

    :param geojson: Geojson dictionary

    :raises InvalidGeojsonError: If geojson file is invalid format
    :raises InvalidGeojsonFeatureError: If geojson file has invalid feature
    :raises InvalidGeojsonGeometryError: If geojson file has invalid geometry

    :return: validated Geojson dictionary"""
    if "type" not in geojson or geojson["type"] != "FeatureCollection":
        raise InvalidGeojsonError("Invalid geojson format.")

    features = geojson.get("features", [])
    if not features:
        raise ValueError("No features found in geojson.")

    for feature in features:
        validate_geojson_feature(feature)

    return geojson


def validate_geojson_feature(feature: dict) -> dict:
    """Validate geojson feature dictionary with a geometry field.

    :param feature: Geojson feature dictionary

    """
    if feature.get("type") != "Feature":
        raise InvalidGeojsonFeatureError(
            "Invalid geojson feature. Must have 'type' of 'Feature'")

    geometry = feature.get("geometry")
    if geometry is None:
        raise InvalidGeojsonFeatureError("Invalid geojson feature. Must have geometry field")

    geometry = validate_geojson_geometry(geometry)

    return feature


def validate_geojson_geometry(geometry: dict) -> dict:
    geometry_type: str | None = geometry.get('type')
    coordinates: list | None = geometry.get('coordinates')

    if not geometry_type:
        raise InvalidGeojsonGeometryError("No geometry type found")
    if not coordinates or not isinstance(coordinates, list):
        raise InvalidGeojsonGeometryError("No coordinates found")

    geometry_validation_map = {
        GeometryType.POINT.__str__: _validate_point_coordinates,
        GeometryType.MULTIPOINT.__str__: _validate_multipoint_coordinates,
        GeometryType.LINESTRING.__str__: _validate_linestring_coordinates,
        GeometryType.MULTILINESTRING.__str__: _validate_multilinestring_coordinates,
        GeometryType.POLYGON.__str__: _validate_polygon_coordinates,
        GeometryType.MULTIPOLYGON.__str__: _validate_multipolygon_coordinates,
    }

    if geometry_type.lower() not in geometry_validation_map:
        raise NotSupportedGeometryTypeError(f"Invalid geometry type: {geometry_type}")

    validation_func = geometry_validation_map[geometry_type]
    validation_func(coordinates)

    return geometry

def _validate_point_coordinates(coordinates: list[float]) -> None:
    if len(coordinates) != 2:
        raise InvalidGeojsonGeometryError("Point must have 2 coordinates")

def _validate_multipoint_coordinates(coordinates: list[list[float]]) -> None:
    for point in coordinates:
        _validate_point_coordinates(point)

def _validate_linestring_coordinates(coordinates: list[list[float]]) -> None:
    if len(coordinates) < 2:
        raise InvalidGeojsonGeometryError("LineString must have at least 2 coordinates")
    for point in coordinates:
        _validate_point_coordinates(point)

def _validate_multilinestring_coordinates(coordinates: list[list[list[float]]]) -> None:
    for linestring in coordinates:
        _validate_linestring_coordinates(linestring)

def _validate_polygon_coordinates(coordinates: list[list[list[float]]]) -> None:
    lengths = all([len(elem) >= 4 for elem in coordinates])

    if lengths is False:
        raise InvalidGeojsonGeometryError("Polygon must have at least 4 coordinates")

    isring = all([elem[0] == elem[-1] for elem in coordinates])
    if isring is False:
        raise InvalidGeojsonGeometryError("Polygon must be closed")

def _validate_multipolygon_coordinates(coordinates: list[list[list[list[float]]]]) -> None:
    for polygon in coordinates:
        _validate_polygon_coordinates(polygon)


def get_shape_from_geojson(geojson_path: str) -> Union[Polygon, MultiPolygon]:
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
