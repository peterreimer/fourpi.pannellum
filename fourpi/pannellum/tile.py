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

EXIFTOOL = find_executable('exiftool')

FACES = (
    (   0,  0,0, "f"), # front
    (  90,  0,0, "l"), # left
    ( -90,  0,0, "r"), # right
    (-180,  0,0, "b"), # back
    (   0,-90,0, "u"), # up
    (   0, 90,0, "d")  # down
)

if EXIFTOOL:
    logger.info("exiftool found at %s" % EXIFTOOL)
else:
    logger.error("EXIFTOOL required but not found.")

class Pannellum:

    def __init__(self, src, hfov=360):
        
        self.image =  PIL.Image.open(src)
        self.src = src
        self.filename = os.path.split(self.src)[1]
        self.hfov = hfov
        self.width, self.height = self.image.size
        logger.info("panorama width: %s" % (self.width))

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
            script.write('i f4 w%s h%s y%s p%s r%s n"%s"\n' % (self.width, self.height, yaw, pitch, roll, self.src))
        return tmp_name

if __name__ == "__main__":
    
    pano = "/home/reimer/ownCloud/Panoramen/burgfried.jpg"
    p = Pannellum(pano)
    face, tile, levels = p.levels_and_tiles()
    print(levels, face, tile)
    print(p.make_script(face))

    #for pano_width in (3600, 5400, 8000, 11500):#range(5000, 16000, 1000):
    #    face, tile, levels = p.levels_and_tiles(pano_width)
    #    print(pano_width, levels, face, tile, face / (pano_width/math.pi))
