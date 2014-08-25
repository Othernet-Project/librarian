% rebase('base.tpl', title=_('Updates'))
<h1>{{ _('Updates') }}</h1>

<form method="POST">
<p class="controls" id="controls">
    <a class="sel-all button" href="?sel=1">{{ _('Select all') }}</a>
    <a class="sel-none button" href="?sel=0">{{ _('Select none') }}</a>
    <button type="submit" name="action" value="add" class="special">{{ _('Add selected to archive') }}</button>
    <button type="submit" name="action" value="delete" class="danger">{{ _('Delete selected') }}</button>
</p>

<table>
    <thead>
        <tr>
        <th>{{ _('select') }}</th>
        <th>{{ _('title') }}</th>
        <th>{{ _('broadcast') }}</th>
        <th>{{ _('downloaded') }}</th>
        </tr>
    </thead>
    <tbody>
        % if metadata:
            % for meta in metadata:
            <tr>
                <td class="downloads-selection">
                    <input id="check-{{ meta['md5'] }}" type="checkbox" name="selection" value="{{ meta['md5'] }}"{{ selection and ' checked' or ''}}>
                </td>
                <td class="downloads-title">
                    <label for="check-{{ meta['md5'] }}">{{ meta['title'] }}</label>
                </td>
                <td class="downloads-timestamp">{{ h.strft(meta['timestamp'], '%m-%d') }}</td>
                <td class="downloads-ftimestamp">{{ meta['ftimestamp'].strftime('%m-%d') }}</td>
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
<a class="sel-all button" href="?sel=1">{{ _('Select all') }}</a>
<a class="sel-none button" href="?sel=0">{{ _('Select none') }}</a>
<button type="submit" name="action" value="add" class="special">{{ _('Add selected to archive') }}</button>
<button type="submit" name="action" value="delete" class="danger">{{ _('Delete selected') }}</button>
</p>
</form>

<script src="/static/js/jquery.js"></script>
<script src="/static/js/downloads.js"></script>
