<%inherit file="_dashboard_section.tpl"/>

<p>
${_('Database size')}: ${h.hsize(dbsize)}
</p>

<div class="inline-form-wrapper">
    <a class="button primary" href="${url('dbmanage:download')}">${_('Download')}</a>

    <form action="${i18n_url('dbmanage:backup')}" method="POST">
        ## Translators, refers to database backup
        <button>${_('Backup')}</button>
    </form>

    <form action="${i18n_url('dbmanage:rebuild')}" method="POST">
        ## Translators, refers to database rebuild feature
        <button class="delete">${_('Rebuild')}</button>
    </form>
</div>

<p class="warning">
    ## Translators, note about database rebuild shown on dashboard
    ${_("Database rebuild will cause all tags to be lost. It will also put Librarian into maintenance mode and prevent users from accessing content.")}
</p>
