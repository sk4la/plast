#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from plast.framework.contexts.meta import Meta as _meta

import setuptools

setuptools.setup(
    author=_meta.__author__,
    description=_meta.__description__,
    long_description=open("README.adoc").read(),
    name=_meta.__package__,
    url="https://github.com/sk4la/plast",
    version=_meta.__version__,

    packages=setuptools.find_packages(
        _meta.__package__, 
        exclude=[
            "*.tests", 
            "*.tests.*", 
            "tests.*", 
            "tests"
        ]),
    install_requires=[lib.strip() for lib in open("REQUIREMENTS").read().splitlines()],
    include_package_data=True,
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Information Analysis"
    ],
    entry_points={
        "console_scripts": [
            "plast=plast.plast:main",
            "plast=plast.plast-conf:main"
        ]
    }
)
