<%inherit file="/base.tpl"/>
<%namespace name="forms" file="/ui/forms.tpl"/>
<%namespace file="_dashboard_section.tpl" name="section"/>

<%block name="title">
## Translators, used as page title
${_('Settings')}
</%block>

<div class="dashboard-sections o-collapsible" id="dashboard-sections">
    % for plugin in plugins:
        <% taborder = loop.index + 1 %>
        <%section:plugin name="${plugin.get_name()}" heading="${plugin.get_heading()}", extra_classes="${plugin.get_formatted_classes()}" taborder="${taborder}">
            % if request.params.get(plugin.get_name()):
            ${plugin.render(**context.kwargs)}
            % endif
        </%section:plugin>
    % endfor
</div>

<%block name="javascript_templates">
<script id="collapseIcon" type="text/template">
    <a href="javascript:void(0)" class="dash-expand-icon"></a>
</script>
<script type="text/template" id="spinnerIcon">
    <span class="icon icon-spinning-loader"></span>
</script>
<script type="text/template" id="dashboardLoadError">
    <% 
    errors = [_("Dashboard plugin could not be loaded due to application error.")] 
    %>
    ${forms.form_errors(errors)}
</script>
<script type="text/template" id="dashboardPluginError">
    <% 
    errors = [_("Dashboard plugin encountered an error from which it couldn't recover.")] 
    %>
    ${forms.form_errors(errors)}
</script>
</%block>

<%block name="extra_head">
<link rel="stylesheet" href="${assets['css/dashboard']}">
</%block>

<%block name="extra_scripts">
<script src="${assets['js/dashboard']}"></script>
</%block>

