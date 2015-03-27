<%inherit file="../base.tpl"/>
<%namespace name="settings_form" file="_settings_form.tpl"/>

<%block name="title">
## Translators, used as page title
${_('Tuner settings')}
</%block>

<%block name="heading">
## Translators, used as page heading
${_('Tuner settings')}
</%block>

${settings_form.body()}

<%block name="extra_scripts">
<script src="${url('plugins:ondd:static', path='ondd.js')}"></script>
</%block>

