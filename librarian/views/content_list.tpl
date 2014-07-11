% rebase('base.tpl', title=_('Archive'))
<h1>{{ _('Archive') }}</h1>

% if not metadata:
<p>{{ _('Content archive is currently empty') }}</p>
% else:
<table class="content-list">
    <tr class="header">
    <th></th>
    <th>{{ _('date') }}</th>
    <th>{{ _('title') }}</th>
    </tr>
    % for meta in metadata:
    <tr>
    <td class="center">
        % if meta['favorite']:
        <img src="/static/img/fav.png" alt="favorite">
        % else:
        <form action="{{ i18n_path('/favorites/') }}" method="POST">
        {{! h.HIDDEN('md5', meta['md5']) }}
        <button type="submit">{{ _('favorite') }}</button>
        </form>
        % end
    </td>
    <td>{{ meta['updated'].strftime('%m-%d') }}</td>
    <td><a href="{{ i18n_path('/content/%s/' % meta['md5']) }}">{{ meta['title'] }}</a></td>
    </tr>
    % end
</table>
% end 
