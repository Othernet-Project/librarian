#!/usr/bin/env python

"""
cmpmsgs.py: Compile .mo files

(c) 2014, Outernet Inc
All rights reserved.
"""

from __future__ import print_function

import os
import sys
import fnmatch
import subprocess

def convert(po_path):
    base, ext = os.path.splitext(po_path)
    mo_path = base + '.mo'
    subprocess.call(['msgfmt', '-o', mo_path, po_path])

if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser(description='Convert messages in project')
    parser.add_argument('path', metavar='PATH', help='project path')
    args = parser.parse_args(sys.argv[1:])

    for root, dirs, files in os.walk(args.path):
        for f in fnmatch.filter(files, '*.po'):
            if 'LC_MESSAGES' not in root:
                continue
            convert(os.path.join(root, f))

    print('Done')
