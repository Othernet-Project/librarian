import datetime

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


def test_get_default_value():
    with pytest.raises(KeyError):
        mod.get_default_value('invalid', {})

    assert mod.get_default_value('url', {}) is None
    assert mod.get_default_value('keep_formatting', {}) is False

    meta = {'timestamp': '2014-08-10 19:59:19 UTC'}
    broadcast = mod.get_default_value('broadcast', meta)
    assert broadcast == datetime.date(2014, 8, 10)


def test_get_aliases_for():
    with pytest.raises(KeyError):
        mod.get_aliases_for('invalid')

    assert mod.get_aliases_for('url') == []
    assert mod.get_aliases_for('publisher') == ['partner']


def test_is_required():
    with pytest.raises(KeyError):
        mod.is_required('invalid')

    assert mod.is_required('url') is True
    assert mod.is_required('images') is False


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


@mock.patch(MOD + '.dateutil.parser.parse')
def test_adding_missing_keys(date_parse):
    """ Metadata keys that are not in ``d`` will be added """
    d = {}
    mod.add_missing_keys(d)
    for key in mod.STANDARD_FIELDS:
        _has_key(d, key)


@mock.patch(MOD + '.dateutil.parser.parse')
def test_adding_missing_key_doesnt_remove_existing(date_parse):
    """ Existing keys will be kept """
    d = {'url': 'foo'}
    mod.add_missing_keys(d)
    assert d['url'] == 'foo'


@mock.patch(MOD + '.dateutil.parser.parse')
def test_adding_missing_keys_doeesnt_remove_arbitrary_keys(date_parse):
    """" Even non-standard keys will be kept """
    d = {'foo': 'bar'}
    mod.add_missing_keys(d)
    _has_key(d, 'foo')


@mock.patch(MOD + '.dateutil.parser.parse')
def test_add_missing_keys_has_return(date_parse):
    """ Add missing key mutates the supplies dict, but has no return value """
    d = {}
    ret = mod.add_missing_keys(d)
    assert ret is None


def test_clean_keys():
    """ Removes invalid keys """
    d = {'foo': 'bar', 'title': 'title'}
    mod.clean_keys(d)
    assert d == {'title': 'title'}


@mock.patch(MOD + '.dateutil.parser.parse')
@mock.patch(MOD + '.is_required')
@mock.patch(MOD + '.json', autospec=True)
def test_convert_returns__added_keys(json, is_required, date_parse):
    """ Conversion to json calls ``add_missing_keys()`` on converted value """
    json.loads.return_value = {}
    is_required.return_value = False
    date_mock = mock.Mock()
    date_mock.date.return_value = None
    date_parse.return_value = date_mock
    out = mod.convert_json('')
    assert out == {
        'url': None,
        'title': None,
        'images': 0,
        'timestamp': None,
        'keep_formatting': False,
        'is_partner': False,
        'is_sponsored': False,
        'archive': 'core',
        'publisher': '',
        'license': None,
        'language': '',
        'multipage': False,
        'entry_point': 'index.html',
        'broadcast': None,
        'keywords': '',
        'replaces': None
    }


@mock.patch(MOD + '.add_missing_keys')
@mock.patch(MOD + '.is_required')
@mock.patch(MOD + '.json', autospec=True)
def test_convert_add_default_fails(json, is_required, add_missing_keys):
    """ DecodeError must be raised when adding default values raises an exc """
    json.loads.return_value = {}
    is_required.return_value = False
    add_missing_keys.side_effect = Exception()
    try:
        mod.convert_json('')
        assert False, 'Expected to raise'
    except mod.DecodeError:
        pass


@mock.patch(MOD + '.json', autospec=True)
@mock.patch(MOD + '.add_missing_keys')
@mock.patch(MOD + '.is_required')
def test_convert_decodes_string(is_required, *ignored):
    """ During conversion, strings are decoded as UTF8 """
    s = mock.Mock()
    is_required.return_value = False
    mod.convert_json(s)
    s.decode.assert_called_once_with('utf8')


