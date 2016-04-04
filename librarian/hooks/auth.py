from librarian_core.contrib.auth.utils import generate_random_key
from librarian_setup.decorators import autoconfigure

from .menuitems import LogoutMenuItem
from .setup import has_no_superuser, setup_superuser_form, setup_superuser


autoconfigure('session.secret')(generate_random_key)
autoconfigure('csrf.secret')(generate_random_key)


def initialize(supervisor):
    supervisor.exts.menuitems.register(LogoutMenuItem)
    # register setup wizard step
    setup_wizard = supervisor.exts.setup_wizard
    setup_wizard.register('superuser',
                          setup_superuser_form,
                          template='setup/step_superuser.tpl',
                          method='GET',
                          index=3,
                          test=has_no_superuser)
    setup_wizard.register('superuser',
                          setup_superuser,
                          template='setup/step_superuser.tpl',
                          method='POST',
                          index=3,
                          test=has_no_superuser)
