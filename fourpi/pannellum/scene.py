#!/usr/bin/env  python

from __future__ import unicode_literals, print_function
from distutils.spawn import find_executable
import PIL.Image
import logging
import math
import os
import tempfile

MAXIMUM_TILESIZE = 640
MAX_LEVELS = 6

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s - %(message)s')
console.setFormatter(formatter)
logger.addHandler(console)

NONA =find_executable('nona')

FACES = (
    (   0,  0,0, "f"), # front
    (  90,  0,0, "l"), # left
    ( -90,  0,0, "r"), # right
    (-180,  0,0, "b"), # back
    (   0,-90,0, "u"), # up
    (   0, 90,0, "d")  # down
)


if NONA:
    logger.info("nona found at %s" % NONA)
else:
    logger.error("nona required but not found.")


class Scene:

    def __init__(self, scene_id, panorama, hotspots, hfov=360):
        
        self.src = panorama
        self.scene_id = scene_id
        self.filename = os.path.split(panorama)[1]
        self.image =  PIL.Image.open(panorama)
        self.width, self.height = self.image.size
        self.hfov = hfov
        conf = {}
        conf['type'] = 'multires'
        conf['multires'] = self._multires_conf()
        conf['hotSpots'] = hotspots

        self.conf = conf
        
    
    
    def _multires_conf(self):
        
        face_width, tile_width, levels = self.levels_and_tiles()
        conf = {}
        conf['basePath'] = '../tiles/%s/' % self.scene_id 
        conf['path'] = '%l/%s%y_%x'
        conf['fallbackPath'] =  "fallback/%s"
        conf['extension'] =  "jpg"
        conf['tileResolution'] =  tile_width
        conf['maxLevel'] =  levels
        conf['cubeResolution'] = face_width
        return conf


    def levels_and_tiles(self):
        """Return the tile width and number of levels """

        raw_face_width = self.width / math.pi

        tile_fragment = math.floor(raw_face_width / (2 ** MAX_LEVELS))
        face_width = int(tile_fragment * (2 ** MAX_LEVELS))
        exp = 0
        fragments = 2 ** exp
        while (fragments * tile_fragment) < MAXIMUM_TILESIZE:
            tile_width = int(fragments * tile_fragment)
            exp = exp + 1
            fragments = 2 ** exp
        levels = int(math.log(face_width / tile_width, 2) + 1)
        logger.info("Scaling: %s" % (face_width / raw_face_width))
        return face_width, tile_width, levels

    def make_script(self, face_width):

        tmp_fd, tmp_name = tempfile.mkstemp(".txt", "nona")
        script = os.fdopen(tmp_fd, "w")
        script.write('p f0 w%s h%s n"TIFF_m" u0 v90\n' % (face_width, face_width))
        for yaw, pitch, roll, pos in FACES:
            script.write('i f4 w%s h%s y%s p%s r%s v%s n"%s"\n' % (self.width, self.height, yaw, pitch, roll, self.hfov, self.src))
        logger.info("Script created at %s" % tmp_name)
        return tmp_name

if __name__ == "__main__":
    
    pano = "/home/reimer/Desktop/laschozas-upload.jpg"
    
    scene = Scene(pano)
    print(scene.scene_id) 
    
