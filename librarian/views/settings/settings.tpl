<%inherit file="/narrow_base.tpl"/>
<%namespace name="settings_form" file="_settings_form.tpl"/>

<%block name="title">
## Translators, used as page title
${_('Librarian settings')}
</%block>

<div class="settings">
    ${h.form('post', action=i18n_url('settings:save'), tabindex=2, id="settings-form")}
        ${settings_form.body()}
    </form>
</div>
