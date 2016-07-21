<%inherit file="/narrow_base.tpl"/>
<%namespace name="update_form" file="_update.tpl"/>

<%block name="title">
## Translators, used as page title
${_('Firmware Update')}
</%block>

<h2>
    <span class="icon icon-firmware"></span>
    ## Translators, used as page heading
    <span>${_('Firmware Update')}</span>
</h2>

<div id="firmware-update-container">
${update_form.body()}
</div>
