<%inherit file='/narrow_base.tpl'/>
<%namespace name='notification_list' file='_notification_list.tpl'/>

<%block name="title">
## Translators, used as page title
${_('Messages')}
</%block>

<h2>
    <span class="icon icon-message-alert"></span> 
    ${_('Messages')}
</h2>

${notification_list.body()}
