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

% if 'video' not in facet_types:
<span class="note">${_('No video files to be played.')}</span>
% else:
<%
  selected_entry = get_selected(files, selected)
  video_url = h.quoted_url('files:direct', path=selected_entry.rel_path)
%>
<div class="video-controls" id="video-controls">
    ${video_control(video_url)}
</div>
% endif

<%def name="sidebar()">
    %if 'video' in facet_types:
        <%
        selected_entry = get_selected(files, selected)
        %>
        ${self.sidebar_playlist(files, selected_entry)}
    %endif
</%def>

<%def name="sidebar_playlist_item_metadata(entry)">
    <% metadata = entry.facets %>
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
        url = i18n_url('files:path', view=view, path=path, selected=file)
        meta_url = i18n_url('files:path', view=view, path=path, info=file)
        direct_url = h.quoted_url('files:direct', path=file_path)
        metadata = entry.facets
        title = metadata.get('title') or titlify(file)
        description = metadata.get('description') or _('No description')
        duration = metadata.get('duration', 0)
        hduration = durify(duration)
        width = metadata.get('width', 0)
        height = metadata.get('height', 0)
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
