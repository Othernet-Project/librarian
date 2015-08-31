from bottle import request, redirect, MultiDict, abort
from bottle_utils.html import hsize
from bottle_utils.i18n import lazy_gettext as _, i18n_url

from librarian.librarian_core.contrib.templates.renderer import view
from librarian.librarian_library.library.archive import Archive

from . import zipballs


@view('diskspace/cleanup', message=None, vals=MultiDict())
def cleanup_list():
    """ Render a list of items that can be deleted """
    free = zipballs.free_space()[0]
    return {'metadata': zipballs.cleanup_list(free),
            'needed': zipballs.needed_space(free)}


@view('diskspace/cleanup', message=None, vals=MultiDict())
def cleanup():
    forms = request.forms
    action = forms.get('action', 'check')
    if action not in ['check', 'delete']:
        # Translators, used as response to innvalid HTTP request
        abort(400, _('Invalid request'))
    free = zipballs.free_space()[0]
    cleanup = list(zipballs.cleanup_list(free))
    selected = forms.getall('selection')
    metadata = list(cleanup)
    selected = [z for z in metadata if z['md5'] in selected]
    if action == 'check':
        if not selected:
            # Translators, used as message to user when clean-up is started
            # without selecting any content
            message = _('No content selected')
        else:
            tot = hsize(sum([s['size'] for s in selected]))
            message = str(
                # Translators, used when user is previewing clean-up, %s is
                # replaced by amount of content that can be freed in bytes,
                # KB, MB, etc
                _('%s can be freed by removing selected content')) % tot
        return {'vals': forms, 'metadata': metadata, 'message': message,
                'needed': zipballs.needed_space(free)}
    else:
        conf = request.app.config
        archive = Archive.setup(conf['librarian.backend'],
                                request.db.main,
                                unpackdir=conf['content.unpackdir'],
                                contentdir=conf['content.contentdir'],
                                spooldir=conf['content.spooldir'],
                                meta_filename=conf['content.metadata'])
        if selected:
            archive.remove_from_archive([z['md5'] for z in selected])
            request.app.exts.cache.invalidate(prefix='content')
            redirect(i18n_url('content:list'))
        else:
            # Translators, error message shown on clean-up page when there was
            # no deletable content
            message = _('Nothing to delete')
        return {'vals': MultiDict(), 'metadata': cleanup,
                'message': message, 'needed': archive.needed_space()}


def routes(config):
    return (
        ('diskspace:list', cleanup_list, 'GET', '/diskspace/cleanup/', {}),
        ('diskspace:cleanup', cleanup, 'POST', '/diskspace/cleanup/', {}),
    )
