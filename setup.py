#!/usr/bin/env	python

from setuptools import setup, find_packages
import os


setup(name='fourpi.pannellum',
      version='0.0.1',
      description="Pannellum stuff",
      long_description="to be written",
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        ],
      keywords='',
      author='Peter Reimer',
      author_email='peter@4pi.org',
      url='https://github.com/peterreimer/fourpi.pannellum',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['fourpi', 'fourpi.pannellum'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'Pillow'
          # -*- Extra requirements: -*-
      ],
      entry_points={
          'console_scripts':[
            'pannellum=fourpi.pannellum.pannellum:main',
          ]  
      },
      )
