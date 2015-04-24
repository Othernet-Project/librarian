<input type="hidden" name="preset">
<div class="lnb-settings">
    <p class="lnb">
        ## Translators, form label for LNB type selection
        <label for="lnb">${_('LNB type:')}</label>
        ${h.vselect('lnb', LNB_TYPES, vals)}
        ${h.field_error('lnb', errors)}
    </p>
</div>
<div class="settings-fields">
    <p class="frequency">
        ## Translators, form label for transponder frequency
        <label for="frequency">${_('Frequency:')}</label>
        ${h.vinput('frequency', vals, type='text')}
        ${h.field_error('frequency', errors)}
    </p>
    <p class="symbolrate">
        ## Translators, form label for transponder symbol rate
        <label for="symbolrate">${_('Symbol rate:')}</label>
        ${h.vinput('symbolrate', vals, type='text')}
        ${h.field_error('symbolrate', errors)}
    </p>
    <p class="delivery">
        ## Translators, form label for transponder delivery system (DVB-S or DVB-S2)
        <label for="delivery">${_('Delivery system:')}</label>
        ${h.vselect('delivery', DELIVERY, vals)}
        ${h.field_error('delivery', errors)}
    </p>
    <p class="modulation">
        ## Translators, form label for transponder modulation mode (QPSK, etc)
        <label for="modulation">${_('Modulation:')}</label>
        ${h.vselect('modulation', MODULATION, vals)}
        ${h.field_error('modulation', errors)}
    </p>
    <p class="polarization">
        ## Translation, form label for transpornder polarization (Vertical/Horizontal)
        <label for="polarization">${_('Polarization:')}</label>
        ${h.vselect('polarization', POLARIZATION, vals)}
        ${h.field_error('polarization', errors)}
    </p>
    ## TODO: Add support for DiSEqC azimuth value
</div>
