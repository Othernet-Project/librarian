<%namespace name="tags" file="/_tags.tpl"/>

<%def name="reader_display()">
    <%
        content_url = i18n_url('content:reader', content_id=meta.md5)
        img_count = len(meta['image']['album'])
        try:
            img_index = int(chosen_path)
        except Exception:
            img_index = None
    %>
    % if img_index >= 0 and img_index < img_count:
        <div class="top-controls">
            <a class="back" href="${content_url + h.set_qparam(content_type=chosen_content_type).del_qparam('path').to_qs()}">&larr;</a>
        </div>
        <div class="image-viewer">
            % if img_index > 0:
            <a class="previous" href="${content_url + h.set_qparam(content_type=chosen_content_type).set_qparam(path=img_index - 1).to_qs()}"></a>
            % endif
            <div class="image-container">
                <img src=${url('content:file', content_path=th.get_content_path(meta.md5), filename=meta['image']['album'][img_index]['file'])} />
            </div>
            % if img_index < img_count - 1:
            <a class="next" href="${content_url + h.set_qparam(content_type=chosen_content_type).set_qparam(path=img_index + 1).to_qs()}"></a>
            % endif
        </div>
    % else:
    <ul class="album">
    % for image in meta['image']['album']:
        <%
            thumb_path = image.get('thumbnail')
            if not thumb_path:
                thumb_path = image['file']
            thumb_url = url('content:file', content_path=th.get_content_path(meta.md5), filename=thumb_path)
        %>
        <li class="album-item">
            <a href="${content_url + h.set_qparam(content_type=chosen_content_type).set_qparam(path=loop.index).to_qs()}">
                <img class="thumbnail" src="${thumb_url}" />
                <span class="title">${image['title'] if image.get('title') else _('Image %s of %s') % (loop.index, img_count)}</span>
            </a>
        </li>
    % endfor
    </ul>
    % endif
</%def>

<%def name="meta_display()">
    <div class="tag-editor">
        ${tags.tags(meta)}
    </div>
    ## Translators, attribution line appearing in the content list
    <p class="attrib">
    ## Translators, used in place of publisher name if publsiher name is not known
    <% publisher = meta.publisher or _('unknown publisher') %>
    ${_('%(date)s by %(publisher)s.') % dict(date=meta.timestamp.strftime('%Y-%m-%d'), publisher=publisher)}
    ${th.readable_license(meta.license)}
    </p>
</%def>
