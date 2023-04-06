from typing import Optional

import pyproj
from pyproj.aoi import AreaOfInterest
from pyproj.database import query_utm_crs_info
from shapely.geometry import (GeometryCollection, LinearRing, LineString,
                              MultiLineString, MultiPoint, MultiPolygon, Point,
                              Polygon)
from shapely.ops import BaseGeometry


def determine_utm_epsg(
    source_epsg:int,
    west_lon:float,
    south_lat:float,
    east_lon:float,
    north_lat:float,
    contains: bool = True) -> int:
    """
    Determine the UTM EPSG code for a given epsg code and bounding box

    :param source_epsg: The source EPSG code
    :param west_lon: The western longitude
    :param south_lat: The southern latitude
    :param east_lon: The eastern longitude
    :param north_lat: The northern latitude
    :param contains: If True, the UTM CRS must contain the bounding box,
        if False, the UTM CRS must intersect the bounding box.

    :return: The UTM EPSG code

    :raises ValueError: If no UTM CRS is found for the epsg and bbox
    """
    datum_name = pyproj.CRS.from_epsg(source_epsg).to_dict()['datum']

    utm_crs_info = query_utm_crs_info(
        datum_name= datum_name,
        area_of_interest=AreaOfInterest(
                west_lon, south_lat, east_lon, north_lat),
        contains=contains)

    if not utm_crs_info:
        raise ValueError(
            f'No UTM CRS found for the datum {datum_name} and bbox')
    print(utm_crs_info[0].code)
    return int(utm_crs_info[0].code)

def is_utm_epsg(epsg: int) -> bool:
    """ Check if an EPSG code is a UTM code."""
    return pyproj.CRS.from_epsg(epsg).to_dict()['proj'] == 'utm'

def create_transformer(
    source_epsg: int,
    target_epsg: int,
    centroid: Optional[Point] = None
    ) -> pyproj.Transformer:
    """
    Create a pyproj transformer for a given source and target EPSG code.
    """
    source_crs = pyproj.CRS.from_epsg(source_epsg)

    if is_utm_epsg(target_epsg):
        target_crs = pyproj.CRS.from_epsg(target_epsg)
    else:
        if centroid is None:
            raise ValueError("A centroid must be provided for non-UTM projections")

        lon, lat = centroid.x, centroid.y
        proj_name = pyproj.CRS.from_epsg(target_epsg).to_dict()['proj']
        target_crs = pyproj.CRS(
            proj=proj_name, lat_1=lat, lat_2=lat, lat_0=lat, lon_0=lon)

    return pyproj.Transformer.from_crs(
        source_crs, target_crs, always_xy=True)


def project_geometry_equal_area(
    geometry:BaseGeometry,
    source_epsg:int=4326,
    target_epsg:int=3857
    ) -> BaseGeometry:
    """
    Project any shapely geometry to an equal-area projection centered on the centroid.
    For multi-part geometries, each part is processed separately.

    :param geometry: shapely geometry to project
    :param source_epsg: EPSG code of the source geometry

    :return: projected shapely geometry
    :raises TypeError: if the geometry type is not supported
    """
    return _project_geometry(geometry, source_epsg, target_epsg)

def project_geometry_local_utm(
    geometry:BaseGeometry,
    source_epsg:int=4326,
    ) -> BaseGeometry:
    """
    Project any shapely geometry to a local UTM projection.
    For multi-part geometries, each part is processed separately.

    :param geometry: shapely geometry to project
    :param source_epsg: EPSG code of the source geometry

    :return: projected shapely geometry
    :raises TypeError: if the geometry type is not supported
    """
    return _project_geometry(geometry, source_epsg)

def _project_geometry(
    geometry: BaseGeometry,
    source_epsg: int = 4326,
    target_epsg: Optional[int] = None,
    ) -> BaseGeometry:
    geom_map = {
        Point: _project_point,
        LineString: _project_linestring,
        LinearRing: _project_linear_ring,
        Polygon: _project_polygon,
        MultiPoint: lambda mp, source_epsg, target_epsg: MultiPoint(
            [_project_geometry(p, source_epsg, target_epsg) for p in mp.geoms]),
        MultiLineString: lambda mls, source_epsg, target_epsg: MultiLineString(
            [_project_geometry(ls, source_epsg, target_epsg) for ls in mls.geoms]),
        MultiPolygon: lambda mp, source_epsg, target_epsg: MultiPolygon(
            [_project_geometry(p, source_epsg, target_epsg) for p in mp.geoms]),
        GeometryCollection: lambda gc, source_epsg, target_epsg: GeometryCollection(
            [_project_geometry(g, source_epsg, target_epsg) for g in gc.geoms]),
    }

    if type(geometry) not in geom_map:
        raise TypeError(f"Unsupported geometry type: {type(geometry)}")

    if target_epsg is None and isinstance(geometry, (Point, LineString, LinearRing, Polygon)):
        x, y = geometry.centroid.x, geometry.centroid.y
        target_epsg = determine_utm_epsg(source_epsg, x, y, x, y)

    return geom_map[type(geometry)](geometry, source_epsg, target_epsg)

def _project_point(
    point: Point, source_epsg: int, target_epsg: int
    ) -> Point:
    transformer = create_transformer(source_epsg, target_epsg, point)
    return Point(transformer.transform(point.x, point.y))

def _project_linestring(
    linestring: LineString, source_epsg: int, target_epsg: int
    ) -> LineString:
    transformer = create_transformer(source_epsg, target_epsg, linestring.centroid)
    return LineString([transformer.transform(*xy) for xy in linestring.coords])

def _project_linear_ring(
    linear_ring: LinearRing, source_epsg: int, target_epsg: int
    ) -> LinearRing:
    transformer = create_transformer(source_epsg, target_epsg, linear_ring.centroid)
    return LinearRing([transformer.transform(*xy) for xy in linear_ring.coords])

def _project_polygon(
    polygon: Polygon, source_epsg: int, target_epsg: int
    ) -> Polygon:
    transformer = create_transformer(source_epsg, target_epsg, polygon.centroid)

    exterior_coords = [transformer.transform(*xy) for xy in polygon.exterior.coords]

    interior_coords = []
    for interior in polygon.interiors:
        interior_coords.append([transformer.transform(*xy) for xy in interior.coords])

    return Polygon(exterior_coords, interior_coords)
