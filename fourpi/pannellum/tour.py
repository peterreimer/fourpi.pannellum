#!/usr/bin/env  python

from __future__ import unicode_literals, print_function
from distutils.spawn import find_executable
from fourpi.pannellum.scene import Scene
import json
import os
import subprocess
import logging

EXIFTOOL = find_executable('exiftool')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s - %(message)s')
console.setFormatter(formatter)
logger.addHandler(console)

if EXIFTOOL:
    logger.info("exiftool found at %s" % EXIFTOOL)
else:
    logger.error("EXIFTOOL required but not found.")


class Tour:
    
    def __init__(self, author=None, panoramas=[]):

        self.conf = {}
        default = {}
        if author:
            default['author'] = author

        hotspots = {}
        # Matrix = [[0 for x in range(5)] for x in range(5)]  
        scene_ids = [self._scene_id_from_image(panorama) for panorama in panoramas]
        hotspots = [[None for x in scene_ids] for x in scene_ids]
        
        logger.info(hotspots) 
        locations = []
        for panorama in panoramas:
            exif = self.read_exif(panorama)
            scene_id = self._scene_id_from_image(panorama)
            hotspots = "heise Flecken"
            locations.append((scene_id, hotspots, panorama))
            logger.info(exif)  
        
        scenes = {}
        for scene_id, hotspots, panorama in locations:
            scene = Scene(scene_id, panorama, hotspots)
            scenes[scene.scene_id] = scene.conf
        
        default['firstScene'] = scenes.keys()[0]
        self.conf['default'] = default
        self.conf['scenes'] = scenes

    def _scene_id_from_image(self, panorama):
        scene_id = os.path.splitext(os.path.basename(panorama))[0]
        return scene_id

    def read_exif(self, panorama):
        
        if os.path.isfile(panorama):
            exifjson = subprocess.check_output([EXIFTOOL, '-j', '-n', panorama])
            exif = json.loads(exifjson)[0]
            mapping = (
                 ('title', 'DocumentName', ''),
                 ('direction', 'PoseHeadingDegrees', 0),
                 ('pan', 'InitialViewHeadingDegrees', 0),
                 ('tilt', 'InitialViewPitchDegrees', 0),
                 ('fov', 'InitialHorizontalFOVDegrees', 90),
                 ('lng', 'GPSLongitude', None),
                 ('lat', 'GPSLatitude', None)
            )
            values = {}
            for conf, tag, default in mapping:
                values[conf] = exif.get(tag,default)             
            return values
        else:
            logger.error("File not found: %s" % image)
            return None

    def get_json(self):
        return json.dumps(self.conf, indent=4, separators=(',', ': '))
    
