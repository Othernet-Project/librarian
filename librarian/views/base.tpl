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
- ``context_menu_defaults``: Sets the contents of the default context menu 
  items (this should generally not be touched)
- ``main``: Sets the content of the main panel (this is where most of the 
  page-specific UI elements go)
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

<% 
# Global constants
MENUBAR_ID = context.get('MENUBAR_ID', 'menubar-top')
STATUSBAR_ID = context.get('STATUSBAR_ID', 'status') 
CONTEXT_BAR_ID = context.get('CONTEXT_BAR_ID', 'context-bar')
CONTEXT_MENU_ID = context.get('CONTEXT_MENU_ID', 'context-menu')
MAIN_PANEL_ID = context.get('MAIN_PANEL_ID', 'main-panel')
%>

<!doctype html>

<html lang="en" xml:lang="en">
    <head>
        <title><%block name="title"></%block> - Librarian v${th.app_version()}</title>
        <meta name="viewport" content="initial-scale=1, maximum-scale=1, user-scalable=no" />
        <link rel="stylesheet" href="${assets['css/lui']}">
        % if redirect_url is not UNDEFINED:
        <meta http-equiv="refresh" content="${REDIRECT_DELAY}; url=${redirect_url}">
        % endif
        <%block name="extra_head"/>
    </head>
    <body>
        <header class="o-pulldown-menubar" id="${MENUBAR_ID}" role="section">
            <%ui:apps_menu id="${MENUBAR_ID}">
                Hello menu
            </%ui:apps_menu>
            <div class="o-pulldown-menubar-hbar" id="${MENUBAR_ID}-hbar" role="menubar">
                <a href="#${id}-menu" role="button" aria-controls="${MENUBAR_ID}" class="o-pulldown-menubar-hbar-activator o-activator">
                    <span class="o-pulldown-menubar-hbar-activator-label">${_('Toggle apps menu')}</span>
                    <span class="o-pulldown-menubar-hbar-activator-icon icon"></span>
                </a>
                <div class="o-pulldown-menubar-hbar-bar">
                    <div class="o-contextbar o-panel" id="${CONTEXT_BAR_ID}">
                        <div class="o-panel">
                        <%block name="menubar_panel"/>
                        </div>
                        <div class="o-panel">
                            <a href="#${CONTEXT_MENU_ID}" class="o-contextbar-menu" role="button" arial-controls="${CONTEXT_MENU_ID}">
                                <span class="o-contextbar-menu-label">${_('Toggle context menu')}</span>
                                <span class="o-contextbar-menu-icon icon"></span>
                            </a>
                        </div>
                    </div>
                </div>
            </div>
        </header>

        <nav id="${CONTEXT_MENU_ID}" class="o-context-menu" role="menu" aria-hidden="true">
        ## Use ``ui.context_menu_item()`` def to build your context menu
        <%block name="context_menu"/>
        <%block name="context_menu_defaults"/>
        </nav>

        <div id="${MAIN_PANEL_ID}" class="o-main-panel">
            <%block name="main">
                ${self.body(**context.kwargs)}
            </%block>
        </div>

        <footer class="o-statusbar" id="${STATUSBAR_ID}">
            <div class="o-statusbar-hbar o-activator" id="${id}-hbar" role="button" aria-controls="${id}-status">
                <div class="o-statusbar-hbar-quick-status">
                <%block name="statusbar_quick"/>
                </div>
                <a href="#${STATUSBAR_ID}-status" class="o-statusbar-hbar-activator" role="button" aria-controls="${STATUSBAR_ID}-status">
                    <span class="o-statusbar-hbar-activator-label">${_('Toggle status')}</span>
                    <span class="o-statusbar-hbar-activator-icon icon"></span>
                </a>
            </div>
            <div class="o-statusbar-status o-collapsible" id="${STATUSBAR_ID}-status" role="status" aria-expanded="false">
            <%block name="statusbar_panel">
                <p class="progver"><span lang="en">Librarian</span> v${th.app_version()}</p>
                <p class="copyright">2014-2015 <span lang="en">Outernet Inc</span></p>
            </%block>
            </div>
        </footer>

        <!-- inline JS templates -->
        <script type="text/template" id="modalContent">
            <div class="o-modal-overlay" id="modal-content">
                <div class="o-modal-window" role="window" id="modal-content-window" tabindex>
                    <button id="modal-content-close" class="o-modal-close" role="button" aria-controls="modal-content-window">
                        <span class="o-modal-close-label">${_('Close')}</span>
                        <span class="o-modal-close-icon icon"></span>
                    </button>
                    <div class="o-modal-content o-modal-panel" role="document" id="modal-panel">
                        <span class="o-modal-spinner">${_('Loading')}<span class="o-modal-spinner-loading-indicator">...</span></span>
                    </div>
                </div>
            </div>
        </script>

        <script type="text/template" id="modalLoadFailure">
            <div class="o-modal-load-failure o-modal-spinner">
                ${_('Content could not be loaded')}
            </div>
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
                mainPanelId: "${MAIN_PANEL_ID}"
            };
        }(this));
        </script>

        <script src="${assets['js/lui']}"></script>

        <%block name="extra_scripts"/>
    </body>
</html>
