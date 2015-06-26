<%namespace name="widgets" file="../_widgets.tpl"/>

<% snr_pct = h.perc_range(status['snr'], 0, 1.6) %>
<% has_lock = h.yesno(status['has_lock'], h.SPAN(_('Yes'), _class='has-lock'), h.SPAN(_('No'), _class='no-lock')) %>
<% has_service = h.yesno(status['streams'], h.SPAN(_('Yes'), _class='has-lock'), h.SPAN(_('No'), _class='no-lock')) %>
## Translators, label is located next to the satellite signal strength indicator
${widgets.progress(_("Signal"), status['signal'], value=status['signal'], threshold=50)}
## Translators, label is located next to the satellite signal quality indicator
${widgets.progress(_("Quality"), snr_pct, value=status['snr'], threshold=25)}

<p class="lock">
    ## Translators, this indicates whether we locked on to the chosen transponder
    <span class="label">${_('Locked on to transponder')}:</span> ${has_lock}
</p>
<p class="service">
    ## Translators, this indicates whether the signal onto which we locked is broadcasting Outernet service
    <span class="label">${_('Receiving Outernet service')}:</span> ${has_service}
</p>
<p class="bitrate">
    ## Translators, bitrate
    <span class="label">${_('Bitrate')}:</span> ${h.hsize(th.get_bitrate(status), unit='bps', step=1000)}
</p>
