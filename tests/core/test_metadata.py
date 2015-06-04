from functools import wraps
from contextlib import contextmanager

import mock
import pytest

from librarian.core import metadata as mod


MOD = mod.__name__


noop = lambda x: x


def with_mock_open(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        m = mock.mock_open()
        with mock.patch(MOD + '.open', m, create=True):
            return fn(m, *args, **kwargs)
    return wrapper


def _has_key(d, name):
    assert name in d


@contextmanager
def key_overrides(obj, **kwargs):
    new_keys = []
    orig_values = {}
    for key, value in kwargs.items():
        if key not in obj:
            new_keys.append(key)
        else:
            orig_values[key] = obj[key]
        obj[key] = value
    yield
    for key in new_keys:
        del obj[key]
    for key, value in orig_values.items():
        obj[key] = value


@contextmanager
def attr_overrides(obj, **kwargs):
    new_attrs = []
    orig_values = {}
    for key, value in kwargs.items():
        if not hasattr(obj, key):
            new_attrs = key
        else:
            orig_values[key] = getattr(obj, key)
        setattr(obj, key, value)
    yield
    for attr in new_attrs:
        delattr(obj, attr)
    for key, value in orig_values.items():
        setattr(obj, key, value)


def test_get_successor_key():
    assert mod.get_successor_key('partner') == 'publisher'
    assert mod.get_successor_key('index') == 'entry_point'
    assert mod.get_successor_key('publisher') is None
    assert mod.get_successor_key('url') is None


def test_edge_keys():
    assert mod.get_edge_keys() == (
        'publisher',
        'replaces',
        'keep_formatting',
        'language',
        'license',
        'title',
        'url',
        'timestamp',
        'multipage',
        'broadcast',
        'keywords',
        'entry_point',
        'images',
        'is_partner',
        'is_sponsored',
        'archive'
    )


def test_replace_aliases():
    meta = {'url': 'test',
            'title': 'again',
            'is_partner': True,
            'partner': 'Partner',
            'index': 'some.html'}
    expected = {'url': 'test',
                'title': 'again',
                'is_partner': True,
                'publisher': 'Partner',
                'entry_point': 'some.html'}
    mod.replace_aliases(meta)
    assert meta == expected


def test_adding_missing_keys():
    """ Metadata keys that are not in ``d`` will be added """
    d = {}
    mod.add_missing_keys(d)
    for key in mod.EDGE_KEYS:
        _has_key(d, key)


def test_adding_missing_key_doesnt_remove_existing():
    """ Existing keys will be kept """
    d = {'url': 'foo'}
    mod.add_missing_keys(d)
    assert d['url'] == 'foo'


def test_adding_missing_keys_doeesnt_remove_arbitrary_keys():
    """" Even non-standard keys will be kept """
    d = {'foo': 'bar'}
    mod.add_missing_keys(d)
    _has_key(d, 'foo')


def test_add_missing_keys_has_return():
    """ Add missing key mutates the supplies dict, but has no return value """
    d = {}
    ret = mod.add_missing_keys(d)
    assert ret is None


def test_clean_keys():
    """ Removes invalid keys """
    d = {'foo': 'bar', 'title': 'title'}
    mod.clean_keys(d)
    assert d == {'title': 'title'}


@mock.patch.object(mod, 'clean_keys')
@mock.patch.object(mod, 'add_missing_keys')
@mock.patch.object(mod, 'replace_aliases')
@mock.patch.object(mod.validator, 'validate')
def test_process_meta_success(validate, replace_aliases, add_missing_keys,
                              clean_keys):
    meta = {'title': 'test'}
    validate.return_value = {}
    assert mod.process_meta(meta) == meta
    validate.assert_called_once_with(meta, broadcast=True)
    replace_aliases.assert_called_once_with(meta)
    add_missing_keys.assert_called_once_with(meta)
    clean_keys.assert_called_once_with(meta)


@mock.patch.object(mod, 'clean_keys')
@mock.patch.object(mod, 'add_missing_keys')
@mock.patch.object(mod, 'replace_aliases')
@mock.patch.object(mod.validator, 'validate')
def test_process_meta_fail(validate, replace_aliases, add_missing_keys,
                           clean_keys):
    meta = {'title': 'test'}
    validate.return_value = {'error': 'some'}
    with pytest.raises(mod.MetadataError):
        mod.process_meta(meta)

    validate.assert_called_once_with(meta, broadcast=True)
    assert not replace_aliases.called
    assert not add_missing_keys.called
    assert not clean_keys.called


@mock.patch(MOD + '.os', autospec=True)
@mock.patch(MOD + '.json', autospec=True)
def test_meta_class_init(json, os):
    """ Initializing the Meta class must give the instance correct props """
    os.path.normpath.side_effect = noop
    data = {'md5': 'test', 'tags': 'tag json data'}
    meta = mod.Meta(data, 'foo')
    assert meta.meta == data
    assert meta.meta is not data
    json.loads.assert_called_once_with('tag json data')
    assert meta.tags == json.loads.return_value
    assert meta.content_path == 'foo'


@mock.patch(MOD + '.os', autospec=True)
def test_meta_class_init_with_no_tags(*ignored):
    """ Supplying empty string as tags should not cause Meta to raise """
    # Empty strig should not cause ``json.loads()`` to trip
    try:
        meta = mod.Meta({'tags': ''}, 'foo')
        assert meta.tags == {}
    except ValueError:
        assert False, 'Excepted not to raise'


@mock.patch(MOD + '.os', autospec=True)
@mock.patch(MOD + '.json', autospec=True)
def test_meta_attribute_access(*ignored):
    """ Attribute access to mod keys should be possible """
    meta = mod.Meta({'foo': 'bar', 'baz': 1}, 'foo')
    assert meta['foo'] == 'bar'
    assert meta.baz == 1


@mock.patch(MOD + '.json', autospec=True)
def test_meta_attribute_error(json):
    """ AttributeError should be raised on missing key/attribute """
    meta = mod.Meta({}, 'foo')
    try:
        meta.missing
        assert False, 'Expected to raise'
    except AttributeError:
        pass


@mock.patch(MOD + '.os', autospec=True)
@mock.patch(MOD + '.json', autospec=True)
def test_meta_set_key(*ignored):
    """ Setting keys using subscript notation is possible """
    data = {}
    meta = mod.Meta(data, 'foo')
    meta['missing'] = 'not anymore'
    assert meta.missing == 'not anymore'


@mock.patch(MOD + '.os', autospec=True)
@mock.patch(MOD + '.json', autospec=True)
def test_meta_set_key_does_not_update_original(*ignored):
    """ The original mod dict is updated when Meta object is updated """
    data = {}
    meta = mod.Meta(data, 'foo')
    meta['missing'] = 'not anymore'
    assert data == {}


@mock.patch(MOD + '.os', autospec=True)
@mock.patch(MOD + '.json', autospec=True)
def test_meta_get_key(*ignored):
    """ Key values can be obtained using ``get()`` method as with dicts """
    meta = mod.Meta({'foo': 'bar'}, 'foo')
    assert meta.get('foo') == 'bar'
    assert meta.get('missing') is None


@mock.patch.object(mod.scandir, 'scandir')
def test_find_image_no_content_path(scandir):
    meta = mod.Meta({'foo': 'bar'}, '')
    assert meta.find_image() is None
    assert not scandir.called


@mock.patch.object(mod.scandir, 'scandir')
@mock.patch.object(mod.os.path, 'exists')
def test_find_image_content_path_does_not_exist(exists, scandir):
    exists.return_value = False
    meta = mod.Meta({'foo': 'bar'}, '/content/path')
    assert meta.find_image() is None
    assert not scandir.called


@mock.patch.object(mod.scandir, 'scandir')
@mock.patch.object(mod.os.path, 'exists')
def test_find_image_no_files(exists, scandir):
    exists.return_value = True
    scandir.scandir.return_value = []
    meta = mod.Meta({'foo': 'bar'}, '/content/path')
    assert meta.find_image() is None
    scandir.assert_called_once_with('/content/path')


@mock.patch.object(mod.os.path, 'exists')
@mock.patch.object(mod.scandir, 'scandir')
def test_find_image_success(scandir, exists):
    mocked_entry = mock.Mock()
    mocked_entry.name = 'image.jpg'
    exists.return_value = True
    scandir.return_value = [mocked_entry]
    meta = mod.Meta({'foo': 'bar'}, '/content/path')
    assert meta.find_image() == 'image.jpg'
    scandir.assert_called_once_with('/content/path')


@mock.patch(MOD + '.json', autospec=True)
@mock.patch(MOD + '.os', autospec=True)
def test_lang_property(*ignored):
    """ The lang property is an alias for language key """
    meta = mod.Meta({'language': 'foo'}, '/content/path')
    assert meta.lang == 'foo'
    meta['language'] = 'bar'
    assert meta.lang == 'bar'


@mock.patch(MOD + '.json', autospec=True)
@mock.patch(MOD + '.os', autospec=True)
def test_lang_with_missing_language(*ignored):
    """ Lang property returns None if there is no language key """
    meta = mod.Meta({}, 'content_dir')
    assert meta.lang is None


@mock.patch(MOD + '.json', autospec=True)
@mock.patch(MOD + '.os', autospec=True)
def test_label_property_default(*ignored):
    """ Label is 'core' if there is no archive key """
    meta = mod.Meta({}, 'content_dir')
    assert meta.label == 'core'


@mock.patch(MOD + '.json', autospec=True)
@mock.patch(MOD + '.os', autospec=True)
def test_label_property_with_keys(*ignored):
    """ Correct label should be returned for appropriate key values """
    meta = mod.Meta({}, 'content_dir')
    with key_overrides(meta, archive='core'):
        assert meta.label == 'core'
    with key_overrides(meta, is_sponsored=True):
        assert meta.label == 'sponsored'
    with key_overrides(meta, is_partner=True):
        assert meta.label == 'partner'


@mock.patch(MOD + '.json', autospec=True)
@mock.patch(MOD + '.os', autospec=True)
def test_label_property_with_key_combinations(*ignored):
    """ Correct label should be returned for appropriate key combos """
    meta = mod.Meta({}, 'content_dir')
    with key_overrides(meta, archive='core', is_sponsored=True):
        assert meta.label == 'core'
    with key_overrides(meta, archive='ephem', is_sponsored=True):
        assert meta.label == 'sponsored'
    with key_overrides(meta, archive='core', is_partner=True):
        assert meta.label == 'core'
    with key_overrides(meta, archive='ephem', is_partner=True):
        assert meta.label == 'partner'


@mock.patch.object(mod, 'json', autospec=True)
@mock.patch.object(mod, 'os', autospec=True)
@mock.patch.object(mod.Meta, 'find_image')
def test_image_property_cached(find_image, *ignored):
    """ If image path is cached, it is returned immediately """
    meta = mod.Meta({'md5': 'md5'}, '/content/root/')
    meta._image = 'foobar.jpg'
    assert meta.image == 'foobar.jpg'
    assert not find_image.called


@mock.patch.object(mod, 'json', autospec=True)
@mock.patch.object(mod, 'os', autospec=True)
@mock.patch.object(mod.Meta, 'find_image')
def test_image_property_found(find_image, *ignored):
    """ If image exist on dist, it will be found and returned """
    find_image.return_value = 'foobar.jpg'
    meta = mod.Meta({'md5': 'md5'}, 'content_dir')
    assert meta.image == 'foobar.jpg'
