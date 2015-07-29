<%inherit file="base.tpl"/>

<%block name="title">
## Translators, used as page title
${_('Reset your password')}
</%block>

<div class="h-bar">
    ## Translators, used as page title
    <h2>${_('Reset your password')}</h2>
</div>

<div class="full-page-form">
    ${h.form('post')}
        % if form.error:
        ${form.error}
        % endif

        ${th.csrf_tag()}

        <input type="hidden" name="next" value="${next_path}">

        % if not request.user.is_authenticated:
        <p>
            ${form.reset_token.label}
            ${form.reset_token}
            <span class="field-help">
            ${_('This is the 6-digit number you were asked to write down when you created your user account.')}
            </span>
            % if form.reset_token.error:
            ${form.reset_token.error}
            % endif
        </p>
        % endif

        <p>
            ${form.password1.label}
            ${form.password1}
            % if form.password1.error:
            ${form.password1.error}
            % endif
        </p>
        <p>
            ${form.password2.label}
            ${form.password2}
            % if form.password2.error:
            ${form.password2.error}
            % endif
        </p>

        <p class="buttons">
            <button type="submit" class="primary confirm"><span class="icon"></span> ${_('Change password')}</button>
        </p>
    </form>
</div>
