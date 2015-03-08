#!/usr/bin/env python

import os
import sys
import platform
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

import librarian

SCRIPTDIR = os.path.dirname(__file__)
PY3 = sys.version_info >= (3, 0, 0)

def read(fname):
    """ Return content of specified file """
    path = os.path.join(SCRIPTDIR, fname)
    if PY3:
        f = open(path, 'r', encoding='utf8')
    else:
        f = open(path, 'r')
    content = f.read()
    f.close()
    return content

def read_reqs(fname):
    return read(fname).strip().split('\n')


def in_scriptdir(path):
    return os.path.join(SCRIPTDIR, os.path.normpath(path))


# Production requirement, not needed during development
if platform.system() == 'Windows':
    PROD_DEPS = []
else:
    PROD_DEPS = ['bjoern==1.4.2']


REQPATH = in_scriptdir('conf/requirements.txt')
DREQPATH = in_scriptdir('conf/dev_requirements.txt')
DEPS = read_reqs(REQPATH) + PROD_DEPS


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', 'Arguments for py.test')]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run(self):
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


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
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Utilities',
        'Framework :: Bottle',
        'Environment :: Web Environment',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 2.7',
    ],
    tests_require=read_reqs(DREQPATH),
    install_requires=DEPS,
    cmdclass={'test': PyTest},
)
