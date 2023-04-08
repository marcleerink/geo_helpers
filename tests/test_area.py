from shapely.geometry import (GeometryCollection, LinearRing, LineString,
                              MultiLineString, MultiPoint, MultiPolygon, Point,
                              Polygon)

from ..geo_helper.area import calculate_area

POINT = Point(8.0, 50.0)
LINESTRING = LineString([(8.0, 50.0), (8.1, 50.1)])
LINEARRING = LinearRing([(8.0, 50.0), (8.1, 50.1), (8.1, 50.0)])
POLYGON = Polygon([(8.0, 50.0), (8.1, 50.1), (8.1, 50.0)])
MULTIPOINT = MultiPoint([POINT])
MULTIPOLYGON = MultiPolygon([POLYGON])
MULTILINESTRING = MultiLineString([LINESTRING])
GEOMETRYCOLLECTION = GeometryCollection(
    [POINT, LINESTRING, POLYGON, MULTIPOINT, MULTIPOLYGON, MULTILINESTRING])

def test_calculate_area_point():
    assert calculate_area(POINT) == 0.0
    assert calculate_area(POINT, use_local_utm=True) == 0.0

def test_calculate_area_linestring():
    assert calculate_area(LINESTRING) == 0.0
    assert calculate_area(LINESTRING, use_local_utm=True) == 0.0

def test_calculate_area_linearring():
    assert calculate_area(LINEARRING) == 0.0
    assert calculate_area(LINEARRING, use_local_utm=True) == 0.0

def test_calculate_area_polygon():
    assert calculate_area(POLYGON) == 39.873604788232235
    assert calculate_area(POLYGON, use_local_utm=True) == 39.846002633404

def test_calculate_area_multipoint():
    assert calculate_area(MULTIPOINT) == 0.0
    assert calculate_area(MULTIPOINT, use_local_utm=True) == 0.0

def test_calculate_area_multipolygon():
    assert calculate_area(MULTIPOLYGON) == 39.873604788232235
    assert calculate_area(MULTIPOLYGON, use_local_utm=True) == 39.846002633404

def test_calculate_area_multilinestring():
    assert calculate_area(MULTILINESTRING) == 0.0
    assert calculate_area(MULTILINESTRING, use_local_utm=True) == 0.0

def test_calculate_area_geometrycollection():
    assert calculate_area(GEOMETRYCOLLECTION) == 79.74720957646447
    assert calculate_area(GEOMETRYCOLLECTION, use_local_utm=True) == 79.692005266808
