<%namespace name="ui" file="/ui/widgets.tpl"/>


<div class="ondd-status-panel">
    <% status = th.state.ondd['status'] %>
    <table>
        <tr>
            <td>${_("Selected frequency")}</td>
            <td class="value" data-bind="text: ondd.status.freq + ' MHz'">${'{} MHz'.format(status['freq'])}</td>
        </tr>
        <tr>
            <td>${_("Offset from selected frequency")}</td>
            <td class="value" data-bind="text: ondd.status.freq_offset + ' Hz'">${'{} Hz'.format(status['freq_offset'])}</td>
        </tr>
        <tr>
            <td>${_("Symbol rate")}</td>
            <td class="value" data-bind="text: ondd.status.set_rs + ' Hz'">${'{} Hz'.format(status['set_rs'])}</td>
        </tr>
        <tr>
            <td>${_("RSSI")}</td>
            <td class="value" data-bind="text: ondd.status.rssi + ' dBm'">${'{} dBm'.format(status['rssi'])}</td>
        </tr>
        <tr>
            <td>${_("SNR")}</td>
            <td class="value" data-bind="text: ondd.status.snr + ' dB'">${'{} dB'.format(status['snr'])}</td>
        </tr>
        <tr>
            <td>${_("Symbol error rate")}</td>
            <td class="value" data-bind="text: ondd.status.ser">${status['ser']}</td>
        </tr>
        <tr>
            <td>${_("Received packet count")}</td>
            <td class="value" data-bind="text: ondd.status.crc_ok">${status['crc_ok']}</td>
        </tr>
        <tr>
            <td>${_("Packet failure count")}</td>
            <td class="value" data-bind="text: ondd.status.crc_err">${status['crc_err']}</td>
        </tr>
        <tr>
            <td>${_("Algorithmic peak-to-mean ratio")}</td>
            <td class="value" data-bind="text: ondd.status.alg_pk_mn">${status['alg_pk_mn']}</td>
        </tr>
        <tr>
            <td>${_("Signal state")}</td>
            <td class="value" data-bind="text: ondd.status.state">${status['state']}</td>
        </tr>
    </table>
</div>
