#!/usr/bin/env python

from saltmetrics.metadata import *
from setuptools import setup, find_packages

REQUIREMENTS = [
    'salt>=2015.5.0',
]

setup(
    name=NAME,
    description=DESCRIPTION,
    version=VERSION,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    license=LICENCE,
    url=URL,
    packages=find_packages(exclude=['docs']),
    install_requires=REQUIREMENTS,
)
