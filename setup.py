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


def rebuild_static(sdist=False):
    import subprocess
    cmd = ('build', 'dist')[sdist]
    subprocess.check_call(['grunt', cmd])


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
        rebuild_static()


class Package(SdistCommand):
    def run(self):
        rebuild_catalogs()
        rebuild_static(sdist=True)
        clean_pyc()
        SdistCommand.run(self)


class Clean(Command):
    def run(self):
        clean_pyc()


class Benchmark(Command):
    description = 'run siege against the specified path'
    user_options = [('siege-target=', None, 'Target URL'),
                    ('siege-args=', None, 'Arguments for siege')]
    default_args = ['-d1', '-r10']
    default_concurrent = [10, 20, 30, 40]

    def initialize_options(self):
        self.siege_target = None
        self.siege_args = None

    def finalize_options(self):
        pass

    def run(self):
        import subprocess

        if not self.siege_target:
            print('siege-target (target URL) must be specified.')
            return

        if not self.siege_args:
            for concurrent in self.default_concurrent:
                cmd = ['siege',
                       self.siege_target,
                       '-c{0}'.format(concurrent)] + self.default_args
                subprocess.check_call(cmd)
                print("=" * 80)
        else:
            cmd = ['siege', self.siege_target] + self.siege_args.split()
            subprocess.check_call(cmd)


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
    install_requires=DEPS,
    cmdclass={
        'test': PyTest,
        'develop': Develop,
        'sdist': Package,
        'uncache': Clean,
        'benchmark': Benchmark,
    },
)
