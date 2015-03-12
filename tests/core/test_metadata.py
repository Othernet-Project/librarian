from functools import wraps
from contextlib import contextmanager

import mock

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


def test_adding_missing_keys():
    """ Metadata keys that are not in ``d`` will be added """
    d = {}
    mod.add_missing_keys(d)
    _has_key(d, 'url' )
    _has_key(d, 'domain' )
    _has_key(d, 'title' )
    _has_key(d, 'images' )
    _has_key(d, 'timestamp' )
    _has_key(d, 'keep_formatting' )
    _has_key(d, 'is_partner' )
    _has_key(d, 'is_sponsored' )
    _has_key(d, 'archive' )
    _has_key(d, 'partner' )
    _has_key(d, 'license' )
    _has_key(d, 'language' )


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
    assert ret == None


def test_clean_keys():
    """ Removes invalid keys """
    d = {'foo': 'bar', 'title': 'title'}
    mod.clean_keys(d)
    assert d == {'title': 'title'}


@mock.patch(MOD + '.REQUIRED_KEYS')
@mock.patch(MOD + '.json', autospec=True)
def test_convert_returns__added_keys(json, *ignored):
    """ Conversion to json calls ``add_missing_keys()`` on converted value """
    json.loads.return_value = {}
    out = mod.convert_json('')
    assert out == {
        'url': None,
        'domain': None,
        'title': None,
        'images': None,
        'timestamp': None,
        'keep_formatting': None,
        'is_partner': None,
        'is_sponsored': None,
        'archive': None,
        'partner': None,
        'license': None,
        'language': None,
    }


@mock.patch(MOD + '.json', autospec=True)
@mock.patch(MOD + '.add_missing_keys')
@mock.patch(MOD + '.REQUIRED_KEYS')
def test_convert_decodes_string(*ignored):
    """ During conversion, strings are decoded as UTF8 """
    s = mock.Mock()
    mod.convert_json(s)
    s.decode.assert_called_once_with('utf8')


@mock.patch(MOD + '.json', autospec=True)
@mock.patch(MOD + '.add_missing_keys')
@mock.patch(MOD + '.REQUIRED_KEYS')
def test_convert_decoding_fails(*ignored):
    """ DecodeError must be raised when string decoding fails """
    s = mock.Mock()

    class MockError(UnicodeDecodeError):
        def __init__(self, *args, **kwargs):
            pass

    s.decode.side_effect = MockError
    try:
        mod.convert_json(s)
        assert False, 'Expected to raise'
    except mod.DecodeError:
        pass


@mock.patch(MOD + '.add_missing_keys')
@mock.patch(MOD + '.REQUIRED_KEYS')
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
        'domain': 'foo',
        'title': 'foo',
        'timestamp': 'foo',
        'license': 'foo',
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
    assert meta.zip_path == None


@mock.patch(MOD + '.os', autospec=True)
def test_meta_class_init_with_no_tags(*ignored):
    """ Supplying empty string as tags should not cause Meta to raise """
    # Empty strig should not cause ``json.loads()`` to trip
    try:
        meta = mod.Meta({'tags': ''}, 'foo')
        assert meta.tags == []
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


@mock.patch(MOD + '.json', autospec=True)
@mock.patch(MOD + '.os', autospec=True)
@with_mock_open
def test_meta_cache_cover_file_path(mock_open, os, *ignored):
    """ Caching cover image returns the name of the created file """
    os.path.normpath.side_effect = noop
    meta = mod.Meta({'md5': 'md5'}, 'covers_dir')
    name = meta.cache_cover('.jpg', 'fake image data')
    os.path.join.assert_called_once_with('covers_dir', 'md5.jpg')
    os.path.basename.assert_called_once_with(
        os.path.join.return_value)
    assert name == os.path.basename.return_value


@mock.patch(MOD + '.json', autospec=True)
@mock.patch(MOD + '.os', autospec=True)
@with_mock_open
def test_meta_cache_cover_writes_image_data(mock_open, os, *ignored):
    """ Caching cover image writes image data to file """
    fd = mock_open()
    os.path.normpath.side_effect = noop
    meta = mod.Meta({'md5': 'md5'}, 'covers_dir')
    meta.cache_cover('.jpg', 'fake image data')
    fd.write.assert_called_once_with('fake image data')


