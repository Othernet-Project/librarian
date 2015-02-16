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
        % for pname, index, preset in PRESETS:
            % include('ondd/_preset')
        % end
        %# Translators, label for option that allows user to set custom transponder parameters
        <option value="-1">{{ _('Custom...') }}</option>
    </select>
    </p>
</script>

