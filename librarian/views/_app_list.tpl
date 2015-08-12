% for meta in metadata:
<li class="app">
    <a href="${i18n_url('content:reader', content_id=meta.md5) + h.set_qparam(content_type=chosen_content_type).to_qs()}">
        <img src="${url('content:file', content_path=th.get_content_path(meta.md5), filename=meta.cover)}" />
        <span class="title">${meta.title | h}</span>
    </a>
    <span class="version">${meta.app['version']}</span>
    % if th.is_authenticated():
    <form class="uninstall" action="${i18n_url('content:delete', content_id=meta.md5)}" method="GET">
        <button>${_('Uninstall')}</button>
    </form>
    % endif
</li>
% endfor
