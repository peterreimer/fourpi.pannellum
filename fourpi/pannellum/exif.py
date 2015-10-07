#!/usr/bin/env  python
# -*- coding: utf-8 -*-
"""Parse panorama specific exif metadata.
"""
from __future__ import  print_function
from distutils.spawn import find_executable
import argparse
import datetime
import json
import os
import subprocess
import logging

from fourpi.pannellum.utils import _scene_id_from_image

EXIFTOOL = find_executable('exiftool')

logger = logging.getLogger('pannellum.exif')

if EXIFTOOL:
    logger.info("exiftool found at %s" % EXIFTOOL)
else:
    logger.error("EXIFTOOL required but not found.")

mapping = (
    ('title', 'DocumentName', ''),
    ('width', 'ImageWidth', 0),
    ('height', 'ImageHeight', 0),
    ('taken', 'DateTimeOriginal', None),
    ('comment', 'UserComment', ''),
    ('make', 'Make', None),
    ('model', 'Model', None),
    ('lens', 'LensModel', None),
    ('exposure', 'ExposureTime', None),
    ('fnumber', 'FNumber', None),
    ('focallength', 'FocalLength', None),
    ('pan', 'InitialViewHeadingDegrees', 0),
    ('tilt', 'InitialViewPitchDegrees', 0),
    ('fov', 'InitialHorizontalFOVDegrees', 90),
    ('count', 'SourcePhotosCount', 1),
    ('lng', 'GPSLongitude', None),
    ('lat', 'GPSLatitude', None),
    ('northOffset', 'GPSImgDirection', 0)
)

class Exif:

    def __init__(self, panoramas=[], **kwargs):

        self.panoramas = panoramas

    def get_exifdata(self):

        exifdata = {}
        for panorama in self.panoramas:
            if os.path.isfile(panorama):
                exifjson = subprocess.check_output([EXIFTOOL, '-j', '-n', panorama])
                exif = json.loads(exifjson)[0]
                values = {}
                for conf, tag, default in mapping:
                    value = exif.get(tag, default)
                    if conf == 'taken':
                        if value:
                            value = datetime.datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                    # only comment can contain linebreaks
                    if conf == 'comment':
                        value = value.split('\n')
                    if conf == 'exposure' and value:
                        value = int(1 / value)
                    values[conf] = value
                    
                exifdata[_scene_id_from_image(panorama)] = values
                logger.info("EXIF data read from %s" % panorama)
            else:
                logger.error("File not found: %s" % panorama)

        return exifdata

def now():
    return datetime.datetime.now().strftime('%Y-%m-%d')

def main():

    parser = argparse.ArgumentParser(description='Create pelican rst file from exif')
    parser.add_argument('panorama', metavar='INPUT', help='Panoramic image')

    args = parser.parse_args()

    e = Exif([args.panorama])
    scene_id = _scene_id_from_image(args.panorama)  
    fmt = "%-12s: %s"
    
    rst = """%(title)s
%(underline)s

:date:     %(date)s
:category: Panoramas
:tags: 
:template: panorama
:scene_id: %(scene_id)s
"""
    
    exifs = Exif([args.panorama]).get_exifdata()
    exif = exifs.get(scene_id, None)
    if exif['title'] == '':
        exif['title'] = scene_id
        logger.warn('No title found, using scene_id')
    exif['underline'] = '=' * len(exif['title'])
    exif['scene_id'] = scene_id
    exif['date'] = now()
    print(rst % exif)
    for k, v in exif.iteritems():
        print(fmt % (k, v))
    


if __name__ == "__main__":
    
    panos = [
        "/home/peter/Development/4pi.org/content/panos/gehry-bauten.jpg"
        #"../../panos/Gehry Bauten.jpg",
        #"../../panos/Medienhafen Hyatt.jpg",
        #"../../panos/medienhafen-bruecke.jpg"
    ]
    
    e = Exif(panoramas=panos)
    exif = e.get_exifdata() 
    print(exif['gehry-bauten'])
