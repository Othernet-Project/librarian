<%inherit file='/setup_base.tpl'/>
<%namespace name="settings_fields" file="ondd/_settings_fields.tpl"/>
<%namespace name="signal" file="ondd/_signal.tpl"/>
<%namespace name="presets" file="ondd/_presets.tpl"/>

<%block name="extra_head">
<link rel="stylesheet" href="${assets['css/dashboard']}" />
</%block>

<%block name="step_title">
<h2>${_("Please select the satellite you'd like to receive data from.")}</h2>
</%block>

<%block name="step">
<div class="step-ondd-form">
    <div id="settings-form">
        % if form.error:
        ${form.error}
        % endif
        ${settings_fields.body()}
    </div>

    <div id="signal-status" class="signal-status ondd-status" data-url="${i18n_url('ondd:status')}">
        ${signal.body()}
    </div>

</div>
${presets.body()}
<script type="text/template" id="jsFieldError">
    <span class="field-error js-error"></span>
</script>
<script type="application/json" id="validation-messages">
    {
        "preset": "${_('Please select a satellite.')}"
    }
</script>
</%block>

<%block name="extra_scripts">
<script type="text/javascript" src="${assets['js/ondd']}"></script>
</%block>
