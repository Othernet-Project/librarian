% rebase('base.tpl', title=_('Archive clean-up'))
%# Translators, used as page title on clean-up page
<h1>{{ _('Archive clean-up') }}</h1>

% if message:
<p class="message">{{ message }}</p>
% end

% if needed:
<p class="note">
%# Translators, %s represents the amount of space in bytes, KB, MB, etc
{{ str(_('%s more space should be freed.')) % h.hsize(needed) }}
</p>
<p class="note">
%# Translators, used as note that appears on clean-up page
{{ _('Remember that favorited content cannot be deleted.') }}
</p>
% else:
<p class="note">
%# Translators, note that appears on clean-up page when user goes to it even though there is enough space
{{ _('There is enough free space on storage') }}
</p>
% end

<form action="{{ i18n_path('/cleanup/') }}" method="POST">
<table>
    <tr class="header">
    %# Translators, in table header on clean-up page, above checkboxes for marking deletion candidates
    <th>{{ _('delete?') }}</th>
    %# Translators, in table header on clean-up page, date added to archive
    <th>{{ _('date') }}</th>
    %# Translators, in table header on clean-up page, content title
    <th>{{ _('title') }}</th>
    %# Translators, in table header on clean-up page, content size on disk
    <th>{{ _('size') }}</th>
    </tr>
    % if needed:
        % for meta in metadata:
        <tr>
        <td>
        {{! h.checkbox('selection', meta['md5'], vals, default=True) }}
        </td>
        <td>{{ meta['updated'].strftime('%m-%d') }}</td>
        <td><a href="{{ i18n_path('/content/%s/' % meta['md5']) }}">{{ meta['title'] }}</a></td>
        <td>{{ h.hsize(meta['size']) }}</td>
        </tr>
        % end
    % else:
        <tr>
        %# Translators, note that appears on clean-up page inside the table where deletion candidates would normally be shown
        <td colspan="5">{{ _('There is enough free space. No clean-up needed.') }}</td>
        <tr>
    % end
</table>
% if needed:
<p class="buttons">
%# Translators, used as button label for clean-up preview button
<button type="submit" name="action" value="check">{{ _('How much space does this free up?') }}</button>
%# Translators, used as button label for clean-up start button, user selects content to be deleted before using this button
<button type="submit" name="action" value="delete">{{ _('Delete selected now') }}</button>
</p>
% end
</form>
