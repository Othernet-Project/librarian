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
        <span class="paging">
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
    <ul id="content-list" class="content-list">
        % include('_content_list')
    </ul>
    <p class="controls">
    % include('_simple_pager')
    </p>
    % end 
</div>

<script id="loading" type="text/template">
    %# Translators, used as placeholder while infinite scrolling content is being loaded
    <p class="loading">{{ _('Loading...') }}</p>
</script>

<script id="end" type="text/template">
    %# Translators, shown when user reaches the end of the library
    <p class="end">{{ _('You have reached the end of the library') }}</p>
</script>

<script src="/static/js/content.js"></script>