@mock.patch(MOD + '.json', autospec=True)
@mock.patch(MOD + '.add_missing_keys')
@mock.patch(MOD + '.is_required')
def test_convert_decoding_fails(*ignored):
    """ DecodeError must be raised when string decoding fails """
    s = mock.Mock()
    s.decode.side_effect = UnicodeDecodeError('utf-8', b"", 0, 1, 'mock str')
    try:
        mod.convert_json(s)
        assert False, 'Expected to raise'
    except mod.DecodeError:
        pass


@mock.patch(MOD + '.add_missing_keys')
@mock.patch(MOD + '.is_required')
@mock.patch(MOD + '.json', autospec=True)
def test_convert_json_fails(json, *ignored):
    """ DecodeError must be raised when JSON cannot be decoded """
    s = mock.Mock()

    json.loads.side_effect = ValueError
    try:
        mod.convert_json(s)
        assert False, 'Expected to raise'
    except mod.DecodeError:
        pass


@mock.patch(MOD + '.os', autospec=True)
@mock.patch(MOD + '.add_missing_keys', autospec=True)
@mock.patch(MOD + '.json', autospec=True)
def test_convert_missing_keys(json, *ignored):
    """ When required keys are missing, FormatError must be raised """
    s = mock.Mock()
    json.loads.return_value = {}
    try:
        mod.convert_json(s)
        assert False, 'Expected to raise'
    except mod.FormatError:
        pass


@mock.patch(MOD + '.os', autospec=True)
@mock.patch(MOD + '.add_missing_keys')
@mock.patch(MOD + '.json', autospec=True)
def test_convert_correct_keys(json, *ignored):
    """ When correct keys are supplied, no exception should be raised """
    s = mock.Mock()
    json.loads.return_value = {
        'url': 'foo',
        'title': 'foo',
        'timestamp': 'foo',
        'license': 'foo',
        'broadcast': 'foo',
    }
    try:
        mod.convert_json(s)
    except mod.FormatError:
        assert False, 'Expected not to raise'


@mock.patch(MOD + '.os', autospec=True)
@mock.patch(MOD + '.json', autospec=True)
def test_meta_class_init(json, os):
    """ Initializing the Meta class must give the instance correct props """
    os.path.normpath.side_effect = noop
    data = mock.Mock()
    meta = mod.Meta(data, 'foo')
    assert meta.meta == data
    data.get.assert_called_once_with('tags')
    json.loads.assert_called_once_with(data.get.return_value)
    assert meta.tags == json.loads.return_value
    assert meta.cover_dir == 'foo'
    assert meta.zip_path is None


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
def test_meta_set_key_updates_original(*ignored):
    """ The original mod dict is updated when Meta object is updated """
    data = {}
    meta = mod.Meta(data, 'foo')
    meta['missing'] = 'not anymore'
    assert data['missing'] == 'not anymore'


@mock.patch(MOD + '.os', autospec=True)
@mock.patch(MOD + '.json', autospec=True)
def test_meta_get_key(*ignored):
    """ Key values can be obtained using ``get()`` method as with dicts """
    meta = mod.Meta({'foo': 'bar'}, 'foo')
    assert meta.get('foo') == 'bar'
    assert meta.get('missing') is None


def test_find_image_no_zip_path():
    meta = mod.Meta({'foo': 'bar'}, '')
    assert meta.find_image() is None


@mock.patch.object(mod, 'scandir')
def test_find_image_no_files(scandir):
    scandir.scandir.return_value = []
    meta = mod.Meta({'foo': 'bar'}, '/cover/path', '/zip/path')
    assert meta.find_image() is None


@mock.patch.object(mod, 'scandir')
def test_find_image_success(scandir):
    mocked_entry = mock.Mock()
    mocked_entry.name = 'image.jpg'
    mocked_entry.path = '/zip/path/image.jpg'
    scandir.scandir.return_value = [mocked_entry]
    meta = mod.Meta({'foo': 'bar'}, '/cover/path', '/zip/path')
    assert meta.find_image() == '/zip/path/image.jpg'


