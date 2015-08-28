from librarian.librarian_menu.menu import MenuItem

from bottle import request
from bottle_utils.i18n import lazy_gettext as _


class FilesMenuItem(MenuItem):
    name = 'files'
    label = _("Files")
    icon_class = 'files'
    route = 'files:list'

    def is_visible(self):
        return hasattr(request, 'user') and request.user.is_superuser
