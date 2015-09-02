<%namespace name="tags" file="/_tags.tpl"/>

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
                <a class="play" href="javascript:;"></a>
            </li>
            % endfor
        </ul>
    </div>
</%def>

<%def name="meta_display()">
    <div class="content-info">
        <div class="title">${meta.title}</div>
        <div class="download-date">${meta.timestamp.date()}</div>
        % if meta.audio.get('description'):
        <div class="description">${meta.audio['description']}</div>
        % endif
        <% duration = sum([track.get('duration') or 0 for track in meta.audio['playlist']]) %>
        <div class="duration">${duration}</div>
    </div>
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
