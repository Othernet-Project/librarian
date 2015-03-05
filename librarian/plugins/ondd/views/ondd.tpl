% rebase('_dashboard_section')

<style>@import "{{ url('plugins:ondd:static', path='ondd.css') }}";</style>

<p id="signal-status" class="signal-status" data-url="{{ i18n_path(url('plugins:ondd:status')) }}">
    % include('ondd/_signal')
</p>

% include('ondd/_settings_form')

%# Translators, used as title of a subsection in dashboard that lists files that are currently being downloaded
<h3>{{ _('Downloads in progress') }}</h3>
<div id="ondd-file-list" data-url="{{ i18n_path(url('plugins:ondd:files')) }}">
    % include('ondd/_file_list')
</div>

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

