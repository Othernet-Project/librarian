<%def name="token_note(token)">
    <p class="token-note">
        <span class="label">${_('Password reset token')}</span>
        <span class="large">${reset_token}</span>
        <span>
            ## Translators, shown as a message under the password reset token.
            ## Password reset token is a 6-digit number that is used to reset
            ## the user password.
            ${_('Please write this password reset token down and store it securely. You will need it if you ever need to reset your password.')}
        </span>
        ${h.HIDDEN('reset_token', token)}
    </p>
</%def>
