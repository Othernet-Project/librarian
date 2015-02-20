<!doctype html>

<html lang="{{ request.locale }}"{{! ' dir="rtl"' if is_rtl == True else ''}}>
    <head>
        <meta charset="utf-8">
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        %# Translators, used in page title
        <title>{{ title }} :: {{ _('Librarian') }} v{{ app_version }}</title>
        <link rel="stylesheet" href="/static/css/{{ style }}.css">
        <meta name="viewport" content="initial-scale=1, maximum-scale=1, user-scalable=no">
        % setdefault('redirect', None)
        % if redirect:
        <meta http-equiv="refresh" content="5; url={{ redirect }}">
        % end
    </head>
    <body>
        <header>
            <div id="toolbar" class="toolbar">
                % icon = '<span class="icon"></span>'
                %# Translators, used main navigation menu
                {{! h.link_other(icon + _('Library'), i18n_path('/'), request.original_path, h.SPAN, _class="archive navicon") }}
                %# Translators, used main navigation menu
                {{! h.link_other(icon + _('Files'), i18n_path('/files/'), request.original_path, h.SPAN, _class="files navicon") }}
                %# Translators, used main navigation menu
                {{! h.link_other(icon + _('Apps'), i18n_path('/apps/'), request.original_path, h.SPAN, _class="apps navicon") }}
                %# Translators, used main navigation menu
                {{! h.link_other(icon + _('Updates') + (' (%s)' % updates if updates > 0 else ''), i18n_path('/downloads/'), request.original_path, h.SPAN, _class="updates navicon" + (updates > 0 and ' notice' or '')) }}
                %# Translators, used main navigation menu
                {{! h.link_other(icon + _('Dashboard'), i18n_path('/dashboard/'), request.original_path, h.SPAN, _class="dashboard navicon") }}
            </div>
        </header>

        <div class="body">
        {{! base }}
        </div>

        <div id="languages" class="languages">
            % for locale, lang in languages:
                % if locale != request.locale:
                <a href="{{ i18n_path(locale=locale) }}">{{ lang }}</a>
                % else:
                <span class="current">{{ lang }}</span>
                % end
            % end
        </div>

        <div class="footer">
        <p class="logo"><img src="/static/img/outernet_logo.png" alt="Outernet: Humanity's Public Library"></p>
        %# Translators, used in footer
        <p class="appver">{{ _('Librarian') }} v{{ app_version }}</p>
        <p class="copy">2014 Outernet Inc</p>
        </div>

        <script src="/static/js/ui.js"></script>
        % setdefault('extra_scripts', '')
        {{! extra_scripts }}
    </body>
</html>
