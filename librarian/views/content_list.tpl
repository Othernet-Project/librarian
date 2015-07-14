<%inherit file='base.tpl'/>
<%namespace name='simple_pager' file='_simple_pager.tpl'/>
<%namespace name='content_list' file='_content_list.tpl'/>
<%namespace name='library_submenu' file='_library_submenu.tpl'/>
<%namespace name='tag_js_templates' file='_tag_js_templates.tpl'/>

<%block name="title">
${page_title}
</%block>

${library_submenu.body()}

<div class="h-bar">
    <form id="search" class="search">
        ${h.vinput('t', vals, _type='hidden')}
        ${h.vinput('lang', vals, _type='hidden')}
        ${h.vinput('p', vals, _type='hidden')}
        ${h.vinput('pp', vals, _type='hidden')}
        ## Translators, used as label for search field, appears before the text box
        <label for="q"><span class="icon search">${_('Search')}</label>
        ${h.vinput('q', vals, _class='search', _type='text', placeholder=_('Search titles'))}
        <button class="primary">${_('Search')}</button>
    </form>
    % if query:
    ## Translators, used as note on library page when showing search results, %(term)s represents the text typed in by user
    <p class="search-keyword">
    ${_("Showing search results for '%(terms)s'") % {'terms': query}}
    ## Translators, used as label for button that clears search results
    <a href="${i18n_path(request.path)}" class="button small secondary">${_('Clear')}</a>
    </p>
    % endif
</div>

<div class="filters">
    <div class="form langs">
        % if len(th.content_languages()) > 1:
        <form id="lang" class="downloads-langs">
            <input type="hidden" name="q" value="${query or ''}">
            <input type="hidden" name="t" value="${tag_id or ''}">
            ${h.vselect('lang', th.content_languages(), lang)}
            ## Translators, used as label for language filter button
            <button class="fake-go">${_('Filter')}</button>
            </p>
        </form>
        % endif
    </div>
    <div class="forms pager">
        ${simple_pager.prev_next_pager()}
    </div>
</div>

<ul id="content-list" class="content-list" data-total="${int(pager.pages)}">
    ${content_list.body()}
</ul>

% if not metadata:
    <p class="empty">
    % if not query and not tag and not lang['lang']:
    ## Translators, used as note on library page when library is empty
    ${empty_message}
    % elif query:
    ## Translators, used as note on library page when search does not return anything
    ${_("There are no search results for '%(terms)s'") % {'terms': query}}
    % elif tag:
    ## Translators, used as not on library page when there is no content for given tag
    ${_("There are no results for '%(tag)s'") % {'tag': tag}}
    % elif lang['lang']:
    ## Translators, used as not on library page when there is no content for given language
    ${_("Language filter for '%(lang)s' is active. Click %(link)s to see all content") % {'lang': th.lang_name_safe(lang['lang']), 'link': '<a href="%(path)s">%(label)s</a>' % {'path': i18n_url(request.path) + h.set_qparam(lang='').to_qs(), 'label': _('here')}}}
    % endif
    </p>
% endif

<%block name="extra_scripts">
<script src="${assets['js/content']}"></script>
</%block>

<%block name="script_templates">
<script id="loadLink" type="text/template">
    <p id="more" class="load-more">
        <button
            class="primary"
            ## Translators, link that loads more content in infinite scrolling page
            data-active="${_('Load more content')}"
            ## Translators, label on link that loads more content, while content is being loaded
            data-normal="${_('Loading...')}">
                <span class="icon"></span>
                ${_('Load more content')}
        </button>
    </p>
</script>

<script id="end" type="text/template">
    <p class="end">
    ## Translators, shown when user reaches the end of the library
    ${_('You have reached the end of the library.')}
    ## Translators, link that appears at the bottom of infinite-scrolling page that takes the user back to top of the page
    <a href="#content-list">${_('Go to top')}</a>
    </p>
</script>

<script id="toTop" type="text/template">
    <div id="to-top" class="to-top">
        ## Translators, link that appears at the bottom of infinite-scrolling page that takes the user back to top of the page
        <a href="#content-list" class="button small">${_('Go to top')}</a>
    </div>
</script>

${tag_js_templates.body()}
</%block>
