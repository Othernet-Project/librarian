<%namespace name="forms" file="/ui/forms.tpl"/>
<%namespace name="presets" file="_presets.tpl"/>

${forms.form_message(message)}
${forms.form_errors([form.error]) if form.error else ''}

% if is_ku:
    <div class="lnb-settings">
        ${forms.field(form.lnb)}
    </div>
% endif

<div class="settings-presets">
    ${presets.body()}
</div>

<div class="settings-fields">
    % if is_l:
        ${forms.field(form.frequency)}
        ${forms.field(form.uncertainty)}
        ${forms.field(form.symbolrate)}
        ${forms.field(form.sample_rate)}
        ${forms.field(form.rf_filter)}
        ${forms.field(form.descrambler)}
    % else:
        ${forms.field(form.frequency)}
        ${forms.field(form.symbolrate)}
        ${forms.field(form.delivery)}
        ${forms.field(form.modulation)}
        ${forms.field(form.polarization)}
        ## TODO: Add support for DiSEqC azimuth value
    % endif
</div>
