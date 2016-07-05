from bottle_utils import form
from bottle_utils.html import hsize
from bottle_utils.i18n import lazy_gettext as _

from ..data import storage


class ConsolidateForm(form.Form):
    messages = {
        # There is already a task running, so we can't schedule another one
        # Translators, error message shown when moving of files is
        # attempted while another move task is already running.
        'already_running': _('A scheduled move is already running. You will '
                             'be notified when it finishes. Please try again '
                             'once the current operation is finished.'),
        # Translators, error message shown when destination drive is removed
        # or otherwise becomes inaccessible before files are moved to it.
        'storage_not_found': _('Destination drive disappeared. Please '
                               'reattach the drive and retry.'),
        # Translators, error message shown when moving files to a storage
        # device where no other storage devices are present other than the
        # target device.
        'no_move_target': _('There are no other drives to move files from.'),
        # Translators, error message shown when moving files to a storage
        # device, where no movable files are present.
        'nothing_to_move': _('There are no files to be moved.'),
        # Translators, error message shown when moving files to a storage
        # device, that has not enough free space.
        'not_enough_space': _('Not enough free space. {size} needed.'),
    }
    storage_id = form.StringField(validators=[form.Required()])

    def validate(self):
        active_storage_id = storage.get_consolidate_status()
        if active_storage_id:
            raise form.ValidationError('already_running', {})
        # Perform preflight check
        storages = storage.get_content_storages()
        storage_id = self.processed_data['storage_id']
        try:
            dest = storages.move_preflight(storage_id)
        except storage.NotFoundError:
            raise form.ValidationError('storage_not_found', {})
        except storage.NoMoveTargetError:
            raise form.ValidationError('no_move_target', {})
        except storage.NothingToMoveError:
            raise form.ValidationError('nothing_to_move', {})
        except storage.CapacityError as err:
            params = dict(size=hsize(err.capacity))
            raise form.ValidationError('not_enough_space', params)
        else:
            self.processed_data['storages'] = storages
            self.processed_data['dest'] = dest
