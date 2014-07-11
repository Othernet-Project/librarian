% rebase('base.tpl', title=_('Favorites'))
<h1>{{ _('Favorites') }}</h1>

% if not metadata:
<p>{{ _('You have not favorted any content yet') }}</p>
% else:
<table class="content-list">
    <tr class="header">
    <th></th>
    <th>{{ _('date') }}</th>
    <th>{{ _('title') }}</th>
    </tr>
    % for meta in metadata:
    <tr>
    <td class="centered">
        <form action="{{ i18n_path('/favorites/') }}" method="POST">
            {{! h.HIDDEN('fav', '0') }}
            {{! h.HIDDEN('md5', meta['md5']) }}
            <button type="submit">{{ _('unfavorite') }}</button>
        </form>
    </td>
    <td>{{ meta['updated'].strftime('%m-%d') }}</td>
    <td><a href="{{ i18n_path('/content/%s/' % meta['md5']) }}">{{ meta['title'] }}</a></td>
    </tr>
    % end
</table>
% end 
