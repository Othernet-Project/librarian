% rebase('base.tpl', title=_('Updates'))
<h1>{{ _('Updates') }}</h1>

<form method="POST">
<table>
    <thead>
        <tr>
        <th>{{ _('select') }}</th>
        <th>{{ _('title') }}</th>
        <th>{{ _('timestamp') }}</th>
        </tr>
    </thead>
    <tbody>
        % if metadata:
            % for meta in metadata:
            <tr>
                <td class="downloads-selection">
                    <input type="checkbox" name="selection" value="{{ meta['md5'] }}" checked>
                </td>
                <td class="downloads-title">{{ meta['title'] }}</td>
                <td class="downloads-timestamp">{{ meta['timestamp'] }}</td>
            </tr>
            % end
        % else:
            <tr>
            <td class="empty" colspan="3">{{ _('There is no new content') }}</td>
            </tr>
        % end
    </tbody>
</table>

<p class="buttons">
<button type="submit" name="action" value="add">{{ _('Add selected to archive') }}</button>
<button type="submit" name="action" value="delete">{{ _('Delete selected') }}</button>
</p>
</form>

% if errors:
<h2>Errors</h2>
<ul class="error">
    % for error in errors:
    <li>{{ error.message }}</li>
    % end
</ul>
% end
