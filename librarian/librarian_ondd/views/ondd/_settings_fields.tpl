<input type="hidden" name="preset">
<div class="lnb-settings">
    <p class="lnb">
        ${form.lnb.label}
        ${form.lnb}
        % if form.lnb.error:
        ${form.lnb.error}
        % endif
    </p>
</div>
<div class="settings-fields">
    <p class="frequency">
        ${form.frequency.label}
        ${form.frequency}
        % if form.frequency.error:
        ${form.frequency.error}
        % endif
    </p>
    <p class="symbolrate">
        ${form.symbolrate.label}
        ${form.symbolrate}
        % if form.symbolrate.error:
        ${form.symbolrate.error}
        % endif
    </p>
    <p class="delivery">
        ${form.delivery.label}
        ${form.delivery}
        % if form.delivery.error:
        ${form.delivery.error}
        % endif
    </p>
    <p class="modulation">
        ${form.modulation.label}
        ${form.modulation}
        % if form.modulation.error:
        ${form.modulation.error}
        % endif
    </p>
    <p class="polarization">
        ${form.polarization.label}
        ${form.polarization}
        % if form.polarization.error:
        ${form.polarization.error}
        % endif
    </p>
    ## TODO: Add support for DiSEqC azimuth value
</div>
