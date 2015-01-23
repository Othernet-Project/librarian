<span class="lock">
    %# Translators, whether tuner has a lock on the signal or not (note: technical term)
    {{ h.yesno(status['has_lock'], _('has lock'), _('no lock')) }}
</span>
<span class="signal">
    <span class="signal-bar" style="width: {{ status['signal'] }}%">
        {{ status['signal'] }}%
    </span>
<span>
<span class="snr">
    %# Translators, short for 'signal/noise ratio'
    {{ _('SNR') }}: {{ status['snr'] }}
</span>
