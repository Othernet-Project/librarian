from __future__ import print_function

import fnmatch
import locale
import os
import re
import subprocess
import sys


BLACKLIST = ['ht']
CHARSET_RE = re.compile(r'("Content-Type: text/plain; charset=).+(\\n")')
SOURCE_DIRS = set()


def construct_args(localedir, domain, address=None, comment=None):
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
    if not os.path.exists(po_dir):
        os.makedirs(po_dir)

    return os.path.join(po_dir, po_name)


def remove_obsolete(template_path, po_path):
    subprocess.check_call(['msgattrib',
                           '--ignore-file=%s' % template_path,
                           '--set-obsolete',
                           '-o',
                           po_path,
                           po_path])


def update_po(template_path, locale):
    po_path = prep_po_path(template_path, locale)
    if os.path.exists(po_path):
        subprocess.check_call(['msgmerge',
                               '-N',
                               '-o',
                               po_path,
                               po_path,
                               template_path])
    else:
        subprocess.check_call(['msginit',
                               '--locale="%s"' % locale,
                               '--no-translator',
                               '-o',
                               po_path,
                               '-i',
                               template_path])
        subprocess.check_call(['iconv', '-t', 'utf-8', po_path])
        with open(po_path, 'r+') as po_file:
            text = po_file.read()
            po_file.seek(0)
            po_file.truncate()
            po_file.write(CHARSET_RE.sub(r'\1UTF-8\2', text))

    if locale.startswith('en'):
        # Copy msgid to msgstr for English locale
        subprocess.check_call(['msgen', '-o', po_path, po_path])

    remove_obsolete(template_path, po_path)
    return po_path


def process_dir(path, extension, args, template_path):
    """
    Execute ``args`` command on given path for given extensions
    """
    pattern = '*.%s' % extension
    if os.path.exists(template_path):
        args.append('--join-existing')

    app_path = os.path.dirname(path)
    processed = []
    found = []
    for root, dirs, files in os.walk(path):
        for filename in fnmatch.filter(files, pattern):
            src_path = os.path.join(root, filename)
            found.append(os.path.relpath(src_path, app_path))
            processed.append(filename)

    if not found:
        return

    args.extend(found)
    os.chdir(app_path)
    try:
        subprocess.check_call(args)
    except subprocess.CalledProcessError as exc:
        print("xgettext failed with status code %s" % exc.returncode,
              file=sys.stderr)
        print("Command used was: '%s'" % ' '.join(args))
        sys.exit(1)
    else:
        print('\n'.join(["Processed '%s'" % p for p in processed]))


def add_message_source_path(path):
    SOURCE_DIRS.add(path)


def collect_messages(arg, supervisor):
    path = supervisor.config['root']
    project_package_name = supervisor.config['i18n.project_package_name']
    exts = supervisor.config.get('i18n.extensions', ['py'])
    localedir = supervisor.config.get('i18n.localedir', 'locales')
    localedir = os.path.join(path, localedir)
    domain = supervisor.config.get('i18n.domain', 'messages')
    comment_string = supervisor.config.get('i18n.comment_string',
                                           'Translators,')
    address = supervisor.config.get('i18n.bug_report_email', '')
    print("Using project root: %s" % path)
    print("Using domain: %s" % domain)
    print("Using localedir: %s" % localedir)
    # Get list of locales
    locales = [code for code in os.listdir(localedir)
               if not code.endswith('.pot')]
    print("Using locales: %s" % ', '.join(locales))
    # Get list of extensions
    exts = exts if 'py' in exts else ['py'] + exts
    print("Using extensions: %s" % ', '.join(exts))
    print("Using comment string: %s" % comment_string)
    if address:
        print("Using contact address: %s" % address)
    else:
        print("Not using contact address")

    # Process all extensions
    (xgettext_args, template_path) = construct_args(localedir,
                                                    domain,
                                                    address=address,
                                                    comment=comment_string)
    if os.path.exists(template_path):
        os.unlink(template_path)

    for pkg_root in [path] + list(SOURCE_DIRS):
        for ext in exts:
            process_dir(pkg_root, ext, list(xgettext_args), template_path)

    os.chdir(path)
    # Fix the template
    with open(template_path, 'r+') as template_file:
        template = template_file.read()
        template = template.replace('PACKAGE', project_package_name)
        template = template.replace('CHARSET',
                                    locale.getpreferredencoding().upper())
        template_file.seek(0)
        template_file.truncate()
        template_file.write(template)

    for locale_code in locales:
        po_path = update_po(template_path, locale_code)
        with open(po_path, 'r+') as po_file:
            po_data = po_file.read()
            po_file.seek(0)
            po_file.truncate()
            po_file.write(po_data.replace('PACKAGE', project_package_name))

    print("Done")
    raise supervisor.EarlyExit()
