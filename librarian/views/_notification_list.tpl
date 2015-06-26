<%def name="content(group)">
    <span class="description">${ngettext('A content item has been added to the Library with the following title:',
                                         '{count} content items have been added to the Library with the following titles:',
                                         group.count).format(count=group.count)}</span>
    <span class="titles">${', '.join([item.message['title'] for item in group.notifications])}</span>
</%def>
<% notification_templates = {'content': content} %>

% for group in groups:
<li class="notification h-bar ${loop.cycle('white', '')} ${'' if group.is_read else 'unread'}">
    % if not group.is_read:
    <span class="alert">
        <span class="icon${' dismissable' if group.dismissable else ''}"></span>
    </span>
    % endif
    ${h.form('post', _class="notification-body")}
        % for notification in group.notifications:
            <input type="hidden" name="mark_read" value="${notification.notification_id}" />
        % endfor
        <h2 class="message">${notification_templates[notification.category](group)}</h2>
        <span class="timestamp">${group.created_at.date()}</span>
        <span class="icon ${group.category}"></span>
        % if not group.is_read:
        <button class="small" type="submit">${_('Mark read')}</button>
        % endif
    </form>
</li>
% endfor
