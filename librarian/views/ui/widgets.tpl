<%namespace name="forms" file="_forms.tpl"/>

<%! jsvoid = 'javascript:void(0);' %>

## Pulldown menubar
##
## Renders several containers representing pulldown menubars.
##

<%def name="apps_menu(id)">
    <nav class="o-pulldown-menubar-menu o-collapsible" id="${id}-menu" role="menubar" aria-expanded="false">
    ${caller.body()}
    </nav>
</%def>

## Status bar (bottom bar)
##
## Retractable status bar
##

<%def name="statusbar(id, label='open/close')">
    <footer class="o-statusbar" id="${id}">
        <div class="o-statusbar-hbar o-activator" id="${id}-hbar" role="button" aria-controls="${id}-status">
            <div class="o-statusbar-hbar-quick-status">
            ${caller.hbar()}
            </div>
            <a href="#${id}-status" class="o-statusbar-hbar-activator" role="button" aria-controls="${id}-status">
                <span class="o-statusbar-hbar-activator-label">${label}</span>
                <span class="o-statusbar-hbar-activator-icon icon"></span>
            </a>
        </div>
        <div class="o-statusbar-status o-collapsible" id="${id}-status" role="status" aria-expanded="false">
        ${caller.status()}
        </div>
    </footer>
</%def>


## Multisearch
##
## Double-split panel with select list in the first panel, input box in second,
## and submit button in the last panel.
##

<%def name="multisearch(name, route_name=None, method='get', placeholder=None, label='go')">
    <form id="${name}" class="o-multisearch o-panel"${ 'action="{}"'.format(route(route_name)) if route_name else ''} method="${method}">
        <div class="o-panel">
            ${forms.select(name + '_mode')}
        </div>
        <div class="o-panel">
            ${forms.text(name + '_keywords', placeholder=placeholder)}
        </div>
        <div class="o-panel">
            <button id="${name}-button" type="submit" class="o-multisearch-button">
                <span class="o-multisearch-button-label">${label}</span>
                <span class="o-multisearch-button-icon icon"></span>
            </button>
        </div>
    </form>
</%def>

<%def name="context_menu_item(id, label, url, icon='', enabled=True, direct=False, extra_attribs='')">
    <a
        href="${url if enabled else jsvoid}" id="${id}"
        class="o-context-menu-menuitem ${ 'disabled' if not enabled else ''}"
        role="menuitem"
        aria-disabled="${'false' if enabled else 'true'}"
        data-context="${'direct' if direct else 'modal'}"
        ${'tabindex="-1"' if not enabled else ''}
        ${extra_attribs}>
        <span class="${'icon icon-{} '.format(icon) if icon else ''}o-context-menu-menuitem-icon"></span>
        <span class="o-context-menu-menuitem-label">${label}</span>
    </a>
</%def>

<%def name="context_menu_submenu(id, target_id, label, icon='', expand_icon='expand-right', enabled=True, target_url=None)">
    <% target_href = target_url or '#{}'.format(target_id) %>
    <a
        href="${target_href if enabled else jsvoid}" id="${id}"
        class="o-context-menu-menuitem o-context-menu-submenu-activator ${ 'disabled' if not enabled else ''}"
        role="menuitem"
        aria-disabled="${'false' if enabled else 'true'}"
        aria-controls="${target_id}"
        data-context="submenu">
        <span class="${'icon icon-{} '.format(icon) if icon else ''}o-context-menu-menuitem-icon"></span>
        <span class="o-context-menu-menuitem-label">${label}</span>
        <span class="o-context-menu-expand-icon icon icon-${expand_icon}"></span>
    </a>
</%def>

<%def name="context_menu_back(target_id, label, icon='arrow-left')">
    <a
        href="#${target_id}"
        class="o-context-menu-menuitem o-context-menu-back"
        role="menuitem"
        data-context="back">
        <span class="${'icon icon-{} '.format(icon) if icon else ''}o-context-menu-menuitem-icon"></span>
        <span class="o-context-menu-menuitem-label">${label}</span>
    </a>
</%def>

<%def name="context_menu_separator()">
    <span class="o-context-menu-separator"></span>
</%def>

<%def name="modal_container(id, close_button_label)">
    <div class="o-modal-overlay" id="modal-${id}">
        <div class="o-modal-window" role="window" id="modal-${id}-window" tabindex>
            <button id="modal-${id}-close" class="o-modal-close" role="button" aria-controls="modal-${id}-window">
                <span class="o-modal-close-label">${close_button_label}</span>
                <span class="o-modal-close-icon icon"></span>
            </button>
            ${caller.body()}
        </div>
    </div>
</%def>

## Spinner

<%def name="spinner(message='')">
    <span class="icon icon-spinning-loader-xxl"></span>
    ${message}
</%def>

## Tabbable

<%def name="tab_activator(label, icon, target, active=False)">
    <a class="o-tab-handle-activator${ ' active' if active else ''}" href="#${target}" role="tab" aria-controls="info">
        <span class="o-tab-handle-activator-icon icon icon-${icon}"></span>
        <span class="o-tab-handle-activator-label">${label}</span>
    </a>
</%def>

<%def name="tab_panel(id, expanded=False, url='')">
    <div id="${id}" class="o-tab-panel${ ' active' if expanded else ''}" role="tabpanel" aria-expanded="${'true' if expanded else 'false'}"${ ' data-url={}'.format(url) if url else ''}>
        % if not url:
            ${caller.body()}
        % endif
    </div>
</%def>

## Progress bar
<%def name="progress(label, percentage, value, threshold=10)">
    <%
        # Percentages are expressed in 5% increments
        rounded_pct = int(round(percentage / 5) * 5)
        # And we correct the out-of-bounds percentages
        rounded_pct = min(max(rounded_pct, 0), 100)
    %>
    <span class="o-progress">
        <span class="o-progress-indicator o-progress-percentage-${rounded_pct}">
            <span class="o-progress-value">
                ${value}
            </span>
        </span>
        <span class="o-progress-label">
            ${label}
        </span>
    </span>
</%def>

<%def name="progress_mini(percentage, threshold=10, icon=None)">
    <%
        # Percentages are expressed in 5% increments
        rounded_pct = int(round(percentage / 5) * 5)
        # And we correct the out-of-bounds percentages
        rounded_pct = min(max(rounded_pct, 0), 100)
    %>
    <span class="o-progress-mini">
        <span class="o-progress-indicator o-progress-percentage-${rounded_pct}">
            <span class="o-progress-icon">
                % if icon:
                    <span class="icon icon-${icon}"></span>
                % endif
            </span>
        </span>
    </span>
</%def>
