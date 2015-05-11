import os

def _expand(d):
    return os.path.abspath(os.path.expanduser(os.path.expandvars(d)))

def _get_or_create_path(path):
    """create a directory if it does not exist."""

    if not os.path.exists(path):
        os.makedirs(path)
    return path

def _scene_id_from_image(image):
    scene_id = os.path.splitext(os.path.basename(image))[0]
    return scene_id.lower().replace(' ','-')
