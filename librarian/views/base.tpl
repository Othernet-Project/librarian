<!doctype html>

<html>
    <head>
        <meta charset="utf-8">
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <title>{{ title }} v{{ app_version }}</title>
        <link rel="stylesheet" href="/static/css/{{ style }}.css">
    </head>
    <body>
        <div="languages">
            % for locale, lang in languages:
                <a href="{{ i18n_path(locale=locale) }}">{{ lang }}</a>
            % end
        </div>
        <div class="toolbar">
            <a href="{{ i18n_path('/') }}">{{ _('Dashboard') }}</a>
            <a href="{{ i18n_path('/downloads/') }}">{{ _('Updates') }}</a>
            <a href="{{ i18n_path('/content/') }}">{{ _('Archive') }}</a>
        </div>

        <div class="body">
        {{! base }}
        </div>

        <div class="footer">
        <p class="appver">{{ _('Librarian') }} v{{ app_version }}</p>
        <p class="copy">2014 Outernet Inc</p>
        </div>
    </body>
</html>
