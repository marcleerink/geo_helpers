import json
from unittest.mock import patch

import pytest
from shapely.geometry import (GeometryCollection, LinearRing, LineString,
                              MultiLineString, MultiPoint, MultiPolygon, Point,
                              Polygon, shape)

from ..geo_helper.projecting.reproject import (create_transformer,
                                               determine_utm_epsg,
                                               reproject_geometry,
                                               reproject_geometry_local_utm)

POINT = Point(8.0, 50.0)
LINESTRING = LineString([(8.0, 50.0), (8.1, 50.1)])
LINEARRING = LinearRing([(8.0, 50.0), (8.1, 50.1), (8.1, 50.0)])
POLYGON = Polygon([(8.0, 50.0), (8.1, 50.1), (8.1, 50.0)])
MULTIPOINT = MultiPoint([POINT])
MULTIPOLYGON = MultiPolygon([POLYGON])
MULTILINESTRING = MultiLineString([LINESTRING])
GEOMETRYCOLLECTION = GeometryCollection(
    [POINT, LINESTRING, POLYGON, MULTIPOINT, MULTIPOLYGON, MULTILINESTRING])

def open_geom(path):
    with open(path, encoding='utf-8') as f:
        return shape(json.load(f)['features'][0]['geometry'])

POLYGON_GERMANY = open_geom('tests/assets/1sqkm_germany.geojson')
POLYGON_EQUADOR = open_geom('tests/assets/1sqkm_equador.geojson')
POLYGON_JAPAN = open_geom('tests/assets/1sqkm_japan.geojson')
POLYGON_GREENLAND = open_geom('tests/assets/1sqkm_greenland.geojson')
POLYGON_ANTARCTICA = open_geom('tests/assets/1sqkm_antarctica.geojson')
POLYGON_KAZAKHSTAN = open_geom('tests/assets/1msqkm_kazakhstan.geojson')

def test_create_transformer():
    transformer = create_transformer(4326, 32632)
    assert transformer is not None

def test_create_transformer_on_centroid():
    transformer = create_transformer(4326, 3035, centroid=POINT)
    assert transformer is not None

def test_determine_utm_epsg():
    x, y = POINT.x, POINT.y
    epsg = determine_utm_epsg(4326, x, y, x, y)
    assert epsg == 32632

def test_determine_utm_epsg_bounding_box():
    bbox = POLYGON.bounds
    epsg = determine_utm_epsg(4326, *bbox)
    assert epsg == 32632

def test_determine_utm_epsg_far_east():
    epsg = determine_utm_epsg(4326, 180, 0, 180, 0)
    assert epsg == 32660

def test_determine_utm_epsg_far_west():
    epsg = determine_utm_epsg(4326, -180, 0, -180, 0)
    assert epsg == 32601

def test_determine_utm_epsg_north_pole_exception():
    with pytest.raises(ValueError):
        determine_utm_epsg(4326, 0, 90, 0, 90)

def test_determine_utm_epsg_south_pole_exception():
    with pytest.raises(ValueError):
        determine_utm_epsg(4326, 0, -90, 0, -90)

def test_determine_utm_epsg_nad27():
    epsg = determine_utm_epsg(4267, -120, 40, -120, 40)
    assert epsg == 26710

def test_determine_utm_epsg_nad83():
    epsg = determine_utm_epsg(4269, -120, 40, -120, 40)
    assert epsg == 26910

def test_project_geom_local_utm_point():
    projected = reproject_geometry_local_utm(POINT)
    assert projected.geom_type == 'Point'
    assert projected.x == 428333.5524965641
    assert projected.y == 5539109.815298798

def test_project_geom_local_utm_linestring():
    projected = reproject_geometry_local_utm(LINESTRING)
    assert projected.geom_type == 'LineString'
    assert projected.coords[0][0] == 428333.5524965641
    assert projected.coords[0][1] == 5539109.815298798
    assert projected.coords[1][0] == 435633.9854707541
    assert projected.coords[1][1] == 5550137.09562659

