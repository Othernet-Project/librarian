<span class="lock {{ h.yesno(status['has_lock'], 'has', '') }}">
    %# Translators, whether tuner has a lock on the signal or not (note: technical term)
    {{ h.yesno(status['has_lock'], _('has lock'), _('no lock')) }}
</span>
<span class="signal">
    <span class="signal-bar" style="right: {{ 100 - status['signal'] }}%">
        <span>
        {{ status['signal'] }}%

            <span class="snr">
            %# Translators, short for 'signal/noise ratio'
            {{ _('SNR') }}: {{ status['snr'] }}
            </span>
        </span>
    </span>
<span>
