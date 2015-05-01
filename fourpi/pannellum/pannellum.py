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
    


    
