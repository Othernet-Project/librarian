<%def name="reader_display()">
    <iframe id="reader-main" class="reader-main" src="${url('content:file', content_path=th.get_content_path(meta.md5), filename='index.html')}"></iframe>
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
