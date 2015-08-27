from bottle import request
from bottle_utils.i18n import lazy_gettext as _

from librarian.librarian_menu.menu import MenuItem

from .helpers import filter_downloads


class HomeMenuItem(MenuItem):
    label = _("Home")
    route = 'content:list'


class ContentMenuItem(MenuItem):
    label = _("Library")
    icon_class = 'library'
    route = 'content:list'


class UpdatesMenuItem(MenuItem):
    icon_class = 'updates'
    route = 'downloads:list'

    def _updates(self):
        return len(filter_downloads(lang=None))

    def is_visible(self):
        is_admin = hasattr(request, 'user') and request.user.is_superuser
        return is_admin and self._updates() > 0

    @property
    def label(self):
        update_count = self._updates()
        if update_count > 99:
            update_count = '!'
        lbl = _("Updates")
        if update_count > 0:
            lbl += ' <span class="count">{0}</span>'.format(update_count)
        return lbl
