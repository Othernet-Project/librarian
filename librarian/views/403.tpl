<%inherit file="_error_page.tpl"/>

<%block name="title">
## Translators, used as page title
${_('Forbidden')}
</%block>

<%block name="error_title">
## Translators, used as access denied page heading
403: ${_('Forbidden')}
</%block>

<%block name="error_message">
<p class="single">
## Translators, shown when user is denied access to a page
${_('You are not authorized to access this page or the page has expired.')}
</p>
</%block>
