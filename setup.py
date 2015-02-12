#!/usr/bin/env python

import os
import fnmatch
from setuptools import setup, find_packages

import librarian

# Production requirement, not needed during development
BJ = ['bjoern==1.4.1']

def read(fname):
    """ Return content of specified file """
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def data(patterns=[]):
    """ For each pattern, return mapping for data_files """
    data_files = []
    for root, files, dirs in os.walk('librarian'):
        paths = [os.path.join(root, f) for f in files]
        for pattern in patterns:
            files = fnmatch.filter(paths, pattern)
            data_files += files
    return data_files


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
    package_data={
        'librarian': data([
            '*.css',
            '*.png',
            '*.gif',
            '*.js',
            '*.sql',
            '*.tpl',
            '*.[mp]o',
            '*.ini',
            '*.sql',
        ]),
    },
    include_data_files=True,
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
