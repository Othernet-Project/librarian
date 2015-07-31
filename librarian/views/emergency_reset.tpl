<%inherit file='base.tpl'/>

## Translators, used as page title
<%block name="title">${_('Emergency reset')}</%block>

<div class="h-bar">
    ## Translators, used as page heading
    <h2>${_('Perform emergency reset')}</h2>
</div>

<div class="full-page-form">
    ${h.form('post')}
        % if form.error:
        ${form.error}
        % endif

        ${th.csrf_tag()}

        <p>
            ${form.emergency_reset.label}
            ${form.emergency_reset}
            % if form.emergency_reset.error:
            ${form.emergency_reset.error}
            % endif
            <span class="field-help">
            ## Translators, help text displayed below emergency reset token field
            ${_('Please contact Outernet to obtain your emergency reset token.')}
            </span>
        </p>
        <p>
            ${form.username.label}
            ${form.username}
            % if form.username.error:
            ${form.username.error}
            % endif
        </p>
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
        <p class="note">
            <span class="label">${_('Password reset token')}</span>
            <span class="large">${reset_token}</span>
            <span class="field-help">
            ${_('Please write down this password reset token and store it securely. You will need it if you ever need to reset your passwrd.')}
            </span>
            ${h.HIDDEN('reset_token', reset_token)}
        </p>
        <p class="buttons">
            ## Translators, used as label for button that performs emergency reset
            <button class="confirm primary">${_('Reset')}</button>
        </p>
    </form>
</div>


