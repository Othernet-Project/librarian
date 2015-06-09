% for group in groups:
<li class="notification ${'' if group.is_read else 'unread'}">
    ${h.form('post')}
        % for notification in group.notifications:
            <input type="hidden" name="mark_read" value="${notification.notification_id}" />
        % endfor
        <span>${group.message}</span>
        <span>${group.count}</span>
        % if not group.is_read:
        <button type="submit">${_('Mark read')}</button>
        % endif
    </form>
</li>
% endfor
