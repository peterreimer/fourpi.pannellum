#!/usr/bin/env  python

from __future__ import print_function
from distutils.spawn import find_executable
import logging
import math
import subprocess
import os
import json
import tempfile

import PIL.Image

from fourpi.pannellum.hotspot import HotSpot
from fourpi.pannellum.exif import Exif
from fourpi.pannellum.utils import _expand, _scene_id_from_image, _get_or_create_path

MAXIMUM_TILESIZE = 640
MAXIMUM_LEVELS = 6
EXTENSION = "jpg"

FACES = ["f", "b", "l", "r", "u", "d"]
ANGLES = [(0, 0), (-180, 0), (90, 0), (-90, 0), (0, -90), (0, 90)]

RESIZE_FILTERS = {
    'cubic': PIL.Image.CUBIC,
    'bilinear': PIL.Image.BILINEAR,
    'bicubic': PIL.Image.BICUBIC,
    'nearest': PIL.Image.NEAREST,
    'antialias': PIL.Image.ANTIALIAS,
    }

DEFAULT_RESIZE_FILTER = PIL.Image.ANTIALIAS
DEFAULT_IMAGE_FORMAT = 'jpg'
DEFAULT_IMAGE_QUALITY = 0.8

logger = logging.getLogger('pannellum.scene')

NONA = find_executable('nona')

if not NONA:
    logger.error("nona required but not found.")


