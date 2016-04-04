<%inherit file='/setup/setup_base.tpl'/>

<%namespace name="forms" file="/ui/forms.tpl"/>

<%block name="step_title">
    ## Translators, used during setup wizard in language settings step, as step
    ## title
    <span class="icon icon-globe"></span> ${_('Default interface language')}
</%block>

<%block name="step_desc">
    ## Translators, used during setup wizard in language settings step
    <p>${_('Please select the default interface language. Users can change their language preference later.')}</p>
</%block>

<%block name="step">
    <div class="step-language-form">
        ${forms.field(form.language, id='language-select-field')}
    </div>
</%block>
