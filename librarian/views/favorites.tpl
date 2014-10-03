%# Translators, used as page title
% rebase('base.tpl', title=_('Favorites'))
%# Translators, used as page heading
<h1>{{ _('Favorites') }}</h1>

<div class="inner">
    % if not metadata:
    %# Translators, used as note shown on favorites page when user has no favorites
    <p>{{ _('You have not favorted any content yet') }}</p>
    % else:
    <table class="content-list">
        <tr class="header">
        <th></th>
        %# Translators, used in table header, date added to library
        <th>{{ _('date') }}</th>
        %# Translators, used in table header, content title
        <th>{{ _('title') }}</th>
        </tr>
        % for meta in metadata:
        <tr>
        <td class="centered">
            <form action="{{ i18n_path('/favorites/') }}" method="POST">
                {{! h.HIDDEN('fav', '0') }}
                {{! h.HIDDEN('md5', meta['md5']) }}
                %# Translators, used as button label on favorites page, for removing content from favorites
                <button type="submit">{{ _('unfavorite') }}</button>
            </form>
        </td>
        <td>{{ meta['updated'].strftime('%m-%d') }}</td>
        <td><a href="{{ i18n_path('/pages/%s/' % meta['md5']) }}">{{ meta['title'] }}</a></td>
        </tr>
        % end
    </table>
    % end 
</div>
