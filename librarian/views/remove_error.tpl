<%inherit file="base.tpl"/>

<%block name="title">
## Translators, used as page title
${_('Content could not be removed')}
</%block>

<%block name="heading">
## Translators, used as page heading
${_('Content could not be removed')}
</%block>

## Translators, message displayed when content cannot be deleted
<p>${_('Please make sure the storage device is not write-protected and try again.')}</p>

<form method="POST">
    ## Translators, used as label on button for retrying content removal
    <button type="submit">${_('Retry')}</button>
</form>
