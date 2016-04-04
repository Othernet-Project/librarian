import mock

import librarian_dashboard.dashboard as mod


@mock.patch.object(mod, 'template')
@mock.patch.object(mod.DashboardPlugin, 'get_context')
def test_plugin_context_error(get_context, mako_template):
    get_context.side_effect = ValueError('test')
    dashboard = mod.DashboardPlugin()

    dashboard.render()

    default_ctx = {'plugin': dashboard,
                   'name': dashboard.get_name(),
                   'heading': dashboard.get_heading(),
                   'classes': dashboard.get_formatted_classes()}
    mako_template.assert_called_once_with(
        mod.DashboardPlugin.plugin_error_template,
        **default_ctx
    )


@mock.patch.object(mod, 'template')
def test_plugin_render_error(mako_template):
    def error_on_normal_call(template_name, **kwargs):
        if template_name != mod.DashboardPlugin.plugin_error_template:
            raise ValueError('test')

    mako_template.side_effect = error_on_normal_call
    dashboard = mod.DashboardPlugin()

    dashboard.render()

    default_ctx = {'plugin': dashboard,
                   'name': dashboard.get_name(),
                   'heading': dashboard.get_heading(),
                   'classes': dashboard.get_formatted_classes()}

    calls = [
        mock.call(dashboard.get_template(), **default_ctx),
        mock.call(mod.DashboardPlugin.plugin_error_template, **default_ctx)
    ]
    mako_template.assert_has_calls(calls)
