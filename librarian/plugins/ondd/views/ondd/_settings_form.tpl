<%namespace name="settings_fields" file="_settings_fields.tpl"/>
${h.form('post', action=i18n_url('plugins:ondd:settings'), _class='settings-form', _id='settings-form')}
    ${h.form_errors(errors)}
    <input type="hidden" name="backto" value="${request.original_path}">
    ${settings_fields.body()}
    <p class="buttons-left">
    ## Translators, button label that confirms tuner settings
    <button type="submit">${_('Tune in')}</button>
    </p>
    % if message:
    <p>${ message }</p>
    % endif
</form>
