<%inherit file='main.tpl'/>

<%block name="step">
<h3>${_('Please set the current date and time.')}</h3>
<div class="step-datetime-form">
    <p>
        ## Translators, used as label for date time selector
        <label>${_('Date / time:')}</label>
        <span id="noscript-picker">
            ${h.vinput('year', datetime, _type='text', _id="year", _class='year')}&ndash;
            ${h.vselect('month', months, datetime, _id="month")}&ndash;
            ${h.vinput('day', datetime, _type='text', _id="day", _class='time')}
        </span>
        <input type="text" id="datepicker" style="display: none" />
        ${h.vselect('hour', hours, datetime, _class='time')}&#58;
        ${h.vselect('minute', minutes, datetime, _class='time')}
    </p>
    <div class="flow-element">
        <div id="pikaday-container"></div>
    </div>
    <div>
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
<script type="text/javascript" src="${url('sys:static', path='js/setupdatetime.js')}"></script>
</%block>
