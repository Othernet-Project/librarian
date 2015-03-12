#!/usr/bin/env python

import os
import sys
import shutil
import platform
from setuptools import setup, find_packages
from distutils.cmd import Command
from setuptools.command.test import test as TestCommand
from setuptools.command.develop import develop as DevelopCommand
from setuptools.command.sdist import sdist as SdistCommand
from setuptools.command.setopt import option_base as Command

import librarian

SCRIPTDIR = os.path.dirname(__file__) or '.'
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


def rebuild_catalogs():
    import subprocess
    import platform
    needs_shell = platform.system = 'Windows'
    subprocess.call('python scripts/cmpmsgs.py librarian/locales',
                    shell=needs_shell)


def clean_pyc():
    print("cleaning up cached files in '%s'" % SCRIPTDIR)
    for root, dirs, files in os.walk(SCRIPTDIR):
        for f in files:
            if os.path.splitext(f)[1] == '.pyc':
                path = os.path.join(root, f)
                print("removing '%s'" % path)
                os.unlink(path)
        for d in dirs:
            if d == '__pycache__':
                path = os.path.join(root, d)
                print("removing '%s'" % path)
                shutil.rmtree(path)


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


class Develop(DevelopCommand):
    def run(self):
        DevelopCommand.run(self)
        rebuild_catalogs()


class Package(SdistCommand):
    def run(self):
        rebuild_catalogs()
        clean_pyc()
        SdistCommand.run(self)


class Clean(Command):
    def run(self):
        clean_pyc()


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
    cmdclass={
        'test': PyTest,
        'develop': Develop,
        'sdist': Package,
        'uncache': Clean,
    },
)
