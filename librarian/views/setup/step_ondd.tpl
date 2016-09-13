<%inherit file='/setup/setup_base.tpl'/>

<%namespace name="forms" file="/ui/forms.tpl"/>
<%namespace name="settings_fields" file="/ondd/_settings_fields.tpl"/>
<%namespace name="presets" file="/ondd/_presets.tpl"/>

<%block name="step_title">
    <span class="icon icon-satellite"></span>
    ## Translators, used during setup wizard in tuner settings step, as step
    ## title
    ${_('Tuner settings')}
</%block>

<%block name="step_desc">
    ## Translators, used during setup wizard in tuner settings step
    <p>${_("Please select the satellite you'd like to receive data from.")}</p>
</%block>

<%block name="step">
    <div id="ondd-form" class="step-ondd-form">
        <div id="settings-form">
            ${settings_fields.body()}
        </div>
    </div>
</%block>

<%block name="extra_body">
    <script type="text/template" id="jsFieldError">
        <span class="field-error js-error"></span>
    </script>
    <script type="application/json" id="validation-messages">
        {
            "preset": "${_('Please select a satellite.')}"
        }
    </script>
</%block>
