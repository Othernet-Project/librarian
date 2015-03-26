import bottle

from ..lib import auth
from ..lib.i18n import lazy_gettext as _


@bottle.view('login')
def login():
    if bottle.request.method == 'POST':
        next_path = bottle.request.forms.get('next', '/')
        username = bottle.request.forms.get('username', '')
        password = bottle.request.forms.get('password', '')
        if auth.login_user(username, password):
            bottle.redirect(next_path)

        return {'username': username,
                'next': next_path,
                'error': _("Please enter the correct username and password.")}

    next_path = bottle.request.query.get('next', '/')
    return {'username': '', 'next': next_path, 'error': None}
