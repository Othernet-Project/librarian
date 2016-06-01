from bottle_utils.i18n import lazy_gettext as _

from ..presentation.menu.menu import MenuItem


class FilesMenuItem(MenuItem):
    name = 'files'
    label = _("Files")
    icon_class = 'files'
    route = 'filemanager:list'
    route_args = {'path': ''}
