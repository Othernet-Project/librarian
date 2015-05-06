<span class="lock ${h.yesno(status['has_lock'], 'has', '')}">
    ## Translators, whether tuner has a lock on the signal or not (note: technical term)
    ${h.yesno(status['has_lock'], _('has lock'), _('no lock'))}
</span>
<span class="signal">
    <span class="signal-bar" style="right: ${100 - h.perc_range(status['snr'], 0.6, 0.9)}%">
        <span>
            ${h.perc_range(status['snr'], 0.6, 0.9)}%
        </span>
    </span>
</span>
<span class="snr">
    ## Translators, short for 'signal/noise ratio'
    ${_('SNR')} ${status['snr']}
</span>
<span class="bitrate">
    ## Translators, bitrate
    ${_('Bitrate')} ${th.get_bitrate(status)}
</span>
