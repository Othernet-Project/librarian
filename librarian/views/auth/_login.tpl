<%namespace name="forms" file="/ui/forms.tpl"/>

${h.form('post', action=i18n_url('auth:login'), tabindex=1)}
    ${forms.form_errors([form.error]) if form.error else ''}

    ${csrf_tag()}
    <input type="hidden" name="next" value="${next_path}">
    ${forms.field(form.username)}
    ${forms.field(form.password)}
    <p class="buttons">
        <button type="submit" class="primary"><span class="icon"></span> ${_('Login')}</button>
    </p>
    <p class="buttons">
    <a href="${i18n_url('auth:reset_form')}?${h.set_qparam(next=next_path)}">${_('Reset your password')}</a>
    </p>
</form>
