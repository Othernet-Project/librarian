<%inherit file='main.tpl'/>

<%block name="step">
<h3>${_('Please enter the desired credentials for the superuser account.')}</h3>
<div class="step-superuser-form">
    <p>
        ## Translators, used as label for a username field
        <label for="username">${_('Username:')}</label>
        ## Translators, used as placeholder in the username field
        ${h.vinput('username', {}, _type='text', placeholder=_('username'))}
        ${h.field_error('username', errors)}
    </p>
    <p>
        ## Translators, used as label for a password field
        <label for="password">${_('Password:')}</label>
        ## Translators, used as placeholder in the password field
        ${h.vinput('password1', {}, _type='password', placeholder=_('password'))}
        ${h.field_error('password1', errors)}
    </p>
    <p>
        ## Translators, used as label for a password field
        <label for="password">${_('Confirm Password:')}</label>
        ## Translators, used as placeholder in the password field
        ${h.vinput('password2', {}, _type='password', placeholder=_('confirm password'))}
        ${h.field_error('password2', errors)}
    </p>
    ${h.form_errors(errors)}
</div>
</%block>
