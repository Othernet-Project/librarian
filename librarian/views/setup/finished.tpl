<%inherit file='/base.tpl'/>

<%block name="title">
## Translators, used as page title
${_('Setup Finished')}
</%block>

<%block name="heading">
## Translators, used as page heading
${_('Setup Finished')}
</%block>

<div class="setup-finished">
    <p>Libriran has been set up successfully.</p>
    <a class="button" href="${i18n_url('content:list', locale=setup['language'])}">Start Librarian</a>
</div>
