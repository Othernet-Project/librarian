<%inherit file='main.tpl'/>

<%block name="step">
<h3>${_('Please set the current date and time.')}</h3>
<div class="step-datetime-form">
    <p>
        <span id="noscript-picker">
            ${h.vinput('year', datetime, _type='text', _class='year')}&ndash;
            ${h.vselect('month', months, datetime)}&ndash;
            ${h.vinput('day', datetime, _type='text', _class='time')}
        </span>
        <input type="text" id="datepicker" value="${datetime['year']}-${datetime['month']}-${datetime['day']}" style="display: none" />
        ${h.vinput('hour', datetime, _type='text', _class='time')}&#58;
        ${h.vinput('minute', datetime, _type='text', _class='time')}&#58;
        ${h.vinput('second', datetime, _type='text', _class='time')}
    </p>
    <div class="flow-element">
        <div id="pikaday-container"></div>
    </div>
    ${h.form_errors(errors)}
</div>
<script type="text/javascript" src="${url('sys:static', path='js/setupdatetime.js')}"></script>
</%block>
