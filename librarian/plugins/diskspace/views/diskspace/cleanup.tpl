<%inherit file="../base.tpl"/>
<%namespace name="simple_pager" file="../_simple_pager.tpl"/>

<link rel="stylesheet" href="${assets['css/cleanup']}" />

<%block name="title">
## Translators, used as page title
${_('Library Clean-Up')}
</%block>

<div class="h-bar">
    <h1>
        ## Translators, used as page heading on clean-up page
        ${_('Library clean-up')}
    </h1>

    % if message:
    <h4>
    <p class="message">${message}</p>
    </h4>
    % endif

    % if metadata:
        % if needed:
        <p class="note">
        ## Translators, %s represents the amount of space in bytes, KB, MB, etc
        ${_('%s more space should be freed.') % h.hsize(needed)}
        </p>
        % else:
        <p class="note">
        ## Translators, note that appears on clean-up page when user goes to it even though there is enough space
        ${_('There is enough free space on storage')}
        </p>
        % endif
    % else:
        <p class="note">
        ## Translators, note that appears on clean-up page when there is no content to remove
        ${_('There are no items in the library to remove')}
        </p>
    % endif
</div>


% if metadata:
    <form action="${i18n_url('plugins:diskspace:cleanup')}" method="POST">
        <div class="h-bar">
            <p class="buttons">
                ## Translators, used as button lable for checking all boxes
                <button type="button" class="select">${_('Select All')}</button>
                ## Translators, used as button lable for unchecking all boxes
                <button type="button" class="deselect">${_('Deselect All')}</button>

                ## Translators, used as button label for clean-up preview button
                <button type="submit" name="action" value="check">${_('How much space does this free up?')}</button>
                ## Translators, used as button label for clean-up start button, user selects content to be deleted before using this button
                <button type="submit" name="action" value="delete">${_('Delete selected now')}</button>
            </p>
        </div>
        <div class="bottom-pager">
            ${simple_pager.prev_next_pager()}
        </div>

        <table id="cleanup-list">
            <tr class="header">
            ## Translators, in table header on clean-up page, above checkboxes for marking deletion candidates
            <th>${_('delete?')}</th>
            ## Translators, in table header on clean-up page, date added to library
            <th>${_('date')}</th>
            ## Translators, in table header on clean-up page, content size on disk
            <th>${_('size')}</th>
            ## Translators, in table header on clean-up page, content title
            <th>${_('title')}</th>
            </tr>
            % for meta in metadata:
            <tr>
            <td>
            <% id = 'selection-{}'.format(meta['md5']) %>
            ${h.vcheckbox(id, meta['md5'], vals, default=True)}
            <label for="${id}">
            </td>
            <td>${meta['updated'].strftime('%m-%d')}</td>
            <td class="size">${h.hsize(meta['size'])}</td>
            <td><a href="${i18n_url('content:reader', content_id=meta['md5'])}">${meta['title']}</a></td>
            </tr>
            % endfor
        </table>
        <div class="bottom-pager">
            ${simple_pager.prev_next_pager()}
        </div>
        <div class="h-bar">
            <p class="buttons">
                ## Translators, used as button lable for checking all boxes
                <button type="button" class="select">${_('Select All')}</button>
                ## Translators, used as button lable for unchecking all boxes
                <button type="button" class="deselect">${_('Deselect All')}</button>

                ## Translators, used as button label for clean-up preview button
                <button type="submit" name="action" value="check">${_('How much space does this free up?')}</button>
                ## Translators, used as button label for clean-up start button, user selects content to be deleted before using this button
                <button type="submit" name="action" value="delete">${_('Delete selected now')}</button>
            </p>
        </div>
    </form>
% endif
