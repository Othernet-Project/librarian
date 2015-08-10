<%def name="reader_display()">
    <%
        width, height = map(lambda x: int(x) if x else '100%', (meta['video'].get('resolution') or 'x').split('x'))
        video_url = url('content:file', content_path=th.get_content_path(meta.md5), filename=meta['video']['file'])
    %>
    <video width="${width}" height="${height}" controls="controls" preload="none">
        <source src="${video_url}" />
        <object width="${width}" height="${height}" type="application/x-shockwave-flash" data="${assets.url}vendor/mediaelement/flashmediaelement.swf">
            <param name="movie" value="${assets.url}vendor/mediaelement/flashmediaelement.swf" />
            <param name="flashvars" value="controls=true&file=${video_url}" />
        </object>
    </video>
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
