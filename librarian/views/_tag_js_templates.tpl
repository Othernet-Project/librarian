<%block name="templates">
<script id="tagButton" type="text/template">
    ## Translators, used as label for button that appears next to tag list
    <button class="small tag-button"><span class="icon">${_('Edit tags')}</span></button>
</script>

<script id="closeTagButton" type="text/template">
    ## Translators, used as label for button that appears in tag editing form
    <button class="small tag-close-button" type="button">${_('Close')}</button>
</script>

<script id="tagsUpdateError" type="text/template">
    ## Translators, error message shown when updating tags fails
    ${_('Tags could not be updated.')}
</script>
</%block>
