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
            <div class="app-details">
            <span class="app-title"><a href="{{ app.url }}">{{ app.title }}</a></span>
            <span class="app-description">{{ h.trunc(app.description, 50) }}</span>
            %# Translators, refers to app author
            <span class="app-author">{{ _('author:') }} {{ app.author }}</span>
            %# Translators, refers to app version
            <span class="app-version">{{ _('version:') }} {{ app.version }}</span>
            </div>
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
