<%def name="thumb_block(icon, icon_type='icon')">
    <span class="file-list-icon file-list-icon-${icon_type}">
    % if icon_type in ['cover', 'thumb']:
        <span style="background-image: url('${icon}');"></span>
    % else:
        <span class="icon icon-${icon}"></span>
    % endif
    </span>
</%def>

<%def name="file_delete(path)">
    <form action="${i18n_url('files:path', path=path)}" class="file-list-delete file-list-control">
        <input type="hidden" name="action" value="delete">
        <button class="nobutton" type="submit">
            <span class="icon icon-no-outline"></span>
            ## Translators, used as label for folder/file delete button
            <span class="label">${_('Delete')}</span>
        </button>
    </form>
</%def>

<%def name="file_download(path)">
    <a href="${url('files:direct', path=h.urlquote(path))}" class="file-list-control">
        <span class="icon icon-download-outline"></span>
        <span class="label">${_('Download')}</span>
    </a>
</%def>

<%def name="file_parent_folder(path)">
    <a href="${path}" class="file-list-control">
        <span class="icon icon-folder-right"></span>
        <span class="label">
            ## Translators, link to containing folder of a file in search results
            ${_('Open containing folder')}
        </span>
    </a>
</%def>

<%def name="file_info_inner()">
    <span class="file-list-info">
        <span class="file-list-info-inner">
            ${caller.body()}
        </span>
    </span>
</%def>

<%def name="folder(d, with_controls=False)">
    <%
    description = d.dirinfo.get(request.locale, 'description', None)
    default_view = d.dirinfo.get(request.locale, 'view', None)
    varg = {'view': default_view} if default_view else {}
    dpath = i18n_url('files:path', path=d.rel_path, **varg)
    cover_url = th.get_folder_cover(d)
    icon, icon_is_url = th.get_folder_icon(d)
    %>
    <li class="file-list-item file-list-directory${' with-controls' if with_controls else ''}" role="row" aria-selected="false" tabindex>
        <a href="${dpath}" data-type="directory" class="file-list-link">
            ## COVER/ICON
            % if cover_url:
                ${self.thumb_block(cover_url, 'cover')}
            % elif icon_is_url:
                ${self.thumb_block(icon, 'thumb')}
            % else:
                ${self.thumb_block(icon, 'icon')}
            % endif
            ## INFO BLOCK
            <%self:file_info_inner>
                ## NAME
                <span class="file-list-name">
                    ${th.get_folder_name(d) | h}
                </span>
                ## DESCRIPTION
                % if description:
                    <span class="file-list-description">
                        ${description | h}
                    </span>
                % endif
            </%self:file_info_inner>
        </a>
        ## CONTROLS
        % if with_controls:
            <span class="file-list-controls">
                % if request.user.is_superuser:
                    ${self.file_delete(d.rel_path)}
                % endif
            </span>
        % endif
    </li>
</%def>

<%def name="file(f, with_controls=False, is_search=False, use_meta=False)">
    <%
        # FIXME: For some reason known only to gods of programming, the 
        # following line, which otherwise appears completely useless, **MUST** 
        # be there or `h` variable becomes unavailable to the rest of the def.
        h.quoted_url  # <-- again, don't remove this
        fpath = th.get_view_path(f)
        apath = i18n_url('files:path', path=f.rel_path)
        parent_view = 'generic' if is_search else None
        parent_url = th.get_parent_url(f.rel_path, parent_view)
        icon, is_thumb = th.get_file_thumb(f)
        title = f.facets.get('title')
        desc = f.facets.get('description')
    %>
    <li class="file-list-item file-list-file${' with-controls' if with_controls else ''}${' file-list-search-result' if is_search else ''}" role="row" aria-selected="false" tabindex>
        <a
            href="${fpath}"
            data-relpath="${f.rel_path | h.urlquote}"
            data-mimetype="${(f.mimetype or '') | h}"
            data-type="file"
            class="file-list-link"
            >
            ${self.thumb_block(icon, 'cover' if is_thumb else 'icon')}
            <%self:file_info_inner>
                <span class="file-list-name">
                    % if use_meta:
                        ${title or h.to_unicode(f.name) | h}
                    % else:
                        ${h.to_unicode(f.name) | h}
                    % endif
                </span>
                % if is_search and f.parent:
                    <span class="file-list-description">
                        ${_(u"in {}").format(esc(f.parent))}
                    </span>
                % else:
                    % if title:
                        <span class="file-list-description">
                            ${title | h}
                        </span>
                    % endif
                % endif
            </%self:file_info_inner>
        </a>
        <span class="file-list-controls">
            % if is_search:
                ${self.file_parent_folder(parent_url)}
            % endif
            ${self.file_download(f.rel_path)}
            % if with_controls:
                % if request.user.is_superuser:
                    ${self.file_delete(f.rel_path)}
                % endif
            % endif
        </span>
    </li>
</%def>
