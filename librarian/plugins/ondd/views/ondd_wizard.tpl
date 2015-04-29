<%inherit file='/setup/main.tpl'/>
<%namespace name="settings_fields" file="ondd/_settings_fields.tpl"/>
<%namespace name="signal" file="ondd/_signal.tpl"/>
<%namespace name="presets" file="ondd/_presets.tpl"/>

<%block name="step">
<h3>${_("Please select the satellite you'd like to receive data from.")}</h3>
<div class="step-ondd-form">
    <style>@import "${url('plugins:ondd:static', path='ondd.css')}";</style>

    <p id="signal-status" class="signal-status" data-url="${i18n_url('plugins:ondd:status')}">
        ${signal.body()}
    </p>

    <div id="settings-form">
        ${h.form_errors(errors)}
        ${settings_fields.body()}
    </div>
</div>
${presets.body()}
</%block>

<%block name="extra_scripts">
<script type="text/javascript" src="${url('plugins:ondd:static', path='ondd.js')}"></script>
</%block>
