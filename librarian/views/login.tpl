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
    % if form.error:
    ${form.error}
    % endif

    <input type="hidden" name="next" value="${next_path}">

    <p>
        ## Translators, used as label for a login field
        <label for="username">${_('Username:')}</label>
        ${form.username}
        % if form.username.error:
        ${form.username.error}
        % endif
    </p>
    <p>
        ## Translators, used as label for a login field
        <label for="password">${_('Password:')}</label>
        ${form.password}
        % if form.password.error:
        ${form.password.error}
        % endif
    </p>
    <p>
        <button type="submit"><span class="icon"></span> ${_('Login')}</button>
    </p>
</form>
