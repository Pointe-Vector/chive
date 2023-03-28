#!/usr/bin/env python

from setuptools import find_namespace_packages, setup

setup(
    name="pointevector-chive",
    version="0.1.0",
    description="An archival tool with hash tree file integrity",
    author="Andrew Hoekstra",
    email="andrew@pointevector.com",
    url="https://www.github.com/Pointe-Vector/chive",
    packages=find_namespace_packages(),
)
