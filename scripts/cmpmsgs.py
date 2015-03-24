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


def main(path):
    for root, dirs, files in os.walk(path):
        for f in fnmatch.filter(files, '*.po'):
            if 'LC_MESSAGES' not in root:
                continue
            path = os.path.join(root, f)
            print("Processing '%s'" % path)
            convert(path)
    print('Done')


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser(description='Convert messages in project')
    parser.add_argument('path', metavar='PATH', help='project path')
    args = parser.parse_args(sys.argv[1:])
    main(args.path)
