
from typing import Optional, Union

import pyproj
from pyproj.aoi import AreaOfInterest
from pyproj.database import query_utm_crs_info
from shapely.geometry import (GeometryCollection, LinearRing, LineString,
                              MultiLineString, MultiPoint, MultiPolygon, Point,
                              Polygon)


def determine_utm_epsg(
        source_epsg:int,
        west_lon:float,
        south_lat:float,
        east_lon:float,
        north_lat:float) -> int:
    """ Determine the UTM EPSG code for a given source EPSG code and coordinate.

    :param source_epsg: The source EPSG code
    :param x: The x coordinate
    :param y: The y coordinate
    :return: The UTM EPSG code
    """
    utm_crs_info = query_utm_crs_info(
        datum_name= 'WGS84',
        area_of_interest=AreaOfInterest(
                west_lon, south_lat, east_lon, north_lat),
        contains=True)

    return int(utm_crs_info[0].code)

def create_transformer(
    source_epsg: int,
    target_epsg: int,
    centroid: Optional[Point] = None
    ) -> pyproj.Transformer:
    """ Create a pyproj transformer for a given source and target EPSG code.
    If a centroid is provided, the projection center will be set to the centroid.

    :param source_epsg: The source EPSG code
    :param target_epsg: The target EPSG code
    :param centroid: The centroid of the geometry to be projected
    :return: A pyproj transformer
    """
    source_crs = pyproj.CRS.from_epsg(source_epsg)
    target_crs = pyproj.CRS.from_epsg(target_epsg)

    aoi = AreaOfInterest(
        centroid.x, centroid.y, centroid.x, centroid.y) if centroid else None

    return pyproj.Transformer.from_crs(
        source_crs, target_crs, always_xy=True, area_of_interest=aoi)

def project_geometry_local_utm(
    geometry: Union[Point, LineString, Polygon, MultiLineString, MultiPolygon, MultiPoint, GeometryCollection],
    source_epsg: int = 4326
    ) -> Union[Point, LineString, Polygon, MultiLineString, MultiPolygon, GeometryCollection]:
    """
    Project any shapely geometry to the local UTM zone. For multi-part geometries, each part is
    projected separately.

    :param geometry: shapely geometry to project
    :param source_epsg: EPSG code of the source geometry

    :return: projected shapely geometry
    :raises TypeError: if the geometry type is not supported
    """
    geom_map = {
        Point: _project_point,
        LineString: _project_linestring,
        LinearRing: _project_linear_ring,
        Polygon: _project_polygon,
        MultiPoint: lambda mp, source_epsg, _: MultiPoint(
            [project_geometry_local_utm(p, source_epsg) for p in mp.geoms]),
        MultiLineString: lambda mls, source_epsg, _: MultiLineString(
            [project_geometry_local_utm(ls, source_epsg) for ls in mls.geoms]),
        MultiPolygon: lambda mp, source_epsg, _: MultiPolygon(
            [project_geometry_local_utm(p, source_epsg) for p in mp.geoms]),
        GeometryCollection: lambda gc, source_epsg, _: GeometryCollection(
            [project_geometry_local_utm(g, source_epsg) for g in gc.geoms])
    }

    if type(geometry) not in geom_map:
        raise TypeError(f"Unsupported geometry type: {type(geometry)}")

    x, y = geometry.centroid.x, geometry.centroid.y

    return geom_map[type(geometry)](
        geometry, source_epsg, determine_utm_epsg(
            source_epsg , x, y, x, y))


def _project_point(
    point: Point, source_epsg: int, target_epsg: int
    ) -> Point:
    transformer = create_transformer(source_epsg, target_epsg)
    return Point(transformer.transform(point.x, point.y))

def _project_linestring(
    linestring: LineString, source_epsg: int, target_epsg: int
    ) -> LineString:
    transformer = create_transformer(source_epsg, target_epsg)
    return LineString([transformer.transform(*xy) for xy in linestring.coords])

def _project_linear_ring(
    linear_ring: LinearRing, source_epsg: int, target_epsg: int
    ) -> LinearRing:
    transformer = create_transformer(source_epsg, target_epsg)
    return LinearRing([transformer.transform(*xy) for xy in linear_ring.coords])

def _project_polygon(
    polygon: Polygon, source_epsg: int, target_epsg: int
    ) -> Polygon:
    transformer = create_transformer(source_epsg, target_epsg)

    exterior_coords = [transformer.transform(*xy) for xy in polygon.exterior.coords]

    interior_coords = []
    for interior in polygon.interiors:
        interior_coords.append([transformer.transform(*xy) for xy in interior.coords])

    return Polygon(exterior_coords, interior_coords)


def project_polygon_equal_area(multipolygon: Union[Polygon, MultiPolygon]):
    """
    Project a Polygon or MultiPolygon object to an equal-area projection centered on the centroid.
    """
    polys = []
    if isinstance(multipolygon, Polygon):
        multipolygon = MultiPolygon([multipolygon])

    for poly in multipolygon.geoms:
        # Determine the centroid of the polygon
        centroid = poly.centroid
        lon, lat = centroid.x, centroid.y

        # Define the source CRS (WGS 84)
        source_crs = pyproj.CRS.from_epsg(4326)

        # Define the target CRS (an equal-area projection centered on the centroid)
        target_crs = pyproj.CRS.from_proj4(
            f"+proj=aea +lat_1={lat} +lat_2={lat} +lat_0={lat} +lon_0={lon}")

        # Create the projection transformation
        transformer = pyproj.Transformer.from_crs(source_crs, target_crs, always_xy=True)

        # Project the polygon to the equal-area projection
        polys.append(Polygon([transformer.transform(*xy) for xy in poly.exterior.coords]))

    # Return the projected MultiPolygon
    return MultiPolygon(polys)
