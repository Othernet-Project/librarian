<%inherit file="base.tpl"/>

<%block name="title">
## Translators, used as page title of content removal confirmation page
${_("Confirm Removal")}
</%block>

<div class="full-page-form confirm remove">
    <span class="icon"></span>
    ${h.form('post')}
        ## Translators, used as confirmation message before content removal
        <p class="main">${_("Are you sure you want to remove the content entry named {title}").format(title=content['title'])}</p>
        ${th.csrf_tag()}
        <p class="buttons">
            ## Translators, used as title of content removal confirmation button
            <button type="submit" class="primary">${_('Remove')}</button>
            ## Translators, used as title of content removal cancellation button
            <a class="button" href="${cancel_url}">${_('Cancel')}</a>
        </p>
    </form>
</div>
