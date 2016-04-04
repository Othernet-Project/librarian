<%inherit file="/narrow_base.tpl"/>

<%block name="title">
## Translators, used as page title of content removal confirmation page
${_("Confirm removal")}
</%block>

<div class="full-page-form confirm remove">
    <h2>
        <span class="icon icon-alert-question"></span>
        ## Translators, used title at top of the removal confirmation page,
        ## asking user to confirm file/folder deletion.
        <span>${_("Delete permanently?")}</span>
    </h2>
    ${h.form('post')}
        <p class="main">
            ## Translators, used as confirmation message before content removal
            ${_("You are about to delete '{item_name}'.").format(item_name=h.html_escape(item_name))}
            <strong>
                ## Translators, message warning users about deleted files and
                ## folders.
                ${_("Deleted files and folders cannot be recovered.")}
            </strong>
        </p>
        ${csrf_tag()}
        <p class="buttons">
            ## Translators, used as title of content removal confirmation button
            <button name="action" value="delete" type="submit" class="primary delete">${_('Delete')}</button>
            ## Translators, used as title of content removal cancellation button
            <a class="button" href="${cancel_url}">${_('Cancel')}</a>
        </p>
    </form>
</div>
