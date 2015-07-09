<%inherit file='base.tpl'/>
<%namespace name='notification_list' file='_notification_list.tpl'/>

<%block name="title">
## Translators, used as page title
${_('Notifications')}
</%block>

% if groups:
<div class="h-bar">
    <div class="form actions">
        <form method="post">
            <button name="action" value="mark_read_all" class="confirm primary">
                ## Translators, used as label for discarding all unread notifications
                <span class="icon">${_('Dismiss all')}</span>
            </button>
        </form>
    </div>
</div>
% endif

% if not groups:
<p class="empty">
    ## Translators, note that appears on notifications page when there are no new notifications
    ${_('There are no new notifications')}
</p>
% endif

% if groups:
<ul id="notification-list" class="notification-list">
    ${notification_list.body()}
</ul>
% endif
