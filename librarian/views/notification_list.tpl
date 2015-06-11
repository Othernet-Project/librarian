<%inherit file='base.tpl'/>
<%namespace name='notification_list' file='_notification_list.tpl'/>

<%block name="title">
## Translators, used as page title
${_('Notifications')}
</%block>

<%block name="heading">
## Translators, used as page heading
${_('Notifications')}
</%block>

<div class="inner">
    <ul id="notification-list" class="notification-list">
        ${notification_list.body()}
    </ul>
</div>
