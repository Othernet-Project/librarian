<%def name="reader_display()">
    <h3 id="audio-title">${meta['audio']['playlist'][0]['title']}</h3>
    <audio id="audio-player" controls="controls">
        <source src="${url('content:file', content_path=th.get_content_path(meta.md5), filename=meta['audio']['playlist'][0]['file'])}" />
    </audio>
    <ul class="playlist">
        % for track in meta['audio']['playlist']:
        <li data-url="${url('content:file', content_path=th.get_content_path(meta.md5), filename=track['file'])}">
            <span class="title">${track['title']}</span>
            <span>(${track['duration']})</span>
            <a class="play" href="javascript:;">${_("Play")}</a>
        </li>
        % endfor
    </ul>
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
