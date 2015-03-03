# -*- coding: utf-8 -*-
"""
lang.py: Locale constants

Copyright 2014-2015, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

LOCALES = [
    ('ar',    'اللغة العربية'),
    ('bn',    'বাংলা'),
    ('ca',    'català'),
    ('da',    'Dansk'),
    ('de',    'Deutsch'),
    ('en',    'English'),
    ('es',    'español'),
    ('fa',    'فارسى'),
    ('fr',    'français'),
    ('hi',    'हिन्दी'),
    ('hr',    'hrvatski'),
    # ('ht',    'Kreyòl ayisyen'),  # disabled due to bug in Python gettext
    ('hu',    'magyar'),
    ('it',    'Italiano'),
    ('jp',    '日本語'),
    ('kn',    'ಕನ್ನಡ'),
    ('ko',    '한국어'),
    ('lt',    'lietuvių kalba'),
    ('nb',    'Norsk'),
    ('ne',    'नेपाली'),
    ('nl',    'Nederlands'),
    ('pt',    'português'),
    ('pt_BR', 'português brasileiro'),
    ('ro',    'română'),
    ('ru',    'Русский'),
    ('sr',    'srpski'),
    ('sv',    'Svensk'),
    ('ta',    'தமிழ்'),
    ('th',    'ภาษาไทย'),
    ('tr',    'Türkçe'),
    ('ur',    'اردو'),
    ('zh',    '中文'),
]

RTL_LANGS = ['ar', 'he', 'ur', 'yi', 'ji', 'iw', 'fa']
DEFAULT_LOCALE = 'en'
