#!/usr/bin/env  python
# -*- coding: utf-8 -*-

from __future__ import  print_function
import math
import subprocess
import os
import argparse
import PIL.Image

from distutils.spawn import find_executable
    
NONA = find_executable('nona')

parser = argparse.ArgumentParser(description='Remap panoramas from equirectangular to cylindrical projection')
parser.add_argument('panorama', metavar='INPUT', help='Panoramic image')
parser.add_argument('-f', '--vfov', type=float,
                        default=140.0, help='Vertical Field of View. Default: 140')


args = parser.parse_args()
print(args)

pano = PIL.Image.open(args.panorama)
width, height = pano.size

base = os.path.splitext(os.path.basename(args.panorama))[0]
script_name = base + "-cyl.pto"
out_name = base + "-cyl.tif"

cyl_height = 2 * (width / (2 * math.pi) * math.tan(math.radians(args.vfov / 2)))
print(width, int(cyl_height))

script = open(script_name, 'w')
script.write('p f1 w%s h%s n"TIFF" u0 v360\n' % (width, int(cyl_height)))
script.write('i f4 w%s h%s r0 p0 y0 v360 n"%s"\n' % (width, height, args.panorama))

args = [NONA, '-v', '-o', out_name, script_name]
p = subprocess.Popen(args)

