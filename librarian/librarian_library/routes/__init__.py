from .content import (content_list,
                      content_reader,
                      remove_content_confirm,
                      remove_content,
                      content_file)
from .downloads import list_downloads, manage_downloads
from .tags import tag_cloud, edit_tags


EXPORTS = {
    'routes': {'required_by': ['librarian.librarian_system.routes.routes']}
}


def routes(config):
    skip_plugins = config['app.skip_plugins']
    return (
        ('content:list', content_list,
         'GET', '/', {}),
        ('content:reader', content_reader,
         'GET', '/pages/<content_id>', {}),
        ('content:delete', remove_content_confirm,
         'GET', '/delete/<content_id>', {}),
        ('content:delete', remove_content,
         'POST', '/delete/<content_id>', {}),
        # This is a static file route and is shadowed by the static file server
        ('content:file', content_file,
         'GET', '/content/<content_path:re:[0-9a-f]{3}(/[0-9a-f]{3}){9}/[0-9a-f]{2}>/<filename:path>',  # NOQA
         dict(no_i18n=True, skip=skip_plugins)),

        ('downloads:list', list_downloads, 'GET', '/downloads/', {}),
        ('downloads:action', manage_downloads, 'POST', '/downloads/', {}),

        ('tags:list', tag_cloud, 'GET', '/tags/', {}),
        ('tags:edit', edit_tags, 'POST', '/tags/<content_id>', {}),
    )
