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
    ## Translators, attribution line appearing in the content list
    <p class="attrib">
    ## Translators, used in place of publisher name if publsiher name is not known
    <% publisher = meta.publisher or _('unknown publisher') %>
    ${_('%(date)s by %(publisher)s.') % dict(date=meta.timestamp.strftime('%Y-%m-%d'), publisher=publisher)}
    ${th.readable_license(meta.license)}
    </p>
</%def>