@mock.patch(MOD + '.json', autospec=True)
@mock.patch(MOD + '.zipfile', autospec=True)
@with_mock_open
def test_extact_image_looks_for_frist_image(mock_open, zipfile, *ignored):
    """ Extract image looks up the first image-looking in zip file """
    zipfile = zipfile.ZipFile.return_value
    zipfile.namelist.return_value = ['foo.txt', 'bar.jpg']
    meta = mod.Meta({'md5': 'md5'}, 'covers_dir', zip_path='foo.zip')
    extension, content = meta.extract_image()
    mock_open.assert_called_once_with('foo.zip', 'rb')
    zipfile.open.assert_called_once_with('bar.jpg', 'r')
    assert extension == '.jpg'
    assert content == zipfile.open.return_value.read.return_value


@mock.patch(MOD + '.json', autospec=True)
@mock.patch(MOD + '.zipfile', autospec=True)
@with_mock_open
def test_extract_image_no_files(mock_open, zipfile, *ignored):
    """ Extract image  returns None if there are no files in the zipball """
    zipfile = zipfile.ZipFile.return_value
    zipfile.namelist.return_value = []
    meta = mod.Meta({'md5': 'md5'}, 'covers_dir', zip_path='foo.zip')
    extension, content = meta.extract_image()
    assert extension is None
    assert content is None
    assert zipfile.open.called is False


@mock.patch(MOD + '.json', autospec=True)
@mock.patch(MOD + '.zipfile', autospec=True)
@with_mock_open
def test_extact_image_no_image(mock_open, zipfile, *ignored):
    """ Extract image returns None if there are no images in the zipball """
    print(zipfile)
    zipfile = zipfile.ZipFile.return_value
    zipfile.namelist.return_value = ['foo.html']
    meta = mod.Meta({'md5': 'md5'}, 'covers_dir', zip_path='foo.zip')
    extension, content = meta.extract_image()
    assert extension is None
    assert content is None


@mock.patch(MOD + '.os', autospec=True)
@mock.patch(MOD + '.glob', autospec=True)
def test_get_cover_path_search_cover_dir(glob, os):
    """ Get cover path searches cover dir for any file with md5 name """
    os.path.normpath.side_effect = noop
    glob.glob.side_effect = lambda x: ['found']
    meta = mod.Meta({'md5': 'md5'}, 'covers_dir')
    meta.get_cover_path()
    os.path.join.assert_called_once_with('covers_dir', 'md5.*')
    glob.glob.assert_called_once_with(os.path.join.return_value)
    os.path.basename.assert_called_once_with('found')


@mock.patch(MOD + '.os', autospec=True)
@mock.patch(MOD + '.glob', autospec=True)
def test_get_cover_path_no_cover_found(glob, *ignored):
    """ None is returned and no exception raised when no cover is found """
    glob.glob.return_value = []
    meta = mod.Meta({'md5': 'md5'}, 'covers_dir')
    try:
        ret = meta.get_cover_path()
        assert ret is None
    except Exception:
        assert False, 'Expected not to raise'


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
def test_human_label_property(*ignored):
    """ Human label is a translated label """
    faux_labels = {
        'core': 'core translated',
        'sponsored': 'sponsored translated',
        'partner': 'partner translated'
    }
    meta = mod.Meta({}, 'covers_dir')
    with attr_overrides(meta, LABEL_TITLES=faux_labels):
        with key_overrides(meta, archive='core'):
            assert meta.human_label == 'core translated'
        with key_overrides(meta, archive='ephem', is_sponsored=True):
            assert meta.human_label == 'sponsored translated'


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


@mock.patch(MOD + '.json', autospec=True)
@mock.patch(MOD + '.os', autospec=True)
def test_human_license_property(*ignored):
    """ Human license is a translated license name """
    faux_licenses = (
        (None, 'unknown translated'),
        ('ARL', 'ARL translated'),
    )
    meta = mod.Meta({}, 'covers_dir')
    with attr_overrides(mod, LICENSES=faux_licenses):
        assert meta.human_license == 'unknown translated'
        with key_overrides(meta, license='ARL'):
            assert meta.human_license == 'ARL translated'
        with key_overrides(meta, license='DOUBLE'):
            assert meta.human_license == 'unknown translated'


