<%inherit file="/base.tpl"/>
<%namespace file="_dashboard_section.tpl" name="section"/>

<%block name="title">
## Translators, used as page title
${_('Settings')}
</%block>

<div class="dashboard-sections o-collapsible" id="dashboard-sections">
    % for plugin in plugins:
        <% taborder = loop.index + 1 %>
        <%section:plugin name="${plugin.get_name()}" heading="${plugin.get_heading()}", extra_classes="${plugin.get_formatted_classes()}" taborder="${taborder}">
            ${plugin.render(**context.kwargs)}
        </%section:plugin>
    % endfor
</div>

<%block name="javascript_templates">
<script id="collapseIcon" type="text/template">
    <a href="javascript:void(0)" class="dash-expand-icon"></a>
</script>
</%block>

<%block name="extra_head">
<link rel="stylesheet" href="${assets['css/dashboard']}">
</%block>

<%block name="extra_scripts">
<script src="${assets['js/dashboard']}"></script>
</%block>
