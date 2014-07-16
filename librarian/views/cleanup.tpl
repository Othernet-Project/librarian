% rebase('base.tpl', title=_('Archive clean-up'))
<h1>{{ _('Archive clean-up') }}</h1>

% if message:
<p class="message">{{ message }}</p>
% end

% if needed:
<p class="note">
{{ str(_('%s more space should be freed.')) % h.hsize(needed) }}
</p>
<p class="note">
{{ _('Remember that favorited content cannot be deleted.') }}
</p>
% else:
<p class="note">
{{ _('There is enough free space on storage') }}
</p>
% end

<form action="{{ i18n_path('/cleanup/') }}" method="POST">
<table>
    <tr class="header">
    <th>{{ _('delete?') }}</th>
    <th>{{ _('date') }}</th>
    <th>{{ _('title') }}</th>
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
        <td colspan="5">{{ _('There is enough free space. No clean-up needed.') }}</td>
        <tr>
    % end
</table>
% if needed:
<p class="buttons">
<button type="submit" name="action" value="check">{{ _('How much space does this free up?') }}</button>
<button type="submit" name="action" value="delete">{{ _('Delete selected now') }}</button>
</p>
% end
</form>
