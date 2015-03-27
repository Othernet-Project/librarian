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
    <p>
        ## Translators, used as placeholder in the login field
        <input type="text" name="username" placeholder="${_('username')}" value="${username}" />
    </p>
    <p>
        ## Translators, used as placeholder in the password field
        <input type="password" placeholder="${_('password')}" name="password" />
    </p>
    % if error:
    <p class="error">${error}</p>
    % endif
    <p>
        <input type="hidden" name="next" value="${next}" />
        <button type="submit"><span class="icon">${_('Login')}</span></button>
    </p>
</form>
