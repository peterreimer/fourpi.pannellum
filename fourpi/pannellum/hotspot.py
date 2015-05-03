#!/usr/bin/env  python

from __future__ import unicode_literals, print_function

class HotSpot:
    
    def __init__(self, src, dest):
        
        self.src = src
        self.dest = dest
        print(src)
        print(dest)
        self.name = dest
        
    
    def distance(self):
        return 123
    
    def get_conf(self):
        #return {'text': self.name, 'pitch': self.dest, 'yaw': 0}
        title = self.dest['title']
        conf = {}
        conf['type'] = "scene"
        #conf['text'] = self.dest['title']
        conf['text'] = title
        
        #print(title)
        return conf