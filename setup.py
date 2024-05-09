#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

config = {
    'name': 'beziers',
    'author': 'Simon Cozens',
    'author_email': 'simon@simon-cozens.org',
    'url': 'https://github.com/simoncozens/beziers.py',
    'description': 'Bezier curve manipulation library',
    'long_description': open('README.rst', 'r').read(),
    'license': 'MIT',
    'version': '0.6.0',
    'install_requires': [
        'pyclipper'
    ],
    'classifiers': [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 4 - Beta"

    ],
    'packages': find_packages(),
}

if __name__ == '__main__':
    setup(**config)
