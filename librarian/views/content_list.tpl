<%inherit file='base.tpl'/>
<%namespace name='tloud' file='_tag_cloud.tpl'/>
<%namespace name='simple_pager' file='_simple_pager.tpl'/>
<%namespace name='content_list' file='_content_list.tpl'/>
<%namespace name='tag_js_templates' file='_tag_js_templates.tpl'/>

<%block name="title">
## Translators, used as page title
${page_title}
</%block>

<%block name="heading">
## Translators, used as page heading
${page_title}
</%block>

<div class="inner">
    <div id="tag-cloud-container" class="tag-cloud-container" data-url="${i18n_url('tags:list')}" data-current="${tag}" data-base-path="${base_path}">
        ${tloud.cloud(tag_cloud, tag_id, tag)}
    </div>
    <form id="pager" class="pager controls">
        <input type="hidden" name="t" value="${tag_id or ''}">
        <p>
        ## Translators, used as label for search field, appears before the text box
        ${h.vinput('q', vals, _type='text', _class='search', placeholder=_('search titles'))}<button ## NOTE: keep together
        ## Translators, used as label for search button
            class="fake-go"><span class="icon">${_('go')}</span></button>
        % if query:
        ## Translators, used as label for button that clears search results
        <a href="${i18n_path(request.path)}" class="button">${_('clear')}</a>
        % endif
        ${h.vselect('lang', SELECT_LANGS, lang)}<button ## NOTE: keep together
        ## Translators, used as label for language filter button
            class="fake-go">${_('filter')}</button>
        <span class="paging">${simple_pager.body()}</span>
        </p>
    </form>
    % if query:
    ## Translators, used as note on library page when showing search results, %(term)s represents the text typed in by user
    <p class="search-keyword">${_("Showing search results for '%(terms)s'") % {'terms': query}}</p>
    % endif
    <ul id="content-list" class="content-list" data-total="${int(pager.pages)}">
        ${content_list.body()}
    </ul>
    % if not metadata:
        <p class="empty">
        % if not query and not tag and not lang['lang']:
        ## Translators, used as note on library page when library is empty
        ${_('Content library is currently empty')}
        % elif query:
        ## Translators, used as note on library page when search does not return anything
        ${_("There are no search results for '%(terms)s'") % {'terms': query}}
        % elif tag:
        ## Translators, used as not on library page when there is no content for given tag
        ${_("There are no results for '%(tag)s'") % {'tag': tag}}
        % elif lang['lang']:
        ## Translators, used as not on library page when there is no content for given language
        ${_("Language filter for '%(lang)s' is active. Click %(link)s to see all updates") % {'lang': th.lang_name_safe(lang['lang']), 'link': '<a href="%(path)s">%(label)s</a>' % {'path': i18n_url(request.path) + h.set_qparam(lang='').to_qs(), 'label': _('here')}}}
        % endif
        </p>
    % endif
</div>

<%block name="extra_scripts">
<script src="${url('sys:static', path='js/content.js')}"></script>
</%block>

<%block name="script_templates">
<script id="loadLink" type="text/template">
    <p id="more" class="loading">
        ## Translators, link that loads more content in infinite scrolling page
        <span><button class="large special">${_('Load more content')}</button></span>
    </p>
</script>

<script id="loading" type="text/template">
    <p id="loading" class="loading">
        <img src="/static/img/loading.gif">
        ## Translators, used as placeholder while infinite scrolling content is being loaded
        <span>${_('Loading...')}</span>
    </p>
</script>

<script id="end" type="text/template">
    <p class="end">
    ## Translators, shown when user reaches the end of the library
    ${_('You have reached the end of the library.')}
    ## Translators, link that appears at the bottom of infinite-scrolling page that takes the user back to top of the page
    <a href="#content-list" class="to-top">${_('Go to top')}</a>
    </p>
</script>

<script id="toTop" type="text/template">
    <div id="to-top" class="to-top">
        ## Translators, link that appears at the bottom of infinite-scrolling page that takes the user back to top of the page
        <a href="#content-list">${_('Go to top')}</a>
    </div>
</script>

${tag_js_templates.body()}
</%block>
