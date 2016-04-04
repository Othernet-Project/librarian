<%inherit file="/narrow_base.tpl"/>
<%namespace name="settings_form" file="_settings_form.tpl"/>

<%block name="title">
## Translators, used as page title
${_('Tuner settings')}
</%block>

<h2>
    <span class="icon icon-satellite"></span>
    ## Translators, used as page heading
    <span>${_('Tuner settings')}</span>
</h2>

<form action="${i18n_url('ondd:settings')}" method="POST" id="ondd-form">
    ${settings_form.body()}
</form>

<%block name="extra_scripts">
    <script src="${assets['js/ondd_presets']}"></script>
</%block>
