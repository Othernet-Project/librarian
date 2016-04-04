<%doc>
The base template
=================

Base template sets the basic UI elements for all 'full' pages. A 'full' page is
a page that provides the complete set of auxiliarry interface elements such as
navigation, sidebars, status bars, and menus.

The base template provides several Mako blocks that can be used to overload
various parts of the interface. This includes:

- ``title``: Sets the page title
- ``menubar_panel``: Sets the contents of the panel inside the pull-down
  menubar's hbar section (between the logo and context menu)
- ``context_menu``: Sets the contents of the context menu
- ``main``: Sets the content of the main panel (this is where most of the
  page-specific UI elements go)
- ``footer``: Wraps the entire footer for removal in edge cases
- ``statusbar_quick``: Sets the contents of the quick status area (left of the
  statusbar toggle activator
- ``statusbar_panel``: Sets the contetns of the statusbar panel (expandable
  portion)
- ``extra_head``: Can be used to add arbitrary markup to the <head> section
- ``extra_body``: Can be used to add arbitrary markup to the <body> but
  _above_ the scripts
- ``extra_scripts``: Can be used to add arbitrary markup to the <body> but
  _below_ the default scripts
</%doc>

<%namespace name="ui" file="/ui/widgets.tpl"/>
<%namespace name="menu" file="/ui/menu_item.tpl"/>
<%namespace name="nojs" file="/ui/nojs.tpl"/>

<%!
# Global constants
MENUBAR_ID = 'menubar-top'
STATUSBAR_ID = 'status'
CONTEXT_BAR_ID = 'context-bar'
CONTEXT_MENU_ID = 'context-menu'
MAIN_PANEL_ID = 'main-panel'
STATUS_TAB_ID = 'status-tab'
%>

<!doctype html>

<html lang="${request.locale}"${' dir="rtl"' if th.is_rtl(request.locale) == True else ''}>
    <head>
        <meta charset="utf-8">
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <title><%block name="title"></%block> - Librarian v${th.app_version()}</title>
        <meta name="mobile-web-app-capable" content="yes">
        <meta name="viewport" content="initial-scale=1, maximum-scale=1, user-scalable=no">
        <link rel="stylesheet" href="${assets['css/lui']}">
        % if redirect_url is not UNDEFINED:
        <meta http-equiv="refresh" content="${REDIRECT_DELAY}; url=${aesc(redirect_url)}">
        % endif
        <%block name="extra_head"/>
    </head>
    <body>
        <header class="o-pulldown-menubar ${nojs.open_class('menu')}" id="${MENUBAR_ID}" role="section" ${nojs.aria_exp('menu')}>
        <%block name="header">
            <%block name="header_menubar">
                <%ui:apps_menu id="${MENUBAR_ID}">
                    <ul class="o-apps-menu">
                    % for mi in menu_group('main'):
                        ${menu.menu_item(mi)}
                    % endfor
                    </ul>
                </%ui:apps_menu>
            </%block>
            <div class="o-pulldown-menubar-hbar" id="${MENUBAR_ID}-hbar" role="menubar">
                <a href="${nojs.comp_url('menu')}" role="button" aria-controls="${MENUBAR_ID}" class="o-pulldown-menubar-hbar-activator o-activator">
                    <span class="o-pulldown-menubar-hbar-activator-label">
                        <span class="o-pulldown-menubar-hbar-activator-label-icon icon icon-outernet"></span>
                        <span class="o-pulldown-menubar-hbar-activator-label-text">${_('Toggle apps menu')}</span>
                    </span>
                    <span class="o-pulldown-menubar-hbar-activator-icon icon"></span>
                </a>
                <div class="o-pulldown-menubar-hbar-bar">
                    <div class="o-contextbar o-panel" id="${CONTEXT_BAR_ID}">
                        <div class="o-panel">
                        <%block name="menubar_panel"/>
                        </div>
                        <div class="o-panel">
                            <a href="${nojs.comp_url('sidebar')}" class="o-contextbar-menu" role="button" arial-controls="${CONTEXT_MENU_ID}">
                                <span class="o-contextbar-menu-label">${_('Toggle context menu')}</span>
                                <span class="o-contextbar-menu-icon icon"></span>
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </%block>
        </header>

        <nav id="${CONTEXT_MENU_ID}" class="o-context-menu ${nojs.open_class('sidebar')}" role="menu" ${nojs.aria_hidden('sidebar')}>
        ## Translators, label for context menu language switcher
        ${ui.context_menu_submenu('language', 'language-list', _('Language'), 'globe', target_url=i18n_url('ui:lang_list', path=request.path))}

        <%block name="context_menu">
            ## Use ``ui.context_menu_item()`` def to build your context menu,
            ## and be sure to add a separator at the bottom of the
            ## ``context_menu`` block. For menu items, you can use icons
            ## (without 'mdi-' class prefix) listed on this page:
            ##
            ##     https://cdn.materialdesignicons.com/1.2.65/
            ##
        </%block>

        ${ui.context_menu_separator()}

        % if request.user.is_authenticated:
            ## Translators, link to settings dashboard in the context menu
            ${ui.context_menu_item('settings', _('Settings'), i18n_url('dashboard:main'), 'settings', direct=True)}
            ## Translators, link shown in context menu when user is logged in.
            ${ui.context_menu_item('auth', _('Log out'), i18n_url('auth:logout', next=request.path), 'exit', direct=True)}
        % else:
            ## Translators, link shown in context menu when user is not logged in.
            ${ui.context_menu_item('auth', _('Log in'), i18n_url('auth:login', next=request.path), 'enter')}
        % endif
        </nav>

        <nav id="language-list" class="o-context-menu o-context-menu-submenu" role="menu" aria-hidden="true">
        ## Translators, label on back button that appears at the top of
        ## context menu's submenu
        ${ui.context_menu_back(CONTEXT_MENU_ID, _('Back to menu'))}
        % for locale, lang in languages:
            <% lang_url = i18n_path(path=request.path, locale=locale) %>
            ${ui.context_menu_item('lang-{}'.format(locale), lang, lang_url, enabled=locale != request.locale, direct=True)}
        % endfor
        </nav>

        <div id="${MAIN_PANEL_ID}" class="o-main-panel">
            <%block name="main">
                ${self.body(**context.kwargs)}
            </%block>
        </div>

        <%block name="footer">
            <footer class="o-statusbar" id="${STATUSBAR_ID}">
                <div class="o-statusbar-hbar o-activator" id="${id}-hbar" role="button" aria-controls="${id}-status">
                    <div class="o-statusbar-hbar-quick-status">
                        <%block name="statusbar_quick">
                            <%
                                if request.user.is_authenticated:
                                    if request.user.is_superuser:
                                        icon = 'user-up'
                                    else:
                                        icon = 'user'
                                    username = request.user.username
                                else:
                                    icon = 'lock'
                                    # Translators, used as a label for guest account (unauthenticated user)
                                    username = _('guest')
                                notifications = th.get_notification_count()
                            %>
                            <span class="icon icon-${icon}"></span>
                            <span class="username">${username}</span>
                            % if notifications:
                                <span class="separator"></span>
                                <span class="unread-notifications">
                                    <span class="alert icon icon-message-alert"></span>
                                    <span class="unread-notification-count">${notifications}</span>
                                </span>
                            % endif
                            </span>
                        </%block>
                    </div>
                </div>
                <div class="o-statusbar-status o-collapsible" id="${STATUSBAR_ID}-status" role="status" aria-expanded="false">
                    <div class="o-statusbar-panel-content">
                        <%block name="statusbar_panel">
                            <div id="status-tab" class="o-tabbable">
                                <ul class="o-tab-handles" role="tablist">
                                    <li class="o-tab-handle">
                                    ${ui.tab_activator(_('Info'), 'info', 'info-tab', active=True)}
                                    </li>
                                    <li class="o-tab-handle">
                                    ${ui.tab_activator(_('Notifications'), 'message-alert', 'notifications-tab')}
                                    </li>
                                </ul>
                                <div class="o-tab-panels">
                                    <%ui:tab_panel id="info-tab" expanded="true">
                                        <p class="progver"><span lang="en">Librarian</span> v${th.app_version()}</p>
                                        <p class="copyright">2014-2015 <span lang="en">Outernet Inc</span></p>
                                    </%ui:tab_panel>
                                    <%ui:tab_panel id="notifications-tab" url="${i18n_url('notifications:list')}"/>
                                </div>
                            </div>
                        </%block>
                    </div>
                </div>
            </footer>
        </%block>

        <!-- inline JS templates -->
        <script type="text/template" id="modalContent">
            <%ui:modal_container id="content", close_button_label="${_('Close')}">
                <div class="o-modal-content o-modal-panel" role="document">
                    <span class="o-modal-spinner">${_('Loading')}<span class="o-modal-spinner-loading-indicator">...</span></span>
                </div>
            </%ui:modal_container>
        </script>

        <script type="text/template" id="loadFail">
            ${_('Content could not be loaded')}
        </script>

        <script type="text/template" id="modalLoadFailure">
            <div class="o-modal-load-failure o-modal-spinner">
                ${_('Content could not be loaded')}
            </div>
        </script>

        <script type="text/template" id="spinner">
            ## Translators, message shown next to a spinning load icon
            ${ui.spinner(_('Loading...'))}
        </script>

        <script type="text/template" id="statusbarToggle">
            <a href="#${STATUSBAR_ID}-status" class="o-statusbar-hbar-activator" role="button" aria-controls="${STATUSBAR_ID}-status">
                <span class="o-statusbar-hbar-activator-label">${_('Toggle status')}</span>
                <span class="o-statusbar-hbar-activator-icon icon"></span>
            </a>
        </script>

        <%block name="extra_body"/>

        <script type="text/javascript">
        // Global variables
        (function (window) {
            window.o = window.o == null ? {} : window.o;
            window.o.pageVars = {
                menubarId: "${MENUBAR_ID}",
                statusbarId: "${STATUSBAR_ID}",
                contextbarId: "${CONTEXT_BAR_ID}",
                contextmenuId: "${CONTEXT_MENU_ID}",
                mainPanelId: "${MAIN_PANEL_ID}",
                statusTabId: "${STATUS_TAB_ID}"
            };
        }(this));
        </script>

        <script src="${assets['js/lui']}"></script>

        <%block name="extra_scripts"/>
    </body>
</html>