@mock.patch(MOD + '.json', autospec=True)
@mock.patch(MOD + '.os', autospec=True)
def test_lang_property(*ignored):
    """ The lang property is an alias for language key """
    meta = mod.Meta({'language': 'foo'}, 'covers_dir')
    assert meta.lang == 'foo'
    meta['language'] = 'bar'
    assert meta.lang == 'bar'


@mock.patch(MOD + '.json', autospec=True)
@mock.patch(MOD + '.os', autospec=True)
def test_lang_with_missing_language(*ignored):
    """ Lang property returns None if there is no language key """
    meta = mod.Meta({}, 'covers_dir')
    assert meta.lang is None


@mock.patch(MOD + '.json', autospec=True)
@mock.patch(MOD + '.os', autospec=True)
def test_rtl_property(*ignored):
    """ RTL property returns True for RTL languages """
    meta = mod.Meta({}, 'covers_dir')
    meta['language'] = 'en'
    assert meta.rtl is False
    meta['language'] = 'ar'
    assert meta.rtl is True


@mock.patch(MOD + '.json', autospec=True)
@mock.patch(MOD + '.os', autospec=True)
def test_i18n_attrs_property(*ignored):
    """ I18n attributes are returned when langauge is specified """
    meta = mod.Meta({}, 'covers_dir')
    assert meta.i18n_attrs == ''
    meta['language'] = 'en'
    assert meta.i18n_attrs == ' lang="en"'
    meta['language'] = 'ar'
    assert meta.i18n_attrs == ' lang="ar" dir="rtl"'


@mock.patch(MOD + '.json', autospec=True)
@mock.patch(MOD + '.os', autospec=True)
def test_label_property_default(*ignored):
    """ Label is 'core' if there is no archive key """
    meta = mod.Meta({}, 'covers_dir')
    assert meta.label == 'core'


@mock.patch(MOD + '.json', autospec=True)
@mock.patch(MOD + '.os', autospec=True)
def test_label_property_with_keys(*ignored):
    """ Correct label should be returned for appropriate key values """
    meta = mod.Meta({}, 'covers_dir')
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
    meta = mod.Meta({}, 'covers_dir')
    with key_overrides(meta, archive='core', is_sponsored=True):
        assert meta.label == 'core'
    with key_overrides(meta, archive='ephem', is_sponsored=True):
        assert meta.label == 'sponsored'
    with key_overrides(meta, archive='core', is_partner=True):
        assert meta.label == 'core'
    with key_overrides(meta, archive='ephem', is_partner=True):
        assert meta.label == 'partner'


@mock.patch(MOD + '.json', autospec=True)
@mock.patch(MOD + '.os', autospec=True)
def test_free_license_property(*ignored):
    """ Free license is True for free licenses """
    meta = mod.Meta({}, 'covers_dir')
    with key_overrides(meta, license='ARL'):
        assert meta.free_license is False
    with key_overrides(meta, license='ON'):
        assert meta.free_license is False
    with key_overrides(meta, license='GFDL'):
        assert meta.free_license is True
    with key_overrides(meta, license='CC-BY'):
        assert meta.free_license is True


@mock.patch.object(mod, 'json', autospec=True)
@mock.patch.object(mod, 'os', autospec=True)
@mock.patch.object(mod.Meta, 'find_image')
def test_image_property_cached(find_image, *ignored):
    """ If image path is cached, it is returned immediately """
    meta = mod.Meta({'md5': 'md5'}, 'covers_dir', zip_path='foo.zip')
    meta._image = 'foobar.jpg'
    assert meta.image == 'foobar.jpg'
    assert not find_image.called


@mock.patch.object(mod, 'json', autospec=True)
@mock.patch.object(mod, 'os', autospec=True)
@mock.patch.object(mod.Meta, 'find_image')
def test_image_property_found(find_image, *ignored):
    """ If image exist on dist, it will be found and returned """
    find_image.return_value = 'foobar.jpg'
    meta = mod.Meta({'md5': 'md5'}, 'covers_dir')
    assert meta.image == 'foobar.jpg'
