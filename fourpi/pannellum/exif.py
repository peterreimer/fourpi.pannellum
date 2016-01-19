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
    ('title', 'DocumentName', '', 'string'),
    ('width', 'ImageWidth', 0, 'int'),
    ('height', 'ImageHeight', 0, 'int'),
    ('taken', 'DateTimeOriginal', None, 'date'),
    ('comment', 'UserComment', None, 'lines'),
    ('make', 'Make', None, 'string'),
    ('model', 'Model', None, 'string'),
    ('lens', 'LensModel', None, 'string'),
    ('exposure', 'ExposureTime', None, 'float'),
    ('fnumber', 'FNumber', None, 'float'),
    ('iso', 'ISO', None, 'int'),
    ('focallength', 'FocalLength', None, ''),
    ('pan', 'InitialViewHeadingDegrees', 0, 'float'),
    ('tilt', 'InitialViewPitchDegrees', 0, 'float'),
    ('fov', 'InitialHorizontalFOVDegrees', 90, 'float'),
    ('count', 'SourcePhotosCount', 1, 'int'),
    ('lng', 'GPSLongitude', None, 'float'),
    ('lat', 'GPSLatitude', None, 'float'),
    ('northOffset', 'GPSImgDirection', 0, 'float')
)

class Exif:

    def __init__(self, panoramas=[], **kwargs):

        self.panoramas = panoramas

    def get_exifdata(self):

        exifdata = {}
        for panorama in self.panoramas:
            scene_id = _scene_id_from_image(panorama)
            if not os.path.isfile(panorama):
                logger.error("File not found: %s", panorama)
                break
            exifjson = subprocess.check_output([EXIFTOOL, '-j', '-n', panorama])
            exif = json.loads(exifjson)[0]
            values = {}
            for conf, tag, default, type in mapping:
                if not exif.has_key(tag):
                    value = default
                    logger.warn("%s: missing %s (default=%s)", scene_id, tag, default)
                else:
                    value = exif[tag]
                    logger.info("%s: %s", tag, value)
                if value and type == 'date':
                    value = datetime.datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
                if type == 'lines' and value:
                    value = value.split('\n')
                if conf == 'exposure' and value:
                    value = int(1 / value)
                values[conf] = value

            print(values['lat'],values['lng'])
            if values['lat'] and values['lng']:
                values['latlng'] = (values['lat'], values['lng'])
                

            exifdata[scene_id] = values
            logger.info("EXIF data read from %s", panorama)

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

    logger.setLevel(logging.WARN)
    console = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)

    panos = [
        "../../tests/panos/referenz.jpg"
    ]

    e = Exif(panoramas=panos)
    exif = e.get_exifdata() 
    # print(exif['gehry-bauten'])
    print(exif)
    
