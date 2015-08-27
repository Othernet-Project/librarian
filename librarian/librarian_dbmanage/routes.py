import logging
import os

from bottle import static_file
from bottle_utils.common import unicode
from bottle_utils.i18n import lazy_ngettext, lazy_gettext as _, i18n_url

from librarian.librarian_core.contrib.templates.renderer import view
from librarian.librarian_lock.lock import LockFailureError

from .dbmanage import (get_dbpath,
                       get_backup_path,
                       get_file_url,
                       backup,
                       rebuild)


@view('feedback')
def perform_backup():
    dbpath = get_dbpath()
    bpath = get_backup_path()
    try:
        btime = backup(dbpath, bpath)
        logging.debug('Database backup took %s seconds', btime)
    except AssertionError as err:
        # Translators, error message displayed if database backup fails
        base_msg = _('Database backup could not be completed. '
                     'The following error occurred:')
        message = ' '.join(map(unicode, [base_msg, err.message]))
        status = 'error'
        url = i18n_url('dashboard:main')
        # Translators, redirection target if database backup was successful
        target = _('Dashboard')
    else:
        # Translators, message displayed if database backup was successful
        base_msg = _('Database backup has been completed successfully.')
        took_msg = lazy_ngettext('The operation took %s second',
                                 'The operation took %s seconds',
                                 btime) % round(btime, 2)
        message = ' '.join(map(unicode, [base_msg, took_msg]))
        status = 'success'
        url = get_file_url()
        # Translators, redirection target if database backup was successful
        target = _('the backup folder')

    # Translators, used as page title
    title = _('Database backup')
    return dict(status=status,
                page_title=title,
                message=message,
                redirect_url=url,
                redirect_target=target)


@view('feedback')
def perform_rebuild():
    try:
        rtime = rebuild()
    except LockFailureError:
        logging.debug('DBMANAGE: Global lock could not be acquired')
        # Translators, error message displayed if database rebuild fails
        base_msg = _('Database could not be rebuilt. '
                     'The following error occurred:')
        # Translators, error message displayed when locking fails during
        # database rebuild
        reason = _('Librarian could not enter maintenance mode and '
                   'database rebuild was cancelled. Please make '
                   'sure noone else is using Librarian and '
                   'try again.')
        message = ' '.join(map(unicode, [base_msg, reason]))
        status = 'error'
        url = i18n_url('dashboard:main')
        # Translators, redirection target if database backup was successful
        target = _('Dashboard')
    else:
        # Translators, message displayed if database backup was successful
        base_msg = _('Content database has been rebuilt from scratch. A backup'
                     ' copy of the original database has been created. '
                     'You will find it in the files section.')
        # Translators, message displayed if database backup was successful
        took_msg = lazy_ngettext('The operation took %s second',
                                 'The operation took %s seconds',
                                 rtime) % round(rtime, 2)
        message = ' '.join(map(unicode, [base_msg, took_msg]))
        # Translators, message displayed if database backup was successful
        status = 'success'
        url = i18n_url('content:list')
        # Translators, redirection target if database backup was successful
        target = _('Library')

    # Translators, used as page title
    title = _('Database rebuild')
    return dict(status=status,
                page_title=title,
                message=message,
                redirect_url=url,
                redirect_target=target)


def serve_dbfile():
    dbpath = get_dbpath()
    dbdir = os.path.dirname(dbpath)
    dbname = os.path.basename(dbpath)
    return static_file(dbname, root=dbdir, download=True)


def routes(config):
    return (
        (
            'dbmanage:download',
            serve_dbfile,
            'GET',
            '/dbmanage/librarian.sqlite',
            dict(no_i18n=True)
        ), (
            'dbmanage:backup',
            perform_backup,
            'POST',
            '/dbmanage/backup',
            {}
        ), (
            'dbmanage:rebuild',
            perform_rebuild,
            'POST',
            '/dbmanage/rebuild',
            {}
        ),
    )
