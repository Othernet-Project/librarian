<%namespace name="forms" file="/ui/forms.tpl"/>
<%namespace name="settings_form" file="_settings_form.tpl"/>

<div class="settings">
    ${h.form('post', action=i18n_url('settings:save'), tabindex=2, id="settings-form")}
        ${settings_form.body()}
    </form>
</div>

<script type="text/template" id="settingsSaveError">
    <% 
    # Translators, error message when settings cannot be saved
    errors = [_('Settings could not be set due to application error.')] 
    %>
    ${forms.form_errors(errors)}
</script>
<script type="text/template" id="settingsSaveOK">
    <p class="o-form-message">${_('Settings were saved.')}</p>
</script>
