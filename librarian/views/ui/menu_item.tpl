<%doc>
The menu items must follow the librarian-menu API. The def in this module is 
expected to receive a ``librarian_menu.menu.MenuItem`` object as its only 
argument.
</%doc>

<%def name="menu_item(obj)">
    <%
        target_path = obj.get_path()
        current_path = i18n_path(request.path)
        is_current = target_path == current_path
    %>
    % if obj.is_visible():
        <li class="o-apps-menu-item${' current' if is_current else ''}" id="${obj.name}">
        % if is_current:
            <span class="o-apps-menu-current">
        % else:
            <a href="${target_path}" class="o-apps-menu-link">
        % endif
            % if obj.icon_is_bitmap:
                <span class="o-apps-menu-icon o-apps-menu-icon-bitmap">
                    <img src="${i18n_url('sys:static', path=obj.icon_bitmap_path)}" alt="${_('application icon')}">
                </span>
            % else:
                <span class="o-apps-menu-icon">
                    <span class="icon icon-${obj.group or 'app'}-${obj.active_icon_class}"></span>
                </span>
            % endif
            <span class="o-apps-menu-label">
                ${obj.label}
            </span>
        % if is_current:
            </span>
        % else:
            </a>
        % endif
        </li>
    % endif
</%def>
