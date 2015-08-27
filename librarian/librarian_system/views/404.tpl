<%inherit file="_error_page.tpl"/>

<%block name="title">
## Translators, used as page title
${_('Page not found')}
</%block>

<%block name="error_title">
## Translators, used as error page heading
404: ${_('Page not found')}
</%block>

<%block name="error_message">
<p class="single">${_('The page you were looking for could not be found')}</p>
</%block>
