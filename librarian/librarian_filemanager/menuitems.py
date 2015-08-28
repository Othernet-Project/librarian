from librarian_menu.menu import MenuItem

from bottle_utils.i18n import lazy_gettext as _


class FilesMenuItem(MenuItem):
    label = _("Files")
    icon_class = 'files'
    route = 'files:list'
