<%inherit file="base.tpl">

<%block>
## Translators, used as page title
${_('Forbidden')}
</%block>

<%block>
## Translators, used as access denied page heading
403: ${_('Forbidden')}
</%block>

<p>
## Translators, shown when user is denied access to a page
${_('You are not authorized to access this page.')}
</p>
