<%inherit file="/narrow_base.tpl"/>
<%namespace name='password_reset_form' file='_password_reset.tpl'/>

<%block name="title">
## Translators, used as page title
${_('Reset your password')}
</%block>

<div class="h-bar">
    ## Translators, used as page title
    <h2>${_('Reset your password')}</h2>
</div>

<div class="full-page-form">
    ${password_reset_form.body()}
</div>
