from bottle import request

from librarian_core.contrib.auth.helpers import identify_database
from librarian_core.contrib.auth.users import User

from .forms import RegistrationForm


@identify_database
def has_no_superuser(db):
    query = db.Select('COUNT(*) as count',
                      sets='users',
                      where="groups LIKE %s")
    result = db.fetchone(query, ('%superuser%',))
    return result['count'] == 0


def setup_superuser_form():
    return dict(form=RegistrationForm(),
                reset_token=User.generate_reset_token())


def setup_superuser():
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
