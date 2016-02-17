#!/usr/bin/env  python

from __future__ import print_function
from haversine import haversine                    
import math
import logging
from fourpi.pannellum.utils import _pretty_distance

logger = logging.getLogger('pannellum.hotspot')

class HotSpot:

    def __init__(self, scene_id, src, dest):
        """src and dest are the exifdata of the respective scenes"""

        self.scene_id = scene_id
        self.src = src
        self.dest = dest
        self.text = dest.get('title', 'n/a')

        self.northOffset = src.get('northOffset', 0)
        self.targetNorthOffset = dest.get('northOffset', 0)
        
        if self.src.has_key("latlng") and self.dest.has_key("latlng"):
            self.gps = True

    def _get_distance(self):
        """Return distance to hotspot in a humanfriendly way,
            ie 123 m, 1.6 km etc.
        """
        
        if hasattr(self, 'gps'):
            distance = haversine(self.src['latlng'], self.dest['latlng'])
            return _pretty_distance(distance) 
        else:
            return ""

    def _get_bearing(self):
        """Return the bearing of the hotspot, used as yaw angle. 
        """
        
        if hasattr(self, 'gps'):
            lat1 = self.src['latlng'][0]
            lng1 = self.src['latlng'][1]

            lat2 = self.dest['latlng'][0]
            lng2 = self.dest['latlng'][1]

            rlat1 = math.radians(lat1)
            rlat2 = math.radians(lat2)
            # rlng1 = math.radians(lng1)
            # rlng2 = math.radians(lng2)
            dlng = math.radians(lng2 - lng1)

            b = math.atan2(math.sin(dlng) * math.cos(rlat2), math.cos(rlat1) * math.sin(rlat2) - math.sin(rlat1) * math.cos(rlat2) * math.cos(dlng)) # bearing calc
            bd = math.degrees(b)
            bn = (bd + 360) % 360
            return bn
        else:
            return 0

    def get_conf(self):
        """Return the hotspots configuration dictionary.
        """
        
        title = self.text
        yaw = self._get_bearing() - self.northOffset
        targetYaw = yaw + self.northOffset - self.targetNorthOffset
        conf = {}
        conf['type'] = "scene"
        conf['text'] = "%s (%s)" % (title, self._get_distance())
        conf['yaw'] = (yaw + 360) % 360
        conf['pitch'] = 0
        conf['targetPitch'] = 0
        conf['targetYaw'] = (targetYaw + 360) % 360
        conf['sceneId'] = self.scene_id
        return conf
