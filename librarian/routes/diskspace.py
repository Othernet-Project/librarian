import logging
import functools

from bottle import request
from bottle_utils.ajax import roca_view
from bottle_utils.i18n import i18n_url, lazy_gettext as _
from bottle_utils.html import hsize

from librarian_core.contrib.templates.renderer import template
from librarian_core.exts import ext_container as exts

import storage
from .storage import get_content_storages

gettext = lambda x: x


# Translators, notification displayed if files were moved to
# external storage successfully
CONSOLIDATE_SUCCESS = gettext('Files were successfully moved to '
                              '{storage_name}')

# Translators, notification displayed if moving files to
# external storage failed
CONSOLIDATE_FAILURE = gettext('Files could not be moved to '
                              '{storage_name}')


# Translators, notification displayed if moving files to
# external storage only partially succeeded
CONSOLIDATE_PARTIAL = gettext('Some files failed to copy to '
                              '{storage_name}')


def consolidation_notify(message, priority):
    exts.notifications.send(
        message,
        category='consolidate_storage',
        dismissable=True,
        group='superuser',
        priority=priority,
        db=exts.databases.notifications)


def clear_notifications():
    exts.notifications.delete_by_category('consolidate_storage',
                                          exts.databases.notifications)


def consolidate_ok(dest):
    logging.info('Consolidation to %s finished', dest.id)
    message = CONSOLIDATE_SUCCESS.format(storage_name=dest.humanized_name)
    priority = exts.notifications.NORMAL
    consolidation_notify(message, priority)


def consolidate_err(dest):
    logging.error('Consolidation to %s failed', dest.id)
    message = CONSOLIDATE_FAILURE.format(storage_name=dest.humanized_name)
    priority = exts.notifications.URGENT
    consolidation_notify(message, priority)


def consolidate_partial(dest):
    logging.error('Consolidation %s partially succeeded', dest.id)
    message = CONSOLIDATE_PARTIAL.format(storage_name=dest.humanized_name)
    priority = exts.notifications.URGENT
    consolidation_notify(message, priority)


def with_storages(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        storages = get_content_storages()
        kwargs['storages'] = storages
        return fn(*args, **kwargs)
    return wrapper


def consolidate_state():
    return dict(active=storage.get_consoildate_status())


@roca_view('diskspace/consolidate.tpl', 'diskspace/_consolidate_form.tpl',
           template_func=template)
@with_storages
def show_consolidate_form(storages):
    return dict(storages=storages,
                active_storage_id=storage.get_consoildate_status())


@roca_view('diskspace/consolidate.tpl', 'diskspace/_consolidate_form.tpl',
           template_func=template)
@with_storages
def schedule_consolidate(storages):
    """ Gets a ID from request context, gathers a list of all drives and
    moves content from all other drives to the drive with matching ID """
    supervisor = request.app.supervisor
    tasks = supervisor.exts.tasks
    dest_id = request.params.storage_id
    active_storage_id = storage.get_consoildate_status()

    response_ctx = {
        'storages': storages,
        'target_id': dest_id,
        'active_storage_id': active_storage_id,
    }

    if active_storage_id:
        # There is already a task running, so we can't schedule another one
        # Translators, error message shown when moving of files is
        # attempted while another move task is already running.
        response_ctx['error'] = _('A scheduled move is already running. You '
                                  'will be notified when it finishes. Please '
                                  'try again once the current operation is '
                                  'finished.')
        return response_ctx

    # Perform preflight check
    try:
        dest = storages.move_preflight(dest_id)
    except storage.NotFoundError:
        # Translators, error message shown when destination drive is removed or
        # otherwise becomes inaccessible before files are moved to it.
        response_ctx['error'] = _('Destination drive disappeared. Please '
                                  'reattach the drive and retry.')
        return response_ctx
    except storage.NoMoveTargetError:
        # Translators, error message shown when moving files to a storage
        # device where no other storage devices are present other than the
        # target device.
        response_ctx['error'] = _('There are no other drives to move files '
                                  'from.')
        return response_ctx
    except storage.NothingToMoveError:
        # Translators, error message shown when moving files to a storage
        # device, where no movable files are present.
        response_ctx['error'] = _('There are no files to be moved.')
        return response_ctx
    except storage.CapacityError as err:
        # Not enough space on target drive
        response_ctx['error'] = _(
            "Not enough free space. {size} needed.").format(
                size=hsize(err.capacity))
        return response_ctx

    tasks.schedule(storages.move_content_to,
                   args=(dest_id, clear_notifications, consolidate_ok,
                         consolidate_err, consolidate_partial),
                   periodic=False)
    storage.mark_consolidate_started(dest_id)

    message = _('Files are now being moved to {destination}. You will be '
                'notified when the operation is finished.').format(
                    destination=dest.humanized_name)

    if request.is_xhr:
        response_ctx['message'] = message
        return response_ctx

    return template('ui/feedback',
                    status='success',
                    page_title="File consolidation scheduled",
                    message=message,
                    redirect_url=i18n_url('dashboard:main'),
                    redirect_target=_("settings"))


def routes(app):
    return (
        ('diskspace:show_consolidate_form', show_consolidate_form,
         'GET', '/diskspace/consolidate/', {}),
        ('diskspace:consolidate', schedule_consolidate,
         'POST', '/diskspace/consolidate/', {}),
        ('diskspace:consolidate_state', consolidate_state,
         'GET', '/diskspace/consolidate/state', {})
    )
