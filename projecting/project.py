
from typing import Optional, Union

import pyproj
from pyproj.aoi import AreaOfInterest
from pyproj.database import query_utm_crs_info
from shapely.geometry import (GeometryCollection, LineString, MultiLineString,
                              MultiPolygon, Point, Polygon)


def determine_utm_epsg(lon: float, lat: float) -> int:
    """Determine the UTM epsg code for a given longitude and latitude.
    """
    utm_crs_list = query_utm_crs_info(
        datum_name="WGS 84",
        area_of_interest=AreaOfInterest(
            west_lon_degree=lon,
            south_lat_degree=lat,
            east_lon_degree=lon,
            north_lat_degree=lat,
        ),
    )
    return int(utm_crs_list[0].code)

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
    geometry: Union[Point, LineString, Polygon, MultiLineString, MultiPolygon, GeometryCollection],
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
        Point: _project_point_local_utm,
        LineString: _project_linestring_local_utm,
        Polygon: _project_polygon_local_utm,
        MultiLineString: lambda mls, source_epsg: MultiLineString(
            [_project_linestring_local_utm(ls, source_epsg) for ls in mls.geoms]),
        MultiPolygon: lambda mp, source_epsg: MultiPolygon(
            [_project_polygon_local_utm(p, source_epsg) for p in mp.geoms]),
        GeometryCollection: lambda gc, source_epsg: GeometryCollection(
            [project_geometry_local_utm(g, source_epsg) for g in gc.geoms])
    }

    if type(geometry) not in geom_map:
        raise TypeError(f"Unsupported geometry type: {type(geometry)}")

    return geom_map[type(geometry)](geometry, source_epsg)

def project_geometry_equal_area(
    geometry: Union[Point, LineString, Polygon, MultiLineString, MultiPolygon, GeometryCollection],
    source_epsg: int = 4326,
    target_epsg: int = 3035
    ) -> Union[Point, LineString, Polygon, MultiLineString, MultiPolygon, GeometryCollection]:
    """
    Project any shapely geometry to the equal area projection centered on the geometry's centroid.
    For multi-part geometries, each part is projected separately.

    :param geometry: shapely geometry to project
    :param source_epsg: EPSG code of the source geometry
    :param target_epsg: EPSG code of the target projection

    :return: projected shapely geometry
    :raises TypeError: if the geometry type is not supported
    """

    geom_map = {
        Point: _project_point_equal_area,
        LineString: _project_linestring_equal_area,
        Polygon: _project_polygon_equal_area,
        MultiLineString: lambda mls, source_epsg, target_epsg: MultiLineString(
            [_project_linestring_equal_area(ls, source_epsg, target_epsg) for ls in mls.geoms]),
        MultiPolygon: lambda mp, source_epsg, target_epsg: MultiPolygon(
            [_project_polygon_equal_area(p, source_epsg, target_epsg) for p in mp.geoms]),
        GeometryCollection: lambda gc, source_epsg, target_epsg: GeometryCollection(
            [project_geometry_equal_area(g, source_epsg, target_epsg) for g in gc.geoms])
    }

    if type(geometry) not in geom_map:
        raise TypeError(f"Unsupported geometry type: {type(geometry)}")

    return geom_map[type(geometry)](geometry, source_epsg, target_epsg)

def _project_point_equal_area(point: Point, source_epsg: int, target_epsg: int) -> Point:
    """
    Project a Point to the equal area projection centered on the Point.
    """
    lon, lat = point.x, point.y
    transformer = create_transformer(source_epsg, target_epsg)

    # Project the point to the equal area projection
    return Point(transformer.transform(lon, lat))

def _project_polygon_equal_area(polygon: Polygon, source_epsg: int, target_epsg: int) -> Polygon:
    """
    Project a Polygon to the equal area projection centered on the Polygon.
    """
    transformer = create_transformer(source_epsg, target_epsg)

    exterior_coords = [transformer.transform(*xy) for xy in polygon.exterior.coords]

    interior_coords = []
    for interior in polygon.interiors:
        interior_coords.append([transformer.transform(*xy) for xy in interior.coords])

    return Polygon(exterior_coords, interior_coords)

def _project_linestring_equal_area(linestring: LineString, source_epsg: int, target_epsg: int) -> LineString:
    """
    Project a LineString to the equal area projection centered on the LineString.
    """
    transformer = create_transformer(source_epsg, target_epsg)

    coords = [transformer.transform(*xy) for xy in linestring.coords]

    return LineString(coords)



def _project_point_local_utm(point: Point, source_epsg: int) -> Point:
    """
    Project a Point to the local UTM zone.
    """
    lon, lat = point.x, point.y
    target_epsg = determine_utm_epsg(lon, lat)

    transformer = create_transformer(source_epsg, target_epsg)

    # Project the point to the local UTM zone
    return Point(transformer.transform(lon, lat))

def _project_polygon_local_utm(polygon: Polygon, source_epsg: int) -> Polygon:
    """
    Project a Polygon to the local UTM zone.
    """
    target_epsg = determine_utm_epsg(polygon.centroid.x, polygon.centroid.y)
    transformer = create_transformer(source_epsg, target_epsg)

    exterior_coords = [transformer.transform(*xy) for xy in polygon.exterior.coords]

    interior_coords = []
    for interior in polygon.interiors:
        interior_coords.append([transformer.transform(*xy) for xy in interior.coords])

    return Polygon(exterior_coords, interior_coords)

def _project_linestring_local_utm(linestring: LineString, source_epsg: int) -> LineString:
    """
    Project a LineString to the local UTM zone.
    """
    target_epsg = determine_utm_epsg(linestring.centroid.x, linestring.centroid.y)
    transformer = create_transformer(source_epsg, target_epsg)
    return LineString([transformer.transform(*xy) for xy in linestring.coords])

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
