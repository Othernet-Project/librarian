<%namespace name="ui" file="/ui/widgets.tpl"/>

<%
    BRATE_MAX = 90000.0
    bitrate = th.get_bitrate(status)
    snr = status['snr']
    snr_max_delta = SNR_MAX - SNR_MIN
    snr_pct = round(max(snr - SNR_MIN, 0) / snr_max_delta * 100)
    bitrate_pct = round(bitrate / BRATE_MAX * 100)

    has_tuner = th.has_tuner()
    has_lock = status['has_lock'] 
    has_service = has_lock and status['streams'] and bitrate

    all_ok = False
    if not has_tuner:
        # Translators, used as main status text when there is no tuner
        status_text = _('no tuner')
    elif not has_lock:
        # Translators, used as main status text when there is no signal lock
        status_text = _('no lock')
    elif not has_service:
        # Translators, used as main status text when there is no service
        status_text = _('no service')
    else:
        # Translators, used as main status text when everything is ok
        status_text = _('receiving')
        all_ok = True
%>

<%def name="status_indicator(name, icon_name, active)">
    <span class="ondd-status-indicator ondd-status-${name} ondd-status-${'ok' if active else 'ng'}">
        <span class="icon icon-${icon_name}">
        </span>
    </span>
</%def>

<div class="ondd-status-panel">
    <div class="ondd-main-status">
        <p>
            <span class="ondd-quick-status${' ondd-all-ok' if all_ok else ''}">
                ${status_text}
            </span>
            <span class="ondd-status-icons">
                ${self.status_indicator('tuner', 'tuner', has_tuner)}
                ${self.status_indicator('lock', 'signal', has_lock)}
                ${self.status_indicator('service', 'download-bar', has_service)}
            </span>
        </p>
    </div>
    <div class="ondd-status-indicators">
        ## Translators, label is located next to the satellite signal strength
        ## indicator
        ${ui.progress(_('Signal'), status['signal'], value=status['signal'], threshold=50)}
        ## Translators, label is located next to the satellite signal quality
        ## indicator
        ${ui.progress(_('Quality'), snr_pct, value=status['snr'], threshold=25)}
        ## Translators, labe is located next to the bitrate indicator
        ${ui.progress(_('Bitrate'), bitrate_pct, h.hsize(bitrate, '', 1000, rounding=0, sep=''), threshold=10)}
    </div>
</div>
