<%def name="content(group)">
    <h2 class="description">${ngettext('A content item has been added to the Library with the following title:',
                                       '{count} content items have been added to the Library with the following titles:',
                                       group.count).format(count=group.count)}</h2>
    <p class="titles">${', '.join([item.safe_message('title') for idx, item in enumerate(group.notifications) if idx < 20])}</p>
</%def>

<%def name="diskspace(group)">
    <h2 class="description">
        Please go to the <a href="${i18n_url('plugins:diskspace:cleanup')}">clean up tool</a> 
        and remove unwanted content, your disk is getting full. 
        % if not request.user.is_superuser:
            You need to be 
            <a href="${i18n_url('auth:login', next='/')}">logged in</a> as 
            a superuser in order to delete content.
        % endif
    </h2>
    <p class="size">Diskspace remaining at last check: ${group.notifications[-1].message}</p>
    <p class="since">First triggered on ${group.notifications[0].created_at.strftime('%A, %B %d')}</p>
</%def>
<% notification_templates = {'content': content, 'diskspace': diskspace} %>

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
        <div class="message">${notification_templates[notification.category](group)}</div>
        <span class="timestamp">${group.created_at.date()}</span>
        <span class="icon ${group.category}"></span>
        % if not group.is_read:
        <button class="small" type="submit">${_('Dismiss')}</button>
        % endif
    </form>
</li>
% endfor
