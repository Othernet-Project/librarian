<%inherit file="base.tpl"/>

<%block name="title">
## Translators, used as page title
${_('Login')}
</%block>

<%block name="heading">
## Translators, used as page heading
${_('Login')}
</%block>

${h.form('post')}
    % if errors:
    ${h.form_errors(errors)}
    % endif

    <input type="hidden" name="next" value="${next_path}">

    <p>
        ## Translators, used as label for a login field
        <label for="username">${_('Username:')}</label>
        ## Translators, used as placeholder in the login field
        ${h.vinput('username', vals, _type='text', placeholder=_('username'))}
        ${h.field_error('username', errors)}
    </p>
    <p>
        ## Translators, used as label for a login field
        <label for="password">${_('Password:')}</label>
        ## Translators, used as placeholder in the password field
        ${h.vinput('password', vals, _type='password', placeholder=_('password'))}
        ${h.field_error('password', errors)}
    </p>
    <p>
        <button type="submit"><span class="icon"></span> ${_('Login')}</button>
    </p>
</form>
