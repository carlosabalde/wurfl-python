#!/usr/bin/env python
"""
WURFL Python
============

WURFL Python allows matching user agent strings with devices in the WURFL
(Wireless Universal Resource File) database using Python. Check out
https://github.com/carlosabalde/wurfl-python for a detailed description,
extra documentation and other useful information.

:copyright: (c) 2013 by Carlos Abalde, see AUTHORS.txt for more details.
:license: GPL, see LICENSE.txt for more details.
"""

from __future__ import absolute_import
from setuptools import setup, find_packages

setup(
    name='wurfl-python',
    version='0.1',
    author='Carlos Abalde',
    author_email='carlos.abalde@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/carlosabalde/wurfl-python',
    description='WURFL Python: matching user agent strings with devices in the WURFL database using Python.',
    long_description=__doc__,
    license='GPL',
    entry_points={
        'console_scripts': [
            'wurfl-python-processor = wurfl_python.processor:main',
        ],
    },
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'ordereddict',
        'python-Levenshtein',
        'elementtree',
    ],
)
