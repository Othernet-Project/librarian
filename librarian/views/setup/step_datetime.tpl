<%inherit file='main.tpl'/>

<%block name="step">
<h3>${_('Please set the current date and time.')}</h3>
<div class="step-datetime-form">
    <div class="date-field">
        ${form.date.label}
        <div id="noscript-picker">
            ${form.date}
            %if form.date.error:
            ${form.date.error}
            %endif
            <p class="helptext">${_('Please enter the date in YYYY-MM-DD format (e.g.: %s)') % form.date.value}</p>
        </div>
        <input type="text" id="datepicker" style="display: none" />
        <div class="flow-element">
            <div id="pikaday-container"></div>
        </div>
        %if form.date.error:
        <span class="js-error">${form.date.error}</span>
        %endif
    </div>
    <div class="date-field">
        ## Translators, used as label for time input
        <label>${_('Time:')}</label>
        ${form.hour}&#58;
        ${form.minute}
        % if form.hour.error:
        ${form.hour.error}
        % endif
        % if form.minute.error:
        ${form.minute.error}
        % endif
    </div>
    <div class="date-field">
        ${form.timezone.label}
        <div class="timezone-container">
            ${form.timezone}
            % if form.timezone.error:
            ${form.timezone.error}
            % endif
        </div>
    </div>
</div>
</%block>

<%block name="extra_scripts">
<script type="text/javascript" src="${th.static_url('sys:static', path='js/setupdatetime.js')}"></script>
</%block>
