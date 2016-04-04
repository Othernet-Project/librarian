<%inherit file="_playlist.tpl" />

<div class='gallery-container' id="gallery-container">
    % if 'image' not in facet_types:
        <span class="note">${_('No images to be shown.')}</span>
    % else:
        <%
            selected_entry = get_selected(files, selected)
            previous, next = get_adjacent(files, selected_entry)
            previous_url = i18n_url('files:path', view=view, path=path, selected=previous.name)
            next_url = i18n_url('files:path', view=view, path=path, selected=next.name)
            direct_url = h.quoted_url('files:direct', path=selected_entry.rel_path)
        %>
        <div class="gallery-current-image" id="gallery-current-image">
            <img class="gallery-current-image-img" src='${direct_url}'/>
        </div>
        <a
            class="gallery-control gallery-control-previous"
            id="gallery-control-previous"
            href="${previous_url}">
            <span class="icon icon-expand-left"></span>
            <span class="label">
                ${_('Previous')}
            </span>
        </a>
        <a
            class="gallery-control gallery-control-next"
            id="gallery-control-next"
            href="${next_url}">
            <span class="icon icon-expand-right"></span>
            <span class="label">
                ${_('Next')}
            </span>
        </a>
    % endif
</div>

<%def name="sidebar()">
    % if 'image' in facet_types:
        <%
            selected_entry = get_selected(files, selected)
        %>
        ${self.sidebar_playlist(files, selected_entry)}
    % endif
</%def>

<%def name="sidebar_playlist_item_metadata(entry)">
    <% metadata = entry.facets %>
    ${self.sidebar_playlist_item_metadata_desc(metadata)}
    ${self.sidebar_playlist_item_metadata_author(metadata)}
    ${self.sidebar_playlist_image_dimensions(metadata)}
    ${self.sidebar_playlist_aspect_ratio(metadata)}
</%def>


<%def name="sidebar_playlist_item(entry, selected_entry)">
    <%
        file = entry.name
        current = entry == selected_entry
        file_path = entry.rel_path
        url = i18n_url('files:path', view=view, path=path, selected=file)
        meta_url = i18n_url('files:path', view=view, path=path, info=file)
        direct_url = h.quoted_url('files:direct', path=file_path)
        thumb_url = h.quoted_url('files:direct', path=th.get_thumb_path(file_path))
        metadata = entry.facets
        title = metadata.get('title') or titlify(file)
        img_width = metadata.get('width', 0)
        img_height = metadata.get('height', 0)
    %>
    <li
    class="gallery-list-item ${'gallery-list-item-current' if current else ''}"
    role="row"
    aria-selected="false"
    data-title="${title | h}"
    data-direct-url="${direct_url}"
    data-url="${url}"
    data-img-width="${img_width}"
    data-meta-url="${meta_url}"
    data-img-height="${img_height}">
    <a class="gallery-list-item-link" href="${url}">
        <img class="gallery-list-item-thumbnail" src="${thumb_url}" alt="${title}" title="${title}"/>
    </a>
    </li>
</%def>
