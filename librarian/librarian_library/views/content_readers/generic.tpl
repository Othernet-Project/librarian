<%namespace name="tags" file="/_tags.tpl"/>

<%def name="reader_display()">
    % if len(meta.files) == 1:
    <% ((filename, filesize),) = meta.files %>
    <div class="single-download">
        <a class="download-button" href="${url('content:file', content_path=th.get_content_path(meta.md5), filename=filename)}"></a>
        <div class="filename">${filename}</div>
        <div class="filesize">${h.hsize(filesize)}</div>
    </div>
    % else:
    <ul class="download-list">
        % for download in meta.files:
        <li>
            <%
            filename, filesize = download
            download_url = url('content:file', content_path=th.get_content_path(meta.md5), filename=filename)
            %>
            <span class="file-info">
                <a class="filename" href="${download_url}">${filename}</a>
                <span class="filesize">${h.hsize(filesize)}</span>
            </span>
            <a class="download-link" href="${download_url}"></a>
        </li>
        % endfor
    </ul>
    % endif
</%def>

<%def name="meta_display()">
    <div class="content-info">
        <div class="title">${meta.title}</div>
        <div class="download-date">${meta.timestamp.date()}</div>
        % if meta.generic.get('description'):
        <div class="description">${meta.generic['description']}</div>
        % endif
    </div>
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
