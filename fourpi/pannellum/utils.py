from math import radians, cos, sin, asin, sqrt
import os

AVG_EARTH_RADIUS = 6371  # in km


def haversine(point1, point2, miles=False):
    """Calculate the great-circle distance bewteen two points on the Earth surface.

    :input: two 2-tuples, containing the latitude and longitude of each point
    in decimal degrees.

    Example: haversine((45.7597, 4.8422), (48.8567, 2.3508))

    :output: Returns the distance bewteen the two points.
    The default unit is kilometers. Miles can be returned
    if the ``miles`` parameter is set to True.

    """
    # unpack latitude/longitude
    lat1, lng1 = point1
    lat2, lng2 = point2

    # convert all latitudes/longitudes from decimal degrees to radians
    lat1, lng1, lat2, lng2 = map(radians, (lat1, lng1, lat2, lng2))

    # calculate haversine
    lat = lat2 - lat1
    lng = lng2 - lng1
    d = sin(lat * 0.5) ** 2 + cos(lat1) * cos(lat2) * sin(lng * 0.5) ** 2
    h = 2 * AVG_EARTH_RADIUS * asin(sqrt(d))
    if miles:
        return h * 0.621371  # in miles
    else:
        return h  # in kilometers


def _expand(d):
    return os.path.abspath(os.path.expanduser(os.path.expandvars(d)))


def _get_or_create_path(path):
    """create a directory if it does not exist."""

    if not os.path.exists(path):
        os.makedirs(path)
    return path


def _scene_id_from_image(image):
    """create an id from the images filename"""

    scene_id = os.path.splitext(os.path.basename(image))[0]
    return scene_id.lower().replace(' ', '-')


def _pretty_distance(kilometer):
    if kilometer < 0.1:
        distance = "%3.0f m" % (kilometer * 1000)
    elif kilometer < 1:
        distance = "%3.0f m" % (kilometer * 1000)
    elif kilometer < 10:
        distance = "%3.1f km" % kilometer
    elif kilometer < 100:
        distance = "%3.0f km" % kilometer
    else:
        distance = "%5.0f km" % kilometer
    return distance.strip()


if __name__ == "__main__":

    print(_pretty_distance(1234.56))
    print(_pretty_distance(345.65))
    print(_pretty_distance(89.2345235))
    print(_pretty_distance(1.52345))
    print(_pretty_distance(0.123456))
    print(_pretty_distance(0.035623452))
