#!/usr/bin/env  python
# -*- coding: utf-8 -*-
from __future__ import  print_function
from distutils.spawn import find_executable
from scene import Scene
from scene import DEFAULT_IMAGE_FORMAT, DEFAULT_IMAGE_QUALITY, DEFAULT_RESIZE_FILTER
from utils import _scene_id_from_image
import json
import os
import subprocess
import logging
import argparse


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
    
    def __init__(self, author=None, debug=False, panoramas=[]):
        
        self.panoramas = panoramas
        self.debug = debug
        self.conf = {}
        default = {}
        if author:
            default['author'] = author
        
        # read all exifdats from the images
        self.exifdata = self.get_exifdata()
        
        scenes = {}
        for panorama in panoramas:
            scene = Scene(panorama, exifdata=self.exifdata, image_quality=0.9)
            scenes[scene.scene_id] = scene.conf
        
        default['firstScene'] = scenes.keys()[0]
        default['autoLoad'] = True
        if debug:
            default['hotSpotDebug'] = True
        self.conf['default'] = default
        self.conf['scenes'] = scenes
        
    
    def _make_hotspot(self, src, dest):
        
        return "%s to %s" % (src, dest)


    def get_exifdata(self):
        
        exifdata = {}
        for panorama in self.panoramas:
            if os.path.isfile(panorama):
                exifjson = subprocess.check_output([EXIFTOOL, '-j', '-n', panorama])
                exif = json.loads(exifjson)[0]
                mapping = (
                     ('title', 'DocumentName', ''),
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

    def get_json(self):
        if self.debug:
            return json.dumps(self.conf, indent=4, separators=(',', ': '))
        else:
            return json.dumps(self.conf,)
    

def main():
    
    parser = argparse.ArgumentParser(description='Pannellum configurator')
    parser.add_argument('panoramas', nargs='+', help='Panoramic image')

    parser.add_argument("-a", "--author", help="The Creator of this tour.")
    parser.add_argument("-d", "--debug", action="store_true", help="Turn on debug mode.")
    parser.add_argument("-v", "--verbose", action="store_true", help="be verbose")
    parser.add_argument('-f', '--tile_format',
                      default=DEFAULT_IMAGE_FORMAT, help='Image format of the tiles (jpg or png). Default: jpg')
    parser.add_argument('-q', '--image_quality', type=float,
                      default=DEFAULT_IMAGE_QUALITY, help='Quality of the image output (0-1). Default: 0.8')
    parser.add_argument('-r', '--resize_filter', default=DEFAULT_RESIZE_FILTER,
                      help='Type of filter for resizing (bicubic, nearest, bilinear, antialias (best). Default: antialias')

    args = parser.parse_args()
    debug = args.debug
    panoramas = args.panoramas
    tour = Tour(author=args.author, debug=debug, panoramas=panoramas)
    print(tour.get_json()) 
    
    print(args)


if __name__ == "__main__":
    
    panos = [
        "../../panos/Gehry Bauten.jpg",
        "../../panos/Medienhafen Hyatt.jpg",
        "../../panos/medienhafen-bruecke.jpg"
    ]
    
    tour = Tour(author="Peter Reimer", debug=True, panoramas=panos)
    print(tour.get_json()) 

