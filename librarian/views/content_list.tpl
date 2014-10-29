%# Translators, used as page title
% rebase('base.tpl', title=_('Library'))
<h1>
%# Translators, used as page heading
{{ _('Library') }}
% if query:
%# Translators, used as note on library page when showing search results, %(term)s represents the text typed in by user
<span>{{ str(_("Showing search results for '%(terms)s'")) % {'terms': query} }}</span>
% elif metadata:
%# Translators, used as note on library page when showing content list, %(count)s is number of items on the page, %(total)s is total number of items in library
<span>{{ str(ngettext('Showing %(count)s of %(total)s items', 'Showing %(count)s of %(total)s items', total_items)) % {'count': len(metadata), 'total': total_items} }}</span>
% end
</h1>

<div class="inner">
    % if not metadata:
        % if not query:
        %# Translators, used as note on library page when library is empty
        <p>{{ _('Content library is currently empty') }}</p>
        % else:
        %# Translators, used as note on library page when search does not return anything
        <p>{{ str(_("There are no search results for '%(terms)s'")) % {'terms': query} }}</p>
        % end
    % else:
    <form id="pager" class="pager controls">
        <p>
        %# Translators, used as label for search field, appears before the text box
        <label class="search" for="q">{{ _('search titles') }}:
        {{! h.vinput('q', vals) }}
        %# Translators, used as label for search button
        <button class="fake-go small">{{ _('go') }}</button>
        % if query:
        %# Translators, used as label for button that clears search results
        <a href="{{ i18n_path(request.path) }}" class="button">{{ _('clear') }}</a>
        % end
        </label>
        <span class="search">
            % if total_pages > 1:
                %# Translators, used as label for select list in pager for selecting the library page, appears before the select list (in "page N" format)
                <label for="page">{{ _('page') }}</label>
                <select id="page" name="p">
                % for i in range(1, int(total_pages) + 1):
                <option value="{{ i }}"{{ i == page and ' selected' or '' }}>{{ i }}</option>
                % end
                </select>
                /
            % end
            <select id="perpage" name="c">
            % for i in range(1, 5):
            <option value="{{ i }}"{{ i == f_per_page and ' selected' or '' }}>{{ i * 20 }}</option>
            % end
            </select>
            %# Translators, used as label for select list for selecting number of items to show per page, appears after the select list (in "N per page" format)
            <label for="perpage">{{ _('per page') }}</label>
            %# Translators, used as label for pager button that selects the page to which user wants to go, normally hidden when JavaScript is active
            <button id="go-button" type="submit" class="special">{{ _('go') }}</button>
            % include('_simple_pager')
        </span>
        </p>
    </form>
    <table class="content-list">
        <thead>
            <tr class="header">
                <th></th>
                %# Translators, used in table header, page title
                <th>{{ _('title') }}</th>
                %# Translators, used in table header, date added
                <th>{{ _('added') }}</th>
            </tr>
        </thead>
        <tbody>
            % for meta in metadata:
            <tr class="data">
                <td class="center" rowspan="2">
                    % if meta['favorite']:
                    <img src="/static/img/fav.png" alt="favorite">
                    % else:
                    <form action="{{ i18n_path('/favorites/') }}" method="POST">
                    {{! h.HIDDEN('md5', meta['md5']) }}
                    %# Translators, used as button label for adding content to favorites
                    <button type="submit">{{ _('favorite') }}</button>
                    </form>
                    % end
                </td>
                <td><a href="{{ i18n_path('/pages/%s/' % meta['md5']) }}">{{ meta['title'] }}</a></td>
                <td rowspan="2">{{ meta['updated'].strftime('%m-%d') }}</td>
            </tr>
            <tr class="badges">
                <td>
                % include('_badges')
                </td>
            </tr>
            % end
        </tbody>
    </table>
    <p class="controls">
    % include('_simple_pager')
    </p>
    % end 
</div>

<script src="/static/js/jquery.js"></script>
<script src="/static/js/content.js"></script>
