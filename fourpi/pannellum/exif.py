#!/usr/bin/env  python
# -*- coding: utf-8 -*-
from __future__ import  print_function
from distutils.spawn import find_executable
from utils import _scene_id_from_image
import json
import os
import subprocess
import logging

EXIFTOOL = find_executable('exiftool')

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s: %(message)s')
console.setFormatter(formatter)
logger.addHandler(console)

if EXIFTOOL:
    logger.info("exiftool found at %s" % EXIFTOOL)
else:
    logger.error("EXIFTOOL required but not found.")


class Exif:
    
    def __init__(self, panoramas=[], **kwargs):

        self.panoramas = panoramas
    
    
    def get_exifdata(self):
    
        exifdata = {}
        for panorama in self.panoramas:
            if os.path.isfile(panorama):
                exifjson = subprocess.check_output([EXIFTOOL, '-j', '-n', panorama])
                exif = json.loads(exifjson)[0]
                mapping = (
                     ('title', 'DocumentName', ''),
                     ('width', 'ImageWidth', 0),
                     ('height', 'ImageHeight', 0),
                     ('pan', 'InitialViewHeadingDegrees', 0),
                     ('tilt', 'InitialViewPitchDegrees', 0),
                     ('fov', 'InitialHorizontalFOVDegrees', 90),
                     ('lng', 'GPSLongitude', None),
                     ('lat', 'GPSLatitude', None),
                     ('northOffset', 'GPSImgDirection', 0)                     
                )
                values = {}
                for conf, tag, default in mapping:
                    values[conf] = exif.get(tag,default)             
                exifdata[_scene_id_from_image(panorama)] = values
                logger.info("EXIF data read from %s" % panorama)
            else:
                logger.error("File not found: %s" % panorama)
                
        return exifdata

if __name__ == "__main__":
    
    panos = [
        "/home/peter/Development/4pi.org/content/panos/gehry-bauten.jpg"
        #"../../panos/Gehry Bauten.jpg",
        #"../../panos/Medienhafen Hyatt.jpg",
        #"../../panos/medienhafen-bruecke.jpg"
    ]
    
    e = Exif(panoramas=panos)
    print(e.get_exifdata())
