"""
test_i18n.py: Unit tests for ``librarian.i18n`` module

Copyright 2014, Outernet Inc.
Some rights reserved.

This software is free software licensed under the terms of GPLv3. See COPYING
file that comes with the source code, or http://www.gnu.org/licenses/gpl.txt.
"""

from unittest import mock

from librarian.lib.i18n import *

MOD = 'librarian.lib.i18n.'


def is_lazy(obj):
    return hasattr(obj, '_eval')


def test_dummy_gettext():
    """ Dummy gettext simply parrots the input """
    _ = dummy_gettext
    assert _('foo') == 'foo', "Should parrot 'foo'"
    assert _('bar') == 'bar', "Should parrot 'bar'"


def test_dummy_ngettext():
    """ Dummy ngettext returns appropriate form """
    _ = dummy_ngettext
    assert _('foo', 'foos', 1) == 'foo', "Should return 'foo'"
    assert _('foo', 'foos', 2) == 'foos', "Should return 'foos'"


def test_lazy_gettext():
    """ Gettext returns lazy object """
    _ = lazy_gettext
    s = _('foo')
    assert is_lazy(s), "Should be a lazy object"


def test_gettext_string():
    """ Lazy ngettext returns lazy object """
    _ = lazy_ngettext
    s = _('foo', 'foos', 1)
    assert is_lazy(s), "Should be a lazy object"


@mock.patch(MOD + 'request')
def test_lazy_gettext_request(request):
    """ Lazy gettext uses ``request.gettext.gettext`` method """
    _ = lazy_gettext
    s = _('foo')
    s = s._eval()
    assert s == request.gettext.gettext.return_value, "Should use gettext"


@mock.patch(MOD + 'request')
def test_lazy_ngettext_request(request):
    """ Lazy ngettext uses ``request.gettext.ngettext`` method """
    _ = lazy_ngettext
    s = _('singular', 'plural', 1)
    s = s._eval()
    assert s == request.gettext.ngettext.return_value, "Should use ngettext"


@mock.patch(MOD + 'request')
def test_full_path(request):
    """ ``full_path()`` returns full path with query string """
    request.fullpath = '/'
    request.query_string = ''
    s = full_path()
    assert s == '/', "Should return '/', got '%s'" % s
    request.fullpath = '/foo/bar'
    request.query_string = ''
    s = full_path()
    assert s == '/foo/bar', "Should return '/foo/bar', got '%s'" % s
    request.fullpath = '/foo/bar'
    request.query_string = 'foo=bar'
    s = full_path()
    assert s == '/foo/bar?foo=bar', "Should return everything, got '%s'" % s


def test_i18n_returns_lazy():
    """ ``i18n_path()`` returns a lazy object """
    s = i18n_path('/foo', 'en_US')
    assert is_lazy(s), "Should be a lazy object"


@mock.patch(MOD + 'request')
def test_i18n_path(request):
    """ ``i18n_path()`` should use locale to prefix the path """
    request.locale = 'en_US'
    s = i18n_path('/foo')
    assert s == '/en_us/foo'
    request.locale = 'es_ES'
    s = i18n_path('/foo')
    assert s == '/es_es/foo'


@mock.patch(MOD + 'request')
def test_i18n_custom_locale(request):
    """ ``i18n_path()`` should use custom locale if provided """
    request.locale = 'en_US'
    s = i18n_path('/foo', locale='es_es')
    assert s == '/es_es/foo', "Should return specified locale instead"


@mock.patch(MOD + 'request')
def test_i18n_current_path(request):
    """ ``i18n_path()`` uses current path if none is provided """
    request.fullpath = '/foo/bar/baz'
    request.query_string = 'foo=bar'
    s = i18n_path(locale='en_US')
    assert s == '/en_us/foo/bar/baz?foo=bar', "Should return localized path"


def test_api_version():
    assert I18NPlugin.api == 2, "Should be version 2"


@mock.patch(MOD + 'gettext.translation')
@mock.patch(MOD + 'BaseTemplate')
def test_initialization_attrs(BaseTemplate, translation):
    """ Should init with expected attrs """
    app = mock.Mock()
    langs = [('foo', 'bar')]
    ret = I18NPlugin(app, langs, default_locale='foo',
                     locale_dir='nonexistent')
    assert ret.app == app, "Should have app attribute"
    assert ret.langs == langs, "Should have langs attribute"
    assert ret.locales == ['foo'], "Should have locales attribute"
    assert ret.default_locale == 'foo', "Should have default_locale attr"
    assert ret.domain == 'messages', "Should have default domain"
    assert 'foo' in ret.gettext_apis, "Should have gettext API for locale"

    tret = translation.return_value
    assert ret.gettext_apis['foo'] == tret, "Translation API for locale"

@mock.patch(MOD + 'gettext.translation')
@mock.patch(MOD + 'BaseTemplate')
def test_initialization_update_template_basics(BaseTemplate, translation):
    """ Should update template defaults """
    app = mock.Mock()
    langs = [('foo', 'bar')]
    I18NPlugin(app, langs, default_locale='foo', locale_dir='nonexistent')
    BaseTemplate.defaults.update.assert_called_once_with({
        '_': lazy_gettext,
        'gettext': lazy_gettext,
        'ngettext': lazy_ngettext,
        'i18n_path': i18n_path,
        'languages': langs,
    })


@mock.patch(MOD + 'gettext.translation')
@mock.patch(MOD + 'BaseTemplate')
def test_initialization_install_plugin(BaseTemplate, translation):
    """ Should init and install plugin """
    app = mock.Mock()
    langs = [('foo', 'bar')]
    ret = I18NPlugin(app, langs, default_locale='foo',
                     locale_dir='nonexistent')
    app.install.assert_called_once_with(ret)


@mock.patch(MOD + 'gettext.translation')
@mock.patch(MOD + 'BaseTemplate')
def test_initialization_no_plugin(BaseTemplate, translation):
    """ Should not install itself if ``noplugin`` arg is ``True`` """
    app = mock.Mock()
    langs = [('foo', 'bar')]
    ret = I18NPlugin(app, langs, default_locale='foo',
                     locale_dir='nonexistent', noplugin=True)
    assert app.install.called == False, "Should not install the plugin"


@mock.patch(MOD + 'gettext.translation')
@mock.patch(MOD + 'BaseTemplate')
@mock.patch(MOD + 'warn')
def test_initialization_wanrn(warn, BaseTemplate, translation):
    """ Should warn for each locale if gettext.translate() raises OSError """
    def raise_os_error(*args, **kwargs):
        raise OSError('lamma crapped itself')
    translation.side_effect = raise_os_error
    app = mock.Mock()
    langs = [('foo', 'bar'), ('bar', 'baz')]
    ret = I18NPlugin(app, langs, default_locale='foo',
                     locale_dir='nonexistent', noplugin=True)
    wcc = warn.call_count
    assert wcc == 2, "Should be called 2 times, got %s" % wcc
