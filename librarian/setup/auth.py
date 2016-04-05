from bottle import request

from ..core.contrib.auth.helpers import identify_database
from ..core.contrib.auth.users import User
from ..core.contrib.auth.utils import generate_random_key
from ..decorators.setup import autoconfigure
from ..forms.auth import RegistrationForm


autoconfigure('session.secret')(generate_random_key)
autoconfigure('csrf.secret')(generate_random_key)


class SuperuserStep:
    name = 'superuser'
    index = 3
    template = 'setup/step_superuser.tpl',

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

        User.create(form.processed_data['username'],
                    form.processed_data['password1'],
                    is_superuser=True,
                    db=request.db.auth,
                    reset_token=reset_token)
        return dict(successful=True)
