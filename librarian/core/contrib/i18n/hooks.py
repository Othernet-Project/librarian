import os

from bottle_utils.i18n import I18NPlugin

from .cmsgs import compile_messages
from .consts import LANGS
from .xmsgs import collect_messages, add_message_source_path


def component_member_loaded(supervisor, member, config):
    add_message_source_path(member['pkg_path'])


def initialize(supervisor):
    if supervisor.config.get('i18n.enabled'):
        supervisor.exts.commands.register('xmsgs',
                                          collect_messages,
                                          '--xmsgs',
                                          action='store_true',
                                          help='collect gettext messages')
        supervisor.exts.commands.register('cmsgs',
                                          compile_messages,
                                          '--cmsgs',
                                          action='store_true',
                                          help='compile gettext messages')
        default_locale = supervisor.config.get('i18n.default_locale', 'en')
        domain = supervisor.config.get('i18n.domain')
        locale_dir = os.path.join(
            supervisor.config['root'],
            supervisor.config.get('localedir', 'locales')
        )
        locales = supervisor.config.get('i18n.locales', ['en'])
        langs = [(code, name) for code, name in LANGS if code in locales]
        supervisor.wsgi = I18NPlugin(supervisor.app,
                                     langs=langs,
                                     default_locale=default_locale,
                                     domain=domain,
                                     locale_dir=locale_dir)
