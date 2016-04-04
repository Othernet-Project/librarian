<%def name="default(group)">
    % for item in group.notifications:
        <p class="message">${item.safe_message()}</p>
    % endfor
</%def>
<%def name="content(group)">
    <h3 class="description">
        ${ngettext('A content item has been added to the Library with the following title:',
        '{count} content items have been added to the Library with the following titles:',
        group.count).format(count=group.count)}
    </h3>
    <p class="titles">${', '.join([item.safe_message('title') for idx, item in enumerate(group.notifications) if idx < 20])}</p>
</%def>

<%
    notification_templates = {
        'default': default,
        'content': content,
    }
    default_template = default
%>

% if groups:
    <form method="post" action="${i18n_url('notifications:list')}">
        <p class="subtitle-buttons">
            <button name="action" value="mark_read_all" class="clean" tabindex="1">
                <span class="icon icon-no-outline"></span>
                ## Translators, used as label for discarding all unread notifications
                <span>${_('Mark all as read')}</span>
            </button>
        </p>
    </form>

    <ul id="notification-list" class="notification-list">
        % for group in groups:
        <li class="notification notification-${group.category or 'default'} ${group.verbose_priority}">
            <form method="post" action="${i18n_url('notifications:list')}">
                <input type="hidden" name="notification_id" value="${group.first_id}" />
                <div class="notification-body">
                    <div class="message">${notification_templates.get(group.category, default_template)(group)}</div>
                    <p class="notification-meta">
                        <span class="notification-icon ${group.category}"></span>
                        <span class="timestamp">
                            <time datetime="${group.created_at.isoformat()}">${group.created_at.strftime('%Y-%m-%d %H:%M')}</time>
                        </span>
                    </p>
                </div>
                % if not group.is_read and group.dismissable:
                <button name="action" value="mark_read" class="notification-delete clean" type="submit" tabindex="${loop.index + 2}">
                    <span class="icon icon-no"></span>
                    <span class="notification-delete-label">${_('Dismiss')}</span>
                </button>
                % endif
            </form>
        </li>
        % endfor
    </ul>
% else:
    <p class="empty">
        ## Translators, note that appears on notifications page when there are no new notifications
        ${_('There are no new notifications')}
    </p>
% endif
