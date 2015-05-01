#!/usr/bin/env  python

from __future__ import unicode_literals, print_function
from fourpi.pannellum.tour import Tour
import argparse


def main():
    
    parser = argparse.ArgumentParser(description='Pannellum configurator')
    parser.add_argument('panoramas', nargs='+', help='Panoramic image')

    parser.add_argument("-v", "--verbose", action="store_true", help="be verbose")

    args = parser.parse_args()
    print(args)
    


if __name__ == "__main__":
    
    panos = ["/home/peter/public_html/pannellum/eq/gehry-bauten.jpg",
             "/home/peter/public_html/pannellum/eq/medienhafen-hyatt.jpg"]
    
    panos = [
       "/home/reimer/Desktop/laschozas-upload.jpg",
       "/home/reimer/Desktop/mafra-photosphere.jpg"
    ]
    tour = Tour(author="Peter Reimer", panoramas=panos)
    print(tour.get_json()) 
    