@mock.patch(MOD + '.json', autospec=True)
@mock.patch(MOD + '.glob', autospec=True)
@mock.patch(MOD + '.os', autospec=True)
@mock.patch.object(mod.Meta, 'get_cover_path')
@mock.patch.object(mod.Meta, 'extract_image')
@mock.patch.object(mod.Meta, 'cache_cover')
def test_image_property(cache_cover, extract_image, get_cover_path, *ignored):
    """ When there are no covers, new one is extracted and cached """
    get_cover_path.return_value = None
    extract_image.return_value = ('foo', 'bar')
    meta = mod.Meta({}, 'covers_dir', zip_path='foo.zip')
    res = meta.image
    extract_image.assert_any_call()
    cache_cover.assert_called_once_with('foo', 'bar')
    assert res == cache_cover.return_value
    assert meta._image == cache_cover.return_value


@mock.patch(MOD + '.json', autospec=True)
@mock.patch(MOD + '.glob', autospec=True)
@mock.patch(MOD + '.os', autospec=True)
@mock.patch.object(mod.Meta, 'get_cover_path')
@mock.patch.object(mod.Meta, 'extract_image')
@mock.patch.object(mod.Meta, 'cache_cover')
def test_image_exists(cache_cover, extract_image, get_cover_path, *ignored):
    """ When cover image exists on disk, it is returned and cached """
    meta = mod.Meta({}, 'covers_dir', zip_path='foo.zip')
    res = meta.image
    assert res == get_cover_path.return_value
    assert meta._image == get_cover_path.return_value


@mock.patch(MOD + '.json', autospec=True)
@mock.patch(MOD + '.glob', autospec=True)
@mock.patch(MOD + '.os', autospec=True)
@mock.patch.object(mod.Meta, 'cache_cover')
@mock.patch.object(mod.Meta, 'get_cover_path')
@mock.patch.object(mod.Meta, 'extract_image')
def test_extract_error(extract_image, get_cover_path, cache_cover, *ignored):
    """ If extract image fails, cover is not cached, and None is returned """
    get_cover_path.return_value = None
    meta = mod.Meta({'md5': 'md5'}, 'covers_dir', zip_path='foo.zip')

    extract_image.side_effect = TypeError
    assert meta.image is None
    assert not cache_cover.called

    extract_image.side_effect = OSError
    assert meta.image is None
    assert not cache_cover.called


@mock.patch(MOD + '.json', autospec=True)
@mock.patch(MOD + '.glob', autospec=True)
@mock.patch(MOD + '.os', autospec=True)
@mock.patch.object(mod.Meta, 'extract_image')
@mock.patch.object(mod.Meta, 'cache_cover')
@mock.patch.object(mod.Meta, 'get_cover_path')
def test_cache_error(get_cover_path, cache_cover, extract_image, *ignored):
    """ If extract image fails, cover is not cached, and None is returned """
    get_cover_path.return_value = None
    extract_image.return_value = ('foo', 'bar')
    meta = mod.Meta({'md5': 'md5'}, 'covers_dir', zip_path='foo.zip')
    cache_cover.side_effect = OSError
    assert meta.image is None



@mock.patch(MOD + '.json', autospec=True)
@mock.patch(MOD + '.glob', autospec=True)
@mock.patch(MOD + '.os', autospec=True)
@mock.patch.object(mod.Meta, 'extract_image')
@mock.patch.object(mod.Meta, 'cache_cover')
@mock.patch.object(mod.Meta, 'get_cover_path')
def test_cached_image(get_cover_path, cache_cover, extract_image, *ignored):
    """ If image path is cached, it is returned immediately """
    meta = mod.Meta({'md5': 'md5'}, 'covers_dir', zip_path='foo.zip')
    meta._image = 'foobar.jpg'
    assert meta.image == 'foobar.jpg'
    assert not get_cover_path.called
    assert not extract_image.called
    assert not cache_cover.called


@mock.patch(MOD + '.json', autospec=True)
@mock.patch(MOD + '.glob', autospec=True)
@mock.patch(MOD + '.os', autospec=True)
@mock.patch.object(mod.Meta, 'extract_image')
@mock.patch.object(mod.Meta, 'cache_cover')
@mock.patch.object(mod.Meta, 'get_cover_path')
def test_no_zip_path(get_cover_path, cache_cover, extract_image, *ignored):
    """ If image exist on dist, it is returned even if zip_path is None """
    get_cover_path.return_value = 'foobar.jpg'
    meta = mod.Meta({'md5': 'md5'}, 'covers_dir')
    assert meta.image == 'foobar.jpg'

