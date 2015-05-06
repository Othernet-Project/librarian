<%inherit file="base.tpl"/>

<%block name="title">
## Translators, used as page title
${_('Dashboard')}
</%block>

<%block name="heading">
## Translators, used as page heading
${_('Dashboard')}
</%block>

% for plugin in plugins:
    ${plugin.render()}
% endfor

<%block name="javascript_templates">
<script id="collapseIcon" type="text/template">
    <a href="javascript:void(0)" class="dash-expand-icon"></a>
</script>
</%block>

<%block name="extra_scripts">
<script src="${th.static_url('sys:static', path='js/dashboard.js')}"></script>
% for p in plugins:
    ${p.render_javascript()}
% endfor
</%block>
