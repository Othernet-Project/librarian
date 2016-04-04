<%inherit file="_noframe.tpl"/>

## Translators, used as error page heading
<%block name="narrow_main">
    <h2 class="error-name">
        <%block name="error_title"/>
    </h2>
    <p class="error-code">
        ## Translators, shown on error page below the error title
        ${_('Error code:')} 
        ## Translators, shown on error page as error code when error code
        ## is unknown.
        <%block name="error_code">${_('unknown')}</%block>
    </p>

    <div class="error-content">
        <%block name="error_message"/>
    </div>
</%block>
