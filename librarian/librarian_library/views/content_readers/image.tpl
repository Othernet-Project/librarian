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
            <a class="back" href="${content_url + h.set_qparam(content_type=chosen_content_type).del_qparam('path').to_qs()}"></a>
        </div>
        <div class="image-viewer">
            <script id="imageURLs" type="application/json">
                {
                    "urls": [
                    % for image in meta['image']['album']:
                        <% sep = ',' if not loop.last else '' %>
                        "${url('content:file', content_path=th.get_content_path(meta.md5), filename=image['file'])}"${sep}
                    % endfor
                    ]
                }
            </script>
            % if img_index > 0:
            <div class="cell">
                <a class="previous" href="${content_url + h.set_qparam(content_type=chosen_content_type).set_qparam(path=img_index - 1).to_qs()}"></a>
            </div>
            % endif
            <div class="cell image-container">
                <img src=${url('content:file', content_path=th.get_content_path(meta.md5), filename=meta['image']['album'][img_index]['file'])} data-index="${img_index}" />
            </div>
            % if img_index < img_count - 1:
            <div class="cell">
                <a class="next" href="${content_url + h.set_qparam(content_type=chosen_content_type).set_qparam(path=img_index + 1).to_qs()}"></a>
            </div>
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
    <%
        img_count = len(meta['image']['album'])
        try:
            img_index = int(chosen_path)
        except Exception:
            img_index = None
    %>
    % if img_index >= 0 and img_index < img_count:
    <div class="content-info">
        <% image = meta.image['album'][img_index] %>
        % if image.get('title'):
        <div class="title">${image['title']}</div>
        % endif
        % if image.get('caption'):
        <div class="caption">${image['caption']}</div>
        % endif
        % if image.get('resolution'):
        <div class="dimensions">${image['resolution']}</div>
        % endif
    </div>
    % else:
    <div class="content-info">
        <div class="title">${meta.title}</div>
        <div class="download-date">${meta.timestamp.date()}</div>
        % if meta.image.get('description'):
        <div class="description">${meta.image['description']}</div>
        % endif
    </div>
    <div class="tag-editor">
        ${tags.tags(meta)}
    </div>
    % endif
    ## Translators, attribution line appearing in the content list
    <p class="attrib">
    % if meta.publisher:
    ${_('%(date)s by %(publisher)s.') % dict(date=meta.timestamp.strftime('%Y-%m-%d'), publisher=meta.publisher)}
    % else:
    ${meta.timestamp.strftime('%Y-%m-%d')}
    % endif
    ${th.readable_license(meta.license)}
    </p>
</%def>
