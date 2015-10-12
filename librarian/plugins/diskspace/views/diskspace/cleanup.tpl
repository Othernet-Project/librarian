<%inherit file="../base.tpl"/>

<%block name="title">
## Translators, used as page title
${_('Library Clean-Up')}
</%block>

<%block name="heading">
## Translators, used as page heading on clean-up page
${_('Library clean-up')}
</%block>

% if message:
<p class="message">${message}</p>
% endif

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

<form action="${i18n_url('plugins:diskspace:cleanup')}" method="POST">
    <table>
        <tr class="header">
        ## Translators, in table header on clean-up page, above checkboxes for marking deletion candidates
        <th>${_('delete?')}</th>
        ## Translators, in table header on clean-up page, date added to library
        <th>${_('date')}</th>
        ## Translators, in table header on clean-up page, content title
        <th>${_('title')}</th>
        ## Translators, in table header on clean-up page, content size on disk
        <th>${_('size')}</th>
        </tr>
        % if needed:
            % for meta in metadata:
            <tr>
            <td>
            <% id = 'selection-{}'.format(meta['md5']) %>
            ${h.vcheckbox(id, meta['md5'], vals, default=True)}
            <label for="${id}">
            </td>
            <td>${meta['updated'].strftime('%m-%d')}</td>
            <td><a href="${i18n_url('content:reader', content_id=meta['md5'])}">${meta['title']}</a></td>
            <td>${h.hsize(meta['size'])}</td>
            </tr>
            % endfor
        % else:
            <tr>
            ## Translators, note that appears on clean-up page inside the table where deletion candidates would normally be shown
            <td colspan="5">${_('There is enough free space. No clean-up needed.')}</td>
            <tr>
        % endif
    </table>
    % if needed:
    <p class="buttons">
    ## Translators, used as button label for clean-up preview button
    <button type="submit" name="action" value="check">${_('How much space does this free up?')}</button>
    ## Translators, used as button label for clean-up start button, user selects content to be deleted before using this button
    <button type="submit" name="action" value="delete">${_('Delete selected now')}</button>
    </p>
    % endif
</form>
## Translators, used as button lable for checking all boxes
<button id="select">${_('Select All')}</button>
## Translators, used as button lable for unchecking all boxes
<button id="deselect">${_('Deselect All')}</button>
