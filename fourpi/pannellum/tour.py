#!/usr/bin/env  python

from __future__ import unicode_literals, print_function
from fourpi.pannellum.scene import Scene
import json
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s - %(message)s')
console.setFormatter(formatter)
logger.addHandler(console)


class Tour:
    
    def __init__(self, author=None, panoramas=[]):

        self.conf = {}
        default = {}
        if author:
            default['author'] = author

        self.conf['default'] = default

        scenes = {}
        for panorama in panoramas:
            scene = Scene(panorama)
            scenes[scene.scene_id] = scene.conf
            
        self.conf['scenes'] = scenes

    def get_json(self):
        return json.dumps(self.conf, indent=4, separators=(',', ': '))
    