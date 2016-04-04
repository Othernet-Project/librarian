"""
emergency_reset.py: Emergency reset handlers

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import os

from bottle import request, abort, redirect
from bottle_utils.ajax import roca_view
from bottle_utils.i18n import i18n_url, lazy_gettext as _
from bottle_utils.csrf import csrf_protect, csrf_token

from librarian_core.contrib.auth.users import User
from librarian_core.contrib.templates.renderer import template

from ..forms import EmergencyResetForm


@roca_view('auth/emergency_reset', 'auth/_emergency_reset', template_func=template)
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
                reset_token=User.generate_reset_token())


@roca_view('auth/emergency_reset', 'auth/_emergency_reset', template_func=template)
@csrf_protect
def reset():
    reset_token = request.params.get('reset_token')
    form = EmergencyResetForm(request.params)
    if not form.is_valid():
        return dict(form=form,
                    reset_token=reset_token)

    request.db.auth.execute(request.db.auth.Delete('users'))
    request.db.sessions.execute(request.db.sessions.Delete('sessions'))
    username = form.processed_data['username']
    User.create(username,
                form.processed_data['password1'],
                is_superuser=True,
                db=request.db.auth,
                reset_token=reset_token)
    return template('ui/feedback.tpl',
                    # Translators, used as page title on feedback page
                    page_title=_('Emergency reset successful'),
                    # Translators, used as link label on feedback page in "You
                    # will be taken to log-in page..."
                    redirect_target=_('log-in page'),
                    # Translators, shown after emergency reset
                    message=_("You may now log in as "
                              "'{username}'.").format(username=username),
                    status='success',
                    redirect_url=i18n_url('auth:login_form'))
