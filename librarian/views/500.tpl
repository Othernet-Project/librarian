<%inherit file="_error_page.tpl"/>

<%block name="title">
## Translators, used as page title
${_('Error')}
</%block>

<%block name="error_title">
## Translators, used as error page heading
500: ${_('Error')}
</%block>

<%block name="error_message">
<p class="single">${_('Librarian has failed to fulfill your request due to unexpected error in the program. Details are provided below.')}</p>

<pre class="trace"><code>${trace}</code></pre>

<p class="single">
<a class="button primary" href="${url('sys:librarian_log')}">${_('Download application log')}</a>
</p>
</%block>



