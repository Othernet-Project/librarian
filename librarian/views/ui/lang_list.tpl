<%inherit file="/narrow_base.tpl"/>
<%namespace name="lang_list" file="_lang_list.tpl"/>

<p class="language-list-back">
    <a href="${request.params.get(path, i18n_path('/'))}">
        <span class="icon icon-arrow-left"></span>
        ## Translators, used as link label for link that takes user back to 
        ## a page from which they came (usually used when they temporarily 
        ## visit the current page to change some option such as language)
        <span>${_('Back to previous page')}</span>
    </a>
</p>

${lang_list.body()}
