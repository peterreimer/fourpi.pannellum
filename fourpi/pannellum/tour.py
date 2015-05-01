#!/usr/bin/env  python
# -*- coding: utf-8 -*-
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


class  Tour:
    
    def __init__(self, author=None, panoramas=[]):

        self.conf = {}
        default = {}
        if author:
            default['author'] = author
        
        # List with all scene_ids used in this tour
        scene_ids = [self._scene_id_from_image(panorama) for panorama in panoramas]
        
        # lookup matrix for hotspots
        hotspots = dict((scene_id,0) for scene_id in scene_ids)
        hotspots = dict((scene_id,hotspots) for scene_id in scene_ids)
        for src in scene_ids:
             for dest in scene_ids:
                 hotspots[src][dest] = self._make_hotspot(src, dest)
                 print(hotspots[src][dest])
         
        locations = []
        for panorama in panoramas:
            #exif = self.read_exif(panorama)
            scene_id = self._scene_id_from_image(panorama)
            locations.append((scene_id, hotspots[scene_id], panorama))
        
        scenes = {}
        for scene_id, hotspots, panorama in locations:
            scene = Scene(scene_id, panorama, hotspots)
            scenes[scene.scene_id] = scene.conf
        
        default['firstScene'] = scenes.keys()[0]
        self.conf['default'] = default
        self.conf['scenes'] = scenes
    
    def _make_hotspot(self, src, dest):
        return "%s to %s" % (src, dest)

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
            logger.error("File not found: %s" % panorama)
            return None

    def get_json(self):
        return json.dumps(self.conf, indent=4, separators=(',', ': '))
    
if __name__ == "__main__":
    
    panos = [
        "../../panos/gehry-bauten.jpg",
        "../../panos/medienhafen-hyatt.jpg",
        "../../panos/medienhafen-bruecke.jpg"
    ]
    
    #panos = [
    #   "/home/reimer/Desktop/laschozas-upload.jpg",
    #   "/home/reimer/Desktop/mafra-photosphere.jpg"
    #]
    tour = Tour(author="Peter Reimer", panoramas=panos)
    print(tour.get_json()) 
