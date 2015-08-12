<%def name="reader_display()">
    <div class="player">
        <h3 id="audio-title">${meta['audio']['playlist'][0]['title']}</h3>
        <audio id="audio-player" src="${url('content:file', content_path=th.get_content_path(meta.md5), filename=meta['audio']['playlist'][0]['file'])}"></audio>
        <ul class="playlist">
            % for track in meta['audio']['playlist']:
            <li data-url="${url('content:file', content_path=th.get_content_path(meta.md5), filename=track['file'])}">
                <span class="track-info">
                    <span class="title">${track['title']}</span>
                    % if track.get('duration'):
                    <span>(${track['duration']})</span>
                    % endif
                </span>
                <a class="play" href="javascript:;">&#9658;</a>
            </li>
            % endfor
        </ul>
    </div>
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
