from __future__ import unicode_literals

import os
import functools
import itertools
import logging

from bottle import request

from librarian_core.exts import ext_container as exts
from librarian_core.utils import is_string

from .facets import Facets
from .archive import FacetsArchive
from .processors import (get_facet_processors,
                         split_name,
                         is_html_file,
                         HtmlFacetProcessor)


class IterLookup(object):
    """
    This object wraps an iterable, and returns an item with specified
    characteristic while also creating a lookup table of items that were
    missed speeding up lookups for those items the next time lookup is
    performed.
    """

    def __init__(self, iterable, key=lambda x: x):
        """
        The ``key`` argument can be used to specify the lookup value. This
        argument should be a function that takes an object and returns a value
        that will be used in lookups.
        """
        self.iterable = ((key(i), i) for i in iterable)
        self.lut = {}

    def get(self, val):
        if val in self.lut:
            return self.lut[val]
        for v, i in self.iterable:
            self.lut[v] = i
            if v == val:
                return i
        # The object was not found
        raise KeyError('No object for key {}'.format(val))


def to_list(func):
    """In case a single string parameter is passed to the function wrapped
    with this decorator, the single parameter will be wrapped in a list."""
    @functools.wraps(func)
    def wrapper(self, arg, **kwargs):
        if is_string(arg):
            arg = [arg]
        return func(self, arg, **kwargs)
    return wrapper


def get_archive(db=None, config=None):
    if not db:
        db = exts.databases.facets
    if not config:
        config = request.app.supervisor.config
    fsal = exts.fsal
    return FacetsArchive(db=db, config=config, fsal=fsal)


def get_facets(paths, partial=True, facet_type=None):
    supervisor = request.app.supervisor
    archive = get_archive()
    schedule_paths = []
    for path in paths:
        facets = archive.get_facets(path, facet_type=facet_type)
        if not facets:
            logging.debug("Facets not found for '{}'."
                          " Scheduling generation".format(path))
            schedule_paths.append(path)
            if partial:
                facets = generate_partial_facets(path, supervisor)
        yield facets
    if schedule_paths:
        schedule_facets_generation(supervisor.config, paths=schedule_paths,
                                   archive=archive)


def get_dir_facets(path, files, partial=False, facet_type=None):
    """
    Return facets for a specified directory path, and use the file list to
    schedule facet generation when files are missing facets.

    The ``files`` argument is expected to be an iterable of all files under the
    specified path. Facets are not returned for any paths not found in this
    iterable.
    """
    # TODO: Factor out duplication of code from get_facets()
    supervisor = request.app.supervisor
    archive = get_archive()
    facets = archive.get_all_facets(path, facet_type)
    facets = IterLookup(facets, key=lambda x: x['file'])
    schedule_paths = []
    for f in files:
        try:
            facet = facets.get(f)
        except KeyError:
            fpath = os.path.join(path, f)
            logging.debug("Facets not found for '%s'."
                          " Scheduling generation", fpath)
            schedule_paths.append(path)
            if partial:
                facet = generate_partial_facets(fpath, supervisor)
            else:
                facet = {}
        yield facet
    if schedule_paths:
        schedule_facets_generation(supervisor.config, paths=schedule_paths,
                                   archive=archive)


def find_html_index(paths, any_html=True):
    first_html_file = None
    best_html_file, best_html_index = (None, 10000)
    for path in paths:
        fname = os.path.basename(path)
        name, ext = split_name(fname)
        if is_html_file(ext):
            first_html_file = first_html_file or fname
            for i, index_name in enumerate(HtmlFacetProcessor.INDEX_NAMES):
                if name == index_name and i < best_html_index:
                    best_html_file = fname
                    best_html_index = i
    result = best_html_file
    if not result and any_html:
        result = first_html_file
    return result


def get_facet_types(paths):
    facet_types = ['generic', 'updates']
    for path in paths:
        types = [p.name for p in get_facet_processors(path)]
        facet_types.extend(types)
    return list(set(facet_types))


def filter_by_facet_type(paths, facet_type):
    return itertools.ifilter(lambda path: is_facet_valid(path, facet_type),
                             paths)


def is_facet_valid(path, facet_type):
    processors = get_facet_processors(path)
    for p in processors:
        if p.name == facet_type:
            return True
    return False


def generate_partial_facets(path, supervisor):
    fsal = exts.fsal
    success, fso = fsal.get_fso(path)
    if not success:
        return None

    facets = FacetsArchive.create_partial(path)
    for processor in get_facet_processors(path):
        processor.process_file(facets, path, partial=True)
    return Facets(supervisor, path, facets)


def schedule_facets_generation(config, *args, **kwargs):
    delay = config.get('facets.ondemand_delay', 0)
    exts.tasks.schedule(generate_facets,
                        args=args,
                        kwargs=kwargs,
                        delay=delay)


def generate_facets(paths, archive):
    for path in paths:
        logging.debug(u'Scheduled facet generation triggered for {}'.format(
            path))
        success, fso = exts.fsal.get_fso(path)
        if not success:
            logging.debug(u'Facet gen cancelled. {} does not exist'.format(
                path))
            continue
        facets = archive.get_facets(path)
        if facets:
            logging.debug(u'Facets already generated for {}'.format(
                path))
            continue
        logging.debug(u"Generating facets for '{}'".format(path))
        archive.update_facets(path)


# TODO: Remove this after facets become stable
def log_facets(prefix, facets):
    import pprint
    import logging
    logging.debug('{} {}'.format(prefix, pprint.pformat(dict(facets))))