def test_project_geom_local_utm_linearring():
    projected = reproject_geometry_local_utm(LINEARRING)
    assert projected.geom_type == 'LinearRing'
    assert projected.coords[0][0] == 428333.5524965641
    assert projected.coords[0][1] == 5539109.815298798
    assert projected.coords[1][0] == 435633.9854707541
    assert projected.coords[1][1] == 5550137.09562659
    assert projected.coords[2][0] == 435500.0898666492
    assert projected.coords[2][1] == 5539018.78114923

def test_project_geom_local_utm_polygon():
    projected = reproject_geometry_local_utm(POLYGON)
    assert projected.geom_type == 'Polygon'
    assert projected.exterior.coords[0][0] == 428333.5524965641
    assert projected.exterior.coords[0][1] == 5539109.815298798
    assert projected.exterior.coords[1][0] == 435633.9854707541
    assert projected.exterior.coords[1][1] == 5550137.09562659
    assert projected.exterior.coords[2][0] == 435500.0898666492
    assert projected.exterior.coords[2][1] == 5539018.78114923

def test_project_geom_local_utm_multipoint():
    projected = reproject_geometry_local_utm(MULTIPOINT)
    assert projected.geom_type == 'MultiPoint'
    assert projected.geoms[0].x == 428333.5524965641
    assert projected.geoms[0].y == 5539109.815298798

def test_project_geom_local_utm_multipolygon():
    projected = reproject_geometry_local_utm(MULTIPOLYGON)
    assert projected.geom_type == 'MultiPolygon'
    assert projected.geoms[0].exterior.coords[0][0] == 428333.5524965641
    assert projected.geoms[0].exterior.coords[0][1] == 5539109.815298798
    assert projected.geoms[0].exterior.coords[1][0] == 435633.9854707541
    assert projected.geoms[0].exterior.coords[1][1] == 5550137.09562659
    assert projected.geoms[0].exterior.coords[2][0] == 435500.0898666492
    assert projected.geoms[0].exterior.coords[2][1] == 5539018.78114923

def test_project_geom_local_utm_multilinestring():
    projected = reproject_geometry_local_utm(MULTILINESTRING)
    assert projected.geom_type == 'MultiLineString'
    assert projected.geoms[0].coords[0][0] == 428333.5524965641
    assert projected.geoms[0].coords[0][1] == 5539109.815298798
    assert projected.geoms[0].coords[1][0] == 435633.9854707541
    assert projected.geoms[0].coords[1][1] == 5550137.09562659

def test_project_geom_local_utm_geometrycollection():
    projected = reproject_geometry_local_utm(GEOMETRYCOLLECTION)
    assert projected.geom_type == 'GeometryCollection'
    assert projected.geoms[0].geom_type == 'Point'
    assert projected.geoms[0].x == 428333.5524965641
    assert projected.geoms[0].y == 5539109.815298798
    assert projected.geoms[1].geom_type == 'LineString'
    assert projected.geoms[1].coords[0][0] == 428333.5524965641
    assert projected.geoms[1].coords[0][1] == 5539109.815298798
    assert projected.geoms[1].coords[1][0] == 435633.9854707541
    assert projected.geoms[1].coords[1][1] == 5550137.09562659
    assert projected.geoms[2].geom_type == 'Polygon'
    assert projected.geoms[2].exterior.coords[0][0] == 428333.5524965641
    assert projected.geoms[2].exterior.coords[0][1] == 5539109.815298798
    assert projected.geoms[2].exterior.coords[1][0] == 435633.9854707541
    assert projected.geoms[2].exterior.coords[1][1] == 5550137.09562659
    assert projected.geoms[2].exterior.coords[2][0] == 435500.0898666492
    assert projected.geoms[2].exterior.coords[2][1] == 5539018.78114923
    assert projected.geoms[3].geom_type == 'MultiPoint'
    assert projected.geoms[3].geoms[0].x == 428333.5524965641
    assert projected.geoms[3].geoms[0].y == 5539109.815298798
    assert projected.geoms[4].geom_type == 'MultiPolygon'
    assert projected.geoms[4].geoms[0].exterior.coords[0][0] == 428333.5524965641
    assert projected.geoms[4].geoms[0].exterior.coords[0][1] == 5539109.815298798
    assert projected.geoms[4].geoms[0].exterior.coords[1][0] == 435633.9854707541
    assert projected.geoms[4].geoms[0].exterior.coords[1][1] == 5550137.09562659
    assert projected.geoms[4].geoms[0].exterior.coords[2][0] == 435500.0898666492
    assert projected.geoms[4].geoms[0].exterior.coords[2][1] == 5539018.78114923
    assert projected.geoms[5].geom_type == 'MultiLineString'
    assert projected.geoms[5].geoms[0].coords[0][0] == 428333.5524965641
    assert projected.geoms[5].geoms[0].coords[0][1] == 5539109.815298798
    assert projected.geoms[5].geoms[0].coords[1][0] == 435633.9854707541
    assert projected.geoms[5].geoms[0].coords[1][1] == 5550137.09562659

