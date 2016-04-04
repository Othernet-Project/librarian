<%inherit file="/narrow_base.tpl"/>
<%namespace name='login_form' file='_login.tpl'/>

<%block name="title">
## Translators, used as page title
${_('Login')}
</%block>

<div class="h-bar">
    ## Translators, used as page title
    <h2>${_('Log into Librarian')}</h2>
</div>

<div class="full-page-form">
    ${login_form.body()}
</div>
