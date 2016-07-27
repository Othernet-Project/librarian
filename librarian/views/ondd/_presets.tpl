<%namespace name="forms" file="/ui/forms.tpl"/>

<%
selected_preset = context.get('selected_preset', 0)
value = request.params.get('preset', str(selected_preset))
%>

<%def name="preset_attrs(data)">
    % for k in preset_keys:
        data-${k}="${data[k]}"
    % endfor
</%def>

<p class="o-field{' o-field-error' if form.preset.error else ''}">
    ## Translators, label for select list that allows user to pick a satellite to tune into
    ${forms.label(_('Satellite'), id='transponders')}
    <select name="preset" id="transponders" class="transponders" data-fields="${' '.join(preset_keys)}">
        ## Translators, placeholder for satellite selection select list
        <option value="">${_('Select a satellite')}</option>
        % for pname, index, preset in form.PRESETS:
            <option value="${index}" ${ 'selected' if value == str(index) else ''} ${preset_attrs(preset)}>${pname}</option>
        % endfor
        ## Translators, label for option that allows user to set custom
        ## transponder parameters
        <option value="-1"${' selected' if value == '-1' else ''}>${_('Custom...')}</option>
    </select>
    ## Translators, instruction for the user on how to use the presets select
    ## list
    ${forms.field_help(_("Select a preset or use 'Custom' and enter data manually"))}
    % if form.preset.error:
    ${forms.field_error(form.preset.error)}
    % endif
</p>
