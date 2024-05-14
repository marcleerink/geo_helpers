from shapely.geometry import Polygon
from shapely.geometry.polygon import orient

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
    polygon = orient(polygon)

    print(polygon.exterior.is_ccw)  # True
    print(all(not interior.is_ccw for interior in polygon.interiors))  # True
