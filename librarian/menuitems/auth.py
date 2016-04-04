from bottle import request
from bottle_utils.i18n import i18n_url, lazy_gettext as _

from librarian_menu.menu import MenuItem


class LogoutMenuItem(MenuItem):
    name = 'logout'
    label = _("Log out")
    icon_class = 'logout'
    route = 'auth:logout'

    def is_visible(self):
        return hasattr(request, 'user') and request.user.is_authenticated

    def get_path(self):
        return i18n_url(self.route) + '?next=' + request.fullpath
