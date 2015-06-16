<%inherit file='main.tpl'/>

<%block name="step_title">
<h3>${_('Please select the interface language.')}</h3>
</%block>

<%block name="step">
<div class="step-language-form">
    <p>
        ${form.language.label}
        ${form.language}
        % if form.language.error:
        ${form.language.error}
        % endif
    </p>
</div>
</%block>
