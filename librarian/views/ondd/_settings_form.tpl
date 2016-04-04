<%namespace name="settings_fields" file="_settings_fields.tpl"/>

<input type="hidden" name="backto" value="${request.original_path}">
${settings_fields.body()}
<p class="buttons">
## Translators, button label that confirms tuner settings
<button type="submit" class="primary">${_('Update settings')}</button>
</p>
