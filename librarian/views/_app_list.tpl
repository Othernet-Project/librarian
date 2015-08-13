% for meta in metadata:
<li class="app-item ${'thumbnails' if view == 'thumbnails' else 'details'}">
    <% app_url = i18n_url('content:reader', content_id=meta.md5) + h.set_qparam(content_type=chosen_content_type).to_qs() %>
    <a class="thumbnail" href="${app_url}">
        <img src="${url('content:file', content_path=th.get_content_path(meta.md5), filename=meta.thumbnail)}" />
    </a>
    <div class="app-info">
        <a class="field title" href="${app_url}">${meta.title | h}</a>
        % if meta.publisher:
        <span class="field author">(${_('by %s') % meta.publisher})</span>
        % endif
        <span class="field download-date">${meta.timestamp.date()}</span>
        % if meta.app.get('description'):
        <span class="field description">${meta.app['description']}</span>
        % endif
        <span class="field version">${meta.app['version']}</span>
        % if th.is_authenticated():
        <form class="uninstall-button" action="${i18n_url('content:delete', content_id=meta.md5)}" method="GET">
            <button>${_('Uninstall')}</button>
        </form>
        % endif
    </div>
</li>
% endfor
<div class="controls">
    <a class="thumbnails-view" href="${i18n_path(request.path) + h.set_qparam(view='thumbnails').to_qs()}"></a>
    <a class="details-view" href="${i18n_path(request.path) + h.set_qparam(view='details').to_qs()}"></a>
</div>
