import mock

from librarian.utils import core_helpers as mod


@mock.patch.object(mod.metadata, 'Meta')
@mock.patch.object(mod, 'open_archive')
@mock.patch.object(mod, 'request')
def test_with_content(request, open_archive, metadata_class):
    request.app.config = {'content.contentdir': '/content/root/'}
    content_id = '202ab62b551f6d7fc002f65652525544'
    content_path = '/content/root/202/ab6/2b5/51f/6d7/fc0/02f/656/525/255/44'

    mocked_archive = mock.Mock()
    mocked_archive.get_single.return_value = {'md5': content_id}
    open_archive.return_value = mocked_archive

    mocked_meta_obj = mock.Mock()
    metadata_class.return_value = mocked_meta_obj

    mocked_route = mock.Mock(__name__='fake route')
    mocked_route.return_value = {'return': 'data'}
    decorated = mod.with_content(mocked_route)
    assert decorated(content_id) == {'return': 'data'}

    mocked_archive.get_single.assert_called_once_with(content_id)
    mocked_route.assert_called_once_with(meta=mocked_meta_obj)
    metadata_class.assert_called_once_with({'md5': content_id}, content_path)
