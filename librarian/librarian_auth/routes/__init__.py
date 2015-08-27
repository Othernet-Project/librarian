from . import auth
from . import emergency_reset


def routes(config):
    return (
        (
            'auth:login_form',
            auth.show_login_form,
            'GET',
            '/login/',
            {}
        ), (
            'auth:login',
            auth.login,
            'POST',
            '/login/',
            {}
        ), (
            'auth:logout',
            auth.logout,
            'GET',
            '/logout/',
            {}
        ), (
            'auth:reset_form',
            auth.show_reset_form,
            'GET',
            '/reset-password/',
            {}
        ), (
            'auth:reset',
            auth.reset,
            'POST',
            '/reset-password/',
            {}
        ), (
            'emergency:reset_form',
            emergency_reset.show_emergency_reset_form,
            'GET',
            '/emergency/',
            {'skip': ['sessions']}
        ), (
            'emergency:reset',
            emergency_reset.reset,
            'POST',
            '/emergency/',
            {'skip': ['sessions']}
        ),
    )
