<%namespace name="forms" file="/ui/forms.tpl"/>

${h.form('post', action=i18n_url('auth:reset'))}
    ${forms.form_errors([form.error]) if form.error else ''}

    ${csrf_tag()}

    <input type="hidden" name="next" value="${next_path}">

    % if not request.user.is_authenticated:
    <p>
        ${forms.field(form.reset_token)}
        <span class="field-help">
        ${_('This is the 6-digit number you were asked to write down when you created your user account.')}
        </span>
    </p>
    % endif

    <p>
        ${forms.field(form.password1)}
    </p>
    <p>
        ${forms.field(form.password2)}
    </p>

    <p class="buttons">
        <button type="submit" class="primary confirm"><span class="icon"></span> ${_('Change password')}</button>
    </p>
</form>
