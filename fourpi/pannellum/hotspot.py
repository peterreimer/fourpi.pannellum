#!/usr/bin/env  python

from __future__ import print_function
import logging
from haversine import haversine                    
import math
from fourpi.pannellum.utils import _pretty_distance

logger = logging.getLogger('pannellum.hotspot')

class HotSpot:

    def __init__(self, scene_id, src, dest):

        self.src = src
        self.scene_id = scene_id
        self.dest = dest
        self.text = dest.get('title', 'n/a')
        self.lat = src.get('lat', None)
        self.lng = src.get('lng', None)
        
        self.lat1 = self.src.get('lat', None)
        self.lng1 = self.src.get('lng', None)

        self.lat2 = self.dest.get('lat', None)
        self.lng2 = self.dest.get('lng', None)

        
        self.northOffset = src.get('northOffset', 0)

    def _get_distance(self):
        try:
            distance = haversine((self.lng1, self.lat1), (self.lng2, self.lat2))
        except:
            distance = None
        logger.warn("%s %s: %s", self.scene_id, self.dest['title'], distance )
        return _pretty_distance(distance) 
 
    def _get_bearing(self):

        try:
            lat1 = self.src.get('lat', None)
            lng1 = self.src.get('lng', None)

            lat2 = self.dest.get('lat', None)
            lng2 = self.dest.get('lng', None)

            rlat1 = math.radians(lat1)
            rlat2 = math.radians(lat2)
            rlng1 = math.radians(lng1)
            rlng2 = math.radians(lng2)
            dlng = math.radians(lng2 - lng1)

            b = math.atan2(math.sin(dlng) * math.cos(rlat2), math.cos(rlat1) * math.sin(rlat2) - math.sin(rlat1) * math.cos(rlat2) * math.cos(dlng)) # bearing calc
            bd = math.degrees(b)
            br, bn = divmod(bd + 360, 360) # the bearing remainder and final bearing
            return bn - self.northOffset
        except:
            return 0

    def get_conf(self):
        title = self.text
        conf = {}
        conf['type'] = "scene"
        conf['text'] = "%s (%s)" % (title, self._get_distance())
        conf['yaw'] = self._get_bearing()
        conf['pitch'] = 0
        conf['sceneId'] = self.scene_id
        return conf
