"""
bundler.py: Bundles javascript files in .bundle files and creates single JS

2014 Outernet Inc <hello@outernet.is>
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from __future__ import unicode_literals, print_function

import os
import sys
import locale
import platform
import StringIO
import tempfile
import subprocess

NEEDS_SHELL = platform.system() == 'Windows'

sources = sys.argv[-1]

if not sources:
    print('No source directory')

sources = os.path.normpath(sources)

print('Processing %s' % sources)


class MinificationError(Exception):
    def __init__(self, paths):
        self.paths = paths
        super(MinificationError, self).__init__(
            'Error minifying %s' % ', '.join(paths))


def uglify(paths, bundledir, bundlename, outpath):
    stdout = tempfile.TemporaryFile()
    map_path = os.path.join(bundledir, bundlename + '.js.map')
    map_url = os.path.relpath(
        map_path, sources).replace('\\', '/')
    map_options = ['--source-map', map_path, '--source-map-url', map_url, '-p',
                   'relative']
    command = ['uglifyjs'] + paths + map_options + ['-o', outpath]
    try:
        subprocess.call(command, stdout=stdout, shell=NEEDS_SHELL)
    except subprocess.CalledProcessError as err:
        raise MinificationError(paths)
    stdout.seek(0)
    return stdout.read()


def bundle(bundlefile):
    bundledir = os.path.dirname(bundlefile)
    bundlename = os.path.basename(bundlefile)[:-7]
    jsfile = os.path.join(bundledir, '%s.js' % bundlename)
    with open(bundlefile, 'r') as f:
        pieces = [l.strip() for l in f]
    out = ''
    paths = [os.path.join(bundledir, os.path.normpath(p)) for p in pieces]
    out += uglify(paths, bundledir, bundlename, jsfile)
    print('Written %s' % jsfile)


for root, dirs, files in os.walk(sources):
    for f in files:
        if not f.endswith('.bundle'):
            continue
        path = os.path.join(root, f)
        bundle(path)
