<%namespace name="tag_list" file="_tag_list.tpl"/>

<%def name="tags(meta)">
<p class="tags" data-has-tags="${bool(meta.tags)}">
${tag_list.list(meta=meta)}
</p>
<form action="${i18n_url('tags:edit', content_id=meta.md5) + h.set_qparam(base_path=base_path).to_qs()}" method="POST" class="tag-form inline">
    <input type="text" name="tags" value="${', '.join(meta.tags)}">
    ## Translators, button label for a button that saves user tags for a piece of content
    <button class="small primary">${_('Save')}</button>
</form>
<p class="field-help tags-help">
## Translators, note below the tag form (please note that it has to be the comma characters such as the one used in English language regardless of the interface language selected by user, so emphasize this where appropriate)
${_('Separate tags with commas')}<br>
</p>
</%def>

${tags(meta)}
