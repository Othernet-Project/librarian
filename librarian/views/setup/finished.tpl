<%inherit file='/base.tpl'/>

<%block name="title">
## Translators, used as page title
${_('Setup Completed')}
</%block>

<%block name="heading">
## Translators, used as page heading
${_('Setup Completed')}
</%block>

<div class="setup-finished">
    <p>${_('Libriran has been set up successfully.')}</p>
    <a class="button" href="${i18n_url('content:list', locale=setup['language'])}">${_('Start using Librarian')}</a>
</div>
