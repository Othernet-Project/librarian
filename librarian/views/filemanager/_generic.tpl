<%namespace name="folder", file="_folder.tpl"/>

<% 
    is_super = request.user.is_superuser 
    name = current.dirinfo.get(request.locale, 'name', 
                               titlify(current.name))
    cover = current.dirinfo.get(request.locale, 'cover', None)
    desc = current.dirinfo.get(request.locale, 'description', None)
    needs_intro = cover or desc
%>

% if cover or desc:
    <div class="file-list-current${' with-cover' if cover else ''}">
        % if cover:
            <div class="file-list-current-cover file-list-current-block">
                <img src="${h.quoted_url('files:direct', path=current.other_path(cover))}">
            </div>
        % endif
        <div class="file-list-current-info file-list-current-block">
            <h2>${name | h}</h2>
            % if desc:
                <p class="file-list-current-description">
                    ${desc | h}
                </p>
            % endif
            <p class="file-list-current-stats">
                ${ngettext("{} file", "{} files", len(files)).format(len(files))} /
                ${ngettext("{} folder", "{} folders", len(dirs)).format(len(dirs))}
            </p>
        </div>
    </div>
% endif 

<ul class="file-list" id="file-list" role="grid" aria-multiselectable="true">

    ## *** FOLDER LISTING ***

    % if (not dirs) and (not files):

        ## If the listing is empty, then only the empty listing li is shown
        <li class="file-list-empty file-list-item">
        <span class="note">
            % if is_search:
            ${_('No files or folders match your search keywords.')}
            % else:
            ${_('There are currently no files or folders here.')}
            % endif
        </span>
        </li>

    % else:

        ## Directories

        % for d in dirs:
            ${folder.folder(d, not is_search)}
        % endfor

        ## Files

        % for f in files:
            ${folder.file(f, with_controls=not is_search, is_search=is_search)}
        % endfor
    % endif
</ul>
