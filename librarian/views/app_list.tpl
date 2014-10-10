%# Translators, used as page title
% rebase('base', title=_('Apps'))

<h1>
%# Translators, used as page heading
{{ _('Apps') }}
</h1>

<ul class="app-list">
    % if apps:
        % for app in apps:
        <li id="app-{{ app.appid }}" data-url="{{ app.url }}" data-id="{{ app.appid }}">
            <a id="link-{{ app.appid }}" class="app-icon" href="{{ app.url }}"><img src="{{ app.url }}/icon.png"></a>
            <span class="app-title">{{ app.title }} v{{ app.version }}</span>
            <span class="app-desc">{{ app.description }}</span>
            % if app.icon_behavior:
            <script src="{{ app.url }}/behavior.js"></script>
            % end
        </li>
        % end
    % else:
        %# Translators, message show in app listing when no apps are present.
        <p>{{ _('No apps found.') }}</p>
    % end
</ul>
