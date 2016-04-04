# -*- coding: utf-8 -*-
"""
lang.py: Locale constants

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from __future__ import unicode_literals

from bottle_utils.i18n import lazy_gettext as _

from librarian_core.contrib.i18n.consts import LOCALES, LANGS
from librarian_core.contrib.templates.decorators import template_helper


SELECT_LANGS = [('', _('any language'))] + LANGS
RTL_LANGS = ['ar', 'he', 'ur', 'yi', 'ji', 'iw', 'fa']


def lang_name(code):
    """ Return native language name for locale code """
    return LOCALES[code]


@template_helper
def lang_name_safe(code):
    """ Return native language name for locale code """
    try:
        return lang_name(code)
    except KeyError:
        return _('unknown')


@template_helper
def is_rtl(code):
    return code in RTL_LANGS


@template_helper
def dir(code):
    return 'rtl' if code in RTL_LANGS else 'auto'


@template_helper
def i18n_attrs(lang):
    s = ''
    if lang:
        # XXX: Do we want to keep the leading space?
        s += ' lang="%s"' % lang
    if template_helper.is_rtl(lang):
        s += ' dir="rtl"'
    return s

