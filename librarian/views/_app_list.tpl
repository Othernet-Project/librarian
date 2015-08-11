% for meta in metadata:
<li class="app">
    <img src="${url('content:file', content_path=th.get_content_path(meta.md5), filename=meta.cover) if meta.cover else ''}" />
    <a href="${i18n_url('content:reader', content_id=meta.md5) + h.set_qparam(content_type=chosen_content_type).to_qs()}">${meta.title | h}</a>
    <span>${meta.app['version']}</span>
</li>
% endfor
