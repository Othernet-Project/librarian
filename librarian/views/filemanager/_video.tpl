<%inherit file="_playlist.tpl" />

<%def name="video_control(url)">
    <div id="video-controls-video-wrapper" class="video-controls-video-wrapper">
        <video id="video-controls-video" controls="controls" width="100%" height="100%" preload="none">
            <source src="${url | h}" />
            <object type="application/x-shockwave-flash" data="${assets.url}vendor/mediaelement/flashmediaelement.swf">
                <param name="movie" value="${assets.url}vendor/mediaelement/flashmediaelement.swf" />
                <param name="flashvars" value="controls=true&file=${url | h}" />
            </object>
        </video>
    </div>
</%def>

% if 'video' not in current.meta.content_type_names:
<span class="note">${_('No video files to be played.')}</span>
% else:
<%
  video_url = h.quoted_url('filemanager:direct', path=selected.rel_path)
%>
<div class="video-controls" id="video-controls">
    ${video_control(video_url)}
</div>
% endif

<%def name="sidebar()">
    %if 'video' in current.meta.content_type_names:
        ${self.sidebar_playlist(files, selected)}
    %endif
</%def>

<%def name="sidebar_playlist_item_metadata(entry)">
    <% metadata = entry.meta %>
    ${self.sidebar_playlist_item_metadata_desc(metadata)}
    ${self.sidebar_playlist_item_metadata_author(metadata)}
    ${self.sidebar_playlist_item_metadata_duration(metadata)}
    ${self.sidebar_playlist_video_dimensions(metadata)}
    ${self.sidebar_playlist_aspect_ratio(metadata)}
</%def>

<%def name="sidebar_playlist_item(entry, selected_entry)">
    <%
        file = entry.name
        current = entry.name == selected_entry.name
        file_path = entry.rel_path
        mimetype = entry.meta.mime_type or ''
        url = i18n_url('filemanager:list', view=view, path=path, selected=file)
        meta_url = i18n_url('filemanager:details', view=view, path=path, info=file)
        direct_url = h.quoted_url('filemanager:direct', path=file_path)
        metadata = entry.meta
        title = metadata.get('title') or th.facets.titlify(file)
        description = metadata.get('description') or _('No description')
        duration = metadata.get('duration', default=0)
        hduration = th.facets.durify(duration)
        width = metadata.get('width', default=0)
        height = metadata.get('height', default=0)
    %>
    <li
    class="playlist-list-item ${'playlist-list-item-current' if current else ''}"
    role="row"
    aria-selected="false"
    data-title="${title | h}"
    data-description="${description | h}"
    data-duration="${duration}"
    data-width="${width}"
    data-height="${height}"
    data-mimetype="${mimetype | h}"
    data-type="file"
    data-relpath="${file_path | h.urlquote}"
    data-url="${url}"
    data-meta-url="${meta_url}"
    data-direct-url="${direct_url}">
    <a class="playlist-list-item-link" href="${url}">
        <span class="playlist-list-duration">
            ${hduration}
        </span>
        <span class="playlist-list-title">
            ${title | h}
        </span>
    </a>
    </li>
</%def>
