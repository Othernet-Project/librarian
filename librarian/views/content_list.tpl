% rebase('base.tpl', title=_('Archive'))
<h1>{{ _('Archive') }}</h1>

% if not metadata:
<p>Content archive is currently empty</p>
% else:
<table class="content-list">
    <tr class="header">
    <th>{{ _('date') }}</th>
    <th>{{ _('title') }}</th>
    </tr>
    % for meta in metadata:
    <tr>
    <td>{{ meta['updated'].strftime('%m-%d') }}</td>
    <td><a href="{{ i18n_path('/content/%s/' % meta['md5']) }}">{{ meta['title'] }}</a></td>
    </tr>
    % end
</table>
% end 
