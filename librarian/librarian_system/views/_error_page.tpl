<%inherit file="_noframe.tpl"/>

## Translators, used as error page heading
<%block name="inner">
<div class="h-bar">
    <h2>
        <%block name="error_title"/>
    <h2>
</div>

<div class="error-content">
    <%block name="error_message"/>
</div>
</%block>
