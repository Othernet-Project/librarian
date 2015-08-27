<%inherit file="_error_page.tpl"/>

<%block name="title">
## Translators, used as page title
${_('Under maintenance')}
</%block>

<%block name="error_title">
## Translators, used as maintenance page heading
503: ${_('Under maintenance')}
</%block>

<%block name="error_message">
<p class="single">
${_('Librarian is currently in maintenance mode. Please wait a few minutes and try again.')}
</p>
</%block>
