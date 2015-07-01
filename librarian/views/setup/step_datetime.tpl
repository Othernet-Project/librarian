<%inherit file='main.tpl'/>

<%block name="step_title">
<h2>${_('Please set the current timezone.')}</h2>
</%block>

<%block name="step">
<div class="step-datetime-form">
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
