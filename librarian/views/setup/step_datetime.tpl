<%inherit file='main.tpl'/>

<%block name="step">
<h3>${_('Please set the current date and time.')}</h3>
<div class="step-datetime-form">
    <div class="date-field">
        ## Translators, used as label for date selector
        <label>${_('Date:')}</label>
        <div id="noscript-picker">
            ${h.vinput('date', datetime, _type='text', _id="date", _class='date')}
            ${h.field_error('date', errors)}
            <p class="helptext">${_('Please enter the date in YYYY-MM-DD format (e.g.: %s)') %datetime['date']}</p>
        </div>
        <input type="text" id="datepicker" style="display: none" />
        <div class="flow-element">
            <div id="pikaday-container"></div>
        </div>
        <span class="js-error">${h.field_error('date', errors)}</span>
    </div>
    <div class="date-field">
        ## Translators, used as label for time input
        <label>${_('Time:')}</label>
        ${h.vselect('hour', hours, datetime, _class='time')}&#58;
        ${h.vselect('minute', minutes, datetime, _class='time')}
        ${h.field_error('time', errors)}
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
