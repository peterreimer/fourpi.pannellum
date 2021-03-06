#!/usr/bin/env  python
# -*- coding: utf-8 -*-

import configparser
import json
import os
import logging
import argparse
from fourpi.pannellum.scene import Scene
from fourpi.pannellum.exif import Exif
from fourpi.pannellum.scene import DEFAULT_IMAGE_FORMAT, DEFAULT_IMAGE_QUALITY, DEFAULT_RESIZE_FILTER

logger = logging.getLogger('pannellum')


class Tour:

    def __init__(self, exifdata, panoramas=[], **kwargs):

        # self.read_configuration()
        self.panoramas = panoramas
        self.debug = kwargs.get('debug', False)
        tile_folder = kwargs.get('tile_folder', None)
        basePath = kwargs.get('basePath', None)

        self.conf = {}
        default = {}
        author = kwargs.get('author', None)
        autoRotate = kwargs.get('autoRotate', 0)
        sceneFadeDuration = kwargs.get('sceneFadeDuration', 0)

        scenes_conf = {}
        self.scenes = []
        for panorama in panoramas:
            scene = Scene(panorama,
                          exifdata=exifdata,
                          image_quality=0.9,
                          autoRotate=autoRotate,
                          basePath=basePath,
                          tile_folder=tile_folder)
            self.scenes.append(scene)
            scenes_conf[scene.scene_id] = scene.conf

        firstScene = kwargs.get('firstScene', list(scenes_conf.keys())[0])
        default['firstScene'] = firstScene
        default['autoLoad'] = True
        if author:
            default['author'] = author
        if self.debug:
            default['hotSpotDebug'] = True
        if sceneFadeDuration:
            default['sceneFadeDuration'] = sceneFadeDuration

        self.conf['default'] = default
        self.conf['scenes'] = scenes_conf

    def read_configuration(self):
        cwd = os.getcwd()
        config_file = "pannellumrc"
        cfg = [os.path.join(cwd, config_file), os.path.expanduser('~/.pannellumrc')]
        config = configparser.ConfigParser()
        config.read(cfg)
        author = config.get('default', 'author')
        print(author)
        header = config.get('default', 'header')

    def get_json(self):
        if self.debug:
            return json.dumps(self.conf, sort_keys=True, indent=4, separators=(', ', ': '))
        else:
            return json.dumps(self.conf, sort_keys=False, indent=None, separators=(',', ':'))


def main():

    parser = argparse.ArgumentParser(description='Pannellum configurator')
    parser.add_argument('panoramas', nargs='+', metavar='INPUT', help='Panoramic image(s)')

    parser.add_argument("-a", "--author", help="The Creator of this tour.")
    parser.add_argument("-d", "--debug", action="store_true", help="Turn on debug mode.")
    parser.add_argument("-v", "--verbose", action="store_true", help="be verbose")
    parser.add_argument("-t", "--tile", action="store_true", help="Remap and tile the panorama.")
    parser.add_argument("-p", "--projection", default='equirectangular',
                        help='Projection type. Can be equirectangular, cubemap, or multires. Default: equirectangular')
    parser.add_argument("-f", "--force", action="store_true", help="force recreation of tiles, even if they already exist.")
    parser.add_argument('-o', '--tile_folder', help='Tile folder', default='')
    parser.add_argument('-q', '--image_quality', type=float,
                        default=DEFAULT_IMAGE_QUALITY, help='Quality of the image output (0-1). Default: 0.8')
    parser.add_argument('--tile_format',
                        default=DEFAULT_IMAGE_FORMAT, help='Image format of the tiles (jpg or png). Default: jpg')
    parser.add_argument('--resize_filter', default=DEFAULT_RESIZE_FILTER,
                        help='Type of filter for resizing (bicubic, nearest, bilinear, antialias (best). Default: antialias')

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.WARN)
    console = logging.StreamHandler()
    logger.addHandler(console)

    e = Exif(args.panoramas)
    exifdata = e.get_exifdata()

    tour = Tour(author=args.author,
                debug=args.debug,
                tile_folder=args.tile_folder,
                exifdata=exifdata,
                panoramas=args.panoramas)

    if args.tile:
        for scene in tour.scenes:
            scene.tile(force=args.force)
            scene.fallback(force=args.force)

    print(tour.get_json())


if __name__ == "__main__":

    panos = [
        "../../tests/panos/pano1.jpg",
        "../../tests/panos/pano2.jpg"
        # "../../panos/medienhafen-bruecke.jpg"
    ]

    e = Exif(panos)
    exifdata = e.get_exifdata()

    tour = Tour(author="Peter Reimer",
                debug=True,
                autoRotate=10,
                tile_folder='tiles',
                basePath='../tiles',
                sceneFadeDuration=1500,
                exifdata=exifdata,
                panoramas=panos)

    for scene in tour.scenes:
        scene.tile(force=True)
    print(tour.get_json())
