<p class="list-controls" id="controls">
    ## Translators, used as button label on updates page for marking all content for import
    <a class="sel-all button small" href="${i18n_path(request.path) + h.set_qparam(sel=1).to_qs()}">${_('Select all')}</a>
    ## Translators, used as button label on updates page for unmarking all content for import
    <a class="sel-none button small" href="${i18n_path(request.path) + h.set_qparam(sel=0).to_qs()}">${_('Select none')}</a>
    ## Translators, used as button label on updates page for adding marked content to library
    <button type="submit" name="action" value="add" class="special small">${_('Add selected to library')}</button>
    ## Translators, used as button label on updates page for permanently deleting all downloaded content
    <button type="submit" name="action" value="delete" class="danger small">${_('Delete selected')}</button>
    ## Translators, used as button label on updates page for permanently deleting all downloaded content
    <button type="submit" name="action" value="deleteall" class="danger small">${_('Delete all')}</button>
</p>
