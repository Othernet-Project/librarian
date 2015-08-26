from bottle import request

from librarian.librarian_setup.setup import setup_wizard

from .forms import RegistrationForm
from .helpers import generate_reset_token, create_user


def has_no_superuser():
    db = request.db.sessions
    query = db.Select(sets='users', where='is_superuser = ?')
    db.query(query, True)
    return db.result is None


@setup_wizard.register_step('superuser', template='setup/step_superuser.tpl',
                            method='GET', index=3, test=has_no_superuser)
def setup_superuser_form():
    return dict(form=RegistrationForm(),
                reset_token=generate_reset_token())


@setup_wizard.register_step('superuser', template='setup/step_superuser.tpl',
                            method='POST', index=3, test=has_no_superuser)
def setup_superuser():
    form = RegistrationForm(request.forms)
    reset_token = request.params.get('reset_token')
    if not form.is_valid():
        return dict(successful=False, form=form, reset_token=reset_token)

    create_user(form.processed_data['username'],
                form.processed_data['password1'],
                is_superuser=True,
                db=request.db.sessions,
                overwrite=True,
                reset_token=reset_token)
    return dict(successful=True)
