<%inherit file="base.tpl"/>

<%block name="title">
## Translators, used as page title
${_('Dashboard')}
</%block>

<div class="dashboard-sections accordion">
    % for plugin in plugins:
    ${plugin.render()}
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
% for p in plugins:
    ${p.render_javascript()}
% endfor
</%block>
