#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

config = {
    'name': 'beziers',
    'author': 'Simon Cozens',
    'author_email': 'simon@simon-cozens.org',
    'url': '',
    'description': '',
    'long_description': open('README.rst', 'r').read(),
    'license': 'MIT',
    'version': '0.0.1',
    'install_requires': [],
    'classifiers': [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 1 - Planning",
    ],
    'packages': find_packages(),
}

if __name__ == '__main__':
    setup(**config)
