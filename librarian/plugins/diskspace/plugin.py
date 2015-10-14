"""
plugin.py: Diskspace plugin

Display application log on dashboard.

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import logging
import os

from bottle import request, MultiDict, abort

from bottle_utils.html import hsize
from bottle_utils.i18n import lazy_ngettext, lazy_gettext as _, i18n_path

from ...core.archive import Archive
from ...utils.template import view
from ...utils.notifications import Notification
from ...lib.auth import login_required
from ...lib.paginator import Paginator

from ..dashboard import DashboardPlugin
from ..exceptions import NotSupportedError

from . import zipballs


def row_to_dict(row):
    return dict((key, row[key]) for key in row.keys())


def notify_cleanup(app, notifications, DELAY):
    (free, _) = zipballs.free_space(config=app.config)
    needed_space = zipballs.needed_space(free, config=app.config)
    if not needed_space:
        return

    notifications.send(hsize(needed_space), category='diskspace',
                       db=app.config['db']['sessions'])
    app.exts.tasks.schedule(notify_cleanup, args=(app, notifications, DELAY,),
                            delay=DELAY)


def install_cleanup_notification(app):
    notifications = Notification
    try:
        os.statvfs
    except AttributeError:
        raise NotSupportedError(
            'Disk space information not available on this platform')
    START = 15
    DELAY = 1200
    app.exts.tasks.schedule(notify_cleanup, args=(app, notifications, DELAY,),
                            delay=START)


def auto_cleanup(app):
    (free, _) = zipballs.free_space(config=app.config)
    needed_space = zipballs.needed_space(free, config=app.config)
    if not needed_space:
        return

    archive = Archive.setup(app.config['librarian.backend'],
                            app.databases.main,
                            unpackdir=app.config['content.unpackdir'],
                            contentdir=app.config['content.contentdir'],
                            spooldir=app.config['content.spooldir'],
                            meta_filename=app.config['content.metadata'])
    deletable_content = zipballs.cleanup_list(free,
                                              db=app.databases.main,
                                              config=app.config)
    content_ids = [content['md5'] for content in deletable_content]
    deleted = archive.remove_from_archive(content_ids)
    msg = "Automatic cleanup has deleted {0} content entries.".format(deleted)
    logging.info(msg)


@login_required()
@view('diskspace/cleanup', message=None, vals=MultiDict())
def cleanup_list():
    """ Render a list of items that can be deleted """
    db = request.db['main']
    config = request.app.config
    free = zipballs.free_space()[0]
    # get count to trick paginator
    db.query("""
             SELECT COUNT(md5) AS count
             FROM zipballs;
             """)
    count = db.result['count']
    page = Paginator.parse_page(request.params)
    per_page = Paginator.parse_per_page(request.params)
    paginator = Paginator(range(count), page, per_page)

    limit = page * per_page
    offset = (page - 1) * per_page
    meta = zipballs.list_all_zipballs(limit, offset, db=db, config=config)

    res = {'pager': paginator, 'metadata': meta,
            'needed': zipballs.needed_space(free)}

    check = request.params.get('check')
    if check != None:
        checked = check.split(',')
        selected = [z for z in meta if z['md5'] in checked]
        if not selected:
            # Translators, used as message to user when clean-up is started
            # without selecting any content
            message = _('No content selected')
            values = []
        else:
            values = {
                name: md5 for (name, md5) in
                (('selection-{}'.format(zipball['md5']), zipball['md5'])
                for zipball in selected)}
            tot = hsize(sum([s['size'] for s in selected]))
            message = str(
                # Translators, used when user is previewing clean-up, %s is
                # replaced by amount of content that can be freed in bytes,
                # KB, MB, etc
                _('%s can be freed by removing selected content')) % tot
        res['message'] = message
        res['vals'] = values
    return res


def get_selected(forms, prefix="selection-"):
    """ Returns a list of md5s from a FormsDict object and a kwarg 'prefix' """
    md5s = []
    for key, value in forms.items():
        if key[0:len(prefix)] != prefix:
            continue
        md5s.append(value)
    return md5s


@login_required()
@view('feedback')
def cleanup():
    forms = request.forms
    db = request.db['main']
    config = request.app.config
    page = Paginator.parse_page(request.params)
    per_page = Paginator.parse_per_page(request.params)

    action = forms.get('action', 'check')
    if action not in ['delete']:
        # Translators, used as response to innvalid HTTP request
        abort(400, _('Invalid request'))

    limit = page * per_page
    offset = (page - 1) * per_page
    cleanup = list(zipballs.list_all_zipballs(limit, offset, db=db, config=config))
    selected = get_selected(forms)
    metadata = list(cleanup)
    selected = [z for z in metadata if z['md5'] in selected]
    conf = request.app.config
    archive = Archive.setup(conf['librarian.backend'],
                            request.db.main,
                            unpackdir=conf['content.unpackdir'],
                            contentdir=conf['content.contentdir'],
                            spooldir=conf['content.spooldir'],
                            meta_filename=conf['content.metadata'])
    if selected:
        archive.remove_from_archive([z['md5'] for z in selected])
        request.app.exts.cache.invalidate(prefix='content')
        # Translators, used as confirmation message after the chosen updates were
        # successfully removed from the library
        selected_len = len(selected)
        message = lazy_ngettext(
            "Content has been removed from the Library.",
            "{update_count} updates have been removed from the Library.",
            selected_len
        ).format(update_count=selected_len)
        return dict(status='success',
            page_title='Library Clean-Up',
            message=message,
            redirect_url=i18n_path('/p/diskspace/cleanup/'),
            redirect_target=_("Cleanup"))
    else:
        message = _("Nothing to delete.\n The library has not been modified.")
        return dict(status='error',
            page_title='Library Clean-Up',
            message=message,
            redirect_url=i18n_path('/p/diskspace/cleanup/'),
            redirect_target=_("Cleanup"))


def install(app, route):
    try:
        os.statvfs
    except AttributeError:
        raise NotSupportedError(
            'Disk space information not available on this platform')

    if app.config.get('storage.auto_cleanup', False):
        app.events.subscribe('background', auto_cleanup)

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
