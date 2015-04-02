# -*- coding: utf-8 -*-
"""
lang.py: Locale constants

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from __future__ import unicode_literals

import babel
from bottle_utils.i18n import lazy_gettext as _

# Helper functions are defined above the constants because we used them to
# generate runtime constants.


def to_locale(code):
    """ Return `babel.locale` instance matching the locale code """
    return babel.Locale(*babel.parse_locale(code))


def lang_name(code):
    """ Return native language name for locale code """
    return to_locale(code).get_display_name()


def lang_list(locales):
    """ Return a list of locale-language two-tuples given list of locales """
    return [(l, lang_name(l)) for l in locales]


def lang_name_getter(ltuple):
    """ Getter used for sorting language names """
    return ltuple[1].lower()


# These are locales used for language filtering and similar cases. We want them
# to be as generic as possible, so we only use the main locale without
# territory part. We assume that a consumer of territorry-specific locale is
# able to (at least to an extent) understand generic locale (e.g., pt_BR is
# similar enough to pt).
LOCALES = [l for l in babel.localedata.locale_identifiers() if len(l) == 2]
LOCALES.sort()

UI_LOCALES = (
    'ar',
    'bn',
    'ca',
    'da',
    'de',
    'en',
    'es',
    'fa',
    'fr',
    'hi',
    'hr',
    #'ht',   # disabled due to bug in Python gettext
    'hu',
    'it',
    'ja',
    'kn',
    'ko',
    'lt',
    'nb',
    'ne',
    'nl',
    'pt',
    'pt_BR',
    'ro',
    'ru',
    'sr_Latn',
    'sv',
    'ta',
    'th',
    'tr',
    'ur',
    'zh',
)

LANGS = list(sorted(lang_list(LOCALES), key=lang_name_getter))
SELECT_LANGS = [('', _('any language'))] + LANGS
UI_LANGS = list(sorted(lang_list(UI_LOCALES), key=lang_name_getter))
RTL_LANGS = ['ar', 'he', 'ur', 'yi', 'ji', 'iw', 'fa']
DEFAULT_LOCALE = 'en'
