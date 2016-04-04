<%inherit file="_error_page.tpl"/>

<%block name="title">
## Translators, used as page title
${_('Under maintenance')}
</%block>

<%block name="error_title">
## Translators, used as maintenance page heading
<span class="icon icon-alert-key"></span> ${_('Under maintenance')}
</%block>

<%block name="error_code">
503
</%block>

<%block name="error_message">
<p class="single">
${_('Librarian is currently in maintenance mode. Please wait a few minutes and try again.')}
</p>
</%block>
