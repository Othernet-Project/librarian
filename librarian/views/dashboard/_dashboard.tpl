<%namespace file="_dashboard_section.tpl" name="section"/>

% for plugin in plugins:
    % if request.params.get(plugin.get_name()):
        ${plugin.render(**context.kwargs)}
    % endif
% endfor
