<%inherit file='main.tpl'/>

<%block name="step">
<h3>${_('Please set the current date and time.')}</h3>
<div class="step-datetime-form">
    <div class="date-field">
        ## Translators, used as label for date selector
        <label>${_('Date ("YYYY-MM-DD"):')}</label>
        <span id="noscript-picker">
            ${h.vinput('date', datetime, _type='text', _id="date", _class='date')}
        </span>
        <input type="text" id="datepicker" style="display: none" />
        <div class="flow-element">
            <div id="pikaday-container"></div>
        </div>
    </div>
    <div class="date-field">
        ## Translators, used as label for time input
        <label>${_('Time:')}</label>
        ${h.vselect('hour', hours, datetime, _class='time')}&#58;
        ${h.vselect('minute', minutes, datetime, _class='time')}
    </div>
    <div class="date-field">
        ## Translators, used as label for timezone
        <label for="timezone">${_('Timezone:')}</label>
        <div class="timezone-container">
        ${h.vselect('timezone', timezones, {'timezone': tz}, _id="timezone")}
        ${h.field_error('timezone', errors)}
        </div>
    </div>
    ${h.form_errors(errors)}
</div>
</%block>

<%block name="extra_scripts">
<script type="text/javascript" src="${th.static_url('sys:static', path='js/setupdatetime.js')}"></script>
</%block>
