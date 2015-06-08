<!doctype html>

<html lang="${request.locale}"${' dir="rtl"' if th.is_rtl(request.locale) == True else ''}>
    <head>
        <meta charset="utf-8">
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        ## Translators, used in page title
        <title><%block name="title">Outernet</%block> :: ${_('Librarian')} v${app_version}</title>
        <link rel="stylesheet" href="${th.static_url('sys:static', path="css/%s.css" %  style)}">
        <meta name="viewport" content="initial-scale=1, maximum-scale=1, user-scalable=no">
        % if redirect is not UNDEFINED:
        <meta http-equiv="refresh" content="5; url=${redirect}">
        % endif
        <%block name="extra_head"/>
    </head>
    <body>
        <%block name="header">
        <header>
            <div id="toolbar" class="toolbar">
                <% icon = '<span class="icon"></span>' %>
                ## Translators, used main navigation menu
                % for mi in menu_group('main'):
                    % if mi.is_visible():
                        ${mi}
                    % endif
                % endfor
            </div>
        </header>
        </%block>

        <div class="body">
        <%block name="main">
            <h1><%block name="heading"/></h1>
            <%block name="content">
                <div class="inner">
                <%block name="inner">
                    ${self.body(**context.kwargs)}
                </%block>
                </div>
            </%block>
        </%block>
        </div>

        <div id="languages" class="languages">
            % for locale, lang in languages:
                % if locale != request.locale:
                <a href="${i18n_path(locale=locale)}" dir="${th.dir(locale)}" lang="${locale}">${lang}</a>
                % else:
                <span class="current" dir="${th.dir(locale)}" lang="${locale}">${lang}</span>
                % endif
            % endfor
        </div>

        <div class="footer">
        <p class="logo"><img src="${th.static_url('sys:static', path='img/outernet_logo.png')}" alt="Outernet: Humanity's Public Library"></p>
        ## Translators, used in footer
        <p class="appver">${_('Librarian')} v${app_version}</p>
        <p class="copy">2014 Outernet Inc</p>
        </div>

        <%block name="script_templates"/>
        <script src="${th.static_url('sys:static', path='js/ui.js')}"></script>
        <%block name="extra_scripts"/>
    </body>
</html>
