<%inherit file="_error_page.tpl"/>

<%block name="title">
## Translators, used as page title
${_('Error')}
</%block>

<%block name="error_title">
## Translators, used as error page heading
<span class="icon icon-alert-stop"></span> ${_('Error')}
</%block>

<%block name="error_code">
    500
</%block>

<%block name="error_message">
    <p>
        ${_('Librarian has failed to fulfill your request due to unexpected error in the program.')}
        % if trace:
            ${_('Details are provided below.')}
        % else:
            ${_('Error details are not available.')}
        % endif
    </p>

    % if trace:
        <pre class="error-trace"><code>${trace}</code></pre>
    % endif

    <p class="buttons">
    <a class="button" href="${url('/')}">${_('Return to main page')}</a>
    <a class="button" href="${url('sys:applog')}">${_('Download application log')}</a>
    </p>
</%block>



