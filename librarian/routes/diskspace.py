import logging

from bottle_utils.i18n import i18n_url, lazy_gettext as _
from streamline import RouteBase, XHRPartialFormRoute

from ..core.contrib.templates.renderer import template
from ..core.exts import ext_container as exts
from ..data import storage
from ..forms.diskspace import ConsolidateForm


gettext = lambda x: x


class ConsolidateState(RouteBase):
    path = '/diskspace/consolidate/state'

    def get(self):
        return dict(active=storage.get_consoildate_status())


class Consolidate(XHRPartialFormRoute):
    """ Gets a ID from request context, gathers a list of all drives and
    moves content from all other drives to the drive with matching ID """
    path = '/diskspace/consolidate/'
    template_func = template
    template_name = 'diskspace/consolidate.tpl'
    partial_template_name = 'diskspace/_consolidate_form.tpl'
    form_factory = ConsolidateForm
    messages = {
        # Translators, message shown when the file moving operation is
        # successfully scheduled
        'started': gettext('Files are now being moved to {destination}. You '
                           'will be notified when the operation is finished.'),
        # Translators, notification displayed if files were moved to
        # external storage successfully
        'success': gettext('Files were successfully moved to {storage_name}'),
        # Translators, notification displayed if moving files to
        # external storage failed
        'failure': gettext('Files could not be moved to {storage_name}'),
        # Translators, notification displayed if moving files to
        # external storage only partially succeeded
        'partial': gettext('Some files failed to copy to {storage_name}'),
    }

    def clear_notifications(self):
        exts.notifications.delete_by_category('consolidate_storage',
                                              exts.databases.notifications)

    def consolidation_notify(self, message, priority):
        exts.notifications.send(message,
                                category='consolidate_storage',
                                dismissable=True,
                                group='superuser',
                                priority=priority,
                                db=exts.databases.notifications)

    def success(self, dest):
        logging.info('Consolidation to %s finished', dest.id)
        msg = self.messages['success'].format(storage_name=dest.humanized_name)
        priority = exts.notifications.NORMAL
        self.consolidation_notify(msg, priority)

    def failure(self, dest):
        logging.error('Consolidation to %s failed', dest.id)
        msg = self.messages['failure'].format(storage_name=dest.humanized_name)
        priority = exts.notifications.URGENT
        self.consolidation_notify(msg, priority)

    def partial(self, dest):
        logging.error('Consolidation %s partially succeeded', dest.id)
        msg = self.messages['partial'].format(storage_name=dest.humanized_name)
        priority = exts.notifications.URGENT
        self.consolidation_notify(msg, priority)

    def get_context(self):
        context = super(Consolidate, self).get_context()
        context.update(storages=storage.get_content_storages(),
                       active_storage_id=storage.get_consoildate_status(),
                       target_id=self.request.params.get('storage_id'))
        return context

    def form_valid(self):
        dest_id = self.form.processed_data['storage_id']
        dest = self.form.processed_data['dest']
        storages = self.form.processed_data['storages']
        args = (dest_id,
                self.clear_notifications,
                self.success,
                self.failure,
                self.partial)
        exts.tasks.schedule(storages.move_content_to, args=args)
        storage.mark_consolidate_started(dest_id)
        msg = self.messages['started'].format(destination=dest.humanized_name)
        if self.request.is_xhr:
            return dict(message=msg)
        # Translators, used as page title when the file moving operation
        # is successfully started
        page_title = _("File consolidation scheduled")
        body = template('ui/feedback',
                        status='success',
                        page_title=page_title,
                        message=msg,
                        redirect_url=i18n_url('dashboard:dashboard'),
                        redirect_target=_("settings"))
        return self.HTTPResponse(body=body)
