import pytest

try:
    from unittest import mock
except ImportError:
    import mock

from librarian.core.contrib.assets import static as mod


MOD = mod.__name__


@pytest.mark.parametrize('seq,out', [
    ('ABCDABCD', 'ABCD'),
    ('AABBCCDD', 'ABCD'),
    ('ABCDDCBA', 'ABCD'),
    ('DCBAABCD', 'DCBA'),
    ('ABCD', 'ABCD'),
    ('', ''),
])
def test_unique(seq, out):
    assert ''.join(mod.Assets._unique(seq)) == out


@mock.patch.object(mod.webassets, 'Bundle')
@mock.patch.object(mod.Assets, '_env_factory')
def test_add_js_bundle(env_fac, Bundle):
    a = mod.Assets()
    a.add_js_bundle('foo', ['bar', 'baz'])
    Bundle.assert_called_once_with('bar.js', 'baz.js', filters='rjsmin',
                                   output='js/foo-bundle-%(version)s.js')
    a.env.register.assert_called_once_with('js/foo', Bundle.return_value)


@mock.patch.object(mod.webassets, 'Bundle')
@mock.patch.object(mod.Assets, '_env_factory')
def test_add_js_bundle_with_dupes(env_fac, Bundle):
    a = mod.Assets()
    a.add_js_bundle('foo', ['bar', 'baz', 'bar', 'baz'])
    Bundle.assert_called_once_with('bar.js', 'baz.js', filters='rjsmin',
                                   output='js/foo-bundle-%(version)s.js')
    a.env.register.assert_called_once_with('js/foo', Bundle.return_value)


@mock.patch.object(mod.webassets, 'Bundle')
@mock.patch.object(mod.Assets, '_env_factory')
def test_add_css_bundle(env_fac, Bundle):
    a = mod.Assets()
    a.add_css_bundle('foo', ['bar', 'baz'])
    Bundle.assert_called_once_with('bar.css', 'baz.css', filters='cssmin',
                                   output='css/foo-bundle-%(version)s.css')
    a.env.register.assert_called_once_with('css/foo', Bundle.return_value)


@mock.patch.object(mod.webassets, 'Bundle')
@mock.patch.object(mod.Assets, '_env_factory')
def test_add_css_bundle_with_dupes(env_fac, Bundle):
    a = mod.Assets()
    a.add_css_bundle('foo', ['bar', 'baz', 'bar', 'baz'])
    Bundle.assert_called_once_with('bar.css', 'baz.css', filters='cssmin',
                                   output='css/foo-bundle-%(version)s.css')
    a.env.register.assert_called_once_with('css/foo', Bundle.return_value)


@mock.patch.object(mod.Assets, 'add_static_source')
def test_from_config_single(add_static_source):
    """
    Regression: Assets get double-registered if assets.directory/assets.source
    configuration conincides with a component that is being registered.
    """
    mock_conf = {
        'root': 'foo',
        'assets.directory': 'bar',
        'assets.url': '/static/',
        'assets.sources': {'comp': ('foo/bar', '/static/')},
        'assets.debug': False,
        'assets.js_bundles': [
            'foo: bar, baz',
        ],
        'assets.css_bundles': [
            'foo: bar, baz',
        ]
    }
    mod.Assets.from_config(mock_conf)
    # With the bug that was discovered, below would be 4, and would have
    # repeated calls for foo/bar/{js,css} and /static/
    assert add_static_source.call_count == 2
    add_static_source.assert_has_calls([
        mock.call('foo/bar/js', url='/static/'),
        mock.call('foo/bar/css', url='/static/'),
    ], any_order=True)
