<%namespace name="forms" file="/ui/forms.tpl"/>

<% 
selected_preset = context.get('selected_preset', 0)
value = request.params.get('preset', str(selected_preset))
%>

<p class="o-field">
    ## Translators, label for select list that allows user to pick a satellite to tune into
    ${forms.label(_('Satellite'), id='transponders')}
    <select name="preset" id="transponders" class="transponders">
        ## Translators, placeholder for satellite selection select list
        <option value="">${_('Select a satellite')}</option>
        % for pname, index, preset in form.PRESETS:
            <option value="${index}" ${ 'selected' if value == str(index) else ''}
                data-frequency="${preset['frequency']}"
                data-symbolrate="${preset['symbolrate']}"
                data-polarization="${preset['polarization']}"
                data-delivery="${preset['delivery']}"
                data-modulation="${preset['modulation']}"
                data-coverage="${preset['coverage']}">${pname}</option>
        % endfor
        ## Translators, label for option that allows user to set custom
        ## transponder parameters
        <option value="-1"${' selected' if value == '-1' else ''}>${_('Custom...')}</option>
    </select>
    ## Translators, instruction for the user on how to use the presets select
    ## list
    ${forms.field_help(_("Select a preset or use 'Custom' and enter data manually"))}
</p>
