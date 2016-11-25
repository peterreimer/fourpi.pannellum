fourpi.pannellum
================

.. image:: https://travis-ci.org/peterreimer/fourpi.pannellum.svg?branch=master
    :target: https://travis-ci.org/peterreimer/fourpi.pannellum

create multiresolution tiles and tour configuration files for pannellum

-  read size of panorama
-  extract six cubic faces
-  make tiles
-  make json

pannellum equi pano1, pano2,

Usage
-----


::

    usage: pannellum [-h] [-a AUTHOR] [-d] [-v] [-f TILE_FORMAT] [-t TILE_FOLDER]
                     [-q IMAGE_QUALITY] [-r RESIZE_FILTER]
                     INPUT [INPUT ...]

    Pannellum configurator

    positional arguments:
      INPUT                 Panoramic image(s)

    optional arguments:
      -h, --help            show this help message and exit
      -a AUTHOR, --author AUTHOR
                            The Creator of this tour.
      -d, --debug           Turn on debug mode.
      -v, --verbose         be verbose
      -f TILE_FORMAT, --tile_format TILE_FORMAT
                            Image format of the tiles (jpg or png). Default: jpg
      -t TILE_FOLDER, --tile_folder TILE_FOLDER
                            Tile folder
      -q IMAGE_QUALITY, --image_quality IMAGE_QUALITY
                            Quality of the image output (0-1). Default: 0.8
      -r RESIZE_FILTER, --resize_filter RESIZE_FILTER
                            Type of filter for resizing (bicubic, nearest,
                            bilinear, antialias (best). Default: antialias
