<%inherit file="/narrow_base.tpl"/>
<%namespace name='reset_password_form' file='_reset_password.tpl'/>

<%block name="title">
## Translators, used as page title
${_('Reset your password')}
</%block>

<div class="h-bar">
    ## Translators, used as page title
    <h2>${_('Reset your password')}</h2>
</div>

<div class="full-page-form">
    ${reset_password_form.body()}
</div>
