#!/usr/bin/env python

import os
import sys
import shutil
from subprocess import check_output
from distutils.cmd import Command
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
from setuptools.command.develop import develop as DevelopCommand
from setuptools.command.sdist import sdist as SdistCommand

import librarian

SCRIPTDIR = os.path.dirname(__file__) or '.'
PY3 = sys.version_info >= (3, 0, 0)
VERSION = librarian.__version__

if '--snapshot' in sys.argv:
    sys.argv.remove('--snapshot')
    head = check_output(['git', 'rev-parse', 'HEAD'], cwd=SCRIPTDIR).strip()
    VERSION += '+git%s' % head[:8]


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


REQPATH = in_scriptdir('conf/requirements.txt')
DEPS = read_reqs(REQPATH)


def rebuild_catalogs():
    import subprocess
    subprocess.call('python scripts/cmpmsgs.py librarian/locales', shell=True)


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


class Siege(Command):
    description = 'perform load testing with siege'
    user_options = [('target=', None, 'Target URL'),
                    ('args=', None, 'Arguments for siege')]
    default_args = ['-c10', '-d1', '-r10']

    def initialize_options(self):
        self.target = None
        self.args = None

    def finalize_options(self):
        pass

    def run(self):
        import subprocess

        if not self.target:
            print("usage: setup.py siege --target=http://domain.tld "
                  "[--args='-c10 -d1 -r10']")
            return

        args = self.args.split() if self.args else self.default_args
        cmd = ['siege', self.target] + args
        subprocess.check_call(cmd)


class Phantom(Command):
    description = 'perform load testing with phantomjs'
    user_options = [('target=', None, 'Target URL'),
                    ('workers=', None, 'Number of workers'),
                    ('cycles=', None, 'Number of cycles'),
                    ('silent', None, 'Disable verbose output')]
    boolean_options = ['silent']
    default_cycles = 10
    default_workers = 10

    def initialize_options(self):
        self.target = None
        self.workers = None
        self.cycles = None
        self.silent = 0

    def finalize_options(self):
        self.workers = int(self.workers or self.default_workers)
        self.cycles = int(self.cycles or self.default_cycles)

    def run(self):
        from scripts import loadtest

        if not self.target:
            print("usage: setup.py phantom --target=http://domain.tld "
                  "[--workers=10 --cycles=10]")
            return

        loadtest.perform(self.target, self.workers, self.cycles, self.silent)


setup(
    name='librarian',
    version=VERSION,
    author='Outernet Inc',
    author_email='branko@outernet.is',
    description=('Web-based UI for managing local Outernet broadcast '
                 'content'),
    license='GPLv3',
    keywords='outernet content archive library',
    url='https://github.com/Outernet-Project/librarian',
    packages=find_packages(),
    include_package_data=True,
    long_description=read('README.rst'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Utilties',
        'Topic :: Communications :: File Sharing'
        'Framework :: Bottle',
        'Environment :: Web Environment',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
    ],
    entry_points = {
        'console_scripts': [
            'librarian = librarian.app:main',
        ],
    },
    install_requires=DEPS,
    cmdclass={
        'test': PyTest,
        'develop': Develop,
        'sdist': Package,
        'uncache': Clean,
        'siege': Siege,
        'phantom': Phantom,
    },
)
