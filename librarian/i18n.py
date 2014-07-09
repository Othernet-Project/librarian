"""
i18n.py: Localization support for bottle and SimpleTemplate

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

import re
import gettext
from warnings import warn

from bottle import request, redirect, BaseTemplate

from .lazy import lazy, caching_lazy
from . import __version__ as _version, __author__ as _author

__version__ = _version
__author__ = _author
__all__ = ('dummy_gettext', 'dummy_ngettext', 'lazy_gettext', 'lazy_ngettext',
           'full_path', 'i18n_path', 'I18NPlugin',)


def dummy_gettext(message):
    return message


def dummy_ngettext(singular, plural, n):
    if n == 1:
        return singular
    return plural


@lazy
def lazy_gettext(message):
    gettext = request.gettext.gettext
    return gettext(message)


@lazy
def lazy_ngettext(singular, plural, n):
    ngettext = request.gettext.ngettext
    return ngettext(singular, plural, n)


def full_path():
    path = request.fullpath
    qs = request.query_string
    if qs:
        return '%s?%s' % (path, qs)
    return path

@lazy
def i18n_path(path=None, locale=None):
    path = path or full_path()
    locale = locale or request.locale
    return '/{}{}'.format(locale.lower(), path)


class I18NWarning(RuntimeWarning):
    pass


class I18NPlugin(object):
    """ Bottle plugin and WSGI middleware for handling i18n routes

    This class is a middleware. However, if the ``app`` argument is a
    ``Bottle`` object (bottle app), it will also install itself as a plugin.
    The plugin follows the `version 2 API`_ and implements the ``apply()``
    method which applies the plugin to all routes. The plugin and middleware
    parts were merged into one class because they depend on each other and
    can't really be used separately.

    During initialization, the class will set up references to locales,
    directory paths, and build a mapping between locale names and appropriate
    gettext translation APIs. The translation APIs are created using the
    ``gettext.translation()`` call. This call tries to access matching MO file
    in the locale directory, and will emit a warning if such file is not found.
    If a MO file does not exist for a given locale, or it is not readable, the
    API for that locale will be downgraded to generic `gettext API`_.

    The class will also update the ``bottle.BaseTemplate.defaults`` dict with
    translation-related methods so they are always available in templates (at
    least those that are rendered using bottle's API. The following variables
    become available in all templates:

    - ``_``: alias for ``lazy_gettext``
    - ``gettext``: alias for ``lazy_gettext``
    - ``ngettext``: alias for ``lazy_ngettext``
    - ``i18n_path``
    - ``languages``: iterable containing available languages as ``(locale,
      name)`` tuples

    The middleware itself derives the desired locale from the URL. It does not
    read cookies or headers. It only looks for the ``/ll_cc/`` prefix where
    ``ll`` is the two-ltter language ID, and ``cc`` is country code. If it
    finds such a prefix, it will set the locale in the envionment dict
    (``LOCALE`` key) and fix the path so it doesn't include the prefix. This
    allows the bottle app to have routes matching any number of locales. If it
    doesn't find the prefix, it will redirect to the default locale.

    If there is no appropriate locale, and ``LOCALE`` key is therfore set to
    ``None``, the plugin will automatically respond with a 302 redirect to a
    location of the default locale.

    The plugin reads the ``LOCALE`` key set by the middleware, and aliases the
    API for that locale as ``request.gettext``. It also sets ``request.locale``
    attribute to the selected locale. These attributes are used by the
    ``lazy_gettext`` and ``lazy_ngettext``, as well as ``i18n_path`` functions.

    The plugin installation during initialization can be competely suppressed,
    if you wish (e.g., you wish to apply the plugin yourself some other way).

    .. _gettext API: https://docs.python.org/3.4/library/gettext.html
    """

    name = 'i18n'
    api = 2

    def __init__(self, app, langs, default_locale, locale_dir,
                 domain='messages', noplugin=False):
        """
        The locale directory should be in a format which
        ``gettext.translations()`` understands. This is a path that contains a
        subtree matching this format:

            locale_dir/LANG/LC_MESSAGES/DOMAIN.mo

        The ``LANG`` should match any of the supported languages, and
        ``DOMAIN`` should match the specified domain.

        .. _version 2 API: http://bottlepy.org/docs/0.12/plugindev.html

        :param app:             ``Bottle`` object
        :param langs:           iterable containing languages as ``(locale,
                                name)`` tuples
        :param default_locale:  default locale
        :param locale_dir:      directory containing translations
        :param domain:          the gettext domain
        :param noplugin:
        """
        self.app = app
        self.langs = langs
        self.locales = [lang[0] for lang in langs]
        self.default_locale = default_locale
        self.locale_dir = locale_dir
        self.domain = domain

        self.gettext_apis = {}
        # Prepare gettext class-based APIs for consumption
        for locale in self.locales:
            try:
                api = gettext.translation(domain, locale_dir,
                                          languages=[locale])
            except OSError:
                api = gettext
                warn(I18NWarning("No MO file found for '%s' locale" % locale))
            self.gettext_apis[locale] = api

        BaseTemplate.defaults.update({
            '_': lazy_gettext,
            'gettext': lazy_gettext,
            'ngettext': lazy_ngettext,
            'i18n_path': i18n_path,
            'languages': langs,
        })

        if noplugin:
            return
        try:
            self.app.install(self)
        except AttributeError:
            # It's not strictly necessary to install the plugin automatically
            # like this, especially if there are other WSGI middleware in the
            # stack. We should still warn. It may be unintentional.
            warn(I18NWarning('I18NPlugin: Not a bottle app. Skipping '
                             'plugin installation.'))

    def __call__(self, e, h):
        """ Middleware """
        path = e['PATH_INFO']
        e['LOCALE'] = locale = self.match_locale(path)
        e['ORIGINAL_PATH'] = path
        if locale:
            e['PATH_INFO'] = self.strip_prefix(path, locale)
        return self.app(e, h)

    def apply(self, callback, route):
        """ Bottle plugin """
        ignored = route.config.get('no_i18n', False)
        def wrapper(*args, **kwargs):
            if not ignored:
                request.locale = locale = request.environ.get('LOCALE')
                if locale not in self.locales:
                    # If no locale had been specified, redirect to default one
                    path = request.environ.get('ORIGINA_PATH', '/')
                    redirect(i18n_path(path, self.default_locale))
                request.gettext = self.gettext_apis[locale]
            return callback(*args, **kwargs)
        return wrapper

    def match_locale(self, path):
        path_prefix = path.split('/')[1].lower()
        for locale in self.locales:
            if path_prefix == locale.lower():
                return locale
        return None

    @staticmethod
    def strip_prefix(path, locale):
        return path[len(locale) + 1:]

