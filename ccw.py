from shapely.geometry import Polygon


def _force_exterior_ccw(polygon: Polygon) -> Polygon:
    if polygon.exterior.is_ccw:
        return polygon
    else:
        return Polygon(polygon.exterior.coords[::-1], polygon.interiors)


def _force_interior_cw(polygon: Polygon) -> Polygon:
    if all(not interior.is_ccw for interior in polygon.interiors):
        return polygon
    else:
        return Polygon(
            polygon.exterior.coords,
            [interior.coords[::-1] for interior in polygon.interiors],
        )


def force_polygon_ccw(polygon: Polygon) -> Polygon:
    """Build a new polygon with the same coordinates but with the exterior
    ring in counter-clockwise order and all interior rings in clockwise order.
    See: https://postgis.net/docs/ST_ForcePolygonCCW.html"""
    return _force_interior_cw(_force_exterior_ccw(polygon))


if __name__ == "__main__":
    # create a polygon with exterior ring in counter-clockwise order and
    # interior ring in clockwise order
    polygon = Polygon(
        [
            (0, 0),
            (0, 1),
            (1, 1),
            (1, 0),
            (0, 0),
        ],
        [
            [(0.25, 0.25), (0.75, 0.25), (0.75, 0.75), (0.25, 0.75), (0.25, 0.25)],
        ],
    )
    print(polygon.exterior.is_ccw)  # False
    print(all(not interior.is_ccw for interior in polygon.interiors))  # False

    # force exterior ring to be counter-clockwise and interior ring to be
    # clockwise
    polygon = force_polygon_ccw(polygon)

    print(polygon.exterior.is_ccw)  # True
    print(all(not interior.is_ccw for interior in polygon.interiors))  # True
