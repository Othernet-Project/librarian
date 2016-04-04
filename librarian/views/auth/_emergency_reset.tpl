<%namespace name="forms" file="/ui/forms.tpl"/>

<%namespace name="note" file="_reset_token.tpl"/>

${h.form('post', action=i18n_url('emergency:reset'))}
    ${forms.form_errors([form.error]) if form.error else ''}
    ${csrf_tag()}
    ${forms.field(form.emergency_reset, 
        ## Translators, help text displayed below emergency reset token field 
        help=_('Please contact Outernet to obtain your emergency reset token.'))}
    ${forms.field(form.username)}
    ${forms.field(form.password1)}
    ${forms.field(form.password2)}
    ${note.token_note(reset_token)}
    <p class="buttons">
        ## Translators, used as label for button that performs emergency reset
        <button type="submit" class="primary"><span class="icon"></span> ${_('Reset')}</button>
    </p>
</form>
