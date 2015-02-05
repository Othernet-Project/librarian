% rebase('_dashboard_section')

<style>@import "/s/ondd/ondd.css";</style>

<p id="signal-status" class="signal-status" data-url="{{ i18n_path('/p/ondd/status') }}">
    % include('ondd/_signal')
</p>

% include('ondd/_settings_form')

<script type="text/template" id="satPresets">
    <p class="transponder-selection">
    %# Translators, label for select list that allows user to pick a satellite to tune into
    <label for="transponders">{{ _('Satellite:') }}</label>
    <select name="preset" id="transponders" class="transponders">
        %# Translators, placeholder for satellite selection select list
        <option value="0">{{ _('Select a satellite') }}</option>
        <option value="1"
            data-frequency="12177000"
            data-symbolrate="23000000"
            data-polarization="v"
            data-delivery="1"
            data-modulation="qp">Galaxy 19 (97.0&deg;W)</option>
        <option value="2"
            data-frequency="11470000"
            data-symbolrate="27500000"
            data-polarization="v"
            data-delivery="1"
            data-modulation="qp">Hotbird 13 (13.0&deg;E)</option>
        <option value="3"
            data-frequency="12522000"
            data-symbolrate="27500000"
            data-polarization="v"
            data-delivery="1"
            data-modulation="qp">Intelsat 20 (68.5&deg;E)</option>
        %# Translators, label for option that allows user to set custom transponder parameters
        <option value="-1">{{ _('Custom...') }}</option>
    </select>
    </p>
</script>

