from shapely.geometry import Polygon


def force_polygon_ccw(polygon: Polygon) -> Polygon:
    """Force a polygon to be counter-clockwise
    according to the right-hand rule."""
    if polygon.exterior.is_ccw:
        return polygon
    else:
        exterior_coords = list(polygon.exterior.coords)[::-1]
        interior_coords = [
            list(interior.coords)[::-1] for interior in polygon.interiors
        ]
        return Polygon(exterior_coords, interior_coords)
