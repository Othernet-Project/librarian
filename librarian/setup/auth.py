import logging

from bottle import request

from ..core.contrib.auth.helpers import identify_database
from ..core.contrib.auth.users import User
from ..core.contrib.auth.utils import generate_random_key
from ..core.exts import ext_container as exts
from ..forms.auth import RegistrationForm
from ..utils.sysuser import replace_user

DEFAULT_USER = 'outernet'


class SessionSecretGenerator:
    key = 'session.secret'
    fn = staticmethod(generate_random_key)


class CSRFSecretGenerator:
    key = 'csrf.secret'
    fn = staticmethod(generate_random_key)


class SuperuserStep:
    name = 'superuser'
    index = 20
    template = 'setup/step_superuser.tpl'

    @staticmethod
    @identify_database
    def test(db):
        query = db.Select('COUNT(*) as count',
                          sets='users',
                          where="groups LIKE %s")
        result = db.fetchone(query, ('%superuser%',))
        return result['count'] == 0

    @staticmethod
    def get():
        return dict(form=RegistrationForm(),
                    reset_token=User.generate_reset_token())

    @staticmethod
    def post():
        form = RegistrationForm(request.forms)
        reset_token = request.params.get('reset_token')
        if not form.is_valid():
            return dict(successful=False, form=form, reset_token=reset_token)

        username = form.processed_data['username']
        password = form.processed_data['password1']

        User.create(username, password, is_superuser=True,
                    db=exts.databases.librarian, reset_token=reset_token)

        if not exts.config['setup.super_is_system']:
            return dict(successful=True)

        try:
            replace_user(DEFAULT_USER, username, password)
        except RuntimeError:
            # TODO: Decide what to do here
            logging.exception('Failed to create system user')

        return dict(successful=True)
