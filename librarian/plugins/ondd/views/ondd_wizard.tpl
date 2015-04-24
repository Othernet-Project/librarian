<%inherit file='/setup/main.tpl'/>
<%namespace name="settings_fields" file="ondd/_settings_fields.tpl"/>
<%namespace name="signal" file="ondd/_signal.tpl"/>

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
<script type="text/template" id="satPresets">
    <p class="transponder-selection">
    ## Translators, label for select list that allows user to pick a satellite to tune into
    <label for="transponders">${_('Satellite:')}</label>
    <select name="preset" id="transponders" class="transponders">
        ## Translators, placeholder for satellite selection select list
        <option value="0">${_('Select a satellite')}</option>
        % for pname, index, preset in PRESETS:
        <option value="${index}"
            data-frequency="${preset['frequency']}"
            data-symbolrate="${preset['symbolrate']}"
            data-polarization="${preset['polarization']}"
            data-delivery="${preset['delivery']}"
            data-modulation="${preset['modulation']}">${pname}</option>
        % endfor
        ## Translators, label for option that allows user to set custom transponder parameters
        <option value="-1">${_('Custom...')}</option>
    </select>
    </p>
</script>
</%block>

<%block name="extra_scripts">
<script type="text/javascript" src="${url('plugins:ondd:static', path='ondd.js')}"></script>
</%block>
