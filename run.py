#!/usr/bin/env python

"""
Wrapper script that sets up librarian
"""

from __future__ import unicode_literals

import os
import sys

scriptdir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, scriptdir)

def ensure_dir(path):
    try:
        os.makedirs(path)
    except OSError:
        pass

os.chdir(scriptdir)

from librarian import app

ensure_dir('tmp/downloads/content')
ensure_dir('tmp/downloads/files')
ensure_dir('tmp/outernet')
ensure_dir('tmp/zipballs')
app.main('local.ini', False)

