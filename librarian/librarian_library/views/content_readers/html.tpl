<%namespace name="tags" file="/_tags.tpl"/>

<%def name="reader_display()">
    <iframe id="reader-main" class="reader-main" src="${url('content:file', content_path=th.get_content_path(meta.md5), filename=meta['html']['main'])}" data-keep-formatting="${meta['html']['keep_formatting']}"></iframe>
</%def>

<%def name="meta_display()">
    <div class="tag-editor">
        ${tags.tags(meta)}
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
