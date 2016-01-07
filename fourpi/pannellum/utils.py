import os

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
    return scene_id.lower().replace(' ','-')

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

    print _pretty_distance(1234.56)
    print _pretty_distance(345.65)
    print _pretty_distance(89.2345235)
    print _pretty_distance(1.52345)
    print _pretty_distance(0.123456)
    print _pretty_distance(0.035623452)