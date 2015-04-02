<%inherit file="_dashboard_section.tpl"/>
<%namespace name="settings_form" file="ondd/_settings_form.tpl"/>
<%namespace name="signal" file="ondd/_signal.tpl"/>
<%namespace name="file_list" file="ondd/_file_list.tpl"/>

<style>@import "${url('plugins:ondd:static', path='ondd.css')}";</style>

<p id="signal-status" class="signal-status" data-url="${i18n_url('plugins:ondd:status')}">
    ${signal.body()}
</p>

${settings_form.body()}

% if files:
<h3>
## Translators, used as title of a subsection in dashboard that lists files that are currently being downloaded
${_('Downloads in progress')}
</h3>
<div id="ondd-file-list" data-url="${i18n_url('plugins:ondd:files')}">
    ${file_list.body()}
</div>
% endif

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

