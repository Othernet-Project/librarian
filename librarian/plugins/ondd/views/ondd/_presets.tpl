<script type="text/template" id="satPresets">
    <p class="transponder-selection">
    ## Translators, label for select list that allows user to pick a satellite to tune into
    <label for="transponders">${_('Satellite:')}</label>
    <select name="preset" id="transponders" class="transponders">
        ## Translators, placeholder for satellite selection select list
        <option value="0">${_('Select a satellite')}</option>
        % for pname, index, preset in form.PRESETS:
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
