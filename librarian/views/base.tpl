<!doctype html>

<html>
    <head>
        <meta charset="utf-8">
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        %# Translators, used in page title
        <title>{{ title }} :: {{ _('Librarian') }} v{{ app_version }}</title>
        <link rel="stylesheet" href="/static/css/{{ style }}.css">
    </head>
    <body>
        <div id="languages">
            % for locale, lang in languages:
                % if locale != request.locale:
                <a href="{{ i18n_path(locale=locale) }}">{{ lang }}</a>
                % else:
                <span class="current">{{ lang }}</span>
                % end
            % end
        </div>
        <div class="toolbar">
            %# Translators, used main navigation menu
            {{! h.link_other(_('Library'), i18n_path('/'), request.original_path, h.SPAN, _class="archive") }}
            %# Translators, used main navigation menu
            {{! h.link_other(_('Files'), i18n_path('/files/'), request.original_path, h.SPAN, _class="files") }}
            %# Translators, used main navigation menu
            {{! h.link_other(_('Apps'), i18n_path('/apps/'), request.original_path, h.SPAN, _class="apps") }}
            %# Translators, used main navigation menu
            {{! h.link_other(_('Favorites'), i18n_path('/favorites/'), request.original_path, h.SPAN, _class="favorites") }}
            %# Translators, used main navigation menu
            {{! h.link_other(_('Updates') + (' (%s)' % updates if updates > 0 else ''), i18n_path('/downloads/'), request.original_path, h.SPAN, _class="updates" + (updates > 0 and ' notice' or '')) }}
            %# Translators, used main navigation menu
            {{! h.link_other(_('Dashboard'), i18n_path('/dashboard/'), request.original_path, h.SPAN, _class="dashboard") }}
        </div>

        <div class="body">
        {{! base }}
        </div>

        <div class="footer">
        <p class="logo"><img src="/static/img/outernet_logo.png" alt="Outernet: Humanity's Public Library"></p>
        %# Translators, used in footer
        <p class="appver">{{ _('Librarian') }} v{{ app_version }}</p>
        <p class="copy">2014 Outernet Inc</p>
        </div>
    </body>
</html>