class Scene:

    def __init__(self, panorama, exifdata={}, **kwargs):
        
        conf = {}
        self.src = panorama
        self.exifdata = exifdata
        self.scene_id = _scene_id_from_image(panorama)
        dest = _expand(os.path.dirname(self.src))
        self.output_dir = os.path.join(dest, self.scene_id)
        image_quality = kwargs.get('image_quality', DEFAULT_IMAGE_QUALITY)
        self.image_quality = int(image_quality * 100)
        autoRotate = kwargs.get('autoRotate', None)
        if autoRotate:
            conf['autoRotate'] = autoRotate
        basePath = kwargs.get('basePath', None)
        if basePath:
            self.basePath = '/'.join((basePath, self.scene_id))
        else:
            self.basePath = None
        #    self.basePath = self.scene_id
        self.hfov = kwargs.get('hfov', 360)
        self.tile_size = kwargs.get('tile_size', None)
        tile_folder = kwargs.get('tile_folder', '')
        self.tile_folder = os.path.join(tile_folder, self.scene_id)
        self.filename = os.path.split(panorama)[1]
        self.exif = self.exifdata.get(self.scene_id, {})
        self.width = self.exif.get('width', 0)
        self.height = self.exif.get('height', 0)
        self.title = self.exif.get('title', 'n/a')
        self.northOffset = self.exif.get('northOffset', 0)
        self._levels_and_tiles(self.tile_size)

        conf['type'] = 'multires'
        conf['northOffset'] = self.northOffset
        conf['title'] = self.title
        conf['compass'] = True
        minPitch, maxPitch = self._pitch()
        conf['maxPitch'] = maxPitch
        conf['minPitch'] = minPitch
        
        conf['multiRes'] = self._multires_conf()
        hotspots = []
        for dest_scene_id in self.exifdata.keys():
            src_scene_id = self.scene_id
            if src_scene_id != dest_scene_id:
                hs = HotSpot(dest_scene_id, self.exifdata[src_scene_id], self.exifdata[dest_scene_id])
                hotspots.append(hs.get_conf())            
        conf['hotSpots'] = hotspots
        self.conf = conf

    def _multires_conf(self):

        conf = {}
        conf['basePath'] = self.basePath 
        conf['path'] = '/%l/%s%y_%x'
        conf['fallbackPath'] = "/fallback/%s"
        conf['extension'] = EXTENSION
        conf['tileResolution'] = self.tileResolution
        conf['maxLevel'] = self.maxLevel
        conf['cubeResolution'] = self.cubeResolution
        return conf

    def get_json(self):
        return json.dumps(self.conf, sort_keys=True, indent=4, separators=(', ', ': '))

    def _pitch(self):
        """return pitch values for symmetrical eq Panoramas"""
        vfov = float(self.height) / float(self.width) * float(self.hfov)
        min = - 0.5 * vfov
        max = + 0.5 * vfov
        return min, max

    def _levels_and_tiles(self, tile_size):
        """Return the tile width and number of levels """
        raw_face_width = self.width / math.pi
        if tile_size:
            self.tileResolution = tile_size
            self.cubeResolution =int(raw_face_width)
        else:
            tile_fragment = math.floor(raw_face_width / (2 ** MAXIMUM_LEVELS))
            self.cubeResolution = int(tile_fragment * (2 ** MAXIMUM_LEVELS))
            exp = 0
            fragments = 2 ** exp
            logger.info("width %d" % self.width)
            while (fragments * tile_fragment) < MAXIMUM_TILESIZE:
                self.tileResolution = int(fragments * tile_fragment)
                exp = exp + 1
                fragments = 2 ** exp
        self.maxLevel = int(math.log(self.cubeResolution / self.tileResolution, 2) + 1)
        scale = self.cubeResolution / raw_face_width
        logger.info("Scaling: %s, Tile: %s, Face: %s " % (scale, self.tileResolution, self.cubeResolution) )
        return scale

    def _make_script(self):

        tmp_fd, tmp_name = tempfile.mkstemp(".txt", "nona")
        script = os.fdopen(tmp_fd, "w")
        script.write('p f0 w%s h%s n"TIFF_m" u0 v90\n' % (self.cubeResolution,self.cubeResolution))
        for yaw, pitch in ANGLES:
            script.write('i f4 w%s h%s y%s p%s r0 v%s n"%s"\n' % (self.width, self.height, yaw, pitch, self.hfov, _expand(self.src)))
        logger.info("Script created at %s" % tmp_name)
        return tmp_name
    
    def extract(self):
        """extract all six cubic faces from the panorama"""
        
        output = os.path.join(self.output_dir, self.scene_id)
        _get_or_create_path(output)
        script = self._make_script()
        args = (NONA, '-v', '-o', output, script)
        nona = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        nona.communicate()
        faces = [os.path.join(self.output_dir, "%s%04d.tif" % (self.scene_id, + i)) for i in range(6)] 
        self.faces = zip(FACES, faces)

    def tile(self, force=False):
        """check existing output """
        levels = self.maxLevel
        tile_size = self.tileResolution
        exists = os.path.isdir(self.tile_folder)
        if not exists or force:
            #_get_or_create_path(self.tile_folder)# os.makedirs(self.output_dir)
            self.extract()
            for f, image in self.faces:
                if not os.path.isfile(image):
                    logger.info(" face %s not found" % f)
                else:
                    logger.info("tiling face %s" % f)
                    size = self.cubeResolution
                    face = PIL.Image.open(image)
                    for level in range(levels, 0, -1):
                        level_dir = _get_or_create_path(os.path.join(self.tile_folder, str(level)))
                        tiles = int(math.ceil(size / tile_size))
                        if (level < levels):
                            face = face.resize([size, size], PIL.Image.ANTIALIAS)
                        for i in range(0, tiles):
                            for j in range(0, tiles):
                                left = j * tile_size
                                upper = i * tile_size
                                right = min(j * tile_size + tile_size, size)
                                lower = min(i * tile_size + tile_size, size)
                                tile = face.crop([left, upper, right, lower])
                                tile.load()
                                tile.save(os.path.join(level_dir, "%s%s_%s.%s" % (f, i, j, EXTENSION)), 'JPEG', quality=self.image_quality)
                        size = int(size / 2)
        else:
            logger.info("Skipping extraction and tile creation, %s exists" % self.tile_folder)

    def fallback(self, force=False):
        
        for f, image in self.faces:
            logger.debug("fallback face %s" % f)
            fallback_dir = _get_or_create_path(os.path.join(self.tile_folder, 'fallback'))
            face = PIL.Image.open(image)
            face = face.resize([1024, 1024], PIL.Image.ANTIALIAS)
            face.save(os.path.join(fallback_dir, f + '.jpg'), quality = self.image_quality)
    
        

if __name__ == "__main__":
    
    logger.setLevel(logging.DEBUG)
    console = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)

    pano = "/home/reimer/Panoramen/Bokul/bokul-grid-crop.jpg"
    #pano = "/home/peter/Development/4pi.org/content/panos/gehry-bauten.jpg"
    e = Exif([pano])
    exifdata = e.get_exifdata()
    # scene = Scene(pano)
    scene = Scene(pano, exifdata=exifdata)
    # scene = Scene(pano)
    # scene.tile(force=True)
    scene.tile(force=False)
    # scene.fallback()
    print(scene.get_json())
