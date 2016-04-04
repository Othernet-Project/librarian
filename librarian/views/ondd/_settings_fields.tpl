<%namespace name="forms" file="/ui/forms.tpl"/>
<%namespace name="presets" file="_presets.tpl"/>

${forms.form_message(message)}
${forms.form_errors([form.error]) if form.error else ''}


<div class="lnb-settings">
    ${forms.field(form.lnb)}
</div>

<div class="settings-presets">
    ${presets.body()}
</div>

<div class="settings-fields">
    ${forms.field(form.frequency)}
    ${forms.field(form.symbolrate)}
    ${forms.field(form.delivery)}
    ${forms.field(form.modulation)}
    ${forms.field(form.polarization)}
    ## TODO: Add support for DiSEqC azimuth value
</div>
