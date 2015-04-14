"""
backend.archive.py: Download handling

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from . import backend


archive = backend.archive

FACTORS = {
    'b': 1,
    'k': 1024,
    'm': 1024 * 1024,
    'g': 1024 * 1024 * 1024,
}


def get_count(tag=None, lang=None, multipage=None):
    return archive.get_count(tag=tag, lang=lang, multipage=multipage)


def get_search_count(terms, tag=None, lang=None, multipage=None):
    return archive.get_search_count(terms,
                                    tag=tag,
                                    lang=lang,
                                    multipage=multipage)


def get_content(offset=0, limit=0, tag=None, lang=None, multipage=None):
    return archive.get_content(offset=offset,
                               limit=limit,
                               tag=tag,
                               lang=lang,
                               multipage=multipage)


def get_single(md5):
    return archive.get_single(md5)


def get_titles(ids):
    return archive.get_titles(ids)


def get_replacements(metadata):
    return archive.get_replacements(metadata)


def search_content(terms, offset=0, limit=0, tag=None, lang=None,
                   multipage=None):
    return archive.search_content(terms,
                                  offset=offset,
                                  limit=limit,
                                  tag=tag,
                                  lang=lang,
                                  multipage=multipage)


def content_for_domain(domain):
    return archive.content_for_domain(domain)


def prepare_metadata(md5, path):
    return archive.prepare_metadata(md5, path)


def add_meta_to_db(db, metadata, replaced):
    return archive.add_meta_to_db(db, metadata, replaced)


def delete_obsolete(obsolete):
    return archive.delete_obsolete(obsolete)


def copy_to_archive(paths, target_dir):
    return archive.copy_to_archive(paths, target_dir)


def process_content_files(content):
    return archive.process_content_files(content)


def process_content(db, to_add, to_replace, to_delete, to_copy):
    return archive.process_content(db,
                                   to_add,
                                   to_replace,
                                   to_delete,
                                   to_copy)


def process(db, content, no_file_ops=False):
    return archive.process(db, content, no_file_ops=no_file_ops)


def add_to_archive(hashes):
    return archive.add_to_archive(hashes)


def remove_from_archive(hashes):
    return archive.remove_from_archive(hashes)


def reload_data(db):
    return archive.reload_data(db)


def clear_and_reload(db):
    return archive.clear_and_reload(db)


def zipball_count():
    return archive.zipball_count()


def last_update():
    return archive.last_update()


def add_view(md5):
    return archive.add_view(md5)


def add_tags(meta, tags):
    return archive.add_tags(meta, tags)


def remove_tags(meta, tags):
    return archive.remove_tags(meta, tags)


def get_tag_name(tag_id):
    return archive.get_tag_name(tag_id)


def get_tag_cloud():
    return archive.get_tag_cloud()


def needs_formatting(md5):
    return archive.needs_formatting(md5)


def parse_size(size):
    """ Parses size with B, K, M, or G suffix and returns in size bytes

    :param size:    human-readable size with suffix
    :returns:       size in bytes or 0 if source string is using invalid
                    notation
    """
    size = size.strip().lower()
    if size[-1] not in 'bkmg':
        suffix = 'b'
    else:
        suffix = size[-1]
        size = size[:-1]
    try:
        size = float(size)
    except ValueError:
        return 0
    return size * FACTORS[suffix]
