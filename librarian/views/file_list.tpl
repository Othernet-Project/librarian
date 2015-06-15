<%inherit file="base.tpl"/>
<%namespace name='library_submenu' file='_library_submenu.tpl'/>

<%block name="title">
## Translators, used as page title
${_('Files')}
</%block>

${library_submenu.body()}

<div class="h-top-bar">
    ${h.form('get', _class='location-bar inline')}
        ## Translators, used in file search box
        <input type="text" name="p" class="search" value="${path if path != '.' else ''}" placeholder="${_('Search')}">
        ## Translators, used as button in file view address bar
        <button type="submit" class="fake-go">${_('go')}</button>
    </form>
</div>

<div class="file-list">

    <table class="file-list-listing">
        % if path != '.':
        <tr class="up">
            <% uppath = i18n_url('files:path', path=up) %>
            <td class="icon"><a href="${uppath}"><span class="icon"></span></a></td>
            ## Translators, used as label for link that leads to parent directory in file listing
            <td colspan="4"><a href="${uppath}" class="upone">${_('Go up one level')}<a></td>
        </tr>
        % elif is_missing or is_search:
        <tr class="up">
            <td class="icon"><a href="${i18n_url('files:list')}"><span class="icon"></span></a></td>
            ## Translators, used as label for link that leads to file list
            <td colspan="4"><a href="${i18n_url('files:list')}">${_('(go to file list)')}<a></td>
        </tr>
        % endif
        % if (not dirs) and (not files):
        <tr class="empty">
            ## Tanslators, shown in files section when current folder is empty
            <td class="empty" colspan="6">${_('There are currently no files or folders here.')}</td>
        </tr>
        % else:
            % for d in dirs:
            <tr class="dir">
                <% dpath = i18n_url('files:path', path=d.path) %>
                <td class="icon"><a href="${dpath}"><span class="icon"></span></a></td>
                <td class="name" colspan="2"><a href="${dpath}">${d.name}</a></td>
                <td class="rename">
                    ${h.form('post', action=dpath)}
                        <input type="text" name="name" value="${d.name}"><button name="action" value="rename" type="submit">${_('Rename')}
                    </form>
                </td>
                <td class="delete">
                    ${h.form('post', action=dpath)}
                        <button class="delete" name="action" value="delete" type="submit">${_('Delete')}
                    </form>
                </td>
                <td>
                </td>
            </tr>
            % endfor
            % for f in files:
            <tr class="file">
                <% fpath = i18n_url('files:path', path=f.path) %>
                <td class="icon"><a href="${fpath}?filename=${f.name}"><span class="icon"></span></a></td>
                <td class="name"><a href="${fpath}?filename=${f.name}">${f.name}</a></td>
                <td class="size">${h.hsize(f.size)}</td>
                <td class="rename">
                    ${h.form('post', action=fpath)}
                        <input type="text" name="name" value="${f.name}"><button name="action" value="rename" type="submit">${_('Rename')}
                    </form>
                </td>
                <td class="delete">
                    ${h.form('post', action=fpath)}
                        <button class="danger" name="action" value="delete" type="submit">${_('Delete')}
                    </form>
                </td>
                <td class="execute">
                    % if f.path.endswith('.sh'):
                    ${h.form('post', action=fpath)}
                        ## Translators, label for button in file listing that allows user to run a script
                        <button class="small" name="action" value="exec" type="submit">${_('Run')}
                    </form>
                    % endif
                </td>
            </tr>
            % endfor
        % endif
    </table>

    % if readme:
    <div class="files-readme">
        <h2>${_('About this folder')}</h2>
        <pre class="readme">${readme}</pre>
    </div>
    % endif
</div>
