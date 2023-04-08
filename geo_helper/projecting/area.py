from shapely.geometry.base import BaseGeometry

from .reproject import reproject_geometry, reproject_geometry_local_utm


def calculate_area_geometry(
    geometry: BaseGeometry,
    source_epsg: int = 4326,
    target_epsg: int = 9822,
    ) -> float:
    """
    Calculate the area of a shapely geometry in square kilometers.

    :param geometry: shapely geometry to calculate the area of
    :param source_epsg: EPSG code of the source geometry.
        Default is WGS84 (4326)
    :param target_epsg: EPSG code of the target geometry.
        Defaults is Lambert Conformal Conic (9822)

    :return: area in square kilometers
    :raises TypeError: if the geometry type is not supported
    """
    projected_geom = reproject_geometry(geometry, source_epsg, target_epsg)
    return projected_geom.area / 1e6

def calculate_area_geometry_local_utm(
    geometry: BaseGeometry,
    source_epsg: int = 4326,
    ) -> float:
    """
    Calculate the area of a shapely geometry in square kilometers.

    :param geometry: shapely geometry to calculate the area of
    :param source_epsg: EPSG code of the source geometry.
        Default is WGS84 (4326)

    :return: area in square kilometers
    :raises TypeError: if the geometry type is not supported
    """
    projected_geom = reproject_geometry_local_utm(geometry, source_epsg)
    return projected_geom.area / 1e6
