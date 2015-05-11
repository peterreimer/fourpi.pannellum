#!/usr/bin/env  python

from __future__ import print_function
from distutils.spawn import find_executable
import PIL.Image
import logging
import math
import subprocess
import os
import tempfile
from hotspot import HotSpot
from utils import _expand, _scene_id_from_image, _get_or_create_path

MAXIMUM_TILESIZE = 640
MAXIMUM_LEVELS = 6

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

RESIZE_FILTERS = {
    'cubic': PIL.Image.CUBIC,
    'bilinear': PIL.Image.BILINEAR,
    'bicubic': PIL.Image.BICUBIC,
    'nearest': PIL.Image.NEAREST,
    'antialias': PIL.Image.ANTIALIAS,
    }


if NONA:
    logger.info("nona found at %s" % NONA)
else:
    logger.error("nona required but not found.")


class Scene:

    def __init__(self, panorama, exifdata={}, hfov=360):
        
        self.src = panorama
        self.scene_id = _scene_id_from_image(panorama)
        self.hfov = hfov
        self.filename = os.path.split(panorama)[1]
        self.image =  PIL.Image.open(panorama)
        self.width, self.height = self.image.size
        
        self.cubeResolution, self.tileResolution, self.maxLevel = self._levels_and_tiles()
        self.exif = exifdata.get(self.scene_id, {})
        self.title = self.exif.get('title', 'n/a')
        self.northOffset = self.exif.get('northOffset', 0)
        conf = {}
        conf['type'] = 'multires'
        conf['northOffset'] = self.northOffset
        conf['title'] = self.title
        conf['compass'] = True
        
        conf['multiRes'] = self._multires_conf()
        hotspots = []
        for dest_scene_id in exifdata.keys():
            src_scene_id = self.scene_id
            if src_scene_id != dest_scene_id:
                hs = HotSpot(dest_scene_id, exifdata[src_scene_id], exifdata[dest_scene_id])
                hotspots.append(hs.get_conf())            
        conf['hotSpots'] = hotspots

        self.conf = conf
        
    
    
    def _multires_conf(self):
        
        conf = {}
        conf['basePath'] = '../tiles/%s' % self.scene_id 
        conf['path'] = '/%l/%s%y_%x'
        conf['fallbackPath'] =  "/fallback/%s"
        conf['extension'] =  "jpg"
        conf['tileResolution'] =  self.tileResolution
        conf['maxLevel'] =  self.maxLevel
        conf['cubeResolution'] = self.cubeResolution
        return conf


    def _levels_and_tiles(self):
        """Return the tile width and number of levels """

        raw_face_width = self.width / math.pi

        tile_fragment = math.floor(raw_face_width / (2 ** MAXIMUM_LEVELS))
        cubeResolution = int(tile_fragment * (2 ** MAXIMUM_LEVELS))
        exp = 0
        fragments = 2 ** exp
        while (fragments * tile_fragment) < MAXIMUM_TILESIZE:
            tileResolution = int(fragments * tile_fragment)
            exp = exp + 1
            fragments = 2 ** exp
        maxLevel = int(math.log(cubeResolution / tileResolution, 2) + 1)
        logger.info("Scaling: %s" % (cubeResolution / raw_face_width))
        return cubeResolution, tileResolution, maxLevel

    def _make_script(self):

        tmp_fd, tmp_name = tempfile.mkstemp(".txt", "nona")
        script = os.fdopen(tmp_fd, "w")
        script.write('p f0 w%s h%s n"TIFF_m" u0 v90\n' % (self.cubeResolution,self.cubeResolution))
        for yaw, pitch, roll, pos in FACES:
            script.write('i f4 w%s h%s y%s p%s r%s v%s n"%s"\n' % (self.width, self.height, yaw, pitch, roll, self.hfov, _expand(self.src)))
        logger.info("Script created at %s" % tmp_name)
        return tmp_name
    
    def extract(self):
        """extract all six cubic faces from the panorama"""
        
        dest = _expand(os.path.dirname(self.src))
        self.output_dir = _get_or_create_path(os.path.join(dest, self.scene_id))
        output = os.path.join(self.output_dir, self.scene_id)
        script = self._make_script()
        args = (NONA, '-o', output, script)
        #nona = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #nona.communicate()
        os.remove(script)
        faces = [os.path.join(self.output_dir, "%s%04d.tif" % (self.scene_id, + i)) for i in range(5)] 
        return faces

    def tile(self):
        for face in self.extract():
            for level in range(self.maxLevel, 0, -1):
                #print(level)
                _get_or_create_path(os.path.join(self.output_dir, str(level)))
                
            


if __name__ == "__main__":
    
    #pano = "../../panos/Medienhafen Bruecke.jpg"
    pano = "../../panos/Gehry Bauten.jpg"
    scene = Scene(pano)
    print(scene.scene_id)
    #print(scene.extract())
    print(scene.tile())
