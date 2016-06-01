from bottle_utils import form
from bottle_utils.i18n import lazy_gettext as _

from ..core.exts import ext_container as exts


class DeleteForm(form.Form):
    messages = {
        # Translators, used as message when a file's removal is
        # retried, but it was already deleted before
        'already_deleted': _("The specified file has already been removed.")
    }
    path = form.HiddenField(_("Path"), validators=[form.Required()])

    def postprocess_path(self, value):
        if not exts.fsal.exists(value):
            raise form.ValidationError('already_deleted', {})
        return value
