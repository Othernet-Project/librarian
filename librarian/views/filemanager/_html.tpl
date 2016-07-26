% if 'html' not in current.meta.content_type_names:
    <span class="note">${_('No documents to be shown.')}</span>
% else:
    <%
    full_path = th.join(path, selected_name or current.meta.get('main', language=request.locale))
    %>

    <div class="views-reader" id="views-reader">
        <iframe class="views-reader-frame" src="${h.quoted_url('filemanager:direct', path=full_path)}" id="views-reader-frame" data-override-partial="${assets['css/overrides']}" data-override-full="${assets['css/restyle']}"></iframe>
    </div>
% endif
