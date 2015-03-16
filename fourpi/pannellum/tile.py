#!/usr/bin/env  python

from __future__ import unicode_literals, print_function
import math

MAXIMUM_TILESIZE = 640
MAX_LEVELS = 6

class Pannellum:

    def levels_and_tiles(self, pano_width):
        """Return the tile width and number of levels """

        raw_face_width = pano_width / math.pi

        tile_fragment = math.floor(raw_face_width / (2 ** MAX_LEVELS))
        face_width = int(tile_fragment * (2 ** MAX_LEVELS))
        exp = 0
        fragments = 2 ** exp
        while (fragments * tile_fragment) < MAXIMUM_TILESIZE:
            tile_width = int(fragments * tile_fragment)
            exp = exp + 1
            fragments = 2 ** exp
            #print(exp, fragments, tile_width)
        levels = int(math.log(face_width / tile_width, 2) + 1)
        return face_width, tile_width, levels


if __name__ == "__main__":

    p = Pannellum()

    for pano_width in range(5000, 36000, 1000):
        face, tile, levels = p.levels_and_tiles(pano_width)
        print(pano_width, levels, face, tile, face / (pano_width/math.pi))