def test_project_determine_utm_epsg_called_for_each_geom():
    with patch('geo_helper.geo_helper.projecting.reproject.determine_utm_epsg',
               wraps=determine_utm_epsg) as mock:
        reproject_geometry_local_utm(GEOMETRYCOLLECTION)
    assert mock.call_count == 6

    #assert that not all calls are with the same arguments
    assert mock.call_args_list[0] != mock.call_args_list[1]

def test_project_geometry_determine_utm_epsg_not_called():
    with patch('geo_helper.geo_helper.projecting.reproject.determine_utm_epsg',
               wraps=determine_utm_epsg) as mock:
        reproject_geometry(GEOMETRYCOLLECTION)
    assert mock.call_count == 0

@pytest.mark.parametrize(
    'polygon',
    [POLYGON_GERMANY, POLYGON_EQUADOR, POLYGON_GREENLAND,
    POLYGON_ANTARCTICA, POLYGON_JAPAN],
    ids=['germany', 'equador', 'greenland',
        'antarctica', 'japan'])
def test_project_geometry_local_utm_correct_polygon_area(polygon):
    projected = reproject_geometry_local_utm(polygon)
    assert projected.geom_type == 'Polygon'
    assert projected.area / 1e6 == pytest.approx(1, abs=0.01)

@pytest.mark.parametrize(
    'polygon',
    [POLYGON_GERMANY, POLYGON_EQUADOR, POLYGON_GREENLAND,
    POLYGON_ANTARCTICA, POLYGON_JAPAN],
    ids=['germany', 'equador', 'greenland',
            'antarctica', 'japan'])
def test_project_geometry_correct_polygon_area(polygon):
    projected = reproject_geometry(polygon)
    assert projected.geom_type == 'Polygon'
    assert projected.area / 1e6 == pytest.approx(1, abs=0.01)

def test_projec_geometry_correct_multipolygon_area():
    multipolygon = MultiPolygon([POLYGON_GERMANY, POLYGON_EQUADOR, POLYGON_GREENLAND,
                                POLYGON_ANTARCTICA, POLYGON_JAPAN])
    projected = reproject_geometry(multipolygon)
    assert projected.geom_type == 'MultiPolygon'
    assert projected.area / 1e6 == pytest.approx(5, abs=0.01)

def test_project_geometry_local_utm_correct_multipolygon_area():
    multipolygon = MultiPolygon([POLYGON_GERMANY, POLYGON_EQUADOR, POLYGON_GREENLAND,
                                POLYGON_ANTARCTICA, POLYGON_JAPAN])
    projected = reproject_geometry_local_utm(multipolygon)
    assert projected.geom_type == 'MultiPolygon'
    assert projected.area / 1e6 == pytest.approx(5, abs=0.01)

def test_project_multi_geometry_multithreading_catch_exception():
    with patch('geo_helper.geo_helper.projecting.reproject._reproject',
               side_effect=Exception):
        with pytest.raises(Exception):
            reproject_geometry(GEOMETRYCOLLECTION)
