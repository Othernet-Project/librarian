<%namespace name="widgets" file="../_widgets.tpl"/>

<% snr_pct = h.perc_range(status['snr'], 0, 1.6) %>
<% has_lock = h.yesno(status['has_lock'], h.SPAN(_('has lock'), _class='has-lock'), h.SPAN(_('no lock'), _class='no-lock')) %>
${widgets.progress(has_lock, snr_pct, value=status['snr'], threshold=25)}

<p class="bitrate">
    ## Translators, bitrate
    <span class="label">${_('Bitrate')}</span> ${h.hsize(th.get_bitrate(status), unit='bps', step=1000)}
</p>
