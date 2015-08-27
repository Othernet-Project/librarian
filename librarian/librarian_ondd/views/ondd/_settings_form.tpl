<%namespace name="settings_fields" file="_settings_fields.tpl"/>
${h.form('post', action=i18n_url('plugins:ondd:settings'), _class='settings-form', _id='settings-form')}
    % if message:
    <p class="message">${ message }</p>
    % endif
    % if form.error:
    ${form.error}
    % endif
    <input type="hidden" name="backto" value="${request.original_path}">
    ${settings_fields.body()}
    <p class="buttons-left">
    ## Translators, button label that confirms tuner settings
    <button type="submit" class="primary">${_('Tune in')}</button>
    </p>
</form>
