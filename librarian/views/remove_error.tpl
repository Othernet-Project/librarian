<%inherit file="base.tpl"/>

<%block name="title">
## Translators, used as page title
${_('Content file missing')}
</%block>

<%block name="heading">
## Translators, used as page heading
${_('Content file missing')}
</%block>

## Translators, message displayed when content file is missing, but database record was successfully removed
<p>${_('The content file was not found, but has been removed from the database. You will be redirected to the content list shortly.')}</p>

