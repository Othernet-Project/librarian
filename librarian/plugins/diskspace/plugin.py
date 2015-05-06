"""
plugin.py: Diskspace plugin

Display application log on dashboard.

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os

from bottle import request, mako_view as view, redirect, MultiDict, abort

from ...core.archive import Archive

from bottle_utils.html import hsize
from bottle_utils.i18n import lazy_gettext as _, i18n_url

from ..dashboard import DashboardPlugin
from ..exceptions import NotSupportedError

from . import zipballs


@view('diskspace/cleanup', message=None, vals=MultiDict())
def cleanup_list():
    """ Render a list of items that can be deleted """
    free = zipballs.free_space()[0]
    return {'metadata': zipballs.cleanup_list(free),
            'needed': zipballs.needed_space(free)}


@view('diskspace/cleanup', message=None, vals=MultiDict())
def cleanup():
    forms = request.forms
    action = forms.get('action', 'check')
    if action not in ['check', 'delete']:
        # Translators, used as response to innvalid HTTP request
        abort(400, _('Invalid request'))
    free = zipballs.free_space()[0]
    cleanup = list(zipballs.cleanup_list(free))
    selected = forms.getall('selection')
    metadata = list(cleanup)
    selected = [z for z in metadata if z['md5'] in selected]
    if action == 'check':
        if not selected:
            # Translators, used as message to user when clean-up is started
            # without selecting any content
            message = _('No content selected')
        else:
            tot = hsize(sum([s['size'] for s in selected]))
            message = str(
                # Translators, used when user is previewing clean-up, %s is
                # replaced by amount of content that can be freed in bytes,
                # KB, MB, etc
                _('%s can be freed by removing selected content')) % tot
        return {'vals': forms, 'metadata': metadata, 'message': message,
                'needed': zipballs.needed_space(free)}
    else:
        conf = request.app.config
        archive = Archive.setup(conf['librarian.backend'],
                                request.db.main,
                                contentdir=conf['content.contentdir'],
                                spooldir=conf['content.spooldir'],
                                meta_filename=conf['content.metadata'])
        if selected:
            archive.remove_from_archive([z['md5'] for z in selected])
            redirect(i18n_url('content:list'))
        else:
            # Translators, error message shown on clean-up page when there was
            # no deletable content
            message = _('Nothing to delete')
        return {'vals': MultiDict(), 'metadata': cleanup,
                'message': message, 'needed': archive.needed_space()}


def install(app, route):
    try:
        os.statvfs
    except AttributeError:
        raise NotSupportedError(
            'Disk space information not available on this platform')
    route(
        ('list', cleanup_list, 'GET', '/cleanup/', {}),
        ('cleanup', cleanup, 'POST', '/cleanup/', {}),
    )


class Dashboard(DashboardPlugin):
    # Translators, used as dashboard section title
    heading = _('Content library stats')
    name = 'diskspace'

    def get_context(self):
        free, total = zipballs.free_space()
        count, used = zipballs.used_space()
        needed = zipballs.needed_space(free)
        return dict(free=free, total=total, count=count, used=used,
                    needed=needed)
