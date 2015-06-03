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
EXTENSION = "jpg"

FACES = [ "f", "b", "u", "d", "l", "r" ]
ANGLES = [(0,0),(-180,0),(0,-90),(0,90),(90,0),(-90,0)]

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

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
console = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s: %(message)s')
console.setFormatter(formatter)
logger.addHandler(console)

NONA =find_executable('nona')


if not NONA:
    logger.error("nona required but not found.")


class Scene:

    def __init__(self, panorama, **kwargs):
        
        self.src = panorama
        self.scene_id = _scene_id_from_image(panorama)
        dest = _expand(os.path.dirname(self.src))
        self.output_dir = os.path.join(dest, self.scene_id)
        image_quality = kwargs.get('image_quality', DEFAULT_IMAGE_QUALITY)
        self.image_quality  = int(image_quality * 100)
        basePath = kwargs.get('basePath', None)
        if basePath:
            self.basePath = '/'.join((basePath, self.scene_id))
        else:
            self.basePath = self.scene_id
        self.exifdata = kwargs.get('exifdata', {})
        self.hfov = kwargs.get('hfov', 360)
        self.tile_size = kwargs.get('tile_size', None)
        tile_folder = kwargs.get('tile_folder', None)
        self.tile_folder = os.path.join(tile_folder, self.scene_id)
        self.filename = os.path.split(panorama)[1]
        self.image =  PIL.Image.open(panorama)
        self.width, self.height = self.image.size
        self._levels_and_tiles(self.tile_size)
        self.exif = self.exifdata.get(self.scene_id, {})
        self.title = self.exif.get('title', 'n/a')
        self.northOffset = self.exif.get('northOffset', 0)
        conf = {}
        conf['type'] = 'multires'
        conf['northOffset'] = self.northOffset
        conf['title'] = self.title
        conf['compass'] = True
        
        conf['multiRes'] = self._multires_conf()
        hotspots = []
        for dest_scene_id in self.exifdata.keys():
            src_scene_id = self.scene_id
            if src_scene_id != dest_scene_id:
                hs = HotSpot(dest_scene_id, self.exifdata[src_scene_id], self.exifdata[dest_scene_id])
                hotspots.append(hs.get_conf())            
        conf['hotSpots'] = hotspots
        lat = self.exif.get('lat',None)
        lng = self.exif.get('lng',None)
        conf['location'] = {'lat':lat,'lng':lng}

        self.conf = conf
    
   
    def _multires_conf(self):
        
        conf = {}
        conf['basePath'] = self.basePath 
        conf['path'] = '/%l/%s%y_%x'
        conf['fallbackPath'] =  "/fallback/%s"
        conf['extension'] = EXTENSION
        conf['tileResolution'] =  self.tileResolution
        conf['maxLevel'] =  self.maxLevel
        conf['cubeResolution'] = self.cubeResolution
        return conf


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
            _get_or_create_path(self.tile_folder)# os.makedirs(self.output_dir)
            self.extract()
            for f, image in self.faces:
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
            logger.info("Skipping extraction and file creation, %s exists" % self.tile_folder)

    def fallback(self, force=False):
        
        for f, image in self.faces:
            logger.debug("fallback face %s" % f)
            fallback_dir = _get_or_create_path(os.path.join(self.tile_folder, 'fallback'))
            face = PIL.Image.open(image)
            face = face.resize([1024, 1024], PIL.Image.ANTIALIAS)
            face.save(os.path.join(fallback_dir, f + '.jpg'), quality = self.image_quality)
    
    def thumbs(self, ratio, width):
        thumbs_dir = _get_or_create_path(os.path.join(self.tile_folder, 'thumbs'))
        h_crop = self.width / ratio
        left = 0
        upper = int(0.5 * (self.height - h_crop))
        right = self.width
        lower = upper + h_crop
        print(lower)
        pano = PIL.Image.open(self.src)
        cropped = pano.crop([left, upper, right, lower])
        cropped = cropped.resize([width, width / ratio], PIL.Image.ANTIALIAS)
        cropped.save(os.path.join(thumbs_dir, '%s-%s.jpg' % (self.scene_id, str(width))), quality = self.image_quality)
                
        
        

if __name__ == "__main__":
    
    pano = "../../panos/bruecke2400.jpg"
    scene = Scene(pano, tile_folder="tiles")
    #scene = Scene(pano, image_quality=0.95)
    #scene.tile(force=True)
    #scene.fallback()
    for r, w in((4,1000),(3,600),(3,150)):
        scene.thumbs(r, w)
