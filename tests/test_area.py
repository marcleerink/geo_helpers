from shapely.geometry import (GeometryCollection, LinearRing, LineString,
                              MultiLineString, MultiPoint, MultiPolygon, Point,
                              Polygon)

from ..geo_helper.projecting.area import (calculate_area_geometry,
                                          calculate_area_geometry_local_utm)

POINT = Point(8.0, 50.0)
LINESTRING = LineString([(8.0, 50.0), (8.1, 50.1)])
LINEARRING = LinearRing([(8.0, 50.0), (8.1, 50.1), (8.1, 50.0)])
POLYGON = Polygon([(8.0, 50.0), (8.1, 50.1), (8.1, 50.0)])
MULTIPOINT = MultiPoint([POINT])
MULTIPOLYGON = MultiPolygon([POLYGON])
MULTILINESTRING = MultiLineString([LINESTRING])
GEOMETRYCOLLECTION = GeometryCollection(
    [POINT, LINESTRING, POLYGON, MULTIPOINT, MULTIPOLYGON, MULTILINESTRING])

def test_calculate_area_geometry_point():
    assert calculate_area_geometry(POINT) == 0.0

def test_calculate_area_geometry_linestring():
    assert calculate_area_geometry(LINESTRING) == 0.0

def test_calculate_area_geometry_linearring():
    assert calculate_area_geometry(LINEARRING) == 0.0

def test_calculate_area_geometry_polygon():
    assert calculate_area_geometry(POLYGON) == 39.873604788232235

def test_calculate_area_geometry_multipoint():
    assert calculate_area_geometry(MULTIPOINT) == 0.0

def test_calculate_area_geometry_multipolygon():
    assert calculate_area_geometry(MULTIPOLYGON) == 39.873604788232235

def test_calculate_area_geometry_multilinestring():
    assert calculate_area_geometry(MULTILINESTRING) == 0.0

def test_calculate_area_geometry_geometrycollection():
    assert calculate_area_geometry(GEOMETRYCOLLECTION) == 79.74720957646447
