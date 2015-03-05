%# Translators, used as page title
% scripts = ('<script src="%s"></script>' % url('sys:static', path='js/dashboard.js')) + ''.join([p.render_javascript() for p in plugins])
% rebase('base.tpl', title=_('Dashboard'), extra_scripts=scripts)

%# Translators, used as page heading
<h1>{{ _('Dashboard') }}</h1>

<div class="inner">
    % for plugin in plugins:
    {{! plugin.render() }}
    % end
</div>

<script id="collapseIcon" type="text/template">
    <a href="javascript:void(0)" class="dash-expand-icon"></a>
</script>
