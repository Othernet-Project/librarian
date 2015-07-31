"""
emergency_reset.py: Emergency reset handlers

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os

from bottle import request, abort, redirect
from bottle_utils.i18n import i18n_url, lazy_gettext as _
from bottle_utils.csrf import csrf_protect, csrf_token

from ..forms.auth import EmergencyResetForm
from ..lib.auth import generate_reset_token, create_user

from ..utils.template import view, template


@view('emergency_reset')
@csrf_token
def show_emergency_reset_form():
    config = request.app.config
    token_path = config.get('emergency.file', '')

    if not os.path.isfile(token_path):
        # Not configured or missing emergency reset token file
        abort(404)

    with open(token_path, 'r') as f:
        token = f.read()
        if not token.strip():
            # Token file is empty, so treat it as missing token file
            abort(404)

    # If user is already logged in, redirect to password reset page instead.
    # Thre's no need to do anything heavy-handed in this case.
    if request.user.is_authenticated:
        return redirect(i18n_url('auth:reset_form'))

    return dict(form=EmergencyResetForm(),
                reset_token=generate_reset_token())


@view('emergency_reset')
@csrf_protect
def reset():
    reset_token = request.params.get('reset_token')
    form = EmergencyResetForm(request.params)
    if not form.is_valid():
        return dict(form=form,
                    reset_token=reset_token)

    db = request.db.sessions
    query = db.Delete('users')
    db.query(query)
    query = db.Delete('sessions')
    db.query(query)
    username = form.processed_data['username']
    create_user(username,
                form.processed_data['password1'],
                is_superuser=True,
                db=request.db.sessions,
                overwrite=True,
                reset_token=reset_token)
    return template('feedback.tpl',
                    # Translators, used as page title on feedback page
                    page_title=_('Emergency reset successful'),
                    # Translators, used as link label on feedback page in "You
                    # will be taken to log-in page..."
                    redirect_target=_('log-in page'),
                    # Translators, shown after emergency reset
                    message=_("You may now log in as "
                              "'%(username)s'.") % {'username': username},
                    status='success',
                    redirect_url=i18n_url('auth:login_form'))


def routes(app):
    return (
        ('emergency:reset_form', show_emergency_reset_form, 'GET',
         '/emergency/', {'skip': ['sessions']}),
        ('emergency:reset', reset, 'POST',
         '/emergency/', {'skip': ['sessions']}),
    )
