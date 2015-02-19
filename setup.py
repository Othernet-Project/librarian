#!/usr/bin/env python

import os
import fnmatch
from setuptools import setup, find_packages

import librarian

SCRIPTDIR = os.path.dirname(__file__)
# Production requirement, not needed during development
BJ = ['bjoern==1.4.2']

def read(fname):
    """ Return content of specified file """
    return open(os.path.join(SCRIPTDIR, fname)).read()


setup(
    name = 'librarian',
    version = librarian.__version__,
    author = 'Outernet Inc',
    author_email = 'branko@outernet.is',
    description = ('Web-based UI for managing local Outernet broadcast '
                   'content'),
    license = 'GPLv3',
    keywords = 'outernet content archive library',
    url = 'https://github.com/Outernet-Project/librarian',
    packages=find_packages(),
    include_package_data=True,
    long_description=read('README.rst'),
    install_requires = read('conf/requirements.txt').strip().split('\n') + BJ,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Utilities',
        'Framework :: Bottle',
        'Environment :: Web Environment',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 2.7',
    ],
)
