#!/usr/bin/env python

"""
xmsgs.py: Extract gettext messages from Python code

(c) 2014, Outernet Inc
All rights reserved.
"""

from __future__ import print_function

import os
import re
import sys
import fnmatch
import subprocess
from locale import getpreferredencoding

CHARSET_RE = re.compile(r'("Content-Type: text/plain; charset=).+(\\n")')
BLACKLIST = ['ht']


def make_args(localedir, domain, address=None, comment=None, name=None,
              version=None):
    """
    Create a list of xgettext command arguments
    """
    template_path = os.path.join(localedir, '%s.pot' % domain)
    args = ['xgettext', '-L', 'python', '--force-po', '--from-code=UTF-8']
    if address:
        args.append('--msgid-bugs-address=%s' % address)
    if comment:
        args.append('--add-comments=%s' % comment)
    args.append('-o')
    args.append(template_path)
    return args, template_path


def get_po_dir(localedir, locale):
    return os.path.normpath(os.path.join(localedir, '%s/LC_MESSAGES' % locale))


def prep_po_path(template_path, locale):
    localedir = os.path.dirname(template_path)
    po_name = os.path.splitext(os.path.basename(template_path))[0] + '.po'
    po_dir = get_po_dir(localedir, locale)
    try:
        os.makedirs(po_dir)
    except:
        pass
    po_path = os.path.join(po_dir, po_name)
    return po_path


def remove_obsolete(template_path, po_path):
    subprocess.call(['msgattrib', '--ignore-file=%s' % template_path,
                     '--set-obsolete', '-o', po_path, po_path])


def update_po(template_path, locale):
    po_path = prep_po_path(template_path, locale)
    if os.path.exists(po_path):
        subprocess.call(['msgmerge', '-N', '-o', po_path, po_path,
                         template_path])
    else:
        subprocess.call(['msginit', '--locale="%s"' % locale,
                         '--no-translator', '-o', po_path, '-i',
                         template_path])
        subprocess.call(['iconv', '-t', 'utf-8', po_path])
        with open(po_path, 'r') as f:
            text = f.read()
        with open(po_path, 'w') as f:
            f.write(CHARSET_RE.sub(r'\1UTF-8\2', text))
    if locale.startswith('en'):
        # Copy msgid to msgstr for English locale
        subprocess.call(['msgen', '-o', po_path, po_path])
    remove_obsolete(template_path, po_path)
    return po_path


def process_dir(path, extension, args, template_path):
    """
    Execute ``args`` command on given path for given extensions
    """
    pattern = '*.%s' % extension
    if os.path.exists(template_path):
        args.append('--join-existing')
    processed = []
    for root, dirs, files in os.walk(path):
        for f in fnmatch.filter(files, pattern):
            path = os.path.relpath(os.path.join(root, f))
            processed.append(f)
            args.append(path)
    out = subprocess.call(args)
    if out:
        print("xgettext failed with status code %s" % out,
              file=sys.stderr)
        print("Command used was: '%s'" % ' '.join(args))
        sys.exit(1)
    else:
        print('\n'.join(["Processed '%s'" % p for p in processed]))


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser(description='Extract messages from project using '
                            'xgettext')
    parser.add_argument('path', metavar='PATH', help='project path')
    parser.add_argument('extensions', metavar='EXT', nargs='*',
                        help='extensions to parse without the dot (defaults '
                        'to "py" if none are specified; note that all files '
                        'will be parsed as Python code regardless of their '
                        'extension)')
    parser.add_argument('-l', metavar='PATH', default='locales',
                        dest='locales', help='locales directory (defaults to '
                        '"locales" within the specified path, relative to '
                        'specified path)')
    parser.add_argument('-m', metavar='MODULEPATH', default='main', dest='main',
                        help='path of the main module (defaults to "main")')
    parser.add_argument('-i', metavar='PATH', dest='include',
                        help='include PATH in PYTHONPATH')
    parser.add_argument('-d', metavar='NAME', default='messages',
                        dest='domain', help='Name of gettext domain (defaults '
                        'to "messages")')
    parser.add_argument('-c', metavar='COMMENT', default='Translators,',
                        dest='comment', help='Comment string (default: '
                        '"Translators,")')
    parser.add_argument('-a', metavar='EMAIL', dest='address',
                        help='Contact address for bug reports (default: none)')

    args = parser.parse_args(sys.argv[1:])

    path = os.path.abspath(os.path.normpath(args.path))
    moddir = os.path.dirname(path)
    package_name = os.path.basename(path)
    mainmod = args.main
    modname = '.'.join([
        os.path.basename(os.path.normpath(path)),
        mainmod])

    # Set up PYTHONPATH
    sys.path.insert(0, moddir)
    if args.include:
        sys.path.insert(0, os.path.abspath(os.path.normpath(args.include)))

    # Import main module
    try:
        mod = __import__(modname)
        for mod_name in [mn for mn in modname.split('.')
                         if mn != package_name]:
            mod = getattr(mod, mod_name)
    except Exception as err:
        print('Error: could not import main module %s' % modname,
              file=sys.stderr)
        print('Error message was: %s' % err, file=sys.stderr)
        sys.exit(1)

    if not hasattr(mod, '__version__'):
        version = None
    else:
        version = mod.__version__

    print("Using directory: %s" % path)

    # Get locale dir
    localedir = os.path.join(path, args.locales)
    print("Using localedir: %s" % localedir)

    # Get list of locales
    locales = [l for l in os.listdir(localedir) if not l.endswith('.pot')]
    print("Using locales: %s" % ', '.join(locales))

    # Get list of extensions
    exts = args.extensions
    if 'py' not in exts:
        exts.insert(0, 'py')
    print("Using extensions: %s" % ', '.join(exts))

    print("Using domain: %s" % args.domain)
    if args.address:
        print("Using contact address: %s" % args.address)
    else:
        print("Not using contact address")
    print("Using comment string: %s" % args.comment)

    if version:
        print("Project version: %s" % version)

    # Process all extensions
    xgettext_args, template_path = make_args(
        localedir, args.domain, args.address, args.comment, package_name,
        version)
    if os.path.exists(template_path):
        os.unlink(template_path)
    for ext in exts:
        process_dir(path, ext, xgettext_args, template_path)

    # Fix the template
    with open(template_path, 'r') as f:
        template = f.read()
    with open(template_path, 'w') as f:
        template = template.replace('PACKAGE', package_name)
        template = template.replace('CHARSET', getpreferredencoding().upper())
        f.write(template)

    for locale in locales:
        po_path = update_po(template_path, locale)
        with open(po_path, 'r') as f:
            po = f.read()
        with open(po_path, 'w') as f:
            f.write(po.replace('PACKAGE', package_name))
    print("Done")
