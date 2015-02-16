%# Translators, used as page title
% rebase('base.tpl', title=_('Library'))
<h1>
%# Translators, used as page heading
{{ _('Library') }}
</h1>

<div class="inner">
    <div id="tag-cloud-container" class="tag-cloud-container" data-url="{{ i18n_path('/tags/') }}" data-current="{{ tag }}">
        % include('_tag_cloud')
    </div>
    <form id="pager" class="pager controls">
        <input type="hidden" name="t" value="{{ tag_id or '' }}">
        <p>
        %# Translators, used as label for search field, appears before the text box
        {{! h.vinput('q', vals, _type='text', _class='search', placeholder=_('search titles')) }}<button %# NOTE: keep together
        %# Translators, used as label for search button
            class="fake-go"><span class="icon">{{ _('go') }}</span></button>
        % if query:
        %# Translators, used as label for button that clears search results
        <a href="{{ i18n_path(request.path) }}" class="button small">{{ _('clear') }}</a>
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
    % if query:
    %# Translators, used as note on library page when showing search results, %(term)s represents the text typed in by user
    <p class="search-keyword">{{ u(_("Showing search results for '%(terms)s'")) % {'terms': query} }}</p>
    % end
    <ul id="content-list" class="content-list" data-total="{{ int(total_pages) }}">
        % include('_content_list')
    </ul>
    <p class="controls">
    % include('_simple_pager')
    </p>
    % if not metadata:
        <p class="empty">
        % if not query and not tag:
        %# Translators, used as note on library page when library is empty
        {{ _('Content library is currently empty') }}
        % elif query:
        %# Translators, used as note on library page when search does not return anything
        {{ u(_("There are no search results for '%(terms)s'")) % {'terms': query} }}
        % elif tag:
        %# Translators, used as not on library page when there is no content for given tag
        {{ u(_("There are no results for '%(tag)s'")) % {'tag': tag} }}
        % end
        </p>
    % end
</div>

<script id="loadLink" type="text/template">
    <p id="more" class="loading">
        %# Translators, link that loads more content in infinite scrolling page
        <span><button class="large special">{{ _('Load more content') }}</button></span>
    </p>
</script>

<script id="loading" type="text/template">
    <p id="loading" class="loading">
        <img src="/static/img/loading.gif">
        %# Translators, used as placeholder while infinite scrolling content is being loaded
        <span>{{ _('Loading...') }}</span>
    </p>
</script>

<script id="end" type="text/template">
    <p class="end">
    %# Translators, shown when user reaches the end of the library
    {{ _('You have reached the end of the library.') }}
    %# Translators, link that appears at the bottom of infinite-scrolling page that takes the user back to top of the page
    <a href="#content-list" class="to-top">{{ _('Go to top') }}</a>
    </p>
</script>

<script id="toTop" type="text/template">
    <div id="to-top" class="to-top">
        %# Translators, link that appears at the bottom of infinite-scrolling page that takes the user back to top of the page
        <a href="#content-list">{{ _('Go to top') }}</a>
    </div>
</script>

% include('_tag_js_templates')

<script src="/static/js/content.js"></script>
