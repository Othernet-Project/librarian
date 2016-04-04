<%namespace name="current_view" file="_${context['view']}.tpl"/>

<%!
# Mappings between facets and view urls

_ = lambda x: x

FACET_VIEW_MAPPINGS = (
    ('generic', _('Browse')),
    ('image', _('Gallery')),
    ('audio', _('Listen')),
    ('video', _('Watch')),
    ('html', _('Read')),
    ('updates', _('Updates')),
)

FACET_ICON_MAPPING = {
    'generic': 'list',
    'updates': 'clock',
    'image': 'gallery',
    'audio': 'listen',
    'video': 'watch',
    'html': 'read',
}


def get_default_views():
    yield FACET_VIEW_MAPPINGS[0]


def get_views(facet_types):
    for name, label in FACET_VIEW_MAPPINGS:
        if name in facet_types:
            yield (name, label)
%>

<% 
    view_has_sidebar = hasattr(current_view, 'sidebar')
%>

<div id="views-tabs-container">
    <nav id="views-tabs-strip" class="views-tabs-strip" role="tablist">
        ## The first item is:
        ##
        ## - Blank if current path is top-level and there is no search query
        ## - Link to complete file list if there is search query
        ## - Link to complete file list if invalid path is requested
        ## - Link to parent directory if no search query and not at top-level
        % if is_search or not is_successful:
            <a href="${i18n_url('files:path', path='')}" class="views-tabs-strip-tab views-tabs-special">
                <span class="file-list-icon icon icon-arrow-left"></span>
                ## Translators, label for a link that takes the user to
                ## main file/folder list from search results.
                <span class="label">${_('Go to complete file list')}</span>
            </a>
        % elif path != '.':
            <% uppath = '' if up == '.' else up + '/'%>
            <a href="${i18n_url('files:path', path=up)}" class="views-tabs-strip-tab views-tabs-special">
                <span class="file-list-icon icon icon-folder-up"></span>
                ## Translators, label for a link that takes the user up
                ## one level in folder hierarchy.
                <span class="label">${_('Go up one level')}</span>
            </a>
        % endif
        <% views = get_default_views() if is_search else get_views(facet_types) %>
        % for name, label in views:
            <%
            view_url = i18n_url('files:path', path=path, view=name)
            current = name == view
            icon = FACET_ICON_MAPPING[name]
            %>
            <a class="views-tabs-strip-tab ${'views-tabs-tab-current' if current else ''}" href="${view_url}" role="tab" data-view="${name}">
                <span class="icon icon-${icon}"></span>
                <span class="views-tabs-tab-label label">${_(label)}</span>
            </a>
        % endfor
    </nav>
</div>
<div class="views-container${' with-sidebar' if view_has_sidebar else ''}" id="views-container">
    <div class="views-main">
        ${current_view.body()}
    </div>
    % if view_has_sidebar:
        <div class="views-sidebar views-sidebar-${view}" id="views-sidebar">
            <div class="views-sidebar-content" id="views-sidebar-content">
                ${current_view.sidebar()}
            </div>
        </div>
    % endif
</div>

% if view_has_sidebar:
    <script type="text/template" id="sidebarRetract">
        <a class="views-sidebar-retract" href="javascript:void(0);" data-alt-label="${_('Show')}">
            <span class="icon icon-expand-right"></span>
            <span class="label">${_('Hide')}</span>
        </a>
    </script>
% endif

<script type="text/template" id="unknownAuthor">
    ${_('Unknown author')}
</script>
