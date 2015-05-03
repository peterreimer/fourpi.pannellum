#!/usr/bin/env  python

from __future__ import print_function

class HotSpot:
    
    def __init__(self, src, dest):
        
        self.src = src
        self.dest = dest
        self.text = dest.get('title','n/a')
        
    
    def distance(self):
        return 123
    
    def get_conf(self):
        title = self.text
        conf = {}
        conf['type'] = "scene"
        #conf['text'] = self.dest['title']
        conf['text'] = title
        
        #print(title)
        return conf